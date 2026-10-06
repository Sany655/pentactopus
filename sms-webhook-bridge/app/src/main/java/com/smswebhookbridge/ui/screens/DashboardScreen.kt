package com.smswebhookbridge.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smswebhookbridge.ui.MainUiState

@Composable
fun DashboardScreen(
    state: MainUiState,
    onToggleService: (Boolean) -> Unit,
    onTestWebhook: () -> Unit,
    onNavigateToSettings: () -> Unit,
    onNavigateToLogs: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        // Status Card
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (state.isEnabled) Color(0xFFE8F5E9) else Color(0xFFFFEBEE)
            ),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(16.dp)
                            .background(
                                color = if (state.isEnabled) Color(0xFF2E7D32) else Color(0xFFC62828),
                                shape = CircleShape
                            )
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = if (state.isEnabled) "Service Active" else "Service Stopped",
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp,
                            color = if (state.isEnabled) Color(0xFF1B5E20) else Color(0xFFB71C1C)
                        )
                        Text(
                            text = if (state.isEnabled) "Forwarding incoming SMS" else "Bridge is currently paused",
                            fontSize = 12.sp,
                            color = Color.DarkGray
                        )
                    }
                }

                Switch(
                    checked = state.isEnabled,
                    onCheckedChange = { onToggleService(it) }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Configuration Summary Card
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Current Bridge Config",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))

                InfoRow(
                    label = "Allowed Sender",
                    value = state.config.senderNumber.ifBlank { "(Not configured)" },
                    icon = Icons.Default.Phone
                )
                Spacer(modifier = Modifier.height(8.dp))
                InfoRow(
                    label = "Webhook URL",
                    value = state.config.webhookUrl.ifBlank { "(Not configured)" },
                    icon = Icons.Default.Link
                )
                Spacer(modifier = Modifier.height(8.dp))
                InfoRow(
                    label = "HTTP Method",
                    value = state.config.httpMethod,
                    icon = Icons.Default.Send
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Last Activity Card
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Last Bridge Activity",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))

                InfoRow(
                    label = "Last Matching SMS",
                    value = if (state.lastReceivedSmsSender != null) {
                        "From: ${state.lastReceivedSmsSender}\nMessage: ${state.lastReceivedSmsBody}\nTime: ${state.lastReceivedSmsTime}"
                    } else "None yet",
                    icon = Icons.Default.Sms
                )

                Spacer(modifier = Modifier.height(8.dp))

                InfoRow(
                    label = "Last Webhook Status",
                    value = if (state.lastWebhookStatus != null) {
                        "${state.lastWebhookStatus} at ${state.lastWebhookTime ?: ""}"
                    } else "No transmissions yet",
                    icon = Icons.Default.CloudUpload
                )

                if (state.lastError != null) {
                    Spacer(modifier = Modifier.height(8.dp))
                    InfoRow(
                        label = "Last Error",
                        value = state.lastError,
                        icon = Icons.Default.Warning,
                        isError = true
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Action Buttons Grid
        Text(
            text = "Actions",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(8.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Button(
                onClick = { onToggleService(!state.isEnabled) },
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (state.isEnabled) Color(0xFFD32F2F) else Color(0xFF2E7D32)
                ),
                shape = RoundedCornerShape(10.dp)
            ) {
                Icon(
                    imageVector = if (state.isEnabled) Icons.Default.Stop else Icons.Default.PlayArrow,
                    contentDescription = null
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(if (state.isEnabled) "Disable" else "Enable")
            }

            Button(
                onClick = onTestWebhook,
                enabled = !state.isTestingWebhook && state.config.isHttps,
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                shape = RoundedCornerShape(10.dp)
            ) {
                if (state.isTestingWebhook) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp,
                        color = Color.White
                    )
                } else {
                    Icon(imageVector = Icons.Default.Check, contentDescription = null)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Test Webhook")
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            OutlinedButton(
                onClick = onNavigateToSettings,
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                shape = RoundedCornerShape(10.dp)
            ) {
                Icon(imageVector = Icons.Default.Settings, contentDescription = null)
                Spacer(modifier = Modifier.width(6.dp))
                Text("Settings")
            }

            OutlinedButton(
                onClick = onNavigateToLogs,
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                shape = RoundedCornerShape(10.dp)
            ) {
                Icon(imageVector = Icons.Default.List, contentDescription = null)
                Spacer(modifier = Modifier.width(6.dp))
                Text("View Logs (${state.events.size})")
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
fun InfoRow(
    label: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isError: Boolean = false
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = if (isError) Color(0xFFC62828) else MaterialTheme.colorScheme.primary,
            modifier = Modifier
                .size(20.dp)
                .padding(top = 2.dp)
        )
        Spacer(modifier = Modifier.width(10.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = label,
                fontSize = 12.sp,
                color = Color.Gray,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = value,
                fontSize = 14.sp,
                fontWeight = FontWeight.Normal,
                color = if (isError) Color(0xFFC62828) else MaterialTheme.colorScheme.onSurface
            )
        }
    }
}
