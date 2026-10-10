export default function Home() {
  return (
    <main className="shell">
      <p className="eyebrow">PRIVATE BY DESIGN</p>
      <h1>Your devices, working together.</h1>
      <p className="intro">
        Pentactopus is a personal assistant for your own Windows and Android
        devices. Each device keeps its own agent, model key, and local policy.
      </p>
      <a className="button" href="/account">Sign in with email</a>
      <section className="notice">
        <h2>Before enabling WhatsApp</h2>
        <p>
          Windows support reads the official WhatsApp Desktop app for personal
          use. Automation may be restricted by WhatsApp&apos;s terms. Review
          the current terms and accept that risk before enabling this feature.
        </p>
      </section>
      <p className="footnote">
        Message text may be processed by your chosen model provider. Third
        parties who message you are not party to that agreement. You are
        responsible for your provider account and key. A local-only model
        option keeps content on your devices.
      </p>
    </main>
  );
}
