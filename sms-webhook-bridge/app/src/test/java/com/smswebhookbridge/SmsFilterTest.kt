package com.smswebhookbridge

import com.smswebhookbridge.util.PhoneNumberNormalizer
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SmsFilterTest {

    private val configuredSender = "+8801712345678"

    @Test
    fun testExactMatchPasses() {
        assertTrue(PhoneNumberNormalizer.matches(configuredSender, "+8801712345678"))
    }

    @Test
    fun testFormattedMatchPasses() {
        assertTrue(PhoneNumberNormalizer.matches(configuredSender, "+880 1712-345678"))
        assertTrue(PhoneNumberNormalizer.matches(configuredSender, "01712345678"))
    }

    @Test
    fun testUnrelatedSenderIgnored() {
        assertFalse(PhoneNumberNormalizer.matches(configuredSender, "+8801999999999"))
        assertFalse(PhoneNumberNormalizer.matches(configuredSender, "+1234567890"))
        assertFalse(PhoneNumberNormalizer.matches(configuredSender, "UNKNOWN_BANK"))
    }

    @Test
    fun testMalformedSenderIgnored() {
        assertFalse(PhoneNumberNormalizer.matches(configuredSender, null))
        assertFalse(PhoneNumberNormalizer.matches(configuredSender, ""))
        assertFalse(PhoneNumberNormalizer.matches(configuredSender, "   "))
        assertFalse(PhoneNumberNormalizer.matches(configuredSender, "---//..."))
    }

    @Test
    fun testAlphanumericSenderFiltering() {
        val configuredAlpha = "MY_BANK_ALERT"
        assertTrue(PhoneNumberNormalizer.matches(configuredAlpha, "MY_BANK_ALERT"))
        assertTrue(PhoneNumberNormalizer.matches(configuredAlpha, "my_bank_alert"))
        assertFalse(PhoneNumberNormalizer.matches(configuredAlpha, "OTHER_BANK"))
    }
}
