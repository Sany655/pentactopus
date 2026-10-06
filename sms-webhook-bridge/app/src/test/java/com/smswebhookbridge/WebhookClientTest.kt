package com.smswebhookbridge

import com.smswebhookbridge.data.model.WebhookConfig
import com.smswebhookbridge.data.model.WebhookEvent
import com.smswebhookbridge.network.WebhookClient
import com.smswebhookbridge.network.WebhookResult
import com.smswebhookbridge.util.SecurityUtils
import kotlinx.coroutines.runBlocking
import okhttp3.OkHttpClient
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import okhttp3.mockwebserver.RecordedRequest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.util.UUID

class WebhookClientTest {

    private lateinit var mockServer: MockWebServer
    private lateinit var webhookClient: WebhookClient

    @Before
    fun setUp() {
        mockServer = MockWebServer()
        mockServer.start()
        webhookClient = WebhookClient()
    }

    @After
    fun tearDown() {
        mockServer.shutdown()
    }

    @Test
    fun testRejectsInsecureHttpUrl() = runBlocking {
        val config = WebhookConfig(
            senderNumber = "+15551234567",
            webhookUrl = "http://insecure-api.example.com/api/sms/incoming", // Plain HTTP
            httpMethod = "POST"
        )
        val event = WebhookEvent(
            sender = "+15551234567",
            message = "Test message",
            deviceId = "test-device"
        )

        val result = webhookClient.sendWebhook(config, event)
        assertFalse("HTTP (non-HTTPS) URLs must be strictly rejected", result.isSuccess)
        assertFalse("Security rejection must not be retried", result.isRetryable)
        assertTrue(result.errorMessage?.contains("HTTPS") == true)
    }

    @Test
    fun testSecurityUtilsValidatesHttps() {
        assertTrue(SecurityUtils.isValidHttpsUrl("https://webhook.site/abc-123"))
        assertTrue(SecurityUtils.isValidHttpsUrl("https://api.mycompany.com:8443/sms"))
        assertFalse(SecurityUtils.isValidHttpsUrl("http://insecure.site/webhook"))
        assertFalse(SecurityUtils.isValidHttpsUrl("ftp://files.site/webhook"))
        assertFalse(SecurityUtils.isValidHttpsUrl("not a url"))
        assertFalse(SecurityUtils.isValidHttpsUrl(""))
        assertFalse(SecurityUtils.isValidHttpsUrl(null))
    }

    @Test
    fun testTokenMaskingPreventsExposure() {
        assertEquals("(none)", SecurityUtils.maskToken(null))
        assertEquals("(none)", SecurityUtils.maskToken(""))
        assertEquals("****", SecurityUtils.maskToken("1234"))
        val masked = SecurityUtils.maskToken("my-super-secret-production-token")
        assertFalse("Masked string must not contain middle secrets", masked.contains("super-secret"))
        assertTrue("Masked string contains asterisk placeholder", masked.contains("****"))
    }

    @Test
    fun testSmsMaskingForPrivacy() {
        val longSms = "This is a very confidential message with OTP 987654 sent for authentication"
        val masked = SecurityUtils.maskSms(longSms, 20)
        assertTrue(masked.contains("..."))
        assertTrue(masked.length < longSms.length)
    }
}
