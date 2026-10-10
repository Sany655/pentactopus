package com.pentactopus.android

import java.net.URI

internal object ModelEndpointPolicy {
    private val loopbackHosts = setOf("localhost")

    fun allows(value: String): Boolean = runCatching {
        val uri = URI(value)
        val host = uri.host?.lowercase().orEmpty()
        val isHttps = uri.scheme.equals("https", ignoreCase = true)
        val isLocalHttp = uri.scheme.equals("http", ignoreCase = true) && host in loopbackHosts
        (isHttps || isLocalHttp) &&
            host.isNotBlank() &&
            uri.rawUserInfo == null &&
            uri.rawFragment == null
    }.getOrDefault(false)

    fun requiresApiKey(value: String): Boolean =
        URI(value).scheme.equals("https", ignoreCase = true)
}
