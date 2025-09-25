// frontend/src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/providers";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LearnHub - Online Course Platform",
  description: "Learn new skills with expert-led courses",
  keywords: "online courses, learning, education, skills",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.className}>
      <Analytics/>
      <SpeedInsights/>
      <body className="min-h-screen bg-gray-50 antialiased">
        <Providers>
          <div id="root" className="relative">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
