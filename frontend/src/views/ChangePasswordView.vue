<template>
  <section class="change-page">
    <article class="change-card">
      <h2>修改密码</h2>
      <p class="subtitle">为保障账号安全，请设置新的登录密码。</p>

      <form class="change-form" @submit.prevent="handleSubmit">
        <label class="field">
          <span>当前密码</span>
          <input v-model="form.current_password" type="password" autocomplete="current-password" placeholder="请输入当前密码" />
        </label>
        <label class="field">
          <span>新密码</span>
          <input v-model="form.new_password" type="password" autocomplete="new-password" placeholder="请输入新密码（至少6位）" />
        </label>
        <label class="field">
          <span>确认新密码</span>
          <input
            v-model="form.confirm_password"
            type="password"
            autocomplete="new-password"
            placeholder="请再次输入新密码"
          />
        </label>
        <button class="btn-submit" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? "提交中..." : "确认修改" }}
        </button>
      </form>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success-text">{{ successMessage }}</p>
    </article>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { changePassword, getCurrentUser } from "../api/auth";

const router = useRouter();

const form = reactive({
  current_password: "",
  new_password: "",
  confirm_password: "",
});

const isSubmitting = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

function resolveDefaultHome(role) {
  if (role === "admin") {
    return "/admin";
  }
  return role === "teacher" ? "/teacher/experiments" : "/dashboard";
}

async function handleSubmit() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!form.current_password || !form.new_password || !form.confirm_password) {
    errorMessage.value = "请完整填写所有字段";
    return;
  }
  if (form.new_password.length < 6) {
    errorMessage.value = "新密码长度不能少于 6 位";
    return;
  }
  if (form.new_password !== form.confirm_password) {
    errorMessage.value = "新密码与确认密码不一致";
    return;
  }

  isSubmitting.value = true;
  try {
    await changePassword({
      current_password: form.current_password,
      new_password: form.new_password,
      confirm_password: form.confirm_password,
    });
    const user = await getCurrentUser({ forceRefresh: true });
    successMessage.value = "密码修改成功，正在跳转...";
    setTimeout(() => {
      router.replace(resolveDefaultHome(user?.role));
    }, 300);
  } catch (error) {
    errorMessage.value = error.message || "修改失败，请稍后重试";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.change-page {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: center;
}

.change-card {
  width: min(460px, 92vw);
  background: #fff;
  border: 1px solid #e5e8f0;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.change-card h2 {
  margin: 0;
}

.subtitle {
  margin: 8px 0 18px;
  color: #6b7280;
  font-size: 14px;
}

.change-form {
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

.btn-submit {
  border: 0;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  padding: 10px 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:disabled {
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

.success-text {
  margin: 12px 0 0;
  border-radius: 8px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 10px 12px;
  font-size: 14px;
}
</style>
