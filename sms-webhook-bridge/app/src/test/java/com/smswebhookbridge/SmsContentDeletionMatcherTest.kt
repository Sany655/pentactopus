package com.smswebhookbridge

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SmsContentDeletionMatcherTest {

    // Evaluates deletion match rule according to app logic
    private fun shouldTriggerDeletion(
        messageBody: String,
        deleteTriggerNumber: String,
        isEnabled: Boolean
    ): Boolean {
        if (!isEnabled || deleteTriggerNumber.isBlank()) return false
        return messageBody.contains(deleteTriggerNumber.trim())
    }

    @Test
    fun testContentMatchingSpecificNumberTriggersDeletion() {
        val trigger = "849201"
        val messageWithCode = "Your verification code is 849201. Do not share this."

        val shouldDelete = shouldTriggerDeletion(messageWithCode, trigger, isEnabled = true)
        assertTrue("Message containing the specific number must trigger deletion", shouldDelete)
    }

    @Test
    fun testContentWithoutSpecificNumberDoesNotTriggerDeletion() {
        val trigger = "849201"
        val messageDifferentCode = "Your verification code is 123456. Do not share this."

        val shouldDelete = shouldTriggerDeletion(messageDifferentCode, trigger, isEnabled = true)
        assertFalse("Message without the specific number must not trigger deletion", shouldDelete)
    }

    @Test
    fun testDeletionDisabledDoesNotTriggerEvenWhenNumberPresent() {
        val trigger = "849201"
        val message = "Code: 849201"

        val shouldDelete = shouldTriggerDeletion(message, trigger, isEnabled = false)
        assertFalse("If deletion feature is disabled, must never trigger deletion", shouldDelete)
    }

    @Test
    fun testBlankTriggerNumberDoesNotTrigger() {
        val message = "Your code is 1234"
        val shouldDelete = shouldTriggerDeletion(message, "", isEnabled = true)
        assertFalse("Blank trigger number must not match", shouldDelete)
    }
}
