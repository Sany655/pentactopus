package com.pentactopus.android

import android.util.Base64
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL
import java.security.MessageDigest
import java.security.SecureRandom

data class DeviceTaskSnapshot(
    val queuedCount: Int,
    val activeStatuses: List<String>,
)

class AndroidDeviceApi(
    private val serverUrl: String,
    private val deviceId: String?,
    private val identity: AndroidDeviceIdentity,
) {
    fun pair(name: String, pairingCode: String): String {
        require(isSecureServerUrl(serverUrl)) { "Server URL must use HTTPS." }
        require(name.matches(Regex("^[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}$"))) {
            "Device name is invalid."
        }
        require(pairingCode.length in 8..32) { "Pairing code is invalid." }
        val result = request(
            method = "POST",
            path = "/api/v1/devices/register",
            body = JSONObject()
                .put("pairing_code", pairingCode)
                .put("name", name)
                .put("platform", "android")
                .put("public_key", identity.publicKeyBase64Url())
                .toString(),
            signed = false,
        )
        return result.getString("device_id")
    }

    fun heartbeat() {
        signedRequest("POST", "/api/v1/devices/me/heartbeat", "{}")
    }

    fun pollTasks(): DeviceTaskSnapshot {
        val data = signedRequest("GET", "/api/v1/devices/me/tasks", "")
        val tasks = data.optJSONArray("tasks")
        val active = data.optJSONArray("active_task_updates")
        return DeviceTaskSnapshot(
            queuedCount = tasks?.length() ?: 0,
            activeStatuses = if (active == null) {
                emptyList()
            } else {
                (0 until active.length()).map { index ->
                    active.getJSONObject(index).optString("status", "unknown")
                }
            },
        )
    }

    fun claimTask(taskId: String): JSONObject? {
        val data = request(
            "POST",
            "/api/v1/tasks/$taskId/claim",
            "{}",
            signed = true,
        )
        return data.optJSONObject("task")
    }

    fun transitionTask(taskId: String, status: String, outcomeCode: String? = null) {
        val body = JSONObject().put("status", status)
        if (outcomeCode != null) body.put("outcome_code", outcomeCode)
        signedRequest("POST", "/api/v1/tasks/$taskId/transitions", body.toString())
    }

    private fun signedRequest(method: String, path: String, body: String): JSONObject =
        request(method, path, body, signed = true)

    private fun request(method: String, path: String, body: String, signed: Boolean): JSONObject {
        require(isSecureServerUrl(serverUrl)) { "Server URL must be an HTTPS origin." }
        val bytes = body.toByteArray(Charsets.UTF_8)
        val connection = URL(serverUrl.trimEnd('/') + path).openConnection() as HttpURLConnection
        connection.instanceFollowRedirects = false
        try {
            connection.requestMethod = method
            connection.connectTimeout = 15_000
            connection.readTimeout = 20_000
            connection.setRequestProperty("Accept", "application/json")
            if (method != "GET") {
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
            }
            if (signed) {
                val id = deviceId ?: throw IllegalStateException("This device has not been paired.")
                val timestamp = (System.currentTimeMillis() / 1000L).toString()
                val nonce = Base64.encodeToString(
                    ByteArray(24).also(SecureRandom()::nextBytes),
                    Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING,
                )
                val canonical = listOf(
                    method.uppercase(),
                    path,
                    timestamp,
                    nonce,
                    sha256Hex(bytes),
                ).joinToString("\n")
                val signature = Base64.encodeToString(
                    identity.sign(canonical.toByteArray(Charsets.UTF_8)),
                    Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING,
                )
                connection.setRequestProperty("X-Device-Id", id)
                connection.setRequestProperty("X-Device-Timestamp", timestamp)
                connection.setRequestProperty("X-Device-Nonce", nonce)
                connection.setRequestProperty("X-Device-Signature", signature)
            }
            if (method != "GET" && bytes.isNotEmpty()) {
                connection.outputStream.use { it.write(bytes) }
            }
            val status = connection.responseCode
            if (status == HttpURLConnection.HTTP_NO_CONTENT) return JSONObject()
            val stream = if (status in 200..299) connection.inputStream else connection.errorStream
            val response = stream?.use { input ->
                val output = java.io.ByteArrayOutputStream()
                val buffer = ByteArray(8192)
                var total = 0
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    total += count
                    require(total <= MAX_RESPONSE_BYTES) { "Server response exceeded the local size limit." }
                    output.write(buffer, 0, count)
                }
                output.toString(Charsets.UTF_8.name())
            }.orEmpty()
            if (status !in 200..299) {
                throw IllegalStateException("Pentactopus server returned HTTP $status.")
            }
            val envelope = JSONObject(response)
            require(envelope.optString("schema_version") == API_SCHEMA_VERSION) {
                "The server returned an unsupported API schema version."
            }
            return envelope.optJSONObject("data")
                ?: throw IllegalStateException("The server response did not contain data.")
        } finally {
            connection.disconnect()
        }
    }

    private fun sha256Hex(value: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(value)
            .joinToString("") { "%02x".format(it) }

    private fun isSecureServerUrl(value: String): Boolean = runCatching {
        val uri = URI(value)
        uri.scheme.equals("https", ignoreCase = true) &&
            !uri.host.isNullOrBlank() &&
            uri.rawUserInfo == null &&
            (uri.rawPath.isNullOrEmpty() || uri.rawPath == "/") &&
            uri.rawQuery == null &&
            uri.rawFragment == null
    }.getOrDefault(false)

    companion object {
        private const val API_SCHEMA_VERSION = "1.0.3"
        private const val MAX_RESPONSE_BYTES = 2 * 1024 * 1024
    }
}
