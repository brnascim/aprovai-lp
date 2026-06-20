import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Aprovaí — Assistente Motor Anti-ATS",
  description:
    "Reescreve seu currículo, carta e LinkedIn para passar pela triagem automática (ATS) e chegar ao recrutador.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
