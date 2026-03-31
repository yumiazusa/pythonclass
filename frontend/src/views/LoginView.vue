<template>
  <section class="login-page">
    <article class="login-card">
      <h2>账号登录</h2>
      <p class="subtitle">请使用学生、教师或管理员账号登录教学平台。</p>

      <form class="login-form" @submit.prevent="handleLogin">
        <label class="field">
          <span>用户名</span>
          <input v-model.trim="form.username" type="text" autocomplete="username" placeholder="请输入用户名" />
        </label>
        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" autocomplete="current-password" placeholder="请输入密码" />
        </label>
        <button class="btn-login" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? "登录中..." : "登录" }}
        </button>
      </form>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    </article>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getCurrentUser, login } from "../api/auth";

const route = useRoute();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const isSubmitting = ref(false);
const errorMessage = ref("");

function resolveRedirectTarget(userRole) {
  if (userRole?.must_change_password) {
    return "/change-password";
  }
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "";
  if (redirect && redirect.startsWith("/") && !redirect.startsWith("/login")) {
    return redirect;
  }
  if (userRole?.role === "admin") {
    return "/admin";
  }
  return userRole?.role === "teacher" ? "/teacher/experiments" : "/dashboard";
}

async function handleLogin() {
  const username = form.username.trim();
  const password = form.password;
  if (!username || !password) {
    errorMessage.value = "请输入用户名和密码";
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = "";
  try {
    await login({ username, password });
    const user = await getCurrentUser({ forceRefresh: true });
    await router.replace(resolveRedirectTarget(user));
  } catch (error) {
    errorMessage.value = error.message || "登录失败，请稍后重试";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: center;
}

.login-card {
  width: min(420px, 92vw);
  background: #fff;
  border: 1px solid #e5e8f0;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.login-card h2 {
  margin: 0;
}

.subtitle {
  margin: 8px 0 18px;
  color: #6b7280;
  font-size: 14px;
}

.login-form {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  font-size: 13px;
  color: #374151;
}

.field input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
}

.btn-login {
  border: 0;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  padding: 10px 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-text {
  margin: 12px 0 0;
  border-radius: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 10px 12px;
  font-size: 14px;
}
</style>
