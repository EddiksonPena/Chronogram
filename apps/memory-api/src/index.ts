import { createServer } from "node:http";
import type { ServerResponse, IncomingMessage } from "node:http";

import { createRequestAuthorizer } from "@chronogram/auth";
import { loadConfig } from "@chronogram/config";
import { createMemoryOs, renderModuleMetricsPrometheus } from "@chronogram/core";
import type { IngestMemoryRequest, WorkerHeartbeat } from "@chronogram/schemas";
import {
  ValidationError,
  parseCompactConversationRequest,
  parseFeedbackMemoryRequest,
  parseIngestMemoryRequest,
  parseRecallMemoryRequest,
  isMemoryScope,
} from "@chronogram/schemas";

const config = loadConfig();
const memoryOs = createMemoryOs(config);
const authorizer = createRequestAuthorizer(config);
const persistenceTarget =
  config.memoryStateBackend === "redis"
    ? `${config.redisUrl}#${config.memoryStateRedisKey}`
    : config.memoryDataFile;
const server = createServer(async (req, res) => {
  try {
    const method = req.method ?? "GET";
    const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);

    if (method === "GET" && url.pathname === "/health") {
      const health = await memoryOs.getHealth();
      const payload: WorkerHeartbeat & { memory: typeof health } = {
        service: "memory-api",
        status: "ok",
        timestamp: new Date().toISOString(),
        memory: health,
      };
      return sendJson(res, 200, payload);
    }

    const authorization = await authorizer.authorize(req);
    if (!authorization.authorized) {
      return sendJson(res, 401, {
        error: "unauthorized",
        message:
          config.chronogramAuthMode === "jwt" || config.chronogramAuthMode === "hybrid"
            ? "A valid API key or JWT bearer token is required."
            : "A valid API key is required.",
        ...(authorization.reason ? { reason: authorization.reason } : {}),
      });
    }

    if (method === "GET" && url.pathname === "/v1/memories") {
      const scope = url.searchParams.get("scope") ?? undefined;
      if (scope && !isMemoryScope(scope)) {
        return sendJson(res, 422, {
          error: "validation_failed",
          message:
            "scope must be one of session, agent, user, user-profile, workspace, global, project:<id>, skill:<id>, or session:<id>.",
        });
      }
      const memories = await memoryOs.listMemories(scope as IngestMemoryRequest["scope"] | undefined);
      return sendJson(res, 200, { memories });
    }

    if (method === "POST" && url.pathname === "/v1/memories/ingest") {
      const payload = parseIngestMemoryRequest(await readJson(req));
      const response = await memoryOs.ingest(payload);
      return sendJson(res, 202, response);
    }

    if (method === "POST" && url.pathname === "/v1/memories/recall") {
      const payload = parseRecallMemoryRequest(await readJson(req));
      const response = await memoryOs.recall(payload);
      return sendJson(res, 200, response);
    }

    if (method === "POST" && url.pathname === "/v1/memories/feedback") {
      const payload = parseFeedbackMemoryRequest(await readJson(req));
      const response = await memoryOs.feedback(payload);
      return sendJson(res, response.updated ? 200 : 404, response);
    }

    if (method === "POST" && url.pathname === "/v1/memories/compact") {
      const payload = parseCompactConversationRequest(await readJson(req));
      const response = await memoryOs.compactConversation(payload);
      return sendJson(res, response.triggered ? 202 : 200, response);
    }

    if (method === "GET" && url.pathname === "/v1/workflows/runs") {
      const runs = await memoryOs.getWorkflowRuns();
      return sendJson(res, 200, { runs });
    }

    if (method === "GET" && url.pathname === "/v1/metrics/modules") {
      const modules = await memoryOs.getModuleMetrics();
      return sendJson(res, 200, { modules });
    }

    if (method === "GET" && url.pathname === "/metrics") {
      const health = await memoryOs.getHealth();
      const modules = await memoryOs.getModuleMetrics();
      const runs = await memoryOs.getWorkflowRuns();
      return sendText(res, 200, renderModuleMetricsPrometheus(modules, health, runs, "memory-api"), {
        "content-type": "text/plain; version=0.0.4; charset=utf-8",
      });
    }

    return sendJson(res, 404, {
      error: "not_found",
      message: "Route not found.",
    });
  } catch (error) {
    const candidate = error as Error;
    const isValidation = error instanceof ValidationError;
    return sendJson(res, isValidation ? error.statusCode : 400, {
      error: isValidation ? "validation_failed" : "request_failed",
      message: candidate.message,
    });
  }
});

server.listen(config.memoryApiPort, () => {
  console.log(
    JSON.stringify({
      service: "memory-api",
      event: "listening",
      port: config.memoryApiPort,
      persistenceTarget,
    }),
  );
});

const shutdown = (signal: NodeJS.Signals): void => {
  console.log(JSON.stringify({ service: "memory-api", event: "shutdown_requested", signal }));
  const forceExit = setTimeout(() => {
    console.error(JSON.stringify({ service: "memory-api", event: "shutdown_forced", signal }));
    process.exit(1);
  }, config.shutdownTimeoutMs);
  forceExit.unref();

  server.close((error) => {
    clearTimeout(forceExit);
    if (error) {
      console.error(
        JSON.stringify({
          service: "memory-api",
          event: "shutdown_failed",
          signal,
          message: (error as Error).message,
        }),
      );
      process.exit(1);
    }

    console.log(JSON.stringify({ service: "memory-api", event: "shutdown_complete", signal }));
    process.exit(0);
  });
};

process.once("SIGINT", () => shutdown("SIGINT"));
process.once("SIGTERM", () => shutdown("SIGTERM"));

function sendJson(
  res: ServerResponse<IncomingMessage>,
  statusCode: number,
  body: unknown,
): void {
  res.writeHead(statusCode, { "content-type": "application/json" });
  res.end(JSON.stringify(body, null, 2));
}

function sendText(
  res: ServerResponse<IncomingMessage>,
  statusCode: number,
  body: string,
  headers: Record<string, string>,
): void {
  res.writeHead(statusCode, headers);
  res.end(body);
}

async function readJson(req: NodeJS.ReadableStream): Promise<unknown> {
  const rawBody = await new Promise<string>((resolve, reject) => {
    const chunks: Buffer[] = [];
    let size = 0;
    const destroyableReq = req as NodeJS.ReadableStream & { destroy?: (error?: Error) => void };

    req.on("data", (chunk) => {
      const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
      size += buffer.length;
      if (size > config.maxRequestBytes) {
        reject(new Error(`Request body exceeds MAX_REQUEST_BYTES (${config.maxRequestBytes}).`));
        destroyableReq.destroy?.();
        return;
      }
      chunks.push(buffer);
    });
    req.on("end", () => {
      resolve(Buffer.concat(chunks).toString("utf8"));
    });
    req.on("error", reject);
  });

  return rawBody ? (JSON.parse(rawBody) as unknown) : {};
}
