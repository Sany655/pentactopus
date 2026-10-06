package com.smswebhookbridge.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smswebhookbridge.data.model.AppLog
import com.smswebhookbridge.data.model.EventStatus
import com.smswebhookbridge.data.model.WebhookEvent
import com.smswebhookbridge.ui.MainUiState
import com.smswebhookbridge.util.SecurityUtils

@Composable
fun LogsScreen(
    state: MainUiState,
    onRetryEvent: (WebhookEvent) -> Unit,
    onClearLogs: () -> Unit
) {
    var selectedView by remember { mutableStateOf(0) } // 0: Webhook Events, 1: App Logs

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(
                    selected = selectedView == 0,
                    onClick = { selectedView = 0 },
                    label = { Text("Webhook Queue (${state.events.size})") }
                )
                FilterChip(
                    selected = selectedView == 1,
                    onClick = { selectedView = 1 },
                    label = { Text("System Logs (${state.logs.size})") }
                )
            }

            if (selectedView == 1 && state.logs.isNotEmpty()) {
                IconButton(onClick = onClearLogs) {
                    Icon(
                        imageVector = Icons.Default.DeleteOutline,
                        contentDescription = "Clear Logs",
                        tint = MaterialTheme.colorScheme.error
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        if (selectedView == 0) {
            if (state.events.isEmpty()) {
                EmptyStateView(
                    icon = Icons.Default.Inbox,
                    title = "No Webhook Events Yet",
                    subtitle = "Matching incoming SMS messages will appear here."
                )
            } else {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                    modifier = Modifier.fillMaxSize()
                ) {
                    items(state.events, key = { it.eventId }) { event ->
                        WebhookEventCard(event = event, onRetry = { onRetryEvent(event) })
                    }
                }
            }
        } else {
            if (state.logs.isEmpty()) {
                EmptyStateView(
                    icon = Icons.Default.Description,
                    title = "No Logs Recorded",
                    subtitle = "App background events and activity will be logged here."
                )
            } else {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxSize()
                ) {
                    items(state.logs, key = { it.id }) { log ->
                        AppLogCard(log = log)
                    }
                }
            }
        }
    }
}

@Composable
fun WebhookEventCard(
    event: WebhookEvent,
    onRetry: () -> Unit
) {
    val statusColor = when (event.status) {
        EventStatus.SUCCESS -> Color(0xFF2E7D32)
        EventStatus.PENDING -> Color(0xFFF57C00)
        EventStatus.IN_PROGRESS -> Color(0xFF1976D2)
        EventStatus.FAILED -> Color(0xFFD32F2F)
    }

    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = statusColor.copy(alpha = 0.15f)
                ) {
                    Text(
                        text = event.status.name,
                        color = statusColor,
                        fontWeight = FontWeight.Bold,
                        fontSize = 11.sp,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }

                Text(
                    text = event.receivedAt.take(19).replace("T", " "),
                    fontSize = 11.sp,
                    color = Color.Gray
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "ID: ${event.eventId}",
                fontSize = 11.sp,
                fontFamily = FontFamily.Monospace,
                color = Color.DarkGray
            )

            Text(
                text = "Sender: ${event.sender}",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold
            )

            Text(
                text = "Message: ${SecurityUtils.maskSms(event.message, 50)}",
                fontSize = 13.sp,
                color = MaterialTheme.colorScheme.onSurface
            )

            Spacer(modifier = Modifier.height(6.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Attempts: ${event.attemptCount}" +
                            if (event.responseCode != null) " | HTTP ${event.responseCode}" else "",
                    fontSize = 12.sp,
                    color = Color.Gray
                )

                if (event.status == EventStatus.FAILED || event.status == EventStatus.PENDING) {
                    TextButton(onClick = onRetry) {
                        Icon(Icons.Default.Refresh, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Retry", fontSize = 12.sp)
                    }
                }
            }

            if (!event.errorMessage.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Error: ${event.errorMessage}",
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
fun AppLogCard(log: AppLog) {
    val levelColor = when (log.level.uppercase()) {
        "ERROR" -> MaterialTheme.colorScheme.error
        "WARN" -> Color(0xFFF57C00)
        else -> MaterialTheme.colorScheme.primary
    }

    Card(
        shape = RoundedCornerShape(8.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(10.dp),
            verticalAlignment = Alignment.Top
        ) {
            Surface(
                shape = RoundedCornerShape(4.dp),
                color = levelColor.copy(alpha = 0.15f)
            ) {
                Text(
                    text = log.level,
                    color = levelColor,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                )
            }

            Spacer(modifier = Modifier.width(10.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = log.message,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = log.timestamp.take(19).replace("T", " "),
                    fontSize = 10.sp,
                    color = Color.Gray
                )
            }
        }
    }
}

@Composable
fun EmptyStateView(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    subtitle: String
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = Color.LightGray,
                modifier = Modifier.size(64.dp)
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = title,
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp,
                color = Color.Gray
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = subtitle,
                fontSize = 12.sp,
                color = Color.LightGray
            )
        }
    }
}
