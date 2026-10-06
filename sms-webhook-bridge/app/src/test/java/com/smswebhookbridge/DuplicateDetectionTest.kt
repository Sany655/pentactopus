package com.smswebhookbridge

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.Duration
import java.time.Instant

class DuplicateDetectionTest {

    // Simulates duplicate detector logic without Android SQLite dependency for pure unit testing
    class MemoryDuplicateDetector(private val windowMinutes: Long = 5) {
        private val cache = mutableListOf<Triple<String, String, Instant>>()

        fun isDuplicateAndRecord(sender: String, message: String, now: Instant = Instant.now()): Boolean {
            val cutoff = now.minus(Duration.ofMinutes(windowMinutes))
            // Clean older entries
            cache.removeAll { it.third.isBefore(cutoff) }

            val exists = cache.any { it.first == sender && it.second == message }
            if (exists) {
                return true
            }
            cache.add(Triple(sender, message, now))
            return false
        }
    }

    @Test
    fun testDuplicateDetectionWithinWindow() {
        val detector = MemoryDuplicateDetector(5)
        val t0 = Instant.parse("2026-10-05T12:00:00Z")

        // First message is unique
        val dup1 = detector.isDuplicateAndRecord("+15551234567", "Your code is 4455", t0)
        assertFalse("First message must not be a duplicate", dup1)

        // Same message 1 minute later -> duplicate!
        val t1 = t0.plus(Duration.ofMinutes(1))
        val dup2 = detector.isDuplicateAndRecord("+15551234567", "Your code is 4455", t1)
        assertTrue("Identical message within 5 minutes must be flagged as duplicate", dup2)
    }

    @Test
    fun testDifferentMessageOrSenderNotDuplicate() {
        val detector = MemoryDuplicateDetector(5)
        val t0 = Instant.parse("2026-10-05T12:00:00Z")

        detector.isDuplicateAndRecord("+15551234567", "Your code is 4455", t0)

        // Same sender, different message -> not duplicate
        val diffMsg = detector.isDuplicateAndRecord("+15551234567", "Your code is 9988", t0)
        assertFalse("Different message content must not be a duplicate", diffMsg)

        // Different sender, same message -> not duplicate
        val diffSender = detector.isDuplicateAndRecord("+15559876543", "Your code is 4455", t0)
        assertFalse("Different sender must not be a duplicate", diffSender)
    }

    @Test
    fun testMessageAfterWindowExpiryNotDuplicate() {
        val detector = MemoryDuplicateDetector(5)
        val t0 = Instant.parse("2026-10-05T12:00:00Z")

        detector.isDuplicateAndRecord("+15551234567", "Your code is 4455", t0)

        // 6 minutes later (past 5 min window) -> not duplicate
        val t2 = t0.plus(Duration.ofMinutes(6))
        val afterExpiry = detector.isDuplicateAndRecord("+15551234567", "Your code is 4455", t2)
        assertFalse("Message received after window expiry should not be flagged duplicate", afterExpiry)
    }
}
