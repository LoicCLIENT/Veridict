import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/Header";
import { Providers } from "@/components/Providers";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Veridict - Reconstruccion Forense de Accidentes",
  description:
    "Sistema de reconstruccion forense automatizada de accidentes de trafico",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <body
        className={`${inter.variable} font-sans bg-[#1F3329] text-[#F5F5F0] min-h-screen`}
      >
        <Providers>
          <Header />
          <main className="mx-auto max-w-[1280px] px-6">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
