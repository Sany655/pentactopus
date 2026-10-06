package com.smswebhookbridge.data.model

data class SmsMessageData(
    val sender: String,
    val body: String,
    val timestampMillis: Long = System.currentTimeMillis()
)
