export default function AndroidDownloadPage() {
  const url = process.env.ANDROID_DOWNLOAD_URL;
  return (
    <main className="shell">
      <h1>Android agent</h1>
      {url ? <a className="button" href={url}>Download for Android</a> : <p>A v1 Android release is not available yet.</p>}
      <p className="footnote">Android v1 will support Android 8.0 (API 26) and newer.</p>
    </main>
  );
}
