package com.smswebhookbridge.network

import com.smswebhookbridge.data.model.WebhookConfig
import com.smswebhookbridge.data.model.WebhookEvent
import com.smswebhookbridge.util.SecurityUtils
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.util.concurrent.TimeUnit

class WebhookClient(
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .retryOnConnectionFailure(true)
        .build()
) {

    /**
     * Executes the webhook request according to the configuration and event.
     */
    suspend fun sendWebhook(config: WebhookConfig, event: WebhookEvent): WebhookResult = withContext(Dispatchers.IO) {
        val targetUrl = config.webhookUrl.trim()

        // 1. Enforce HTTPS strictly
        if (!SecurityUtils.isValidHttpsUrl(targetUrl)) {
            return@withContext WebhookResult(
                isSuccess = false,
                statusCode = 0,
                isRetryable = false,
                errorMessage = "Security violation: Only HTTPS URLs are permitted (received: $targetUrl)"
            )
        }

        try {
            val request = if (config.httpMethod.equals("GET", ignoreCase = true)) {
                buildGetRequest(targetUrl, config.authToken, event)
            } else {
                buildPostRequest(targetUrl, config.authToken, event)
            } ?: return@withContext WebhookResult(
                isSuccess = false,
                statusCode = 0,
                isRetryable = false,
                errorMessage = "Failed to parse webhook URL: $targetUrl"
            )

            client.newCall(request).execute().use { response ->
                val code = response.code
                val isSuccess = response.isSuccessful

                if (isSuccess) {
                    WebhookResult(isSuccess = true, statusCode = code)
                } else {
                    // 429 Too Many Requests is retryable, but other 4xx client errors are fatal
                    val retryable = code == 429 || code >= 500
                    val bodySnippet = response.body?.string()?.take(200)?.trim()
                    val errorDetail = "HTTP $code ${response.message}" +
                            if (!bodySnippet.isNullOrBlank()) " - $bodySnippet" else ""

                    WebhookResult(
                        isSuccess = false,
                        statusCode = code,
                        isRetryable = retryable,
                        errorMessage = errorDetail
                    )
                }
            }
        } catch (e: SocketTimeoutException) {
            WebhookResult(
                isSuccess = false,
                statusCode = 0,
                isRetryable = true,
                errorMessage = "Connection timeout (15s): ${e.message}"
            )
        } catch (e: UnknownHostException) {
            WebhookResult(
                isSuccess = false,
                statusCode = 0,
                isRetryable = true,
                errorMessage = "Network unreachable / Host unknown: ${e.message}"
            )
        } catch (e: IOException) {
            WebhookResult(
                isSuccess = false,
                statusCode = 0,
                isRetryable = true,
                errorMessage = "I/O network error: ${e.message}"
            )
        } catch (e: Exception) {
            WebhookResult(
                isSuccess = false,
                statusCode = 0,
                isRetryable = false,
                errorMessage = "Unexpected transmission error: ${e.message}"
            )
        }
    }

    private fun buildPostRequest(url: String, token: String?, event: WebhookEvent): Request? {
        val jsonPayload = JSONObject().apply {
            put("event_id", event.eventId)
            put("sender", event.sender)
            put("message", event.message)
            put("received_at", event.receivedAt)
            put("device_id", event.deviceId)
        }.toString()

        val mediaType = "application/json; charset=utf-8".toMediaType()
        val body = jsonPayload.toRequestBody(mediaType)

        val builder = Request.Builder()
            .url(url)
            .post(body)
            .header("Content-Type", "application/json")
            .header("X-Device-Id", event.deviceId)
            .header("X-Event-Id", event.eventId)

        if (!token.isNullOrBlank()) {
            builder.header("Authorization", "Bearer ${token.trim()}")
        }

        return builder.build()
    }

    private fun buildGetRequest(url: String, token: String?, event: WebhookEvent): Request? {
        val httpUrl = url.toHttpUrlOrNull() ?: return null

        val urlWithParams = httpUrl.newBuilder()
            .addQueryParameter("event_id", event.eventId)
            .addQueryParameter("sender", event.sender)
            .addQueryParameter("message", event.message)
            .addQueryParameter("received_at", event.receivedAt)
            .addQueryParameter("device_id", event.deviceId)
            .build()

        val builder = Request.Builder()
            .url(urlWithParams)
            .get()
            .header("X-Device-Id", event.deviceId)
            .header("X-Event-Id", event.eventId)

        if (!token.isNullOrBlank()) {
            builder.header("Authorization", "Bearer ${token.trim()}")
        }

        return builder.build()
    }
}
