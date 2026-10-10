package com.pentactopus.android

import android.content.Context

object SecureSettings {
    private const val PREFS = "pentactopus_secure_settings"

    fun get(context: Context, name: String): String? {
        val encrypted = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(name, null) ?: return null
        return KeyStoreHelper.decrypt(encrypted)
    }

    fun put(context: Context, name: String, value: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(name, KeyStoreHelper.encrypt(value))
            .apply()
    }

    fun remove(context: Context, name: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .remove(name)
            .apply()
    }
}
