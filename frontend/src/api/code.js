import request from "./request";

const runTimeoutMs = Number(import.meta.env.VITE_CODE_RUN_TIMEOUT_MS || 180000);

export async function runCode(code, experimentId) {
  const { data } = await request.post("/code/run", { code, experiment_id: experimentId }, { timeout: runTimeoutMs });
  return data;
}
