package com.pentactopus.android

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class AndroidModelClient(
    private val endpoint: String,
    private val model: String,
    private val apiKey: String,
) {
    fun complete(prompt: String, context: String): String {
        require(ModelEndpointPolicy.allows(endpoint)) {
            "Use HTTPS for providers, or HTTP only for a localhost model on this device."
        }
        require(prompt.isNotBlank()) { "Prompt must not be empty." }
        require(model.isNotBlank()) { "Model name must not be empty." }
        if (ModelEndpointPolicy.requiresApiKey(endpoint)) {
            require(apiKey.isNotBlank()) { "A provider API key is required." }
        }

        val requestBody = JSONObject()
            .put("model", model)
            .put(
                "messages",
                JSONArray()
                    .put(JSONObject().put("role", "system").put("content", context))
                    .put(JSONObject().put("role", "user").put("content", prompt)),
            )
            .put("temperature", 0.2)
            .toString()
        val connection = URL(endpoint).openConnection() as HttpURLConnection
        try {
            connection.instanceFollowRedirects = false
            connection.requestMethod = "POST"
            connection.connectTimeout = 15_000
            connection.readTimeout = 30_000
            connection.doOutput = true
            if (ModelEndpointPolicy.requiresApiKey(endpoint)) {
                connection.setRequestProperty("Authorization", "Bearer $apiKey")
            }
            connection.setRequestProperty("Content-Type", "application/json")
            connection.outputStream.use { it.write(requestBody.toByteArray(Charsets.UTF_8)) }

            val status = connection.responseCode
            val responseStream = if (status in 200..299) connection.inputStream else connection.errorStream
            val response = responseStream?.use { input ->
                val output = java.io.ByteArrayOutputStream()
                val buffer = ByteArray(8_192)
                var total = 0
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    total += count
                    require(total <= MAX_RESPONSE_BYTES) {
                        "Model provider response exceeded the local size limit."
                    }
                    output.write(buffer, 0, count)
                }
                output.toString(Charsets.UTF_8.name())
            }.orEmpty()
            if (status !in 200..299) {
                throw IllegalStateException("Model provider returned HTTP $status.")
            }
            val choices = JSONObject(response).optJSONArray("choices")
                ?: throw IllegalStateException("Model provider returned no choices.")
            val message = choices.optJSONObject(0)?.optJSONObject("message")
            return message?.optString("content")?.takeIf(String::isNotBlank)
                ?: throw IllegalStateException("Model provider returned an empty response.")
        } finally {
            connection.disconnect()
        }
    }

    companion object {
        private const val MAX_RESPONSE_BYTES = 1_048_576
    }
}
