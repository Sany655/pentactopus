package com.smswebhookbridge.data.model

data class WebhookConfig(
    val senderNumber: String = "",
    val webhookUrl: String = "",
    val httpMethod: String = "POST",
    val authToken: String = "",
    val isEnabled: Boolean = false,
    val maxRetries: Int = 3,
    val retryIntervalSeconds: Int = 10,
    val deleteMatchingContentEnabled: Boolean = false,
    val deleteTriggerNumber: String = "",
    val deviceId: String = ""
) {
    val isHttps: Boolean
        get() = webhookUrl.startsWith("https://", ignoreCase = true)

    val isValid: Boolean
        get() = senderNumber.isNotBlank() && isHttps
}
