package com.smswebhookbridge

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import com.smswebhookbridge.data.AppDatabase
import com.smswebhookbridge.data.PreferencesManager
import com.smswebhookbridge.data.repository.EventRepository
import com.smswebhookbridge.data.repository.LogRepository
import com.smswebhookbridge.network.WebhookClient
import com.smswebhookbridge.service.SmsDeleteManager

class BridgeApplication : Application() {

    lateinit var preferencesManager: PreferencesManager
        private set
    lateinit var appDatabase: AppDatabase
        private set
    lateinit var eventRepository: EventRepository
        private set
    lateinit var logRepository: LogRepository
        private set
    lateinit var webhookClient: WebhookClient
        private set
    lateinit var smsDeleteManager: SmsDeleteManager
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this

        createNotificationChannels()

        preferencesManager = PreferencesManager(this)
        appDatabase = AppDatabase(this)
        eventRepository = EventRepository(appDatabase)
        logRepository = LogRepository(appDatabase)
        webhookClient = WebhookClient()
        smsDeleteManager = SmsDeleteManager(this, preferencesManager, logRepository)

        logRepository.addLog("INFO", "Application initialized")
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                CHANNEL_ID_SERVICE,
                getString(R.string.channel_name),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = getString(R.string.channel_description)
                setShowBadge(false)
            }

            val alertChannel = NotificationChannel(
                CHANNEL_ID_ALERTS,
                "SMS Webhook Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifications for failed webhooks and critical events"
                setShowBadge(true)
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager?.createNotificationChannel(serviceChannel)
            notificationManager?.createNotificationChannel(alertChannel)
        }
    }

    companion object {
        const val CHANNEL_ID_SERVICE = "bridge_service_channel"
        const val CHANNEL_ID_ALERTS = "bridge_alerts_channel"

        lateinit var instance: BridgeApplication
            private set
    }
}
