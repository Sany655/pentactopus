package com.smswebhookbridge.data.model

import java.time.Instant
import java.util.UUID

enum class EventStatus {
    PENDING,
    IN_PROGRESS,
    SUCCESS,
    FAILED
}

data class WebhookEvent(
    val eventId: String = UUID.randomUUID().toString(),
    val sender: String,
    val message: String,
    val receivedAt: String = Instant.now().toString(),
    val deviceId: String,
    val status: EventStatus = EventStatus.PENDING,
    val attemptCount: Int = 0,
    val lastAttemptAt: String? = null,
    val responseCode: Int? = null,
    val errorMessage: String? = null,
    val deletedFromInbox: Boolean = false
)
