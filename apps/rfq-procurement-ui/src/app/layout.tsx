import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RFQ Procurement Control Plane",
  description: "Supplier quote comparison and procurement decision surface",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
