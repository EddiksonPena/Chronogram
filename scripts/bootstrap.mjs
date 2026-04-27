#!/usr/bin/env node

import { randomBytes } from "node:crypto";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { spawn } from "node:child_process";

const workspaceRoot = resolve(dirname(new URL(import.meta.url).pathname), "..");
const envExamplePath = resolve(workspaceRoot, ".env.example");
const envPath = resolve(workspaceRoot, ".env");
const harnessDir = resolve(workspaceRoot, "generated", "harness");

const command = process.argv[2] ?? "help";

const run = (bin, args) =>
  new Promise((resolvePromise) => {
    const child = spawn(bin, args, {
      cwd: workspaceRoot,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => {
      resolvePromise({
        command: [bin, ...args].join(" "),
        ok: false,
        exitCode: 1,
        stdout: stdout.trim(),
        stderr: `${stderr}${stderr ? "\n" : ""}${error.message}`.trim(),
      });
    });
    child.on("close", (code) => {
      resolvePromise({
        command: [bin, ...args].join(" "),
        ok: code === 0,
        exitCode: code ?? 1,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
      });
    });
  });

const runStreaming = (bin, args) =>
  new Promise((resolvePromise) => {
    const child = spawn(bin, args, {
      cwd: workspaceRoot,
      env: process.env,
      stdio: "inherit",
    });

    child.on("error", (error) => {
      resolvePromise({
        command: [bin, ...args].join(" "),
        ok: false,
        exitCode: 1,
        stdout: "",
        stderr: error.message,
      });
    });

    child.on("close", (code) => {
      resolvePromise({
        command: [bin, ...args].join(" "),
        ok: code === 0,
        exitCode: code ?? 1,
        stdout: "",
        stderr: "",
      });
    });
  });

const parseEnv = (raw) => {
  const entries = new Map();
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const index = trimmed.indexOf("=");
    if (index === -1) {
      continue;
    }
    entries.set(trimmed.slice(0, index).trim(), trimmed.slice(index + 1).trim());
  }
  return entries;
};

const serializeEnv = (raw, patch) => {
  const seen = new Set();
  const lines = raw.split(/\r?\n/).map((line) => {
    const index = line.indexOf("=");
    if (index === -1) {
      return line;
    }
    const key = line.slice(0, index).trim();
    if (!(key in patch)) {
      return line;
    }
    seen.add(key);
    return `${key}=${patch[key]}`;
  });

  for (const [key, value] of Object.entries(patch)) {
    if (!seen.has(key)) {
      lines.push(`${key}=${value}`);
    }
  }

  return `${lines.join("\n").replace(/\n+$/u, "")}\n`;
};

const createApiKey = () => randomBytes(24).toString("hex");

const ensureEnv = async () => {
  let created = false;
  if (!existsSync(envPath)) {
    await writeFile(envPath, await readFile(envExamplePath, "utf8"), "utf8");
    created = true;
  }

  const current = await readFile(envPath, "utf8");
  const values = parseEnv(current);
  const apiKey = values.get("CHRONOGRAM_API_KEY") ?? "";
  let generated = false;

  if (!apiKey.trim()) {
    generated = true;
    const updated = serializeEnv(current, { CHRONOGRAM_API_KEY: createApiKey() });
    await writeFile(envPath, updated, "utf8");
  }

  return {
    created,
    generated,
    values: parseEnv(await readFile(envPath, "utf8")),
  };
};

const healthCheck = async (name, url) => {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(1500) });
    return { name, url, ok: response.ok, details: `HTTP ${response.status}` };
  } catch (error) {
    return { name, url, ok: false, details: error.message };
  }
};

const doctor = async () => {
  const checks = await Promise.all([
    run("node", ["--version"]),
    run("pnpm", ["--version"]),
    run("docker", ["--version"]),
    run("docker", ["compose", "version"]),
  ]);
  const compose = await run("docker", ["compose", "ps"]);
  const services = await Promise.all([
    healthCheck("memory-api", "http://127.0.0.1:4000/health"),
    healthCheck("worker", "http://127.0.0.1:4010/health"),
    healthCheck("weaviate", "http://127.0.0.1:8080/v1/.well-known/ready"),
    healthCheck("temporal-ui", "http://127.0.0.1:8233"),
  ]);
  return {
    workspaceRoot,
    envFile: envPath,
    checks,
    compose,
    services,
  };
};

