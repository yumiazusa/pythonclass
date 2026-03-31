<template>
  <section class="admin-page">
    <article class="panel head-panel">
      <h2>管理后台首页</h2>
      <p>查看系统核心统计概览（近7天统计已包含在卡片中）。</p>
    </article>

    <article v-if="isLoading" class="panel">正在加载管理员概览...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <template v-else-if="overview">
      <article class="panel cards-panel">
        <div class="cards-grid">
          <div class="stat-card">
            <span>总用户数</span>
            <strong>{{ overview.total_users }}</strong>
          </div>
          <div class="stat-card">
            <span>学生数</span>
            <strong>{{ overview.student_count }}</strong>
          </div>
          <div class="stat-card">
            <span>教师数</span>
            <strong>{{ overview.teacher_count }}</strong>
          </div>
          <div class="stat-card">
            <span>管理员数</span>
            <strong>{{ overview.admin_count }}</strong>
          </div>
          <div class="stat-card">
            <span>实验总数</span>
            <strong>{{ overview.experiment_count }}</strong>
          </div>
          <div class="stat-card good">
            <span>启用账号数</span>
            <strong>{{ overview.enabled_user_count }}</strong>
          </div>
          <div class="stat-card warn">
            <span>停用账号数</span>
            <strong>{{ overview.disabled_user_count }}</strong>
          </div>
          <div class="stat-card soft">
            <span>近7天新增用户</span>
            <strong>{{ overview.recent_created_users_count }}</strong>
          </div>
          <div class="stat-card soft">
            <span>近7天提交数</span>
            <strong>{{ overview.recent_submission_count }}</strong>
          </div>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getAdminOverview } from "../api/admin";

const isLoading = ref(false);
const errorMessage = ref("");
const overview = ref(null);

async function loadOverview() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    overview.value = await getAdminOverview();
  } catch (error) {
    errorMessage.value = error.message || "管理员概览加载失败";
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  await loadOverview();
});
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 14px;
}

.panel {
  background: #fff;
  border: 1px solid #e5e8f0;
  border-radius: 12px;
  padding: 18px;
}

.head-panel h2 {
  margin: 0;
}

.head-panel p {
  margin: 8px 0 0;
  color: #4b5563;
}

.error {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.cards-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.stat-card {
  border: 1px solid #e5e8f0;
  border-radius: 10px;
  padding: 12px;
  display: grid;
  gap: 6px;
}

.stat-card span {
  color: #6b7280;
  font-size: 13px;
}

.stat-card strong {
  color: #111827;
  font-size: 26px;
  line-height: 1;
}

.stat-card.good {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.stat-card.warn {
  border-color: #fed7aa;
  background: #fff7ed;
}

.stat-card.soft {
  border-color: #dbeafe;
  background: #eff6ff;
}

@media (max-width: 920px) {
  .cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
