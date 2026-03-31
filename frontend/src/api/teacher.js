import request from "./request";

export async function getTeacherExperimentOverview() {
  const { data } = await request.get("/teacher/experiments/overview");
  return data;
}

export async function getTeacherExperimentStudents(experimentId, params = {}) {
  const { data } = await request.get(`/teacher/experiments/${experimentId}/students`, { params });
  return data;
}

export async function exportTeacherExperimentResults(experimentId, params = {}) {
  const response = await request.get(`/teacher/experiments/${experimentId}/export`, {
    params,
    responseType: "blob",
  });
  return response.data;
}

export async function getTeacherExperimentClassSummary(experimentId) {
  const { data } = await request.get(`/teacher/experiments/${experimentId}/class-summary`);
  return data;
}

export async function updateTeacherExperimentSettings(experimentId, payload) {
  const { data } = await request.patch(`/teacher/experiments/${experimentId}/settings`, payload);
  return data;
}

export async function getTeacherStudentHistory(experimentId, userId) {
  const { data } = await request.get(`/teacher/experiments/${experimentId}/students/${userId}/history`);
  return data;
}

export async function getTeacherSubmissionDetail(submissionId) {
  const { data } = await request.get(`/teacher/submissions/${submissionId}`);
  return data;
}

export async function reviewTeacherSubmission(submissionId, payload) {
  const { data } = await request.post(`/teacher/submissions/${submissionId}/review`, payload);
  return data;
}

export async function batchReviewTeacherSubmissions(payload) {
  const { data } = await request.post("/teacher/submissions/batch-review", payload);
  return data;
}

export async function returnTeacherStudentExperiment(experimentId, userId) {
  const { data } = await request.post(`/teacher/experiments/${experimentId}/students/${userId}/return`);
  return data;
}

export async function batchReturnTeacherStudents(experimentId, payload) {
  const { data } = await request.post(`/teacher/experiments/${experimentId}/batch-return`, payload);
  return data;
}

export async function importTeacherStudents(file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await request.post("/teacher/students/import", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

export async function downloadTeacherStudentImportTemplate() {
  const response = await request.get("/teacher/students/import-template", {
    responseType: "blob",
  });
  return response.data;
}

export async function getTeacherStudents(params = {}) {
  const { data } = await request.get("/teacher/students", { params });
  return data;
}

export async function getTeacherStudentClassOptions() {
  const { data } = await request.get("/teacher/students/class-options");
  return data;
}

export async function batchResetTeacherStudentPasswords(payload) {
  const { data } = await request.post("/teacher/students/batch-reset-password", payload);
  return data;
}

export async function enableTeacherStudent(userId) {
  const { data } = await request.post(`/teacher/students/${userId}/enable`);
  return data;
}

export async function disableTeacherStudent(userId) {
  const { data } = await request.post(`/teacher/students/${userId}/disable`);
  return data;
}

export async function batchEnableTeacherStudents(payload) {
  const { data } = await request.post("/teacher/students/batch-enable", payload);
  return data;
}

export async function batchDisableTeacherStudents(payload) {
  const { data } = await request.post("/teacher/students/batch-disable", payload);
  return data;
}

export async function exportTeacherStudents(params = {}) {
  const response = await request.get("/teacher/students/export", {
    params,
    responseType: "blob",
  });
  return response.data;
}
