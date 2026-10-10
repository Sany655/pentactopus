package com.pentactopus.android

import android.content.Context
import android.util.Base64
import org.bouncycastle.jce.provider.BouncyCastleProvider
import java.security.KeyFactory
import java.security.KeyPairGenerator
import java.security.Signature
import java.security.spec.PKCS8EncodedKeySpec

class AndroidDeviceIdentity private constructor(
    private val context: Context,
    private val publicKeyRaw: ByteArray,
) {
    fun publicKeyBase64Url(): String =
        Base64.encodeToString(publicKeyRaw, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)

    fun sign(message: ByteArray): ByteArray {
        val encodedPrivateKey = SecureSettings.get(context, PRIVATE_KEY_PREF)
            ?: throw IllegalStateException("The Android device signing key is unavailable.")
        val privateKey = KeyFactory.getInstance("Ed25519", PROVIDER)
            .generatePrivate(PKCS8EncodedKeySpec(Base64.decode(encodedPrivateKey, Base64.NO_WRAP)))
        return Signature.getInstance("Ed25519", PROVIDER).run {
            initSign(privateKey)
            update(message)
            sign()
        }
    }

    companion object {
        private const val PRIVATE_KEY_PREF = "android_device_ed25519_private_key"
        private const val PUBLIC_KEY_PREF = "android_device_ed25519_public_key"
        private val PROVIDER = BouncyCastleProvider()

        fun getOrCreate(context: Context): AndroidDeviceIdentity {
            KeyStoreHelper.getOrCreateDeviceKey()
            val publicKey = SecureSettings.get(context, PUBLIC_KEY_PREF)
            if (publicKey != null && SecureSettings.get(context, PRIVATE_KEY_PREF) != null) {
                return AndroidDeviceIdentity(
                    context.applicationContext,
                    Base64.decode(publicKey, Base64.NO_WRAP),
                )
            }
            val keyPair = KeyPairGenerator.getInstance("Ed25519", PROVIDER).generateKeyPair()
            val encodedPublicKey = keyPair.public.encoded
            require(encodedPublicKey.size >= RAW_PUBLIC_KEY_SIZE) { "Generated Ed25519 public key is invalid." }
            val rawPublicKey = encodedPublicKey.copyOfRange(
                encodedPublicKey.size - RAW_PUBLIC_KEY_SIZE,
                encodedPublicKey.size,
            )
            SecureSettings.put(
                context,
                PRIVATE_KEY_PREF,
                Base64.encodeToString(keyPair.private.encoded, Base64.NO_WRAP),
            )
            SecureSettings.put(
                context,
                PUBLIC_KEY_PREF,
                Base64.encodeToString(rawPublicKey, Base64.NO_WRAP),
            )
            return AndroidDeviceIdentity(context.applicationContext, rawPublicKey)
        }

        private const val RAW_PUBLIC_KEY_SIZE = 32
    }
}
