package com.smswebhookbridge.service

import android.app.Notification
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.smswebhookbridge.BridgeApplication
import com.smswebhookbridge.R
import com.smswebhookbridge.ui.MainActivity

class BridgeForegroundService : Service() {

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action

        if (action == ACTION_STOP) {
            stopBridgeService()
            return START_NOT_STICKY
        }

        startBridgeService()
        return START_STICKY
    }

    private fun startBridgeService() {
        val app = application as BridgeApplication
        app.preferencesManager.isEnabled = true
        app.logRepository.addLog("INFO", "Foreground service active - SMS monitoring enabled")

        val notification = buildPersistentNotification()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun stopBridgeService() {
        val app = application as BridgeApplication
        app.preferencesManager.isEnabled = false
        app.logRepository.addLog("INFO", "Foreground service stopped - SMS monitoring paused")
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun buildPersistentNotification(): Notification {
        val app = application as BridgeApplication
        val sender = app.preferencesManager.senderNumber.ifBlank { "Unconfigured" }
        val method = app.preferencesManager.httpMethod

        val openIntent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val openPendingIntent = PendingIntent.getActivity(
            this,
            0,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val stopIntent = Intent(this, BridgeForegroundService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this,
            1,
            stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, BridgeApplication.CHANNEL_ID_SERVICE)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(getString(R.string.service_running_title))
            .setContentText("Monitoring SMS from: $sender ($method)")
            .setStyle(
                NotificationCompat.BigTextStyle().bigText(
                    "Service is running transparently in background.\n" +
                            "Configured sender: $sender\n" +
                            "Webhook target: ${app.preferencesManager.webhookUrl.ifBlank { "None" }}"
                )
            )
            .setContentIntent(openPendingIntent)
            .addAction(
                R.drawable.ic_notification,
                getString(R.string.action_stop),
                stopPendingIntent
            )
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()
    }

    companion object {
        const val ACTION_START = "com.smswebhookbridge.action.START"
        const val ACTION_STOP = "com.smswebhookbridge.action.STOP"
        const val NOTIFICATION_ID = 1001

        fun start(context: Context) {
            val intent = Intent(context, BridgeForegroundService::class.java).apply {
                action = ACTION_START
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            val intent = Intent(context, BridgeForegroundService::class.java).apply {
                action = ACTION_STOP
            }
            context.startService(intent)
        }
    }
}
