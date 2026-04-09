import Link from "next/link";

import { listHarnessTargets, readHarnessStatus, type HarnessTargetStatus } from "../../lib/harness";

export const dynamic = "force-dynamic";

function cardStyle(accent: string): React.CSSProperties {
  return {
    padding: 22,
    borderRadius: 20,
    background: "rgba(8, 16, 28, 0.8)",
    border: `1px solid ${accent}`,
    boxShadow: "0 18px 48px rgba(0, 0, 0, 0.18)",
  };
}

function badgeStyle(active: boolean): React.CSSProperties {
  return {
    display: "inline-flex",
    alignItems: "center",
    padding: "5px 10px",
    borderRadius: 999,
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: active ? "#08151a" : "#d8e5f2",
    background: active ? "#7ce2ad" : "rgba(142, 164, 184, 0.18)",
  };
}

function renderBoolean(value: boolean) {
  return value ? "ready" : "missing";
}

function TargetCard({ target }: { target: HarnessTargetStatus }) {
  const missing = Object.entries(target.checks)
    .filter(([, value]) => !value)
    .map(([key]) => key.replace(/_/g, " "));

  return (
    <article style={cardStyle(target.ready ? "rgba(92, 198, 169, 0.25)" : "rgba(255, 191, 91, 0.25)")}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
        <div>
          <p
            style={{
              margin: 0,
              color: "#8ea4b8",
              textTransform: "uppercase",
              letterSpacing: "0.12em",
            }}
          >
            {target.display_name}
          </p>
          <h2 style={{ margin: "8px 0 0" }}>{target.target}</h2>
        </div>
        <span style={badgeStyle(target.ready)}>{target.ready ? "ready" : "partial"}</span>
      </div>

      <div style={{ display: "grid", gap: 10, marginTop: 18 }}>
        <div>
          <p style={{ margin: 0, color: "#8ea4b8" }}>Install root</p>
          <p style={{ margin: "4px 0 0" }}>{target.install_root}</p>
        </div>
        <div>
          <p style={{ margin: 0, color: "#8ea4b8" }}>Capabilities</p>
          <p style={{ margin: "4px 0 0", color: "#dbe8f5" }}>
            MCP {renderBoolean(target.capabilities.supports_mcp)} · hooks{" "}
            {renderBoolean(target.capabilities.supports_hooks)} · HTTP{" "}
            {renderBoolean(target.capabilities.supports_http)} · stdio JSON{" "}
            {renderBoolean(target.capabilities.supports_stdio_json)}
          </p>
        </div>
        <div>
          <p style={{ margin: 0, color: "#8ea4b8" }}>Artifacts</p>
          <div style={{ display: "grid", gap: 8, marginTop: 8 }}>
            {target.artifacts.map((artifact) => (
              <div
                key={artifact.path}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.03)",
                }}
              >
                <span>{artifact.name}</span>
                <span style={{ color: artifact.exists ? "#7ce2ad" : "#ffb86b" }}>
                  {artifact.exists ? "present" : "missing"}
                </span>
              </div>
            ))}
          </div>
        </div>
        {missing.length > 0 ? (
          <div>
            <p style={{ margin: 0, color: "#8ea4b8" }}>Missing checks</p>
            <p style={{ margin: "4px 0 0", color: "#ffcb8a" }}>{missing.join(", ")}</p>
          </div>
        ) : (
          <div>
            <p style={{ margin: 0, color: "#8ea4b8" }}>Missing checks</p>
            <p style={{ margin: "4px 0 0", color: "#7ce2ad" }}>none</p>
          </div>
        )}
      </div>
    </article>
  );
}

export default async function HarnessPage() {
  const status = await readHarnessStatus();
  const targets = listHarnessTargets();
  const statusByTarget = new Map(status.targets.map((target) => [target.target, target]));

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "36px 22px 56px",
        color: "#eef4fb",
        background:
          "radial-gradient(circle at top left, rgba(31, 62, 88, 0.95) 0%, rgba(9, 14, 24, 1) 46%, rgba(4, 6, 9, 1) 100%)",
        fontFamily: "ui-sans-serif, system-ui, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1240, margin: "0 auto" }}>
        <header style={{ display: "grid", gap: 12, marginBottom: 22 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center" }}>
            <div>
              <p style={{ letterSpacing: "0.24em", textTransform: "uppercase", color: "#8fb7d8", margin: 0 }}>
                MemCortex Operator
              </p>
              <h1 style={{ margin: "10px 0 0", fontSize: 52, lineHeight: 1 }}>Harness readiness</h1>
            </div>
            <Link href="/" style={{ color: "#dbe8f5", textDecoration: "none" }}>
              Back to overview
            </Link>
          </div>
          <p style={{ margin: 0, maxWidth: 840, color: "#b9cddd", fontSize: 18 }}>
            This page inspects the project-local bootstrap artifacts emitted by the CLI for each
            supported harness target. Operators can verify which harnesses are ready, which
            integration surfaces each target supports, and what files were generated.
          </p>
        </header>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 16,
            marginBottom: 18,
          }}
        >
          <article style={cardStyle("rgba(112, 172, 230, 0.25)")}>
            <p style={{ margin: 0, color: "#8ea4b8", textTransform: "uppercase", letterSpacing: "0.12em" }}>
              Targets
            </p>
            <p style={{ margin: "10px 0 0", fontSize: 38, fontWeight: 700 }}>{targets.length}</p>
          </article>
          <article style={cardStyle("rgba(92, 198, 169, 0.25)")}>
            <p style={{ margin: 0, color: "#8ea4b8", textTransform: "uppercase", letterSpacing: "0.12em" }}>
              Ready
            </p>
            <p style={{ margin: "10px 0 0", fontSize: 38, fontWeight: 700 }}>
              {status.targets.filter((target) => target.ready).length}
            </p>
          </article>
          <article style={cardStyle("rgba(255, 191, 91, 0.22)")}>
            <p style={{ margin: 0, color: "#8ea4b8", textTransform: "uppercase", letterSpacing: "0.12em" }}>
              MCP-capable
            </p>
            <p style={{ margin: "10px 0 0", fontSize: 38, fontWeight: 700 }}>
              {status.targets.filter((target) => target.capabilities.supports_mcp).length}
            </p>
          </article>
          <article style={cardStyle("rgba(255, 120, 120, 0.22)")}>
            <p style={{ margin: 0, color: "#8ea4b8", textTransform: "uppercase", letterSpacing: "0.12em" }}>
              Hook-capable
            </p>
            <p style={{ margin: "10px 0 0", fontSize: 38, fontWeight: 700 }}>
              {status.targets.filter((target) => target.capabilities.supports_hooks).length}
            </p>
          </article>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: 18,
          }}
        >
          {targets.map((target) => (
            <TargetCard
              key={target.target}
              target={statusByTarget.get(target.target) ?? ({} as HarnessTargetStatus)}
            />
          ))}
        </section>
      </div>
    </main>
  );
}
