package com.smswebhookbridge.data.repository

import android.util.Log
import com.smswebhookbridge.data.AppDatabase
import com.smswebhookbridge.data.model.AppLog

class LogRepository(private val db: AppDatabase) {

    fun addLog(level: String, message: String) {
        when (level.uppercase()) {
            "WARN" -> Log.w(TAG, message)
            "ERROR" -> Log.e(TAG, message)
            else -> Log.i(TAG, message)
        }
        db.insertLog(level.uppercase(), message)
    }

    fun getLogs(limit: Int = 200): List<AppLog> = db.getLogs(limit)

    fun clearLogs() = db.clearLogs()

    companion object {
        private const val TAG = "SMSBridge"
    }
}
