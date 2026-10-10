"use client";

import { useState } from "react";

export default function ConsumeLink() {
  const [message, setMessage] = useState("Confirm that you want to sign in to Pentactopus.");
  const [busy, setBusy] = useState(false);

  async function consume(): Promise<void> {
    const linkToken = new URLSearchParams(window.location.hash.slice(1)).get("token") ?? "";
    if (!linkToken) {
      setMessage("This sign-in link is invalid or expired. Request a new one from your account page.");
      return;
    }
    window.history.replaceState(null, "", window.location.pathname);
    setBusy(true);
    const response = await fetch("/api/v1/auth/magic-links/consume", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: linkToken }),
    });
    if (response.ok) {
      window.location.replace("/account");
      return;
    }
    setMessage("This sign-in link is invalid or expired. Request a new one from your account page.");
    setBusy(false);
  }

  return (
    <section className="panel">
      <h1>Confirm sign-in</h1>
      <p>{message}</p>
      <button className="button" disabled={busy} onClick={() => void consume()}>
        {busy ? "Signing in…" : "Continue"}
      </button>
    </section>
  );
}
