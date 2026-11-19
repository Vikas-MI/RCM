import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart RCM Eligibility",
  description:
    "Patient & Insurance Eligibility Management — HAPI FHIR R4 + Mock Eligibility Provider",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
