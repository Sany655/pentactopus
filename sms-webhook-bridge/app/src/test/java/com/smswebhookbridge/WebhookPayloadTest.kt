package com.smswebhookbridge

import okhttp3.HttpUrl.Companion.toHttpUrl
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

class WebhookPayloadTest {

    @Test
    fun testJsonPayloadStructure() {
        val eventId = "3f4b8a21-99ef-4c40-97b5-bf2193b2a26e"
        val sender = "+8801700000000"
        val message = "Hello from Webhook Bridge!"
        val receivedAt = "2026-10-05T12:30:00Z"
        val deviceId = "local-device-01"

        val json = JSONObject().apply {
            put("event_id", eventId)
            put("sender", sender)
            put("message", message)
            put("received_at", receivedAt)
            put("device_id", deviceId)
        }

        assertEquals(eventId, json.getString("event_id"))
        assertEquals(sender, json.getString("sender"))
        assertEquals(message, json.getString("message"))
        assertEquals(receivedAt, json.getString("received_at"))
        assertEquals(deviceId, json.getString("device_id"))
    }

    @Test
    fun testUrlEncodingForGetRequest() {
        val baseUrl = "https://example.com/api/sms/incoming"
        val eventId = "test-uuid"
        val sender = "+1 (555) 019-2834"
        val message = "Message with special chars & spaces = 100%!"
        val receivedAt = "2026-10-05T12:30:00+06:00"
        val deviceId = "device-test"

        val httpUrl = baseUrl.toHttpUrl().newBuilder()
            .addQueryParameter("event_id", eventId)
            .addQueryParameter("sender", sender)
            .addQueryParameter("message", message)
            .addQueryParameter("received_at", receivedAt)
            .addQueryParameter("device_id", deviceId)
            .build()

        val fullUrl = httpUrl.toString()

        // Verify URL encoding of spaces and special chars
        assertTrue(fullUrl.startsWith(baseUrl))
        assertEquals(sender, httpUrl.queryParameter("sender"))
        assertEquals(message, httpUrl.queryParameter("message"))
        assertEquals(receivedAt, httpUrl.queryParameter("received_at"))
        assertEquals(deviceId, httpUrl.queryParameter("device_id"))
    }
}
