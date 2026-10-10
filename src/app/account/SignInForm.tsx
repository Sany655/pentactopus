"use client";

import { FormEvent, useEffect, useState } from "react";

type Device = { id: string; name: string; platform: string; last_seen_at: string | null };
type AuditEvent = { cursor: string; event_type: string; created_at: string };

export default function SignInForm() {
  const [email, setEmail] = useState("");
  const [notice, setNotice] = useState("");
  const [devices, setDevices] = useState<Device[]>([]);
  const [pairingCode, setPairingCode] = useState("");
  const [signedIn, setSignedIn] = useState(false);
  const [presentation, setPresentation] = useState<"full" | "summary">("full");
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);

  useEffect(() => {
    let active = true;
    fetch("/api/v1/auth/session", { cache: "no-store" })
      .then(async (session) => {
        if (!session.ok || !active) return null;
        setSignedIn(true);
        return Promise.all([
          fetch("/api/v1/devices", { cache: "no-store" }),
          fetch("/api/v1/settings", { cache: "no-store" }),
          fetch("/api/v1/audit-events?limit=5", { cache: "no-store" }),
        ]);
      })
      .then(async (responses) => {
        if (!responses || !active) return;
        const [deviceResponse, settingsResponse, auditResponse] = responses;
        if (deviceResponse.ok) {
          const data = await deviceResponse.json() as { data: { devices: Device[] } };
          if (active) setDevices(data.data.devices);
        }
        if (settingsResponse.ok) {
          const data = await settingsResponse.json() as { data: { settings: { message_presentation: "full" | "summary" } } };
          if (active) setPresentation(data.data.settings.message_presentation);
        }
        if (auditResponse.ok) {
          const data = await auditResponse.json() as { data: { events: AuditEvent[] } };
          if (active) setAuditEvents(data.data.events);
        }
      })
      .catch(() => {
        if (active) setNotice("Unable to load account details. Please retry.");
      });
    return () => { active = false; };
  }, []);

  async function requestLink(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setNotice("");
    const response = await fetch("/api/v1/auth/magic-links", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    setNotice(response.ok
      ? "If this address can receive mail, a sign-in link is on its way."
      : "We could not process that request. Please wait and try again.");
  }

  async function createPairingCode(): Promise<void> {
    setPairingCode("");
    const response = await fetch("/api/v1/pairing-codes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    if (response.ok) {
      const data = await response.json() as { data: { pairing_code: string } };
      setPairingCode(data.data.pairing_code);
      return;
    }
    setNotice("Unable to create a pairing code. Sign in again and retry.");
  }

  async function signOut(): Promise<void> {
    await fetch("/api/v1/auth/logout", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    setSignedIn(false);
    setDevices([]);
    setPairingCode("");
  }

  async function savePresentation(value: "full" | "summary"): Promise<void> {
    const response = await fetch("/api/v1/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_presentation: value }),
    });
    if (!response.ok) {
      setNotice("Unable to update message presentation.");
      return;
    }
    setPresentation(value);
  }

  if (signedIn) {
    return (
      <section className="panel">
        <h1>Your account</h1>
        <h2>Devices</h2>
        {devices.length === 0 ? <p>No devices paired yet.</p> : (
          <ul>{devices.map((device) => (
            <li key={device.id}>{device.name} <span>({device.platform})</span></li>
          ))}</ul>
        )}
        <button className="button" onClick={() => void createPairingCode()}>Pair a device</button>
        {pairingCode && <p className="pairing-code">Pairing code: <strong>{pairingCode}</strong></p>}
        <p className="footnote">This single-use code expires in 10 minutes. Enter it only on a device you own.</p>
        <h2>Message presentation</h2>
        <label htmlFor="presentation">Default for long messages</label>
        <select id="presentation" value={presentation}
          onChange={(event) => {
            const value = event.currentTarget.value;
            if (value === "full" || value === "summary") void savePresentation(value);
          }}>
          <option value="full">Full text</option>
          <option value="summary">Summary, preserving key details verbatim</option>
        </select>
        <h2>Recent account activity</h2>
        {auditEvents.length === 0 ? <p>No account events yet.</p> : (
          <ul>{auditEvents.map((event) => (
            <li key={event.cursor}>{event.event_type} — {new Date(event.created_at).toLocaleString()}</li>
          ))}</ul>
        )}
        <button className="secondary" onClick={() => void signOut()}>Sign out</button>
      </section>
    );
  }

  return (
    <section className="panel">
      <h1>Sign in</h1>
      <p>We will email you a single-use link. No password is created or stored.</p>
      <form onSubmit={(event) => void requestLink(event)}>
        <label htmlFor="email">Email address</label>
        <input id="email" type="email" autoComplete="email" required maxLength={254}
          value={email} onChange={(event) => setEmail(event.target.value)} />
        <button className="button" type="submit">Email me a sign-in link</button>
      </form>
      {notice && <p role="status">{notice}</p>}
      <p className="footnote">
        Message text may be processed by your selected model provider. People
        who message you are not party to that agreement; you are responsible
        for your provider account and key. Local-only models keep content on
        your devices.
      </p>
      <p className="footnote">
        Windows WhatsApp support uses the official Desktop app for personal
        use only. Automation may be restricted by WhatsApp&apos;s terms; review
        them and accept that risk before enabling the feature.
      </p>
    </section>
  );
}
