const CODE_RUN_STATUSES = new Set(["completed", "runtime_error", "timed_out", "blocked", "internal_error"]);

function normalizeStatus(rawStatus, stderr) {
  if (typeof rawStatus === "string" && CODE_RUN_STATUSES.has(rawStatus)) {
    return rawStatus;
  }
  if (typeof stderr === "string" && stderr.trim()) {
    return "runtime_error";
  }
  return "completed";
}

export function normalizeRunResult(payload) {
  if (!payload || typeof payload !== "object") {
    return null;
  }
  const stdout = typeof payload.stdout === "string" ? payload.stdout : "";
  const stderr = typeof payload.stderr === "string" ? payload.stderr : "";
  const status = normalizeStatus(payload.status, stderr);
  const success = typeof payload.success === "boolean" ? payload.success : status === "completed";
  const executionTimeMsRaw = Number(payload.execution_time_ms);
  const executionTimeMs = Number.isFinite(executionTimeMsRaw) ? Math.max(0, Math.floor(executionTimeMsRaw)) : 0;
  return {
    success,
    status,
    stdout,
    stderr,
    returncode: Number.isInteger(payload.returncode) ? payload.returncode : null,
    timed_out: Boolean(payload.timed_out),
    execution_time_ms: executionTimeMs,
    blocked: Boolean(payload.blocked),
    block_reason: typeof payload.block_reason === "string" && payload.block_reason ? payload.block_reason : null,
  };
}

export function hasRunnableResult(result) {
  if (!result || typeof result !== "object") {
    return false;
  }
  const stdout = typeof result.stdout === "string" ? result.stdout.trim() : "";
  const stderr = typeof result.stderr === "string" ? result.stderr.trim() : "";
  const status = typeof result.status === "string" ? result.status.trim() : "";
  return Boolean(stdout || stderr || (status && status !== "not_run"));
}

export function buildRunResultFromSubmission(submission) {
  const runOutput = typeof submission?.run_output === "string" ? submission.run_output : "";
  const trimmedOutput = runOutput.trim();
  if (!trimmedOutput || trimmedOutput === "not_run") {
    return null;
  }
  const statusFromOutput = CODE_RUN_STATUSES.has(trimmedOutput) ? trimmedOutput : null;
  const isPassed = typeof submission?.is_passed === "boolean" ? submission.is_passed : null;
  const status = statusFromOutput || (isPassed === null ? "completed" : isPassed ? "completed" : "runtime_error");
  return normalizeRunResult({
    success: isPassed,
    status,
    stdout: statusFromOutput ? "" : runOutput,
    stderr: "",
    returncode: null,
    timed_out: false,
    execution_time_ms: 0,
    blocked: false,
    block_reason: null,
  });
}
