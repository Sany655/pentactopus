package com.smswebhookbridge.util

import java.net.URI

object SecurityUtils {

    /**
     * Strictly verifies that the provided URL uses HTTPS protocol.
     */
    fun isValidHttpsUrl(url: String?): Boolean {
        if (url.isNullOrBlank()) return false
        return try {
            val uri = URI(url.trim())
            uri.scheme.equals("https", ignoreCase = true) && !uri.host.isNullOrBlank()
        } catch (_: Exception) {
            false
        }
    }

    /**
     * Masks an authentication token so it can be safely displayed or logged.
     */
    fun maskToken(token: String?): String {
        if (token.isNullOrBlank()) return "(none)"
        return if (token.length <= 4) {
            "****"
        } else {
            "${token.take(2)}****${token.takeLast(2)}"
        }
    }

    /**
     * Masks SMS message body for privacy in general log outputs.
     */
    fun maskSms(message: String?, maxLength: Int = 20): String {
        if (message.isNullOrBlank()) return "(empty)"
        val trimmed = message.trim()
        return if (trimmed.length <= maxLength) {
            trimmed
        } else {
            "${trimmed.take(maxLength)}... [${trimmed.length} chars]"
        }
    }
}
