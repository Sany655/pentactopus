package com.pentactopus.android

data class CapabilityRule(
    val name: String,
    val tier: Int,
    val enabled: Boolean = true,
)

class LocalPolicy {
    private val blockedApps = setOf(
        "com.google.android.apps.walletnfcrel",
        "com.samsung.android.spay",
        "com.google.android.apps.authenticator2",
        "com.azure.authenticator",
        "com.microsoft.authenticator",
        "com.lastpass",
        "com.dashlane",
        "com.keepersecurity.android",
        "com.authy",
        "com.bitwarden",
        "com.agilebits.onepassword",
        "com.kaspersky.passwordmanager",
        "com.x8bit.bitwarden",
        "com.chase.sig.android",
        "com.bankofamerica.digitalwallet",
        "com.wf.wellsfargomobile",
        "com.citi.citimobile",
        "com.usbank.mobilebanking",
        "com.infonow.bofa",
        "com.paypal.android.p2pmobile",
        "com.venmo",
        "com.squareup.cash",
    )
    private val blockedAppNameTerms = setOf(
        "bank",
        "wallet",
        "payment",
        "finance",
        "authenticator",
        "password manager",
        "password vault",
        "two-factor",
        "2fa",
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

    fun authorize(
        capability: String,
        actionTier: Int,
        appName: String? = null,
        windowTitle: String? = null,
    ): Boolean {
        val rule = allowedCapabilities[capability] ?: return false
        if (!rule.enabled) return false
        if (actionTier < rule.tier) return false
        if (isForbiddenApp(appName) || isForbiddenWindow(windowTitle)) return false
        return true
    }

    fun isForbiddenApp(packageName: String?): Boolean {
        val normalized = packageName?.trim()?.lowercase().orEmpty()
        return normalized in blockedApps ||
            blockedApps.any { normalized.startsWith("$it.") } ||
            blockedAppNameTerms.any { normalized.contains(it) }
    }

    fun isForbiddenWindow(windowTitle: String?): Boolean {
        val title = windowTitle?.trim().orEmpty()
        return title.isNotEmpty() && blockedWindowTitles.any { title.contains(it, ignoreCase = true) }
    }
}
