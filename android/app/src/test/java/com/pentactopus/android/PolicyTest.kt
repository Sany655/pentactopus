package com.pentactopus.android

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PolicyTest {
    @Test
    fun blocksPasswordManagerFlows() {
        val policy = LocalPolicy()
        assertFalse(policy.authorize("system_settings", 5, appName = "com.lastpass"))
        assertFalse(policy.authorize("system_settings", 5, windowTitle = "2FA"))
    }

    @Test
    fun allowsBasicReadMetadata() {
        val policy = LocalPolicy()
        assertTrue(policy.authorize("read_message_metadata", 1))
        assertTrue(policy.authorize("read_message_content", 2))
    }
}
