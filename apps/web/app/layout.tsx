import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Study Platform",
  description: "A focused workspace for learning from your course material.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
