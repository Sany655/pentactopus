package com.smswebhookbridge.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.smswebhookbridge.ui.screens.DashboardScreen
import com.smswebhookbridge.ui.screens.LogsScreen
import com.smswebhookbridge.ui.screens.OnboardingScreen
import com.smswebhookbridge.ui.screens.SettingsScreen
import com.smswebhookbridge.ui.theme.SMSWebhookBridgeTheme

class MainActivity : ComponentActivity() {

    private val viewModel: MainViewModel by viewModels()

    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            SMSWebhookBridgeTheme {
                val state by viewModel.uiState.collectAsState()
                val snackbarHostState = remember { SnackbarHostState() }

                LaunchedEffect(state.messageSnackbar) {
                    state.messageSnackbar?.let { message ->
                        snackbarHostState.showSnackbar(message)
                        viewModel.clearSnackbar()
                    }
                }

                if (!state.isFirstRunCompleted) {
                    OnboardingScreen(
                        onContinueToConfig = {
                            viewModel.setFirstRunCompleted(true)
                            viewModel.selectTab(1) // Navigate to Settings
                        }
                    )
                } else {
                    Scaffold(
                        topBar = {
                            TopAppBar(
                                title = {
                                    Text(
                                        when (state.currentTab) {
                                            0 -> "SMS Webhook Bridge"
                                            1 -> "Settings"
                                            else -> "Events & Logs"
                                        }
                                    )
                                },
                                colors = TopAppBarDefaults.topAppBarColors(
                                    containerColor = MaterialTheme.colorScheme.primary,
                                    titleContentColor = MaterialTheme.colorScheme.onPrimary
                                )
                            )
                        },
                        bottomBar = {
                            NavigationBar {
                                NavigationBarItem(
                                    selected = state.currentTab == 0,
                                    onClick = { viewModel.selectTab(0) },
                                    icon = { Icon(Icons.Default.Dashboard, contentDescription = "Dashboard") },
                                    label = { Text("Dashboard") }
                                )
                                NavigationBarItem(
                                    selected = state.currentTab == 1,
                                    onClick = { viewModel.selectTab(1) },
                                    icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                                    label = { Text("Settings") }
                                )
                                NavigationBarItem(
                                    selected = state.currentTab == 2,
                                    onClick = { viewModel.selectTab(2) },
                                    icon = { Icon(Icons.Default.List, contentDescription = "Logs") },
                                    label = { Text("Logs") }
                                )
                            }
                        },
                        snackbarHost = { SnackbarHost(snackbarHostState) }
                    ) { innerPadding ->
                        Box(modifier = Modifier.padding(innerPadding)) {
                            when (state.currentTab) {
                                0 -> DashboardScreen(
                                    state = state,
                                    onToggleService = { viewModel.toggleService(it) },
                                    onTestWebhook = { viewModel.testWebhook() },
                                    onNavigateToSettings = { viewModel.selectTab(1) },
                                    onNavigateToLogs = { viewModel.selectTab(2) }
                                )
                                1 -> SettingsScreen(
                                    state = state,
                                    onSaveConfig = { viewModel.saveConfig(it) },
                                    onBack = { viewModel.selectTab(0) }
                                )
                                2 -> LogsScreen(
                                    state = state,
                                    onRetryEvent = { viewModel.retryEvent(it) },
                                    onClearLogs = { viewModel.clearLogs() }
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        viewModel.refresh()
    }
}
