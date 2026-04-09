const cards = [
  {
    title: "Overview",
    body: "System status, current ingestion counts, and maintenance activity.",
  },
  {
    title: "Search",
    body: "Memory and capability recall over graph, vector, and working-memory views.",
  },
  {
    title: "Graph",
    body: "Entity neighborhoods, provenance edges, and temporal drift over time.",
  },
  {
    title: "Jobs",
    body: "Temporal workflows, maintenance jobs, repair runs, and policy actions.",
  },
];

async function getHealth() {
  try {
    const res = await fetch("http://api:8000/v1/health", { cache: "no-store" });
    return await res.json();
  } catch {
    return { status: "unreachable" };
  }
}

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "40px 24px",
        color: "#f5f7fb",
        background:
          "radial-gradient(circle at top left, #0d2b42 0%, #091522 35%, #05070a 100%)",
        fontFamily: "ui-sans-serif, system-ui, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <p style={{ letterSpacing: "0.2em", textTransform: "uppercase", color: "#8bb4d8" }}>
          MemCortex
        </p>
        <h1 style={{ fontSize: 56, lineHeight: 1, margin: "12px 0 16px" }}>
          Brain runtime operator shell
        </h1>
        <p style={{ maxWidth: 700, color: "#b7c9d8", fontSize: 18 }}>
          API, worker, MCP, and control-plane scaffolding are in place. This dashboard is the
          initial control room for operating retrieval, maintenance, policy, and memory-health
          flows.
        </p>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1fr",
            gap: 20,
            marginTop: 32,
          }}
        >
          <div
            style={{
              padding: 24,
              borderRadius: 20,
              background: "rgba(11, 20, 32, 0.8)",
              border: "1px solid rgba(139, 180, 216, 0.15)",
            }}
          >
            <h2>Health</h2>
            <pre style={{ overflowX: "auto", color: "#d7e7f4" }}>
              {JSON.stringify(health, null, 2)}
            </pre>
          </div>
          <div
            style={{
              padding: 24,
              borderRadius: 20,
              background: "rgba(11, 20, 32, 0.8)",
              border: "1px solid rgba(139, 180, 216, 0.15)",
            }}
          >
            <h2>Initial control plane</h2>
            <ul>
              <li>Policy evaluation endpoint</li>
              <li>Temporal workflow starter</li>
              <li>MCP task surface</li>
              <li>Capability recommendation service</li>
            </ul>
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 16,
            marginTop: 20,
          }}
        >
          {cards.map((card) => (
            <article
              key={card.title}
              style={{
                padding: 20,
                borderRadius: 18,
                background: "rgba(245, 247, 251, 0.04)",
                border: "1px solid rgba(245, 247, 251, 0.08)",
              }}
            >
              <h3 style={{ marginTop: 0 }}>{card.title}</h3>
              <p style={{ color: "#b7c9d8" }}>{card.body}</p>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
