import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Gym Recommendation System",
  description: "Browse, compare, and recommend gyms with a Python-powered backend.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="site-header">
            <div className="eyebrow">Fitness Finder</div>
            <h2>Gym Recommendation System</h2>
            <nav className="site-nav">
              <Link href="/">Home</Link>
              <Link href="/browse">Browse</Link>
              <Link href="/recommend">Recommend</Link>
              <Link href="/compare">Compare</Link>
              <Link href="/admin">Admin</Link>
            </nav>
          </header>
        </div>
        {children}
      </body>
    </html>
  );
}
