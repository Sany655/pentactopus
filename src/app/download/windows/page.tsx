export default function WindowsDownloadPage() {
  const url = process.env.WINDOWS_DOWNLOAD_URL;
  return (
    <main className="shell">
      <h1>Windows agent</h1>
      {url ? <a className="button" href={url}>Download for Windows</a> : <p>A v1 Windows release is not available yet.</p>}
      <p className="footnote">Only install releases published by the Pentactopus project.</p>
    </main>
  );
}
