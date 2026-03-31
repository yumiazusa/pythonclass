import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
const tokenKeys = ["token", "teacher_token", "student_token"];

function getTokenFromStorage() {
  for (const key of tokenKeys) {
    const token = localStorage.getItem(key);
    if (token) {
      if (key !== "token") {
        localStorage.setItem("token", token);
      }
      return token;
    }
  }
  return "";
}

function clearAuthStorage() {
  localStorage.removeItem("token");
  localStorage.removeItem("teacher_token");
  localStorage.removeItem("student_token");
  localStorage.removeItem("current_user");
  localStorage.removeItem("role");
}

const request = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
});

request.interceptors.request.use(
  (config) => {
    const token = getTokenFromStorage();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

request.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      clearAuthStorage();
      const isLoginRoute = window.location.pathname === "/login";
      if (!isLoginRoute) {
        const redirectTarget = `${window.location.pathname}${window.location.search}`;
        window.location.href = `/login?redirect=${encodeURIComponent(redirectTarget)}`;
      }
    }
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error.message ||
      "请求失败";
    return Promise.reject(new Error(message));
  },
);

export default request;
