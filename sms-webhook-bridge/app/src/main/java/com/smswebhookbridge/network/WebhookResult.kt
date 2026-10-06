package com.smswebhookbridge.network

data class WebhookResult(
    val isSuccess: Boolean,
    val statusCode: Int = 0,
    val isRetryable: Boolean = false,
    val errorMessage: String? = null
)
