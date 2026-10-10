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
        assertFalse(policy.authorize("system_settings", 5, appName = "com.chase.sig.android"))
        assertFalse(policy.authorize("system_settings", 5, appName = "My Bank"))
    }

    @Test
    fun allowsBasicReadMetadata() {
        val policy = LocalPolicy()
        assertTrue(policy.authorize("read_message_metadata", 1))
        assertTrue(policy.authorize("read_message_content", 2))
    }

    @Test
    fun modelEndpointAllowsHttpsAndLocalOllamaOnly() {
        assertTrue(ModelEndpointPolicy.allows("https://api.example.test/v1/chat/completions"))
        assertTrue(ModelEndpointPolicy.allows("http://localhost:11434/v1/chat/completions"))
        assertFalse(ModelEndpointPolicy.requiresApiKey("http://localhost:11434/v1/chat/completions"))
        assertTrue(ModelEndpointPolicy.requiresApiKey("https://api.example.test/v1/chat/completions"))
        assertFalse(ModelEndpointPolicy.allows("http://model.example.test/v1/chat/completions"))
        assertFalse(ModelEndpointPolicy.allows("http://127.0.0.1:11434/v1/chat/completions"))
        assertFalse(ModelEndpointPolicy.allows("https://user:password@example.test/chat"))
        assertFalse(ModelEndpointPolicy.allows("https://example.test/chat#fragment"))
    }
}