const connect = async () => {
  await ensureEnv();
  const env = parseEnv(await readFile(envPath, "utf8"));
  const apiKey = env.get("CHRONOGRAM_API_KEY") ?? "<your-api-key>";
  const manifest = {
    name: "chronogram",
    baseUrl: "http://127.0.0.1:4000",
    apiKeyEnv: "CHRONOGRAM_API_KEY",
    endpoints: {
      ingest: "/v1/memories/ingest",
      recall: "/v1/memories/recall",
      feedback: "/v1/memories/feedback",
      compact: "/v1/memories/compact",
    },
  };

  await mkdir(harnessDir, { recursive: true });
  const jsonPath = resolve(harnessDir, "chronogram-harness-config.json");
  const mdPath = resolve(harnessDir, "chronogram-harness-config.md");

  const envSnippet = [
    "export CHRONOGRAM_BASE_URL=http://127.0.0.1:4000",
    `export CHRONOGRAM_API_KEY=${apiKey}`,
  ].join("\n");

  const nodeSnippet = `const response = await fetch(\`\${process.env.CHRONOGRAM_BASE_URL}/v1/memories/recall\`, {\n  method: "POST",\n  headers: {\n    "content-type": "application/json",\n    "x-api-key": process.env.CHRONOGRAM_API_KEY ?? "",\n  },\n  body: JSON.stringify({\n    query: "What should I remember from the current session?",\n    scope: "workspace",\n    includeDiagnostics: true,\n  }),\n});\n\nconsole.log(await response.json());`;

  const markdown = [
    "# Chronogram Harness Bundle",
    "",
    "## Environment",
    "```bash",
    envSnippet,
    "```",
    "",
    "## Manifest",
    "```json",
    JSON.stringify(manifest, null, 2),
    "```",
    "",
    "## Node Example",
    "```ts",
    nodeSnippet,
    "```",
  ].join("\n");

  await writeFile(jsonPath, JSON.stringify(manifest, null, 2), "utf8");
  await writeFile(mdPath, markdown, "utf8");

  return {
    envFile: envPath,
    generatedJsonPath: jsonPath,
    generatedMarkdownPath: mdPath,
    manifest,
    snippets: {
      env: envSnippet,
      node: nodeSnippet,
    },
  };
};

const print = (value) => {
  process.stdout.write(`${typeof value === "string" ? value : JSON.stringify(value, null, 2)}\n`);
};

if (command === "help" || command === "--help" || command === "-h") {
  print([
    "Chronogram bootstrap commands",
    "",
    "node scripts/bootstrap.mjs init",
    "node scripts/bootstrap.mjs doctor",
    "node scripts/bootstrap.mjs connect",
    "node scripts/bootstrap.mjs ui",
    "node scripts/bootstrap.mjs down",
    "node scripts/production-readiness.mjs preflight",
    "node scripts/production-readiness.mjs smoke",
    "node scripts/production-readiness.mjs load",
  ].join("\n"));
  process.exit(0);
}

if (command === "doctor") {
  const report = await doctor();
  print(report);
  process.exit(report.checks.every((check) => check.ok) ? 0 : 1);
}

if (command === "connect") {
  print(await connect());
  process.exit(0);
}

if (command === "down") {
  const result = await run("docker", ["compose", "--profile", "app", "down"]);
  print(result);
  process.exit(result.ok ? 0 : 1);
}

if (command === "ui") {
  if (!existsSync(resolve(workspaceRoot, "node_modules"))) {
    const install = await run("pnpm", ["install", "--frozen-lockfile"]);
    if (!install.ok) {
      print(install);
      process.exit(1);
    }
  }

  const result = await runStreaming("pnpm", ["--filter", "@chronogram/onboarding-ui", "start"]);
  process.exit(result.ok ? 0 : 1);
}

if (command === "init") {
  const env = await ensureEnv();
  const steps = [
    {
      id: "env",
      ok: true,
      details: env.created ? "Created .env." : "Using existing .env.",
    },
    await run("pnpm", ["install", "--frozen-lockfile"]),
    await run("docker", ["compose", "up", "-d"]),
    await run("docker", ["compose", "--profile", "app", "up", "-d", "--build"]),
  ];
  const report = {
    steps,
    doctor: await doctor(),
  };
  print(report);
  const ok = steps.every((step) => step.ok);
  process.exit(ok ? 0 : 1);
}

print("Unknown command.");
process.exit(1);
