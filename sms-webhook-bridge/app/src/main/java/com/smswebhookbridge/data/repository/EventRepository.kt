package com.smswebhookbridge.data.repository

import com.smswebhookbridge.data.AppDatabase
import com.smswebhookbridge.data.model.EventStatus
import com.smswebhookbridge.data.model.WebhookEvent
import java.time.Duration
import java.time.Instant

class EventRepository(private val db: AppDatabase) {

    /**
     * Checks if this event is a duplicate within the deduplication window (default 5 min).
     * If not duplicate, persists to queue in PENDING status.
     */
    fun enqueueEventIfUnique(
        sender: String,
        message: String,
        deviceId: String,
        dedupWindowMinutes: Long = 5
    ): WebhookEvent? {
        val cutoff = Instant.now().minus(Duration.ofMinutes(dedupWindowMinutes)).toString()
        if (db.isDuplicateRecent(sender, message, cutoff)) {
            return null // Duplicate detected and suppressed
        }

        val event = WebhookEvent(
            sender = sender,
            message = message,
            deviceId = deviceId,
            status = EventStatus.PENDING
        )
        val inserted = db.insertEvent(event)
        return if (inserted) event else null
    }

    fun updateStatus(
        eventId: String,
        status: EventStatus,
        attemptCount: Int,
        responseCode: Int? = null,
        errorMessage: String? = null,
        deletedFromInbox: Boolean? = null
    ) {
        db.updateEventStatus(
            eventId = eventId,
            status = status,
            attemptCount = attemptCount,
            lastAttemptAt = Instant.now().toString(),
            responseCode = responseCode,
            errorMessage = errorMessage,
            deletedFromInbox = deletedFromInbox
        )
    }

    fun getPendingEvents(): List<WebhookEvent> = db.getPendingEvents()

    fun getAllEvents(limit: Int = 100): List<WebhookEvent> = db.getAllEvents(limit)

    fun getEventById(eventId: String): WebhookEvent? = db.getEventById(eventId)
}
