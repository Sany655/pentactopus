package com.smswebhookbridge.data.model

import java.time.Instant

data class AppLog(
    val id: Long = 0,
    val timestamp: String = Instant.now().toString(),
    val level: String = "INFO",
    val message: String
)
