package com.smswebhookbridge.util

import android.content.Context
import android.os.Build
import java.util.UUID

object DeviceUtils {

    private const val PREF_DEVICE_ID = "key_persistent_device_id"

    fun getOrCreateDeviceId(context: Context): String {
        val prefs = context.getSharedPreferences("bridge_device_prefs", Context.MODE_PRIVATE)
        var deviceId = prefs.getString(PREF_DEVICE_ID, null)
        if (deviceId.isNullOrBlank()) {
            val model = Build.MODEL.replace(" ", "-").filter { it.isLetterOrDigit() || it == '-' }
            val randomSuffix = UUID.randomUUID().toString().substring(0, 8)
            deviceId = "android-$model-$randomSuffix"
            prefs.edit().putString(PREF_DEVICE_ID, deviceId).apply()
        }
        return deviceId
    }
}
