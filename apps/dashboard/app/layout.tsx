import Link from "next/link";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>
        <header
          style={{
            position: "sticky",
            top: 0,
            zIndex: 20,
            backdropFilter: "blur(18px)",
            background: "rgba(4, 8, 14, 0.72)",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
          }}
        >
          <div
            style={{
              maxWidth: 1240,
              margin: "0 auto",
              padding: "16px 22px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 16,
              color: "#eef4fb",
              fontFamily: "ui-sans-serif, system-ui, sans-serif",
            }}
          >
            <div>
              <div style={{ letterSpacing: "0.2em", textTransform: "uppercase", color: "#8fb7d8", fontSize: 12 }}>
                MemCortex
              </div>
              <div style={{ fontSize: 18, fontWeight: 700 }}>Operator dashboard</div>
            </div>
            <nav style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
              <Link href="/" style={{ color: "#eef4fb", textDecoration: "none" }}>
                Overview
              </Link>
              <Link href="/harness" style={{ color: "#eef4fb", textDecoration: "none" }}>
                Harness readiness
              </Link>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
