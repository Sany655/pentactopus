package com.smswebhookbridge.util

object PhoneNumberNormalizer {

    /**
     * Normalizes a raw phone number or sender ID string.
     * - Preserves alphanumeric sender IDs in trimmed uppercase.
     * - Strips spaces, hyphens, brackets, dots from phone numbers.
     * - Converts leading 00 to +.
     * - Strips invalid punctuation.
     */
    fun normalize(raw: String?): String {
        if (raw.isNullOrBlank()) return ""
        val trimmed = raw.trim()

        // Check if sender ID contains alphabetic characters (e.g., BANK, GOOGLE)
        val hasLetters = trimmed.any { it.isLetter() }
        if (hasLetters) {
            return trimmed.replace(Regex("[^A-Za-z0-9_ -]"), "").trim().uppercase()
        }

        var cleaned = trimmed
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace(".", "")
            .replace("/", "")

        if (cleaned.startsWith("00")) {
            cleaned = "+" + cleaned.substring(2)
        }

        // Keep leading + if present, and digits only
        val hasLeadingPlus = cleaned.startsWith("+")
        val digitsOnly = cleaned.filter { it.isDigit() }

        if (digitsOnly.isEmpty()) return ""

        return if (hasLeadingPlus) "+$digitsOnly" else digitsOnly
    }

    /**
     * Checks if the incoming sender matches the configured sender.
     * Returns true only if they represent the same sender.
     */
    fun matches(configured: String?, incoming: String?): Boolean {
        if (configured.isNullOrBlank() || incoming.isNullOrBlank()) return false

        val normConfigured = normalize(configured)
        val normIncoming = normalize(incoming)

        if (normConfigured.isEmpty() || normIncoming.isEmpty()) return false

        // Exact match
        if (normConfigured.equals(normIncoming, ignoreCase = true)) {
            return true
        }

        // Check for alphanumeric sender ID comparison
        if (normConfigured.any { it.isLetter() } || normIncoming.any { it.isLetter() }) {
            return normConfigured.equals(normIncoming, ignoreCase = true)
        }

        // Numeric phone numbers comparison
        val configDigits = normConfigured.removePrefix("+")
        val incomingDigits = normIncoming.removePrefix("+")

        if (configDigits == incomingDigits) return true

        // Compare stripping national trunk prefix '0' (e.g. 017... vs +88017...)
        val configNoTrunk = configDigits.trimStart('0')
        val incomingNoTrunk = incomingDigits.trimStart('0')

        if (configNoTrunk == incomingNoTrunk && configNoTrunk.length >= 7) {
            return true
        }

        // If one is full international (e.g. 8801712345678) and one is local without trunk (1712345678)
        if (configDigits.length > incomingNoTrunk.length && incomingNoTrunk.length >= 7) {
            if (configDigits.endsWith(incomingNoTrunk)) return true
        }
        if (incomingDigits.length > configNoTrunk.length && configNoTrunk.length >= 7) {
            if (incomingDigits.endsWith(configNoTrunk)) return true
        }

        return false
    }
}
