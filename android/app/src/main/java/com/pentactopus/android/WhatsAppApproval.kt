package com.pentactopus.android

import org.json.JSONObject
import java.security.MessageDigest
import java.nio.ByteBuffer
import java.util.UUID

internal object ExactActionHash {
    fun calculate(vararg fields: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        fields.forEach { field ->
            val bytes = field.toByteArray(Charsets.UTF_8)
            digest.update(ByteBuffer.allocate(Int.SIZE_BYTES).putInt(bytes.size).array())
            digest.update(bytes)
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}

data class ApprovedWhatsAppSend(
    val approvalId: String,
    val recipient: String,
    val text: String,
    val expiresAtEpochMs: Long,
    val payloadHash: String,
) {
    fun toJson(): String = JSONObject()
        .put("approval_id", approvalId)
        .put("recipient", recipient)
        .put("text", text)
        .put("expires_at_epoch_ms", expiresAtEpochMs)
        .put("payload_hash", payloadHash)
        .toString()

    companion object {
        fun create(recipient: String, text: String): ApprovedWhatsAppSend {
            val id = UUID.randomUUID().toString()
            val trimmedRecipient = recipient.trim()
            val expiresAtEpochMs = System.currentTimeMillis() + APPROVAL_LIFETIME_MS
            return ApprovedWhatsAppSend(
                approvalId = id,
                recipient = trimmedRecipient,
                text = text,
                expiresAtEpochMs = expiresAtEpochMs,
                payloadHash = hash(id, trimmedRecipient, text, expiresAtEpochMs),
            )
        }

        fun fromJson(value: String): ApprovedWhatsAppSend {
            val json = JSONObject(value)
            val result = ApprovedWhatsAppSend(
                approvalId = json.getString("approval_id"),
                recipient = json.getString("recipient"),
                text = json.getString("text"),
                expiresAtEpochMs = json.getLong("expires_at_epoch_ms"),
                payloadHash = json.getString("payload_hash"),
            )
            require(MessageDigest.isEqual(
                result.payloadHash.toByteArray(Charsets.US_ASCII),
                hash(result.approvalId, result.recipient, result.text, result.expiresAtEpochMs)
                    .toByteArray(Charsets.US_ASCII),
            )) { "Approved message payload was modified." }
            return result
        }

        private const val APPROVAL_LIFETIME_MS = 5 * 60 * 1000L

        private fun hash(approvalId: String, recipient: String, text: String, expiresAtEpochMs: Long): String =
            ExactActionHash.calculate(approvalId, recipient, text, expiresAtEpochMs.toString())
    }
}
