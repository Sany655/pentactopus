package com.smswebhookbridge.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.smswebhookbridge.BridgeApplication
import com.smswebhookbridge.service.BridgeForegroundService

class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action
        if (action != Intent.ACTION_BOOT_COMPLETED &&
            action != Intent.ACTION_MY_PACKAGE_REPLACED
        ) {
            return
        }

        val app = context.applicationContext as BridgeApplication
        if (app.preferencesManager.isEnabled) {
            app.logRepository.addLog("INFO", "Device restarted. Resuming SMS Webhook Bridge service...")
            BridgeForegroundService.start(context)
        }
    }
}
