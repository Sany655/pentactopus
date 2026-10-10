package com.pentactopus.android

data class CapabilityRule(
    val name: String,
    val tier: Int,
    val enabled: Boolean = true,
)

class LocalPolicy {
    private val blockedApps = setOf(
        "com.android.chrome",
        "com.android.settings",
        "com.google.android.apps.authenticator2",
        "com.lastpass",
        "com.dashlane",
        "com.keepersecurity.android",
        "com.authy",
        "com.bitwarden",
    )

    private val blockedWindowTitles = setOf(
        "Authenticator",
        "2FA",
        "Two-factor",
        "Password Manager",
    )

    private val allowedCapabilities = mapOf(
        "device_status" to CapabilityRule("device_status", 0),
        "read_message_metadata" to CapabilityRule("read_message_metadata", 1),
        "read_message_content" to CapabilityRule("read_message_content", 2),
        "draft_message" to CapabilityRule("draft_message", 3),
        "send_message" to CapabilityRule("send_message", 4),
        "delete_item" to CapabilityRule("delete_item", 5),
        "install_app" to CapabilityRule("install_app", 5),
        "system_settings" to CapabilityRule("system_settings", 5),
    )

    fun authorize(capability: String, actionTier: Int, appName: String? = null, windowTitle: String? = null): Boolean {
        val rule = allowedCapabilities[capability] ?: return false
        if (!rule.enabled) return false
        if (actionTier < rule.tier) return false
        if (appName != null && blockedApps.contains(appName)) return false
        if (windowTitle != null && blockedWindowTitles.any { it.equals(windowTitle, ignoreCase = true) }) return false
        return true
    }
}
