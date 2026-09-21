package com.pentactopus.assistant.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Intent
import android.graphics.Path
import android.os.Build
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStream
import java.net.ServerSocket
import java.net.Socket
import kotlin.concurrent.thread

/**
 * PentaAccessibilityService
 *
 * Provides native tactile gesture injection and UI navigation without requiring ADB
 * or root privileges. Listens on a local loopback port (127.0.0.1:18888) to accept
 * commands from the local companion relay or Termux daemon.
 */
class PentaAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "PentaAccessibility"
        private const val SERVER_PORT = 18888
        var instance: PentaAccessibilityService? = null
            private set
    }

    private var serverSocket: ServerSocket? = null
    private var isRunning = false

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.i(TAG, "PentaAccessibilityService connected successfully")
        startCommandServer()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Accessibility events can be captured for real-time window tracking
    }

    override fun onInterrupt() {
        Log.w(TAG, "PentaAccessibilityService interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        isRunning = false
        try {
            serverSocket?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing server socket", e)
        }
    }

    /**
     * Dispatches a single tap gesture at normalized or screen pixel coordinates.
     */
    fun dispatchTap(x: Float, y: Float, durationMs: Long = 50): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) return false

        val path = Path()
        path.moveTo(x, y)
        val stroke = GestureDescription.StrokeDescription(path, 0, durationMs)
        val gesture = GestureDescription.Builder().addStroke(stroke).build()
        return dispatchGesture(gesture, object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) {
                Log.d(TAG, "Tap completed at ($x, $y)")
            }
            override fun onCancelled(gestureDescription: GestureDescription?) {
                Log.w(TAG, "Tap cancelled at ($x, $y)")
            }
        }, null)
    }

    /**
     * Dispatches a smooth swipe gesture between two points.
     */
    fun dispatchSwipe(startX: Float, startY: Float, endX: Float, endY: Float, durationMs: Long = 300): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) return false

        val path = Path()
        path.moveTo(startX, startY)
        path.lineTo(endX, endY)
        val stroke = GestureDescription.StrokeDescription(path, 0, durationMs)
        val gesture = GestureDescription.Builder().addStroke(stroke).build()
        return dispatchGesture(gesture, null, null)
    }

    /**
     * Dispatches system global navigation actions (Back, Home, Recents, Notifications).
     */
    fun performNavigation(action: String): Boolean {
        return when (action.uppercase()) {
            "BACK" -> performGlobalAction(GLOBAL_ACTION_BACK)
            "HOME" -> performGlobalAction(GLOBAL_ACTION_HOME)
            "RECENTS" -> performGlobalAction(GLOBAL_ACTION_RECENTS)
            "NOTIFICATIONS" -> performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)
            "QUICK_SETTINGS" -> performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS)
            else -> false
        }
    }

    /**
     * Starts a lightweight HTTP/JSON command server on localhost to allow companion_relay.py
     * to invoke actions seamlessly.
     */
    private fun startCommandServer() {
        isRunning = true
        thread(name = "PentaA11yServer") {
            try {
                serverSocket = ServerSocket(SERVER_PORT)
                Log.i(TAG, "A11y Command Server listening on 127.0.0.1:$SERVER_PORT")

                while (isRunning) {
                    val client: Socket = serverSocket?.accept() ?: break
                    thread { handleClient(client) }
                }
            } catch (e: Exception) {
                if (isRunning) {
                    Log.e(TAG, "A11y server error: ${e.message}")
                }
            }
        }
    }

    private fun handleClient(client: Socket) {
        try {
            val reader = BufferedReader(InputStreamReader(client.getInputStream()))
            val out: OutputStream = client.getOutputStream()

            var line: String? = reader.readLine()
            var contentLength = 0

            while (!line.isNullOrEmpty()) {
                if (line.startsWith("Content-Length:", ignoreCase = true)) {
                    contentLength = line.substringAfter(":").trim().toIntOrNull() ?: 0
                }
                line = reader.readLine()
            }

            val body = if (contentLength > 0) {
                val chars = CharArray(contentLength)
                reader.read(chars, 0, contentLength)
                String(chars)
            } else ""

            var success = false
            var message = "Unknown action"

            if (body.isNotEmpty()) {
                val json = JSONObject(body)
                val action = json.optString("action", json.optString("type", ""))

                when (action.lowercase()) {
                    "tap", "click" -> {
                        val x = json.optDouble("x", 0.0).toFloat()
                        val y = json.optDouble("y", 0.0).toFloat()
                        success = dispatchTap(x, y)
                        message = if (success) "Tapped at ($x, $y)" else "Tap dispatch failed"
                    }
                    "swipe" -> {
                        val x1 = json.optDouble("x1", 0.0).toFloat()
                        val y1 = json.optDouble("y1", 0.0).toFloat()
                        val x2 = json.optDouble("x2", 0.0).toFloat()
                        val y2 = json.optDouble("y2", 0.0).toFloat()
                        val duration = json.optLong("duration", 300)
                        success = dispatchSwipe(x1, y1, x2, y2, duration)
                        message = if (success) "Swiped from ($x1,$y1) to ($x2,$y2)" else "Swipe failed"
                    }
                    "key", "hotkey", "nav" -> {
                        val key = json.optString("key", "BACK")
                        success = performNavigation(key)
                        message = if (success) "Navigated $key" else "Navigation failed"
                    }
                    "status", "ping" -> {
                        success = true
                        message = "PentaAccessibilityService Active"
                    }
                    else -> {
                        message = "Unsupported action: $action"
                    }
                }
            }

            val responseJson = JSONObject().apply {
                put("success", success)
                put("message", message)
                put("service", "PentaAccessibilityService")
            }.toString()

            val httpResponse = "HTTP/1.1 200 OK\r\n" +
                    "Content-Type: application/json\r\n" +
                    "Content-Length: ${responseJson.toByteArray().size}\r\n" +
                    "Connection: close\r\n\r\n" +
                    responseJson

            out.write(httpResponse.toByteArray())
            out.flush()
            client.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error handling client request", e)
        }
    }
}
