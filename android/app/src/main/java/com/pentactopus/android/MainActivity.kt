package com.pentactopus.android

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.snackbar.Snackbar
import com.pentactopus.android.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val keyAlias = KeyStoreHelper.getOrCreateDeviceKey()
        binding.status.text = "Device key ready: $keyAlias"

        binding.readButton.setOnClickListener {
            val notifications = PentactopusNotificationListener.snapshot()
            val summary = notifications.joinToString(separator = "\n") {
                "${it.title}: ${it.text}"
            }.ifBlank { "No unread notifications" }
            binding.messageText.text = summary
        }

        binding.approveButton.setOnClickListener {
            val intent = Intent(this, ApprovalActivity::class.java)
            startActivity(intent)
        }

        binding.readButton.setOnLongClickListener {
            Snackbar.make(binding.root, "Reading WhatsApp/notification content locally only.", Snackbar.LENGTH_SHORT).show()
            true
        }
    }
}
