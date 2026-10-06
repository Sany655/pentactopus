package com.smswebhookbridge.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import com.smswebhookbridge.BridgeApplication
import com.smswebhookbridge.service.WebhookForwardWorker
import com.smswebhookbridge.util.PhoneNumberNormalizer
import com.smswebhookbridge.util.SecurityUtils
import java.time.Instant

class SmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action
        if (action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION &&
            action != Telephony.Sms.Intents.SMS_DELIVER_ACTION
        ) {
            return
        }

        val app = context.applicationContext as BridgeApplication
        val prefs = app.preferencesManager
        val config = prefs.getConfig()

        if (!config.isEnabled) {
            return
        }

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        if (messages.isNullOrEmpty()) {
            return
        }

        // Group parts by originating address (to handle multi-part long SMS)
        val groupedMessages = mutableMapOf<String, StringBuilder>()
        for (sms in messages) {
            val sender = sms.displayOriginatingAddress ?: sms.originatingAddress ?: continue
            val body = sms.displayMessageBody ?: sms.messageBody ?: ""
            val builder = groupedMessages.getOrPut(sender) { StringBuilder() }
            builder.append(body)
        }

        for ((incomingSender, bodyBuilder) in groupedMessages) {
            val messageBody = bodyBuilder.toString()

            // Strict sender filtering
            val isMatchingSender = PhoneNumberNormalizer.matches(config.senderNumber, incomingSender)
            if (!isMatchingSender) {
                // Ignore messages from all other senders without logging body
                continue
            }

            val nowStr = Instant.now().toString()
            prefs.lastMatchingSmsSender = incomingSender
            prefs.lastMatchingSmsBody = messageBody
            prefs.lastMatchingSmsTime = nowStr

            app.logRepository.addLog(
                "INFO",
                "Matching SMS received from $incomingSender (${messageBody.length} chars)"
            )

            // Deduplication protection & queue
            val event = app.eventRepository.enqueueEventIfUnique(
                sender = incomingSender,
                message = messageBody,
                deviceId = config.deviceId
            )

            if (event == null) {
                app.logRepository.addLog(
                    "WARN",
                    "Duplicate SMS detected from $incomingSender within deduplication window. Webhook suppressed."
                )
                continue
            }

            app.logRepository.addLog(
                "INFO",
                "Event enqueued: ${event.eventId}. Triggering background webhook worker..."
            )

            WebhookForwardWorker.enqueue(
                context = context,
                eventId = event.eventId,
                backoffDelaySeconds = config.retryIntervalSeconds.toLong()
            )
        }
    }
}
