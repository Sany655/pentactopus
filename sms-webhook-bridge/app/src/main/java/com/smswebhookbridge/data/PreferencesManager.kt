package com.smswebhookbridge.data

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.smswebhookbridge.data.model.WebhookConfig
import com.smswebhookbridge.util.DeviceUtils

class PreferencesManager(private val context: Context) {

    private val prefs: SharedPreferences = createEncryptedOrPlainPrefs()

    private fun createEncryptedOrPlainPrefs(): SharedPreferences {
        return try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()

            EncryptedSharedPreferences.create(
                context,
                ENCRYPTED_PREFS_NAME,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            Log.w("PreferencesManager", "Keystore/EncryptedSharedPreferences unavailable; falling back to private SharedPreferences: ${e.message}")
            context.getSharedPreferences(FALLBACK_PREFS_NAME, Context.MODE_PRIVATE)
        }
    }

    var isEnabled: Boolean
        get() = prefs.getBoolean(KEY_IS_ENABLED, false)
        set(value) = prefs.edit().putBoolean(KEY_IS_ENABLED, value).apply()

    var senderNumber: String
        get() = prefs.getString(KEY_SENDER_NUMBER, "") ?: ""
        set(value) = prefs.edit().putString(KEY_SENDER_NUMBER, value.trim()).apply()

    var webhookUrl: String
        get() = prefs.getString(KEY_WEBHOOK_URL, "") ?: ""
        set(value) = prefs.edit().putString(KEY_WEBHOOK_URL, value.trim()).apply()

    var httpMethod: String
        get() = prefs.getString(KEY_HTTP_METHOD, "POST") ?: "POST"
        set(value) = prefs.edit().putString(KEY_HTTP_METHOD, if (value.equals("GET", ignoreCase = true)) "GET" else "POST").apply()

    var authToken: String
        get() = prefs.getString(KEY_AUTH_TOKEN, "") ?: ""
        set(value) = prefs.edit().putString(KEY_AUTH_TOKEN, value.trim()).apply()

    var maxRetries: Int
        get() = prefs.getInt(KEY_MAX_RETRIES, 3)
        set(value) = prefs.edit().putInt(KEY_MAX_RETRIES, value.coerceAtLeast(1)).apply()

    var retryIntervalSeconds: Int
        get() = prefs.getInt(KEY_RETRY_INTERVAL, 10)
        set(value) = prefs.edit().putInt(KEY_RETRY_INTERVAL, value.coerceAtLeast(5)).apply()

    var deleteMatchingContentEnabled: Boolean
        get() = prefs.getBoolean(KEY_DELETE_MATCHING_CONTENT, false)
        set(value) = prefs.edit().putBoolean(KEY_DELETE_MATCHING_CONTENT, value).apply()

    var deleteTriggerNumber: String
        get() = prefs.getString(KEY_DELETE_TRIGGER_NUMBER, "") ?: ""
        set(value) = prefs.edit().putString(KEY_DELETE_TRIGGER_NUMBER, value.trim()).apply()

    var isFirstRunCompleted: Boolean
        get() = prefs.getBoolean(KEY_FIRST_RUN_DONE, false)
        set(value) = prefs.edit().putBoolean(KEY_FIRST_RUN_DONE, value).apply()

    var lastMatchingSmsSender: String?
        get() = prefs.getString(KEY_LAST_SMS_SENDER, null)
        set(value) = prefs.edit().putString(KEY_LAST_SMS_SENDER, value).apply()

    var lastMatchingSmsBody: String?
        get() = prefs.getString(KEY_LAST_SMS_BODY, null)
        set(value) = prefs.edit().putString(KEY_LAST_SMS_BODY, value).apply()

    var lastMatchingSmsTime: String?
        get() = prefs.getString(KEY_LAST_SMS_TIME, null)
        set(value) = prefs.edit().putString(KEY_LAST_SMS_TIME, value).apply()

    var lastWebhookStatus: String?
        get() = prefs.getString(KEY_LAST_WEBHOOK_STATUS, null)
        set(value) = prefs.edit().putString(KEY_LAST_WEBHOOK_STATUS, value).apply()

    var lastWebhookTime: String?
        get() = prefs.getString(KEY_LAST_WEBHOOK_TIME, null)
        set(value) = prefs.edit().putString(KEY_LAST_WEBHOOK_TIME, value).apply()

    var lastError: String?
        get() = prefs.getString(KEY_LAST_ERROR, null)
        set(value) = prefs.edit().putString(KEY_LAST_ERROR, value).apply()

    fun getConfig(): WebhookConfig {
        return WebhookConfig(
            senderNumber = senderNumber,
            webhookUrl = webhookUrl,
            httpMethod = httpMethod,
            authToken = authToken,
            isEnabled = isEnabled,
            maxRetries = maxRetries,
            retryIntervalSeconds = retryIntervalSeconds,
            deleteMatchingContentEnabled = deleteMatchingContentEnabled,
            deleteTriggerNumber = deleteTriggerNumber,
            deviceId = DeviceUtils.getOrCreateDeviceId(context)
        )
    }

    fun saveConfig(config: WebhookConfig) {
        prefs.edit()
            .putString(KEY_SENDER_NUMBER, config.senderNumber.trim())
            .putString(KEY_WEBHOOK_URL, config.webhookUrl.trim())
            .putString(KEY_HTTP_METHOD, config.httpMethod)
            .putString(KEY_AUTH_TOKEN, config.authToken.trim())
            .putBoolean(KEY_IS_ENABLED, config.isEnabled)
            .putInt(KEY_MAX_RETRIES, config.maxRetries)
            .putInt(KEY_RETRY_INTERVAL, config.retryIntervalSeconds)
            .putBoolean(KEY_DELETE_MATCHING_CONTENT, config.deleteMatchingContentEnabled)
            .putString(KEY_DELETE_TRIGGER_NUMBER, config.deleteTriggerNumber.trim())
            .apply()
    }

    companion object {
        private const val ENCRYPTED_PREFS_NAME = "secure_bridge_prefs"
        private const val FALLBACK_PREFS_NAME = "bridge_prefs"

        private const val KEY_IS_ENABLED = "key_is_enabled"
        private const val KEY_SENDER_NUMBER = "key_sender_number"
        private const val KEY_WEBHOOK_URL = "key_webhook_url"
        private const val KEY_HTTP_METHOD = "key_http_method"
        private const val KEY_AUTH_TOKEN = "key_auth_token"
        private const val KEY_MAX_RETRIES = "key_max_retries"
        private const val KEY_RETRY_INTERVAL = "key_retry_interval"
        private const val KEY_DELETE_MATCHING_CONTENT = "key_delete_matching_content"
        private const val KEY_DELETE_TRIGGER_NUMBER = "key_delete_trigger_number"
        private const val KEY_FIRST_RUN_DONE = "key_first_run_done"

        private const val KEY_LAST_SMS_SENDER = "key_last_sms_sender"
        private const val KEY_LAST_SMS_BODY = "key_last_sms_body"
        private const val KEY_LAST_SMS_TIME = "key_last_sms_time"
        private const val KEY_LAST_WEBHOOK_STATUS = "key_last_webhook_status"
        private const val KEY_LAST_WEBHOOK_TIME = "key_last_webhook_time"
        private const val KEY_LAST_ERROR = "key_last_error"
    }
}
