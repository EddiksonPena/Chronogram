import { promises as fs } from "node:fs";
import path from "node:path";

export type HarnessTargetKey = "codex" | "claude" | "gemini" | "copilot" | "openclaw";

export interface HarnessCapabilityMatrix {
  supports_mcp: boolean;
  supports_hooks: boolean;
  supports_http: boolean;
  supports_stdio_json: boolean;
  supports_project_local_config: boolean;
  supports_post_task_writeback: boolean;
}

export interface HarnessArtifact {
  name: string;
  path: string;
  exists: boolean;
  kind: "json" | "script" | "markdown";
}

export interface HarnessTargetStatus {
  target: HarnessTargetKey;
  display_name: string;
  install_root: string;
  ready: boolean;
  capabilities: HarnessCapabilityMatrix;
  checks: Record<string, boolean>;
  artifacts: HarnessArtifact[];
  bootstrap?: Record<string, unknown>;
}

const targets: Array<{
  target: HarnessTargetKey;
  display_name: string;
  supports_mcp: boolean;
  supports_hooks: boolean;
  supports_http: boolean;
  supports_stdio_json: boolean;
  supports_project_local_config: boolean;
  supports_post_task_writeback: boolean;
}> = [
  {
    target: "codex",
    display_name: "Codex",
    supports_mcp: true,
    supports_hooks: true,
    supports_http: true,
    supports_stdio_json: false,
    supports_project_local_config: true,
    supports_post_task_writeback: true,
  },
  {
    target: "claude",
    display_name: "Claude Code",
    supports_mcp: true,
    supports_hooks: true,
    supports_http: true,
    supports_stdio_json: false,
    supports_project_local_config: true,
    supports_post_task_writeback: true,
  },
  {
    target: "gemini",
    display_name: "Gemini CLI",
    supports_mcp: false,
    supports_hooks: true,
    supports_http: true,
    supports_stdio_json: true,
    supports_project_local_config: true,
    supports_post_task_writeback: true,
  },
  {
    target: "copilot",
    display_name: "GitHub Copilot",
    supports_mcp: false,
    supports_hooks: false,
    supports_http: true,
    supports_stdio_json: false,
    supports_project_local_config: true,
    supports_post_task_writeback: true,
  },
  {
    target: "openclaw",
    display_name: "OpenClaw",
    supports_mcp: false,
    supports_hooks: true,
    supports_http: true,
    supports_stdio_json: true,
    supports_project_local_config: true,
    supports_post_task_writeback: true,
  },
];

export async function readHarnessStatus(): Promise<{ ready: boolean; targets: HarnessTargetStatus[] }> {
  const repoRoot = await findRepoRoot();
  const statuses = await Promise.all(targets.map((target) => readHarnessTarget(repoRoot, target)));
  return {
    ready: statuses.every((item) => item.ready),
    targets: statuses,
  };
}

export async function readHarnessTarget(
  repoRoot: string,
  target: (typeof targets)[number],
): Promise<HarnessTargetStatus> {
  const targetRoot = path.join(repoRoot, ".memcortex", target.target);
  const hooksRoot = path.join(targetRoot, "hooks");
  const files = {
    adapter: path.join(targetRoot, "adapter.json"),
    bootstrap: path.join(targetRoot, "bootstrap.json"),
    readme: path.join(targetRoot, "README.md"),
    mcp: path.join(targetRoot, "mcp.json"),
    preTask: path.join(hooksRoot, "pre-task.sh"),
    postTask: path.join(hooksRoot, "post-task.sh"),
    exampleBootstrap: path.join(repoRoot, "examples", target.target, "bootstrap.example.json"),
    exampleMcp: path.join(repoRoot, "examples", target.target, "mcp-config.example.json"),
  };

  const [adapter, bootstrap, readme, mcpConfig, preTask, postTask, exampleBootstrap, exampleMcp] =
    await Promise.all([
      readJsonRecord(files.adapter),
      readJsonRecord(files.bootstrap),
      readText(files.readme),
      readJsonRecord(files.mcp),
      readText(files.preTask),
      readText(files.postTask),
      readJsonRecord(files.exampleBootstrap),
      readJsonRecord(files.exampleMcp),
    ]);

  const checks = {
    target_root: await exists(targetRoot),
    adapter_manifest: adapter !== null,
    bootstrap_config: bootstrap !== null,
    readme: readme !== null,
    example_bootstrap: exampleBootstrap !== null,
    example_mcp: target.supports_mcp ? exampleMcp !== null : true,
    pre_task_hook: target.supports_hooks ? preTask !== null : true,
    post_task_hook: target.supports_hooks ? postTask !== null : true,
    mcp_config: target.supports_mcp ? mcpConfig !== null : true,
  };

  const artifacts: HarnessArtifact[] = [
    { name: "adapter.json", path: relative(repoRoot, files.adapter), exists: adapter !== null, kind: "json" },
    { name: "bootstrap.json", path: relative(repoRoot, files.bootstrap), exists: bootstrap !== null, kind: "json" },
    { name: "README.md", path: relative(repoRoot, files.readme), exists: readme !== null, kind: "markdown" },
    { name: "bootstrap.example.json", path: relative(repoRoot, files.exampleBootstrap), exists: exampleBootstrap !== null, kind: "json" },
  ];

  if (target.supports_mcp) {
    artifacts.push({
      name: "mcp.json",
      path: relative(repoRoot, files.mcp),
      exists: mcpConfig !== null,
      kind: "json",
    });
    artifacts.push({
      name: "mcp-config.example.json",
      path: relative(repoRoot, files.exampleMcp),
      exists: exampleMcp !== null,
      kind: "json",
    });
  }
  if (target.supports_hooks) {
    artifacts.push({
      name: "pre-task.sh",
      path: relative(repoRoot, files.preTask),
      exists: preTask !== null,
      kind: "script",
    });
    artifacts.push({
      name: "post-task.sh",
      path: relative(repoRoot, files.postTask),
      exists: postTask !== null,
      kind: "script",
    });
  }

  return {
    target: target.target,
    display_name: target.display_name,
    install_root: targetRoot,
    ready: Object.values(checks).every(Boolean),
    capabilities: {
      supports_mcp: target.supports_mcp,
      supports_hooks: target.supports_hooks,
      supports_http: target.supports_http,
      supports_stdio_json: target.supports_stdio_json,
      supports_project_local_config: target.supports_project_local_config,
      supports_post_task_writeback: target.supports_post_task_writeback,
    },
    checks,
    artifacts,
    bootstrap: bootstrap ?? undefined,
  };
}

export function listHarnessTargets(): (typeof targets)[number][] {
  return targets;
}

async function findRepoRoot(): Promise<string> {
  let current = process.cwd();
  for (let depth = 0; depth < 8; depth += 1) {
    const marker = path.join(current, "memory-prd.md");
    if (await exists(marker)) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }
  return path.resolve(process.cwd(), "..", "..");
}

async function exists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function readText(filePath: string): Promise<string | null> {
  try {
    return await fs.readFile(filePath, "utf-8");
  } catch {
    return null;
  }
}

async function readJsonRecord(filePath: string): Promise<Record<string, unknown> | null> {
  const text = await readText(filePath);
  if (text === null) {
    return null;
  }
  try {
    return JSON.parse(text) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function relative(repoRoot: string, filePath: string): string {
  return path.relative(repoRoot, filePath);
}
