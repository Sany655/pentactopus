package com.pentactopus.android

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.snackbar.Snackbar
import com.pentactopus.android.databinding.ActivityApprovalBinding

class ApprovalActivity : AppCompatActivity() {
    private lateinit var binding: ActivityApprovalBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityApprovalBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.approveButton.setOnClickListener {
            val appName = binding.appNameInput.text?.toString() ?: ""
            if (appName.isBlank()) {
                Snackbar.make(binding.root, "Recipient or app name is required.", Snackbar.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            Snackbar.make(binding.root, "Approval recorded locally for $appName.", Snackbar.LENGTH_SHORT).show()
            finish()
        }
    }
}
