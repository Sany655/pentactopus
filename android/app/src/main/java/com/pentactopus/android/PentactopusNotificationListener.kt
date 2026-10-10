package com.pentactopus.android

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

data class NotificationMessage(
    val packageName: String,
    val title: String,
    val text: String,
    val timestamp: Long,
)

class PentactopusNotificationListener : NotificationListenerService() {
    companion object {
        private val notifications = mutableListOf<NotificationMessage>()

        fun snapshot(): List<NotificationMessage> = notifications.toList()
    }

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val extras = sbn.notification.extras
        val packageName = sbn.packageName
        val title = extras.getCharSequence("android.title")?.toString() ?: ""
        val text = extras.getCharSequence("android.text")?.toString() ?: ""
        if (title.isNotBlank() || text.isNotBlank()) {
            notifications.add(
                NotificationMessage(
                    packageName = packageName,
                    title = title,
                    text = text,
                    timestamp = System.currentTimeMillis(),
                ),
            )
        }
    }
}
