import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NØVRA",
  description: "NØVRA - status, exclusividade e streetwear premium em drops limitados"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        {children}
      </body>
    </html>
  );
}
