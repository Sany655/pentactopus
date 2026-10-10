package com.pentactopus.android

import android.content.ComponentName
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.snackbar.Snackbar
import com.pentactopus.android.databinding.ActivityApprovalBinding

class ApprovalActivity : AppCompatActivity() {
    private lateinit var binding: ActivityApprovalBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setFlags(
            android.view.WindowManager.LayoutParams.FLAG_SECURE,
            android.view.WindowManager.LayoutParams.FLAG_SECURE,
        )
        binding = ActivityApprovalBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.enableAccessibilityButton.setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }
        binding.approveButton.setOnClickListener {
            approveExactPayload()
        }
    }

    private fun approveExactPayload() {
        val recipient = binding.recipientInput.text?.toString()?.trim().orEmpty()
        val text = binding.messageInput.text?.toString().orEmpty()
        if (!LocalPolicy().authorize("send_message", actionTier = 4, appName = "com.whatsapp")) {
            showMessage("Local policy blocks this app or action.")
            return
        }
        if (recipient.isBlank() || text.isBlank()) {
            showMessage("Enter the exact visible recipient and message text.")
            return
        }
        if (text.length > 16_384) {
            showMessage("Message exceeds the local 16,384-character limit.")
            return
        }
        if (!binding.confirmExactPayload.isChecked) {
            showMessage("Confirm the exact recipient and text before approving.")
            return
        }
        if (!isAccessibilityServiceEnabled()) {
            showMessage("Enable the Pentactopus accessibility service first.")
            return
        }

        try {
            val approval = ApprovedWhatsAppSend.create(recipient, text)
            SecureSettings.put(this, PENDING_SEND_KEY, approval.toJson())
        } catch (error: Exception) {
            showMessage(error.message ?: "Could not store the approved message securely.")
            return
        }
        showMessage(
            "Exact message approved for five minutes. Return to the matching WhatsApp chat to send once.",
        )
        finish()
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val expected = ComponentName(this, PentactopusAccessibilityService::class.java).flattenToString()
        val enabled = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES)
        return enabled.orEmpty().split(':').any { it.equals(expected, ignoreCase = true) }
    }

    private fun showMessage(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
    }

    companion object {
        const val PENDING_SEND_KEY = "pending_approved_whatsapp_send"
    }
}
