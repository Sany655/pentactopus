import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Pentactopus",
  description: "A private, polling-only assistant across your own devices.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
