package com.smswebhookbridge

import com.smswebhookbridge.util.PhoneNumberNormalizer
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PhoneNumberNormalizerTest {

    @Test
    fun testNormalizeStandardInternational() {
        assertEquals("+15551234567", PhoneNumberNormalizer.normalize("+1 (555) 123-4567"))
        assertEquals("+8801712345678", PhoneNumberNormalizer.normalize("+880 1712-345678"))
        assertEquals("+8801712345678", PhoneNumberNormalizer.normalize("008801712345678"))
    }

    @Test
    fun testNormalizeAlphanumericSender() {
        assertEquals("MYBANK", PhoneNumberNormalizer.normalize("MyBank"))
        assertEquals("VERIFY_CODE", PhoneNumberNormalizer.normalize("  VERIFY_CODE  "))
    }

    @Test
    fun testNormalizeMalformedSender() {
        assertEquals("", PhoneNumberNormalizer.normalize(null))
        assertEquals("", PhoneNumberNormalizer.normalize(""))
        assertEquals("", PhoneNumberNormalizer.normalize("   "))
        assertEquals("", PhoneNumberNormalizer.normalize("---"))
        assertEquals("", PhoneNumberNormalizer.normalize("+++"))
        assertEquals("", PhoneNumberNormalizer.normalize("()//.."))
    }

    @Test
    fun testMatchingSenderExactAndFormatted() {
        // Same formatted number
        assertTrue(PhoneNumberNormalizer.matches("+15551234567", "+1 (555) 123-4567"))
        assertTrue(PhoneNumberNormalizer.matches("+8801712345678", "+880 1712 345678"))

        // International vs national with 0 trunk
        assertTrue(PhoneNumberNormalizer.matches("+8801712345678", "01712345678"))
        assertTrue(PhoneNumberNormalizer.matches("01712345678", "+8801712345678"))

        // Alphanumeric sender match
        assertTrue(PhoneNumberNormalizer.matches("Google", "GOOGLE"))
        assertTrue(PhoneNumberNormalizer.matches("BANK_OTP", "bank_otp"))
    }

    @Test
    fun testNonMatchingSender() {
        // Completely different numbers
        assertFalse(PhoneNumberNormalizer.matches("+15551234567", "+15559876543"))
        assertFalse(PhoneNumberNormalizer.matches("+8801712345678", "+8801812345678"))

        // Alphanumeric mismatch
        assertFalse(PhoneNumberNormalizer.matches("Google", "Apple"))

        // Numbers with same prefix but different suffixes
        assertFalse(PhoneNumberNormalizer.matches("+15551234000", "+15551234999"))
    }

    @Test
    fun testMalformedSenderMatching() {
        assertFalse(PhoneNumberNormalizer.matches(null, "+15551234567"))
        assertFalse(PhoneNumberNormalizer.matches("+15551234567", null))
        assertFalse(PhoneNumberNormalizer.matches("", ""))
        assertFalse(PhoneNumberNormalizer.matches("---", "+++"))
        assertFalse(PhoneNumberNormalizer.matches("   ", "+15551234567"))
    }
}
