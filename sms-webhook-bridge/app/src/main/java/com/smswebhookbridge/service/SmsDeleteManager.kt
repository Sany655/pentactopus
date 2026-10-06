package com.smswebhookbridge.service

import android.content.Context
import android.content.Intent
import android.os.Build
import android.provider.Telephony
import com.smswebhookbridge.data.PreferencesManager
import com.smswebhookbridge.data.repository.LogRepository

class SmsDeleteManager(
    private val context: Context,
    private val preferencesManager: PreferencesManager,
    private val logRepository: LogRepository
) {

    /**
     * Checks if this app is configured as the default SMS app on the system.
     */
    fun isDefaultSmsApp(): Boolean {
        val defaultPackage = Telephony.Sms.getDefaultSmsPackage(context)
        return context.packageName.equals(defaultPackage, ignoreCase = true)
    }

    /**
     * Checks if the message content contains the configured deletion trigger number.
     */
    fun shouldDelete(messageBody: String): Boolean {
        val config = preferencesManager.getConfig()
        if (!config.deleteMatchingContentEnabled || config.deleteTriggerNumber.isBlank()) {
            return false
        }
        val trigger = config.deleteTriggerNumber.trim()
        return messageBody.contains(trigger)
    }

    /**
     * Attempts to delete the message from the system SMS inbox.
     * Android KitKat+ strictly requires the app to be the Default SMS App
     * to delete messages from the SMS Content Provider.
     */
    fun deleteMessageIfTriggered(sender: String, messageBody: String): Boolean {
        if (!shouldDelete(messageBody)) {
            return false
        }

        val trigger = preferencesManager.deleteTriggerNumber.trim()
        logRepository.addLog("INFO", "SMS contains delete trigger number '$trigger'. Initiating deletion...")

        if (!isDefaultSmsApp()) {
            val msg = "Auto-delete failed: Android requires this app to be the 'Default SMS App' to delete messages from the inbox. Please enable this in Settings."
            logRepository.addLog("WARN", msg)
            return false
        }

        return try {
            val uri = Telephony.Sms.CONTENT_URI
            // Match messages from this sender containing the text
            val rowsDeleted = context.contentResolver.delete(
                uri,
                "${Telephony.Sms.ADDRESS} = ? AND ${Telephony.Sms.BODY} LIKE ?",
                arrayOf(sender, "%$trigger%")
            )

            if (rowsDeleted > 0) {
                logRepository.addLog("INFO", "Successfully deleted $rowsDeleted SMS message(s) from inbox matching trigger '$trigger'.")
                true
            } else {
                logRepository.addLog("WARN", "No matching SMS rows found in inbox to delete for sender: $sender")
                false
            }
        } catch (e: SecurityException) {
            logRepository.addLog("ERROR", "SecurityException deleting SMS: Android system denied inbox write permission: ${e.message}")
            false
        } catch (e: Exception) {
            logRepository.addLog("ERROR", "Unexpected error deleting SMS: ${e.message}")
            false
        }
    }

    /**
     * Returns an Intent to request setting this app as default SMS app.
     */
    fun createDefaultSmsAppIntent(): Intent {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = context.getSystemService(android.app.role.RoleManager::class.java)
            roleManager?.createRequestRoleIntent(android.app.role.RoleManager.ROLE_SMS)
                ?: Intent(Telephony.Sms.Intents.ACTION_CHANGE_DEFAULT).apply {
                    putExtra(Telephony.Sms.Intents.EXTRA_PACKAGE_NAME, context.packageName)
                }
        } else {
            Intent(Telephony.Sms.Intents.ACTION_CHANGE_DEFAULT).apply {
                putExtra(Telephony.Sms.Intents.EXTRA_PACKAGE_NAME, context.packageName)
            }
        }
    }
}
