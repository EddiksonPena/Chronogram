import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import {
  buildHarnessBundle,
  getWorkspaceRoot,
  runBootstrap,
  runDoctor,
  stopStack,
} from "@chronogram/onboarding";

const port = Number(process.env.ONBOARDING_UI_PORT ?? 4020);
const publicDir = resolve(getWorkspaceRoot(), "apps/onboarding-ui/public");

const sendJson = (res: import("node:http").ServerResponse, statusCode: number, body: unknown): void => {
  res.writeHead(statusCode, { "content-type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(body, null, 2));
};

const sendFile = async (
  res: import("node:http").ServerResponse,
  filePath: string,
  contentType: string,
): Promise<void> => {
  const body = await readFile(filePath);
  res.writeHead(200, { "content-type": contentType });
  res.end(body);
};

const server = createServer(async (req, res) => {
  try {
    const method = req.method ?? "GET";
    const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);

    if (method === "GET" && url.pathname === "/health") {
      return sendJson(res, 200, { service: "onboarding-ui", status: "ok" });
    }

    if (method === "GET" && url.pathname === "/api/status") {
      return sendJson(res, 200, await runDoctor());
    }

    if (method === "GET" && url.pathname === "/api/connect") {
      return sendJson(res, 200, await buildHarnessBundle());
    }

    if (method === "POST" && url.pathname === "/api/actions/init") {
      return sendJson(res, 200, await runBootstrap());
    }

    if (method === "POST" && url.pathname === "/api/actions/down") {
      return sendJson(res, 200, await stopStack());
    }

    if (method === "GET" && url.pathname === "/") {
      return sendFile(res, resolve(publicDir, "index.html"), "text/html; charset=utf-8");
    }

    if (method === "GET" && url.pathname === "/app.js") {
      return sendFile(res, resolve(publicDir, "app.js"), "text/javascript; charset=utf-8");
    }

    if (method === "GET" && url.pathname === "/styles.css") {
      return sendFile(res, resolve(publicDir, "styles.css"), "text/css; charset=utf-8");
    }

    return sendJson(res, 404, { error: "not_found" });
  } catch (error) {
    return sendJson(res, 500, {
      error: "onboarding_ui_failed",
      message: (error as Error).message,
    });
  }
});

server.listen(port, () => {
  console.log(JSON.stringify({ service: "onboarding-ui", event: "listening", port }));
});
