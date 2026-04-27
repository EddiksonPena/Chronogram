const checksList = document.querySelector("#checks-list");
const servicesList = document.querySelector("#services-list");
const snippetsEl = document.querySelector("#snippets");
const logOutput = document.querySelector("#log-output");
const checksSummary = document.querySelector("#checks-summary");
const servicesSummary = document.querySelector("#services-summary");
const initButton = document.querySelector("#init-button");
const refreshButton = document.querySelector("#refresh-button");
const downButton = document.querySelector("#down-button");

const setLog = (value) => {
  logOutput.textContent =
    typeof value === "string" ? value : JSON.stringify(value, null, 2);
};

const statusClass = (ok) => (ok ? "good" : "bad");
const statusLabel = (ok) => (ok ? "Ready" : "Needs Attention");

const renderItems = (root, entries, nameKey = "label") => {
  root.innerHTML = "";
  for (const entry of entries) {
    const article = document.createElement("article");
    article.className = `item ${statusClass(Boolean(entry.ok))}`;
    article.innerHTML = `
      <span class="status">${statusLabel(Boolean(entry.ok))}</span>
      <strong>${entry[nameKey]}</strong>
      <div>${entry.details}</div>
    `;
    root.appendChild(article);
  }
};

const renderSnippets = (bundle) => {
  snippetsEl.innerHTML = "";
  for (const snippet of bundle.snippets) {
    const article = document.createElement("article");
    article.className = "snippet";
    article.innerHTML = `
      <header>
        <strong>${snippet.label}</strong>
        <span class="pill">${snippet.language}</span>
      </header>
      <pre>${snippet.content.replaceAll("<", "&lt;")}</pre>
    `;
    snippetsEl.appendChild(article);
  }
};

const loadStatus = async () => {
  const response = await fetch("/api/status");
  const status = await response.json();
  renderItems(checksList, status.checks);
  renderItems(servicesList, status.services, "name");
  checksSummary.textContent = `${status.checks.filter((entry) => entry.ok).length}/${status.checks.length} ready`;
  servicesSummary.textContent = `${status.services.filter((entry) => entry.ok).length}/${status.services.length} healthy`;
  setLog(status);
};

const loadConnect = async () => {
  const response = await fetch("/api/connect");
  const bundle = await response.json();
  renderSnippets(bundle);
};

const postAction = async (path) => {
  setLog(`Running ${path}...`);
  const response = await fetch(path, { method: "POST" });
  const payload = await response.json();
  setLog(payload);
  await loadStatus();
  await loadConnect();
};

initButton.addEventListener("click", () => postAction("/api/actions/init"));
refreshButton.addEventListener("click", async () => {
  await loadStatus();
  await loadConnect();
});
downButton.addEventListener("click", () => postAction("/api/actions/down"));

await loadStatus();
await loadConnect();
