import request from "./request";

export async function getStudentDashboard() {
  const { data } = await request.get("/student/dashboard");
  return data;
}
