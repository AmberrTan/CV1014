import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Gym Recommendation System",
  description: "Browse and compare gyms with a Python-powered backend.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <div className="shell">
            <div className="eyebrow">Fitness Finder</div>
            <h2>
              <Link href="/">Gym Recommendation System</Link>
            </h2>
            <nav className="site-nav" aria-label="Main Navigation">
              <Link href="/">Home</Link>
              <Link href="/browse">Browse</Link>
              <Link href="/compare">Compare</Link>
            </nav>
          </div>
        </header>
        {children}
        <footer className="shell section" style={{ marginTop: "auto", borderTop: "1px solid var(--line)", padding: "40px 0" }}>
          <p>&copy; {new Date().getFullYear()} Gym Recommendation System. Powered by Python & Next.js.</p>
        </footer>
      </body>
    </html>
  );
}
