import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NØVRA - Premium Streetwear",
  description: "Fashion minimalista e premium",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="bg-black text-white">{children}</body>
    </html>
  );
}
