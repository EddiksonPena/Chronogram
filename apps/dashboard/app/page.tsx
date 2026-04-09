import Link from "next/link";

import { readHarnessStatus } from "../lib/harness";

type JsonRecord = Record<string, unknown>;

export const dynamic = "force-dynamic";

const apiBase = "http://api:8000/v1";

async function fetchJson(path: string, init?: RequestInit): Promise<JsonRecord> {
  const headers = {
    "x-principal-id": "dashboard.operator",
    "x-principal-roles": "admin,operator",
    "x-request-id": `req_${path.replace(/[^a-z0-9]/gi, "_")}`,
  };

  try {
    const response = await fetch(`${apiBase}${path}`, {
      ...init,
      headers: {
        ...headers,
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
    return await response.json();
  } catch {
    return { status: "unreachable" };
  }
}

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

function renderInlineList(items: string[]) {
  if (items.length === 0) {
    return <span style={{ color: "#8ea4b8" }}>none</span>;
  }
  return items.join(", ");
}

export default async function HomePage() {
  const [health, metrics, jobs, policies, search, context, harnessStatus] = await Promise.all([
    fetchJson("/health"),
    fetchJson("/metrics/summary"),
    fetchJson("/jobs?workspace_id=default&namespace=project&limit=6"),
    fetchJson("/policies/decisions?workspace_id=default&namespace=project&limit=6"),
    fetchJson("/memory/search", {
      method: "POST",
      body: JSON.stringify({
        query: "deploy memory policy",
        workspace_id: "default",
        namespace: "project",
      }),
      headers: {
        "content-type": "application/json",
      },
    }),
    fetchJson("/context/packs/build", {
      method: "POST",
      body: JSON.stringify({
        workspace_id: "default",
        namespace: "project",
        task: "explain the current runtime status and policy posture",
      }),
      headers: {
        "content-type": "application/json",
      },
    }),
    readHarnessStatus(),
  ]);

  const metricCards = [
    {
      label: "Memories",
      value: String(metrics.memory_count ?? 0),
      accent: "rgba(92, 198, 169, 0.35)",
    },
    {
      label: "Chunks",
      value: String(metrics.chunk_count ?? 0),
      accent: "rgba(101, 168, 255, 0.35)",
    },
    {
      label: "Capabilities",
      value: String(metrics.capability_count ?? 0),
      accent: "rgba(255, 191, 91, 0.35)",
    },
    {
      label: "Policy Decisions",
      value: String(metrics.policy_decisions ?? 0),
      accent: "rgba(255, 120, 120, 0.35)",
    },
  ];

  const jobsList = Array.isArray(jobs.items) ? (jobs.items as JsonRecord[]) : [];
  const policyList = Array.isArray(policies.items) ? (policies.items as JsonRecord[]) : [];
  const searchResults = Array.isArray(search.results) ? (search.results as JsonRecord[]) : [];
  const contextPack =
    typeof context.context_pack === "object" && context.context_pack !== null
      ? (context.context_pack as JsonRecord)
      : {};
  const graphRelationships = Array.isArray(contextPack.graph_relationships)
    ? (contextPack.graph_relationships as JsonRecord[])
    : [];
  const warnings = Array.isArray(contextPack.warnings) ? (contextPack.warnings as string[]) : [];
  const capabilityItems = Array.isArray(contextPack.capabilities)
    ? (contextPack.capabilities as JsonRecord[])
    : [];
  const readyTargets = harnessStatus.targets.filter((target) => target.ready);
  const mcpTargets = harnessStatus.targets.filter((target) => target.capabilities.supports_mcp);

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "36px 22px 56px",
        color: "#eef4fb",
        background:
          "radial-gradient(circle at top left, rgba(37,77,122,0.95) 0%, rgba(10,18,31,1) 40%, rgba(4,6,9,1) 100%)",
        fontFamily: "ui-sans-serif, system-ui, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1240, margin: "0 auto" }}>
        <header style={{ display: "grid", gap: 10, marginBottom: 28 }}>
          <p style={{ letterSpacing: "0.24em", textTransform: "uppercase", color: "#8fb7d8" }}>
            MemCortex Operator
          </p>
          <h1 style={{ margin: 0, fontSize: 54, lineHeight: 1 }}>Runtime overview and control</h1>
          <p style={{ margin: 0, maxWidth: 780, color: "#b9cddd", fontSize: 18 }}>
            Live API-backed view of memory growth, retrieval context, job activity, and policy
            posture. This page now acts as a single-pane operator surface instead of a static shell.
          </p>
        </header>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1.5fr 1fr",
            gap: 18,
            marginBottom: 18,
          }}
        >
          <div style={cardStyle("rgba(167, 120, 255, 0.22)")}>
            <h2 style={{ marginTop: 0 }}>Harness readiness</h2>
            <p style={{ color: "#dbe8f5", marginTop: 0 }}>
              Supported targets are bootstrapped from project-local artifacts generated by the CLI.
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 14 }}>
              <span style={{ ...badgeStyle(readyTargets.length === harnessStatus.targets.length), fontSize: 12 }}>
                {readyTargets.length}/{harnessStatus.targets.length} ready
              </span>
              <span style={{ ...badgeStyle(mcpTargets.length > 0), fontSize: 12 }}>
                {mcpTargets.length} MCP-capable
              </span>
            </div>
            <div style={{ display: "grid", gap: 10 }}>
              {harnessStatus.targets.slice(0, 3).map((target) => (
                <div
                  key={target.target}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 16,
                    padding: "10px 12px",
                    borderRadius: 14,
                    background: "rgba(255,255,255,0.03)",
                  }}
                >
                  <span>{target.display_name}</span>
                  <span style={{ color: target.ready ? "#7ce2ad" : "#ffcb8a" }}>
                    {target.ready ? "ready" : "partial"}
                  </span>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 14 }}>
              <Link href="/harness" style={{ color: "#9fd1ff", textDecoration: "none" }}>
                Open harness readiness page
              </Link>
            </div>
          </div>
          <div style={cardStyle("rgba(112, 172, 230, 0.25)")}>
            <h2 style={{ marginTop: 0 }}>System health</h2>
            <pre
              style={{
                margin: 0,
                overflowX: "auto",
                color: "#d8e5f2",
                fontSize: 13,
              }}
            >
              {JSON.stringify(health, null, 2)}
            </pre>
          </div>
        </section>

        <section style={{ marginBottom: 18 }}>
          <div style={cardStyle("rgba(255, 191, 91, 0.22)")}>
            <h2 style={{ marginTop: 0 }}>Context summary</h2>
            <p style={{ color: "#dbe8f5" }}>{String(context.summary ?? "Unavailable")}</p>
            <p style={{ color: "#8ea4b8", marginBottom: 6 }}>Warnings</p>
            <p style={{ margin: 0, color: "#f6cb7e" }}>{renderInlineList(warnings)}</p>
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 16,
            marginBottom: 18,
          }}
        >
          {metricCards.map((card) => (
            <article key={card.label} style={cardStyle(card.accent)}>
              <p style={{ margin: 0, color: "#8ea4b8", textTransform: "uppercase", letterSpacing: "0.12em" }}>
                {card.label}
              </p>
              <p style={{ margin: "10px 0 0", fontSize: 38, fontWeight: 700 }}>{card.value}</p>
            </article>
          ))}
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 1fr 1fr",
            gap: 18,
            marginBottom: 18,
          }}
        >
          <div style={cardStyle("rgba(92, 198, 169, 0.28)")}>
            <h2 style={{ marginTop: 0 }}>Search and memory explorer</h2>
            {searchResults.length === 0 ? (
              <p style={{ color: "#8ea4b8" }}>No memory results available yet.</p>
            ) : (
              <div style={{ display: "grid", gap: 12 }}>
                {searchResults.map((item) => (
                  <article
                    key={String(item.memory_id)}
                    style={{
                      padding: 14,
                      borderRadius: 16,
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.06)",
                    }}
                  >
                    <strong>{String(item.title)}</strong>
                    <p style={{ margin: "6px 0 0", color: "#8ea4b8" }}>
                      {String(item.memory_type)} · score {String(item.score)}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>

          <div style={cardStyle("rgba(255, 120, 120, 0.28)")}>
            <h2 style={{ marginTop: 0 }}>Policy decisions</h2>
            {policyList.length === 0 ? (
              <p style={{ color: "#8ea4b8" }}>No recent policy decisions logged.</p>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                {policyList.map((item) => (
                  <article
                    key={String(item.decision_id)}
                    style={{
                      padding: 12,
                      borderRadius: 14,
                      background: "rgba(255,255,255,0.03)",
                    }}
                  >
                    <strong style={{ color: item.allow ? "#7ce2ad" : "#ff9999" }}>
                      {item.allow ? "ALLOW" : "DENY"}
                    </strong>
                    <p style={{ margin: "6px 0 0", color: "#d5e1ec" }}>
                      {String(item.action)} · {String(item.resource)}
                    </p>
                    <p style={{ margin: "4px 0 0", color: "#8ea4b8" }}>
                      {String(item.principal_id)}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>

          <div style={cardStyle("rgba(101, 168, 255, 0.28)")}>
            <h2 style={{ marginTop: 0 }}>Jobs</h2>
            {jobsList.length === 0 ? (
              <p style={{ color: "#8ea4b8" }}>No queued or historical jobs recorded yet.</p>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                {jobsList.map((item) => (
                  <article
                    key={String(item.job_id)}
                    style={{
                      padding: 12,
                      borderRadius: 14,
                      background: "rgba(255,255,255,0.03)",
                    }}
                  >
                    <strong>{String(item.job_name)}</strong>
                    <p style={{ margin: "6px 0 0", color: "#d5e1ec" }}>
                      {String(item.category)} · {String(item.status)}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1.3fr 1fr",
            gap: 18,
          }}
        >
          <div style={cardStyle("rgba(167, 120, 255, 0.2)")}>
            <h2 style={{ marginTop: 0 }}>Graph and explainability snapshot</h2>
            {graphRelationships.length === 0 ? (
              <p style={{ color: "#8ea4b8" }}>No graph relationships available for the current context.</p>
            ) : (
              <div style={{ display: "grid", gap: 12 }}>
                {graphRelationships.map((item) => (
                  <article
                    key={String(item.node_id)}
                    style={{
                      padding: 14,
                      borderRadius: 16,
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.06)",
                    }}
                  >
                    <strong>{String(item.path ?? item.node_id)}</strong>
                    <p style={{ margin: "6px 0 0", color: "#d5e1ec" }}>
                      {String(item.content_class)} · {String(item.strategy)}
                    </p>
                    <p style={{ margin: "4px 0 0", color: "#8ea4b8" }}>
                      {renderInlineList(
                        Array.isArray(item.relationships)
                          ? (item.relationships as string[])
                          : [],
                      )}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>

          <div style={cardStyle("rgba(255, 191, 91, 0.2)")}>
            <h2 style={{ marginTop: 0 }}>Recommended capabilities</h2>
            {capabilityItems.length === 0 ? (
              <p style={{ color: "#8ea4b8" }}>No capability recommendations available.</p>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                {capabilityItems.map((item) => (
                  <article
                    key={String(item.capability_id)}
                    style={{
                      padding: 12,
                      borderRadius: 14,
                      background: "rgba(255,255,255,0.03)",
                    }}
                  >
                    <strong>{String(item.name ?? item.capability_id)}</strong>
                    <p style={{ margin: "6px 0 0", color: "#d5e1ec" }}>
                      score {String(item.score ?? item.success_rate ?? "n/a")}
                    </p>
                    <p style={{ margin: "4px 0 0", color: "#8ea4b8" }}>
                      {String(item.reason ?? "Capability recommendation")}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
