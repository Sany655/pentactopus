package com.pentactopus.android

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import java.util.LinkedHashMap

data class NotificationMessage(
    val packageName: String,
    val title: String,
    val text: String,
    val timestamp: Long,
)

class PentactopusNotificationListener : NotificationListenerService() {
    companion object {
        private const val MAX_NOTIFICATIONS = 50
        private val allowedPackages = setOf("com.whatsapp", "com.whatsapp.w4b")
        private val notifications = LinkedHashMap<String, NotificationMessage>()
        private val policy = LocalPolicy()

        @Synchronized
        fun snapshot(): List<NotificationMessage> = notifications.values.toList()

        @Synchronized
        private fun put(key: String, message: NotificationMessage) {
            notifications.remove(key)
            notifications[key] = message
            while (notifications.size > MAX_NOTIFICATIONS) {
                notifications.remove(notifications.keys.first())
            }
        }

        @Synchronized
        private fun remove(key: String) {
            notifications.remove(key)
        }
    }

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        if (sbn.packageName !in allowedPackages || policy.isForbiddenApp(sbn.packageName)) return
        val extras = sbn.notification.extras
        val packageName = sbn.packageName
        val title = extras.getCharSequence("android.title")?.toString() ?: ""
        val text = extras.getCharSequence("android.text")?.toString() ?: ""
        if (title.isNotBlank() || text.isNotBlank()) {
            put(
                "${sbn.packageName}:${sbn.id}:${sbn.tag.orEmpty()}",
                NotificationMessage(
                    packageName = packageName,
                    title = title.take(256),
                    text = text.take(4_000),
                    timestamp = System.currentTimeMillis(),
                ),
            )
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification) {
        remove("${sbn.packageName}:${sbn.id}:${sbn.tag.orEmpty()}")
    }
}
