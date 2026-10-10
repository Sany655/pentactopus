package com.pentactopus.android

import android.accessibilityservice.AccessibilityService
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Toast

class PentactopusAccessibilityService : AccessibilityService() {
    private var attemptedApprovalId: String? = null
    private var lastWaitingNoticeId: String? = null

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.packageName?.toString() != WHATSAPP_PACKAGE) return
        if (
            event.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED &&
            event.eventType != AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
        ) return
        processPendingApproval()
    }

    override fun onInterrupt() = Unit

    private fun processPendingApproval() {
        val encoded = runCatching {
            SecureSettings.get(this, ApprovalActivity.PENDING_SEND_KEY)
        }.getOrNull() ?: return

        val approval = runCatching { ApprovedWhatsAppSend.fromJson(encoded) }.getOrElse {
            SecureSettings.remove(this, ApprovalActivity.PENDING_SEND_KEY)
            showStatus("Stored approval was invalid and has been discarded.")
            return
        }
        if (System.currentTimeMillis() >= approval.expiresAtEpochMs) {
            SecureSettings.remove(this, ApprovalActivity.PENDING_SEND_KEY)
            showStatus("The five-minute approval expired. Review the message again to approve it.")
            return
        }
        if (approval.approvalId == attemptedApprovalId) return

        val root = rootInActiveWindow ?: return
        if (!visibleExactRecipient(root, approval.recipient)) {
            if (lastWaitingNoticeId != approval.approvalId) {
                showStatus("Waiting for the WhatsApp chat matching the approved recipient.")
                lastWaitingNoticeId = approval.approvalId
            }
            return
        }
        val messageInput = findMessageInput(root) ?: run {
            notifyAndDiscard(approval.approvalId, "No send: the WhatsApp message field was not identified.")
            return
        }
        val sendButton = findSendButton(root) ?: run {
            notifyAndDiscard(approval.approvalId, "No send: the WhatsApp send button was not identified.")
            return
        }

        attemptedApprovalId = approval.approvalId
        SecureSettings.remove(this, ApprovalActivity.PENDING_SEND_KEY)
        val arguments = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, approval.text)
        }
        if (!messageInput.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)) {
            showStatus("No send: WhatsApp did not accept the approved text.")
            return
        }
        if (messageInput.text?.toString() != approval.text) {
            messageInput.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, "")
            })
            showStatus("No send: the visible draft differs from the approved text.")
            return
        }
        val refreshedRoot = rootInActiveWindow
        if (refreshedRoot == null || !visibleExactRecipient(refreshedRoot, approval.recipient)) {
            showStatus("No send: the active WhatsApp chat changed after approval.")
            return
        }
        val refreshedMessageInput = findMessageInput(refreshedRoot)
        if (refreshedMessageInput?.text?.toString() != approval.text) {
            notifyAndDiscard(approval.approvalId, "No send: the visible draft changed after approval.")
            return
        }
        val refreshedSendButton = findSendButton(refreshedRoot)
        if (refreshedSendButton == null ||
            !refreshedSendButton.performAction(AccessibilityNodeInfo.ACTION_CLICK)
        ) {
            showStatus("No send: WhatsApp did not accept the send action.")
            return
        }
        showStatus("Approved message sent once.")
    }

    private fun visibleExactRecipient(root: AccessibilityNodeInfo, recipient: String): Boolean {
        val wanted = normalize(recipient)
        if (wanted.isEmpty()) return false
        return visit(root) { node ->
            if (node.className != "android.widget.TextView") return@visit false
            val visibleText = node.text?.toString()?.trim().orEmpty()
            val resourceId = node.viewIdResourceName.orEmpty()
            val looksLikeHeader = resourceId.contains("title", ignoreCase = true) ||
                resourceId.contains("contact", ignoreCase = true)
            if (!looksLikeHeader) return@visit false
            visibleText.equals(recipient.trim(), ignoreCase = true) ||
                (wanted.length >= 7 && normalize(visibleText) == wanted)
        }
    }

    private fun findMessageInput(root: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        return findFirst(root) { node ->
            if (!node.isEditable || node.className != "android.widget.EditText") return@findFirst false
            val hint = node.hintText?.toString().orEmpty()
            val viewId = node.viewIdResourceName.orEmpty()
            hint.contains("message", ignoreCase = true) ||
                viewId.contains("entry", ignoreCase = true) ||
                viewId.contains("input", ignoreCase = true)
        }
    }

    private fun findSendButton(root: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        return findFirst(root) { node ->
            if (!node.isClickable) return@findFirst false
            val label = listOfNotNull(node.text?.toString(), node.contentDescription?.toString())
                .joinToString(" ")
            label.equals("send", ignoreCase = true)
        }
    }

    private fun findFirst(
        node: AccessibilityNodeInfo,
        predicate: (AccessibilityNodeInfo) -> Boolean,
    ): AccessibilityNodeInfo? {
        if (predicate(node)) return node
        for (index in 0 until node.childCount) {
            val child = node.getChild(index) ?: continue
            val match = findFirst(child, predicate)
            if (match != null) return match
        }
        return null
    }

    private fun visit(
        node: AccessibilityNodeInfo,
        predicate: (AccessibilityNodeInfo) -> Boolean,
    ): Boolean {
        if (predicate(node)) return true
        for (index in 0 until node.childCount) {
            val child = node.getChild(index) ?: continue
            if (visit(child, predicate)) return true
        }
        return false
    }

    private fun normalize(value: String): String =
        value.filter(Char::isLetterOrDigit).lowercase()

    private fun showStatus(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }

    private fun notifyAndDiscard(approvalId: String, message: String) {
        attemptedApprovalId = approvalId
        SecureSettings.remove(this, ApprovalActivity.PENDING_SEND_KEY)
        showStatus(message)
    }

    companion object {
        private const val WHATSAPP_PACKAGE = "com.whatsapp"
    }
}
