import request from "./request";

export async function runCode(code, experimentId) {
  const { data } = await request.post("/code/run", { code, experiment_id: experimentId });
  return data;
}
