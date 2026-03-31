import request from "./request";

export async function getLatestSubmission(experimentId) {
  const { data } = await request.get(`/submissions/latest/${experimentId}`);
  return data;
}

export async function saveSubmission(payload) {
  const { data } = await request.post("/submissions/save", payload);
  return data;
}

export async function submitSubmission(payload) {
  const { data } = await request.post("/submissions/submit", payload);
  return data;
}

export async function getSubmissionHistory(experimentId) {
  const { data } = await request.get(`/submissions/history/${experimentId}`);
  return data;
}

export async function getSubmissionDetail(submissionId) {
  const { data } = await request.get(`/submissions/${submissionId}`);
  return data;
}

export async function getWorkspaceStatus(experimentId) {
  const { data } = await request.get(`/submissions/workspace-status/${experimentId}`);
  return data;
}

export const getSubmissionById = getSubmissionDetail;
