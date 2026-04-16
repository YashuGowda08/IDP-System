import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "IDP System — AI-Powered Document Processing",
  description:
    "Extract text, tables, and images from documents using OCR, NLP, and Computer Vision. Supports PDF, JPG, PNG with automated classification and structured data export.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen">
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
