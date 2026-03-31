<template>
  <section class="profile-page">
    <article class="profile-card">
      <h2>个人信息</h2>
      <p class="subtitle">可查看账号基础信息；教师与管理员可在此修改个人信息。</p>

      <div v-if="isLoading" class="state-text">正在加载个人信息...</div>
      <div v-else-if="errorMessage" class="state-text error">{{ errorMessage }}</div>
      <template v-else-if="user">
        <div class="info-grid">
          <div class="info-item">
            <span>姓名</span>
            <strong>{{ user.full_name || "-" }}</strong>
          </div>
          <div class="info-item">
            <span>用户名</span>
            <strong>{{ user.username || "-" }}</strong>
          </div>
          <div class="info-item">
            <span>学号</span>
            <strong>{{ user.student_no || "-" }}</strong>
          </div>
          <div class="info-item">
            <span>班级</span>
            <strong>{{ user.class_name || "-" }}</strong>
          </div>
          <div class="info-item">
            <span>角色</span>
            <strong>{{ roleLabel }}</strong>
          </div>
          <div class="info-item">
            <span>改密状态</span>
            <strong>{{ user.must_change_password ? "需修改密码" : "正常" }}</strong>
          </div>
        </div>

        <div class="actions">
          <button v-if="canEditProfile" type="button" class="btn edit" @click="openEditDialog">修改信息</button>
          <RouterLink class="btn change" to="/change-password">修改密码</RouterLink>
          <RouterLink class="btn home" :to="homePath">返回首页</RouterLink>
        </div>
      </template>
    </article>

    <div v-if="editDialog.visible" class="dialog-mask" @click.self="closeEditDialog">
      <div class="dialog-card">
        <h3>修改个人信息</h3>
        <label class="field">
          <span>用户名</span>
          <input v-model.trim="editDialog.username" type="text" placeholder="至少3位" :disabled="isSubmitting" />
        </label>
        <label class="field">
          <span>姓名</span>
          <input v-model.trim="editDialog.full_name" type="text" placeholder="可为空" :disabled="isSubmitting" />
        </label>
        <p v-if="editError" class="dialog-error">{{ editError }}</p>
        <div class="dialog-actions">
          <button type="button" class="btn cancel" :disabled="isSubmitting" @click="closeEditDialog">取消</button>
          <button type="button" class="btn submit" :disabled="isSubmitting" @click="submitEditDialog">保存</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { getCurrentUser, getStoredCurrentUser, updateProfile } from "../api/auth";

const user = ref(getStoredCurrentUser());
const isLoading = ref(false);
const errorMessage = ref("");
const isSubmitting = ref(false);
const editError = ref("");
const editDialog = reactive({
  visible: false,
  username: "",
  full_name: "",
});

const roleLabel = computed(() => {
  if (user.value?.role === "admin") {
    return "管理员";
  }
  if (user.value?.role === "teacher") {
    return "教师";
  }
  return "学生";
});

const homePath = computed(() => {
  if (user.value?.role === "admin") {
    return "/admin";
  }
  return user.value?.role === "teacher" ? "/teacher/experiments" : "/dashboard";
});

const canEditProfile = computed(() => ["teacher", "admin"].includes(user.value?.role || ""));

async function loadProfile() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    user.value = await getCurrentUser({ forceRefresh: true });
  } catch (error) {
    errorMessage.value = error.message || "个人信息加载失败";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadProfile();
});

function openEditDialog() {
  if (!user.value || !canEditProfile.value) {
    return;
  }
  editError.value = "";
  editDialog.visible = true;
  editDialog.username = user.value.username || "";
  editDialog.full_name = user.value.full_name || "";
}

function closeEditDialog() {
  if (isSubmitting.value) {
    return;
  }
  editDialog.visible = false;
}

async function submitEditDialog() {
  editError.value = "";
  const username = editDialog.username.trim();
  const fullName = editDialog.full_name.trim();

  if (username.length < 3) {
    editError.value = "用户名长度不能少于 3 位";
    return;
  }

  isSubmitting.value = true;
  try {
    const data = await updateProfile({
      username,
      full_name: fullName || null,
    });
    user.value = data.user;
    editDialog.visible = false;
    window.dispatchEvent(new Event("storage"));
  } catch (error) {
    editError.value = error.message || "修改失败";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: center;
}

.profile-card {
  width: min(640px, 92vw);
  background: #fff;
  border: 1px solid #e5e8f0;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.profile-card h2 {
  margin: 0;
}

.subtitle {
  margin: 8px 0 18px;
  color: #6b7280;
  font-size: 14px;
}

.state-text {
  color: #374151;
}

.state-text.error {
  color: #b91c1c;
}

.info-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.info-item {
  border: 1px solid #e5e8f0;
  border-radius: 10px;
  padding: 10px 12px;
  display: grid;
  gap: 4px;
}

.info-item span {
  color: #6b7280;
  font-size: 12px;
}

.info-item strong {
  color: #111827;
  font-size: 14px;
}

.actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  text-decoration: none;
  border-radius: 8px;
  padding: 9px 12px;
  color: #fff;
  font-weight: 600;
}

.btn.change {
  background: #2563eb;
}

.btn.edit {
  border: 0;
  background: #0891b2;
}

.btn.home {
  background: #4b5563;
}

.dialog-mask {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
  padding: 16px;
}

.dialog-card {
  width: min(420px, 92vw);
  background: #fff;
  border: 1px solid #e5e8f0;
  border-radius: 12px;
  padding: 16px;
  display: grid;
  gap: 10px;
}

.dialog-card h3 {
  margin: 0;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  color: #6b7280;
  font-size: 13px;
}

.field input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 10px;
}

.dialog-error {
  margin: 0;
  color: #b91c1c;
  font-size: 13px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn.cancel {
  border: 0;
  background: #e5e7eb;
  color: #111827;
}

.btn.submit {
  border: 0;
  background: #2563eb;
  color: #fff;
}

@media (max-width: 720px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
