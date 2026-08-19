import "./globals.css";
import React from "react";
import { Sidebar } from "@/components/Sidebar";
import { Navbar } from "@/components/Navbar";
import { CommandPalette } from "@/components/CommandPalette";

export const metadata = {
  title: "QUANTARA — AI Quantitative Trading & Research Platform",
  description: "Institutional-grade event-driven quantitative trading, AI multi-agent research, and deterministic risk execution terminal.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 min-h-screen flex">
        {/* Left Navigation Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar />
          <main className="flex-1 p-4 overflow-y-auto max-w-[1600px] w-full mx-auto">
            {children}
          </main>
        </div>

        {/* Global Command Palette */}
        <CommandPalette />
      </body>
    </html>
  );
}
