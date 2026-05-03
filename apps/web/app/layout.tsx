import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/Providers";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Veridict - Forensic Accident Reconstruction",
  description:
    "AI-powered forensic reconstruction system for traffic accidents",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans m-0 p-0`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
