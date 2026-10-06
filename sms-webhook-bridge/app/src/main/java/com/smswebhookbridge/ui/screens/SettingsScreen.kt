package com.smswebhookbridge.ui.screens

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smswebhookbridge.BridgeApplication
import com.smswebhookbridge.data.model.WebhookConfig
import com.smswebhookbridge.ui.MainUiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    state: MainUiState,
    onSaveConfig: (WebhookConfig) -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val app = context.applicationContext as BridgeApplication

    var senderNumber by remember(state.config) { mutableStateOf(state.config.senderNumber) }
    var webhookUrl by remember(state.config) { mutableStateOf(state.config.webhookUrl) }
    var httpMethod by remember(state.config) { mutableStateOf(state.config.httpMethod) }
    var authToken by remember(state.config) { mutableStateOf(state.config.authToken) }
    var isTokenVisible by remember { mutableStateOf(false) }

    var maxRetries by remember(state.config) { mutableStateOf(state.config.maxRetries.toString()) }
    var retryIntervalSeconds by remember(state.config) { mutableStateOf(state.config.retryIntervalSeconds.toString()) }

    var deleteMatchingContentEnabled by remember(state.config) { mutableStateOf(state.config.deleteMatchingContentEnabled) }
    var deleteTriggerNumber by remember(state.config) { mutableStateOf(state.config.deleteTriggerNumber) }

    val isDefaultSmsApp = app.smsDeleteManager.isDefaultSmsApp()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Webhook Configuration",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Sender Number
        OutlinedTextField(
            value = senderNumber,
            onValueChange = { senderNumber = it },
            label = { Text("Allowed Sender Phone Number / ID") },
            placeholder = { Text("+1XXXXXXXXXX or +8801XXXXXXXXX") },
            supportingText = { Text("Only messages strictly matching this sender will be forwarded.") },
            leadingIcon = { Icon(Icons.Default.Phone, contentDescription = null) },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Webhook URL
        OutlinedTextField(
            value = webhookUrl,
            onValueChange = { webhookUrl = it },
            label = { Text("Webhook URL (HTTPS only)") },
            placeholder = { Text("https://example.com/api/sms/incoming") },
            supportingText = {
                val isHttps = webhookUrl.startsWith("https://", ignoreCase = true)
                Text(
                    text = if (webhookUrl.isNotBlank() && !isHttps) "Error: Only HTTPS endpoints are supported for security." else "Destination webhook endpoint.",
                    color = if (webhookUrl.isNotBlank() && !isHttps) MaterialTheme.colorScheme.error else Color.Gray
                )
            },
            isError = webhookUrl.isNotBlank() && !webhookUrl.startsWith("https://", ignoreCase = true),
            leadingIcon = { Icon(Icons.Default.Link, contentDescription = null) },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        // HTTP Method Selector (POST / GET)
        Text(text = "HTTP Method", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            FilterChip(
                selected = httpMethod.equals("POST", ignoreCase = true),
                onClick = { httpMethod = "POST" },
                label = { Text("POST (JSON Body)") },
                modifier = Modifier.weight(1f)
            )
            FilterChip(
                selected = httpMethod.equals("GET", ignoreCase = true),
                onClick = { httpMethod = "GET" },
                label = { Text("GET (URL Query Params)") },
                modifier = Modifier.weight(1f)
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Auth Token / Secret
        OutlinedTextField(
            value = authToken,
            onValueChange = { authToken = it },
            label = { Text("Shared Secret / Token (Optional)") },
            placeholder = { Text("Bearer token for Authorization header") },
            supportingText = { Text("Sent as: Authorization: Bearer <token>") },
            visualTransformation = if (isTokenVisible) VisualTransformation.None else PasswordVisualTransformation(),
            leadingIcon = { Icon(Icons.Default.Key, contentDescription = null) },
            trailingIcon = {
                IconButton(onClick = { isTokenVisible = !isTokenVisible }) {
                    Icon(
                        imageVector = if (isTokenVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                        contentDescription = "Toggle Token Visibility"
                    )
                }
            },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Divider()

        Spacer(modifier = Modifier.height(16.dp))

        // Reliability / Retry Settings
        Text(
            text = "Reliability & Retry Settings",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(10.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedTextField(
                value = maxRetries,
                onValueChange = { maxRetries = it.filter { char -> char.isDigit() } },
                label = { Text("Max Retries") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier.weight(1f)
            )

            OutlinedTextField(
                value = retryIntervalSeconds,
                onValueChange = { retryIntervalSeconds = it.filter { char -> char.isDigit() } },
                label = { Text("Initial Delay (sec)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier.weight(1f)
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Divider()

        Spacer(modifier = Modifier.height(16.dp))

        // SMS Content Deletion Feature
        Text(
            text = "SMS Auto-Deletion Feature",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = "Automatically delete matching messages if they contain a specific number/code in their content.",
            fontSize = 12.sp,
            color = Color.Gray
        )

        Spacer(modifier = Modifier.height(10.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = "Enable content-based deletion",
                fontWeight = FontWeight.Medium,
                fontSize = 14.sp
            )
            Switch(
                checked = deleteMatchingContentEnabled,
                onCheckedChange = { deleteMatchingContentEnabled = it }
            )
        }

        if (deleteMatchingContentEnabled) {
            Spacer(modifier = Modifier.height(10.dp))
            OutlinedTextField(
                value = deleteTriggerNumber,
                onValueChange = { deleteTriggerNumber = it },
                label = { Text("Specific Number in Content") },
                placeholder = { Text("e.g. 123456 or 999") },
                supportingText = { Text("If this number appears anywhere in the SMS text, deletion will be triggered.") },
                leadingIcon = { Icon(Icons.Default.DeleteSweep, contentDescription = null) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(10.dp))

            // Default SMS app notice card
            Card(
                shape = RoundedCornerShape(10.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (isDefaultSmsApp) Color(0xFFE8F5E9) else Color(0xFFFFF8E1)
                ),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(
                        text = if (isDefaultSmsApp) "Default SMS App: ACTIVE" else "Android Permission Note: Default SMS App Required",
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp,
                        color = if (isDefaultSmsApp) Color(0xFF2E7D32) else Color(0xFFF57F17)
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (isDefaultSmsApp)
                            "This app is the default SMS app and can delete messages from your inbox."
                        else
                            "Android strictly requires an app to be the 'Default SMS App' in order to delete messages from the system inbox. Non-default apps will receive a SecurityException.",
                        fontSize = 12.sp,
                        color = Color.DarkGray
                    )

                    if (!isDefaultSmsApp) {
                        Spacer(modifier = Modifier.height(8.dp))
                        Button(
                            onClick = {
                                try {
                                    val intent = app.smsDeleteManager.createDefaultSmsAppIntent()
                                    context.startActivity(intent)
                                } catch (_: Exception) {}
                            },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFF57F17)),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("Set as Default SMS App (to enable deletion)")
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Save Button
        Button(
            onClick = {
                val updatedConfig = WebhookConfig(
                    senderNumber = senderNumber.trim(),
                    webhookUrl = webhookUrl.trim(),
                    httpMethod = httpMethod,
                    authToken = authToken.trim(),
                    isEnabled = state.isEnabled,
                    maxRetries = maxRetries.toIntOrNull() ?: 3,
                    retryIntervalSeconds = retryIntervalSeconds.toIntOrNull() ?: 10,
                    deleteMatchingContentEnabled = deleteMatchingContentEnabled,
                    deleteTriggerNumber = deleteTriggerNumber.trim(),
                    deviceId = state.config.deviceId
                )
                onSaveConfig(updatedConfig)
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp),
            shape = RoundedCornerShape(12.dp)
        ) {
            Icon(Icons.Default.Save, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Save Configuration")
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}
