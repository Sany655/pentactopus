package com.smswebhookbridge.data

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import com.smswebhookbridge.data.model.AppLog
import com.smswebhookbridge.data.model.EventStatus
import com.smswebhookbridge.data.model.WebhookEvent

class AppDatabase(context: Context) : SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS $TABLE_EVENTS (
                $COL_EVENT_ID TEXT PRIMARY KEY,
                $COL_SENDER TEXT NOT NULL,
                $COL_MESSAGE TEXT NOT NULL,
                $COL_RECEIVED_AT TEXT NOT NULL,
                $COL_DEVICE_ID TEXT NOT NULL,
                $COL_STATUS TEXT NOT NULL,
                $COL_ATTEMPT_COUNT INTEGER NOT NULL DEFAULT 0,
                $COL_LAST_ATTEMPT_AT TEXT,
                $COL_RESPONSE_CODE INTEGER,
                $COL_ERROR_MESSAGE TEXT,
                $COL_DELETED_FROM_INBOX INTEGER NOT NULL DEFAULT 0
            )
            """.trimIndent()
        )

        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS $TABLE_LOGS (
                $COL_LOG_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COL_LOG_TIMESTAMP TEXT NOT NULL,
                $COL_LOG_LEVEL TEXT NOT NULL,
                $COL_LOG_MESSAGE TEXT NOT NULL
            )
            """.trimIndent()
        )

        // Create index for fast status queries and deduplication lookups
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_events_status ON $TABLE_EVENTS ($COL_STATUS)")
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_events_received ON $TABLE_EVENTS ($COL_RECEIVED_AT)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Simple migration if needed in future
    }

    // --- EVENTS CRUD ---

    @Synchronized
    fun insertEvent(event: WebhookEvent): Boolean {
        val db = writableDatabase
        val cv = ContentValues().apply {
            put(COL_EVENT_ID, event.eventId)
            put(COL_SENDER, event.sender)
            put(COL_MESSAGE, event.message)
            put(COL_RECEIVED_AT, event.receivedAt)
            put(COL_DEVICE_ID, event.deviceId)
            put(COL_STATUS, event.status.name)
            put(COL_ATTEMPT_COUNT, event.attemptCount)
            put(COL_LAST_ATTEMPT_AT, event.lastAttemptAt)
            put(COL_RESPONSE_CODE, event.responseCode)
            put(COL_ERROR_MESSAGE, event.errorMessage)
            put(COL_DELETED_FROM_INBOX, if (event.deletedFromInbox) 1 else 0)
        }
        val rowId = db.insertWithOnConflict(TABLE_EVENTS, null, cv, SQLiteDatabase.CONFLICT_IGNORE)
        return rowId != -1L
    }

    @Synchronized
    fun updateEventStatus(
        eventId: String,
        status: EventStatus,
        attemptCount: Int,
        lastAttemptAt: String?,
        responseCode: Int?,
        errorMessage: String?,
        deletedFromInbox: Boolean? = null
    ) {
        val db = writableDatabase
        val cv = ContentValues().apply {
            put(COL_STATUS, status.name)
            put(COL_ATTEMPT_COUNT, attemptCount)
            put(COL_LAST_ATTEMPT_AT, lastAttemptAt)
            put(COL_RESPONSE_CODE, responseCode)
            put(COL_ERROR_MESSAGE, errorMessage)
            if (deletedFromInbox != null) {
                put(COL_DELETED_FROM_INBOX, if (deletedFromInbox) 1 else 0)
            }
        }
        db.update(TABLE_EVENTS, cv, "$COL_EVENT_ID = ?", arrayOf(eventId))
    }

    @Synchronized
    fun getEventById(eventId: String): WebhookEvent? {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_EVENTS,
            null,
            "$COL_EVENT_ID = ?",
            arrayOf(eventId),
            null,
            null,
            null
        )
        return cursor.use {
            if (it.moveToFirst()) cursorToEvent(it) else null
        }
    }

    @Synchronized
    fun getPendingEvents(): List<WebhookEvent> {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_EVENTS,
            null,
            "$COL_STATUS IN (?, ?)",
            arrayOf(EventStatus.PENDING.name, EventStatus.FAILED.name),
            null,
            null,
            "$COL_RECEIVED_AT ASC"
        )
        return cursor.use { cursorToEventList(it) }
    }

    @Synchronized
    fun getAllEvents(limit: Int = 100): List<WebhookEvent> {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_EVENTS,
            null,
            null,
            null,
            null,
            null,
            "$COL_RECEIVED_AT DESC",
            limit.toString()
        )
        return cursor.use { cursorToEventList(it) }
    }

    @Synchronized
    fun isDuplicateRecent(sender: String, message: String, sinceIsoTimestamp: String): Boolean {
        val db = readableDatabase
        val cursor = db.rawQuery(
            """
            SELECT 1 FROM $TABLE_EVENTS 
            WHERE $COL_SENDER = ? AND $COL_MESSAGE = ? AND $COL_RECEIVED_AT >= ?
            LIMIT 1
            """.trimIndent(),
            arrayOf(sender, message, sinceIsoTimestamp)
        )
        return cursor.use { it.moveToFirst() }
    }

    // --- LOGS CRUD ---

    @Synchronized
    fun insertLog(level: String, message: String) {
        val db = writableDatabase
        val cv = ContentValues().apply {
            put(COL_LOG_TIMESTAMP, java.time.Instant.now().toString())
            put(COL_LOG_LEVEL, level)
            put(COL_LOG_MESSAGE, message)
        }
        db.insert(TABLE_LOGS, null, cv)

        // Keep last 500 logs to avoid unbounded growth
        db.execSQL(
            """
            DELETE FROM $TABLE_LOGS WHERE $COL_LOG_ID NOT IN (
                SELECT $COL_LOG_ID FROM $TABLE_LOGS ORDER BY $COL_LOG_ID DESC LIMIT 500
            )
            """.trimIndent()
        )
    }

    @Synchronized
    fun getLogs(limit: Int = 200): List<AppLog> {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_LOGS,
            null,
            null,
            null,
            null,
            null,
            "$COL_LOG_ID DESC",
            limit.toString()
        )
        val list = mutableListOf<AppLog>()
        cursor.use {
            while (it.moveToNext()) {
                list.add(
                    AppLog(
                        id = it.getLong(it.getColumnIndexOrThrow(COL_LOG_ID)),
                        timestamp = it.getString(it.getColumnIndexOrThrow(COL_LOG_TIMESTAMP)),
                        level = it.getString(it.getColumnIndexOrThrow(COL_LOG_LEVEL)),
                        message = it.getString(it.getColumnIndexOrThrow(COL_LOG_MESSAGE))
                    )
                )
            }
        }
        return list
    }

    @Synchronized
    fun clearLogs() {
        val db = writableDatabase
        db.delete(TABLE_LOGS, null, null)
    }

    // --- Helpers ---

    private fun cursorToEventList(cursor: Cursor): List<WebhookEvent> {
        val list = mutableListOf<WebhookEvent>()
        while (cursor.moveToNext()) {
            list.add(cursorToEvent(cursor))
        }
        return list
    }

    private fun cursorToEvent(c: Cursor): WebhookEvent {
        return WebhookEvent(
            eventId = c.getString(c.getColumnIndexOrThrow(COL_EVENT_ID)),
            sender = c.getString(c.getColumnIndexOrThrow(COL_SENDER)),
            message = c.getString(c.getColumnIndexOrThrow(COL_MESSAGE)),
            receivedAt = c.getString(c.getColumnIndexOrThrow(COL_RECEIVED_AT)),
            deviceId = c.getString(c.getColumnIndexOrThrow(COL_DEVICE_ID)),
            status = EventStatus.valueOf(c.getString(c.getColumnIndexOrThrow(COL_STATUS))),
            attemptCount = c.getInt(c.getColumnIndexOrThrow(COL_ATTEMPT_COUNT)),
            lastAttemptAt = c.getString(c.getColumnIndexOrThrow(COL_LAST_ATTEMPT_AT)),
            responseCode = if (c.isNull(c.getColumnIndexOrThrow(COL_RESPONSE_CODE))) null else c.getInt(c.getColumnIndexOrThrow(COL_RESPONSE_CODE)),
            errorMessage = c.getString(c.getColumnIndexOrThrow(COL_ERROR_MESSAGE)),
            deletedFromInbox = c.getInt(c.getColumnIndexOrThrow(COL_DELETED_FROM_INBOX)) == 1
        )
    }

    companion object {
        const val DATABASE_NAME = "sms_webhook_bridge.db"
        const val DATABASE_VERSION = 1

        const val TABLE_EVENTS = "events"
        const val COL_EVENT_ID = "event_id"
        const val COL_SENDER = "sender"
        const val COL_MESSAGE = "message"
        const val COL_RECEIVED_AT = "received_at"
        const val COL_DEVICE_ID = "device_id"
        const val COL_STATUS = "status"
        const val COL_ATTEMPT_COUNT = "attempt_count"
        const val COL_LAST_ATTEMPT_AT = "last_attempt_at"
        const val COL_RESPONSE_CODE = "response_code"
        const val COL_ERROR_MESSAGE = "error_message"
        const val COL_DELETED_FROM_INBOX = "deleted_from_inbox"

        const val TABLE_LOGS = "logs"
        const val COL_LOG_ID = "id"
        const val COL_LOG_TIMESTAMP = "timestamp"
        const val COL_LOG_LEVEL = "level"
        const val COL_LOG_MESSAGE = "message"
    }
}
