package com.smswebhookbridge.service

import android.content.Context
import androidx.work.BackoffPolicy
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import com.smswebhookbridge.BridgeApplication
import com.smswebhookbridge.data.model.EventStatus
import com.smswebhookbridge.util.SecurityUtils
import java.time.Instant
import java.util.concurrent.TimeUnit

class WebhookForwardWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val app = applicationContext as BridgeApplication
        val eventId = inputData.getString(KEY_EVENT_ID)

        if (eventId.isNullOrBlank()) {
            return Result.failure()
        }

        val event = app.eventRepository.getEventById(eventId)
        if (event == null) {
            app.logRepository.addLog("WARN", "Worker could not find event: $eventId")
            return Result.failure()
        }

        val config = app.preferencesManager.getConfig()
        val currentAttempt = runAttemptCount + 1

        app.eventRepository.updateStatus(
            eventId = event.eventId,
            status = EventStatus.IN_PROGRESS,
            attemptCount = currentAttempt
        )

        app.logRepository.addLog(
            "INFO",
            "Transmitting webhook event ${event.eventId} (Attempt $currentAttempt/${config.maxRetries}) to ${config.webhookUrl} [Auth: ${SecurityUtils.maskToken(config.authToken)}]"
        )

        val result = app.webhookClient.sendWebhook(config, event)

        return if (result.isSuccess) {
            val nowStr = Instant.now().toString()
            app.eventRepository.updateStatus(
                eventId = event.eventId,
                status = EventStatus.SUCCESS,
                attemptCount = currentAttempt,
                responseCode = result.statusCode,
                errorMessage = null
            )
            app.preferencesManager.lastWebhookStatus = "HTTP ${result.statusCode} OK"
            app.preferencesManager.lastWebhookTime = nowStr
            app.preferencesManager.lastError = null

            app.logRepository.addLog(
                "INFO",
                "Webhook event ${event.eventId} delivered successfully (HTTP ${result.statusCode})"
            )

            // Content deletion trigger feature:
            if (config.deleteMatchingContentEnabled && config.deleteTriggerNumber.isNotBlank()) {
                val wasDeleted = app.smsDeleteManager.deleteMessageIfTriggered(event.sender, event.message)
                if (wasDeleted) {
                    app.eventRepository.updateStatus(
                        eventId = event.eventId,
                        status = EventStatus.SUCCESS,
                        attemptCount = currentAttempt,
                        responseCode = result.statusCode,
                        deletedFromInbox = true
                    )
                }
            }

            Result.success()
        } else {
            val errorMsg = result.errorMessage ?: "Unknown transmission failure"
            app.preferencesManager.lastWebhookStatus = if (result.statusCode > 0) "HTTP ${result.statusCode} Error" else "Network Error"
            app.preferencesManager.lastError = errorMsg

            if (result.isRetryable && runAttemptCount < config.maxRetries) {
                app.eventRepository.updateStatus(
                    eventId = event.eventId,
                    status = EventStatus.PENDING,
                    attemptCount = currentAttempt,
                    responseCode = result.statusCode,
                    errorMessage = errorMsg
                )
                app.logRepository.addLog(
                    "WARN",
                    "Webhook failed: $errorMsg. Will retry with exponential backoff (attempt $currentAttempt/${config.maxRetries})"
                )
                Result.retry()
            } else {
                app.eventRepository.updateStatus(
                    eventId = event.eventId,
                    status = EventStatus.FAILED,
                    attemptCount = currentAttempt,
                    responseCode = result.statusCode,
                    errorMessage = errorMsg
                )
                app.logRepository.addLog(
                    "ERROR",
                    "Webhook permanently failed for event ${event.eventId}: $errorMsg"
                )
                Result.failure()
            }
        }
    }

    companion object {
        const val KEY_EVENT_ID = "key_event_id"

        fun enqueue(context: Context, eventId: String, backoffDelaySeconds: Long = 10) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val workRequest = OneTimeWorkRequestBuilder<WebhookForwardWorker>()
                .setConstraints(constraints)
                .setInputData(workDataOf(KEY_EVENT_ID to eventId))
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    backoffDelaySeconds,
                    TimeUnit.SECONDS
                )
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "forward_$eventId",
                ExistingWorkPolicy.REPLACE,
                workRequest
            )
        }
    }
}
