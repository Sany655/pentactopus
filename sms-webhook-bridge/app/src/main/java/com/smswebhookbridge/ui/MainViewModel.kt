package com.smswebhookbridge.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.smswebhookbridge.BridgeApplication
import com.smswebhookbridge.data.model.AppLog
import com.smswebhookbridge.data.model.EventStatus
import com.smswebhookbridge.data.model.WebhookConfig
import com.smswebhookbridge.data.model.WebhookEvent
import com.smswebhookbridge.service.BridgeForegroundService
import com.smswebhookbridge.service.WebhookForwardWorker
import com.smswebhookbridge.util.DeviceUtils
import com.smswebhookbridge.util.SecurityUtils
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.Instant
import java.util.UUID

data class MainUiState(
    val config: WebhookConfig = WebhookConfig(),
    val isEnabled: Boolean = false,
    val isFirstRunCompleted: Boolean = false,
    val lastReceivedSmsSender: String? = null,
    val lastReceivedSmsBody: String? = null,
    val lastReceivedSmsTime: String? = null,
    val lastWebhookStatus: String? = null,
    val lastWebhookTime: String? = null,
    val lastError: String? = null,
    val isDefaultSmsApp: Boolean = false,
    val isTestingWebhook: Boolean = false,
    val testWebhookResult: String? = null,
    val events: List<WebhookEvent> = emptyList(),
    val logs: List<AppLog> = emptyList(),
    val currentTab: Int = 0,
    val messageSnackbar: String? = null
)

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val app = application as BridgeApplication
    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        val prefs = app.preferencesManager
        val isDefault = app.smsDeleteManager.isDefaultSmsApp()
        val allEvents = app.eventRepository.getAllEvents(50)
        val allLogs = app.logRepository.getLogs(100)

        _uiState.update { current ->
            current.copy(
                config = prefs.getConfig(),
                isEnabled = prefs.isEnabled,
                isFirstRunCompleted = prefs.isFirstRunCompleted,
                lastReceivedSmsSender = prefs.lastMatchingSmsSender,
                lastReceivedSmsBody = prefs.lastMatchingSmsBody,
                lastReceivedSmsTime = prefs.lastMatchingSmsTime,
                lastWebhookStatus = prefs.lastWebhookStatus,
                lastWebhookTime = prefs.lastWebhookTime,
                lastError = prefs.lastError,
                isDefaultSmsApp = isDefault,
                events = allEvents,
                logs = allLogs
            )
        }
    }

    fun selectTab(tabIndex: Int) {
        _uiState.update { it.copy(currentTab = tabIndex) }
        refresh()
    }

    fun setFirstRunCompleted(completed: Boolean) {
        app.preferencesManager.isFirstRunCompleted = completed
        _uiState.update { it.copy(isFirstRunCompleted = completed) }
    }

    fun toggleService(enable: Boolean) {
        val config = app.preferencesManager.getConfig()
        if (enable && !config.isValid) {
            _uiState.update {
                it.copy(messageSnackbar = "Please configure a valid sender and HTTPS webhook URL first.")
            }
            return
        }

        app.preferencesManager.isEnabled = enable
        if (enable) {
            BridgeForegroundService.start(getApplication())
            app.logRepository.addLog("INFO", "Service started by user.")
        } else {
            BridgeForegroundService.stop(getApplication())
            app.logRepository.addLog("INFO", "Service stopped by user.")
        }
        refresh()
    }

    fun saveConfig(newConfig: WebhookConfig) {
        if (newConfig.webhookUrl.isNotBlank() && !SecurityUtils.isValidHttpsUrl(newConfig.webhookUrl)) {
            _uiState.update {
                it.copy(messageSnackbar = "Security requirement: Webhook URL must use HTTPS (e.g. https://...).")
            }
            return
        }

        app.preferencesManager.saveConfig(newConfig)
        app.logRepository.addLog("INFO", "Configuration updated.")
        refresh()
        _uiState.update {
            it.copy(messageSnackbar = "Configuration saved successfully!")
        }
    }

    fun testWebhook() {
        val config = app.preferencesManager.getConfig()
        if (!config.isHttps) {
            _uiState.update {
                it.copy(messageSnackbar = "Cannot test: Webhook URL is not a valid HTTPS address.")
            }
            return
        }

        _uiState.update { it.copy(isTestingWebhook = true, testWebhookResult = null) }

        viewModelScope.launch {
            val testEvent = WebhookEvent(
                eventId = UUID.randomUUID().toString(),
                sender = config.senderNumber.ifBlank { "+00000000000" },
                message = "TEST_PING: This is a diagnostic test message from SMS Webhook Bridge.",
                deviceId = DeviceUtils.getOrCreateDeviceId(getApplication()),
                status = EventStatus.IN_PROGRESS
            )

            app.logRepository.addLog("INFO", "Sending manual test webhook ping to: ${config.webhookUrl}")
            val result = app.webhookClient.sendWebhook(config, testEvent)

            if (result.isSuccess) {
                val nowStr = Instant.now().toString()
                app.preferencesManager.lastWebhookStatus = "HTTP ${result.statusCode} OK (Test)"
                app.preferencesManager.lastWebhookTime = nowStr
                app.preferencesManager.lastError = null

                _uiState.update {
                    it.copy(
                        isTestingWebhook = false,
                        testWebhookResult = "Success: HTTP ${result.statusCode} received!",
                        messageSnackbar = "Test webhook succeeded (HTTP ${result.statusCode})"
                    )
                }
            } else {
                val err = result.errorMessage ?: "Unknown error"
                app.preferencesManager.lastWebhookStatus = if (result.statusCode > 0) "HTTP ${result.statusCode} (Test Failed)" else "Test Error"
                app.preferencesManager.lastError = err

                _uiState.update {
                    it.copy(
                        isTestingWebhook = false,
                        testWebhookResult = "Failed: $err",
                        messageSnackbar = "Test failed: $err"
                    )
                }
            }
            refresh()
        }
    }

    fun retryEvent(event: WebhookEvent) {
        WebhookForwardWorker.enqueue(getApplication(), event.eventId)
        _uiState.update {
            it.copy(messageSnackbar = "Retry scheduled for event ${event.eventId.take(8)}...")
        }
        refresh()
    }

    fun clearLogs() {
        app.logRepository.clearLogs()
        refresh()
        _uiState.update { it.copy(messageSnackbar = "Logs cleared.") }
    }

    fun clearSnackbar() {
        _uiState.update { it.copy(messageSnackbar = null) }
    }
}
