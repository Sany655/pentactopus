package com.smswebhookbridge.service

import android.app.Service
import android.content.Intent
import android.os.IBinder

/**
 * Headless SMS send service required by Android system specifications
 * when supporting Default SMS Application role capability.
 */
class HeadlessSmsSendService : Service() {
    override fun onBind(intent: Intent?): IBinder? = null
}
