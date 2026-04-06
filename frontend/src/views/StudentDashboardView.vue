<template>
  <section class="dashboard-page">
    <article class="card hero-card">
      <h2>我的主页</h2>
      <p>查看个人信息、实验进度与最近活动。</p>
    </article>

    <article class="card" v-if="isLoading">正在加载个人中心数据...</article>
    <article class="card error" v-else-if="errorMessage">{{ errorMessage }}</article>

    <template v-else-if="dashboard">
      <article class="card">
        <div class="section-head">
          <h3>个人信息</h3>
          <RouterLink class="profile-link" to="/profile">查看完整资料</RouterLink>
        </div>
        <div class="profile-grid">
          <div class="item">
            <span>姓名</span>
            <strong>{{ dashboard.profile.full_name || "-" }}</strong>
          </div>
          <div class="item">
            <span>用户名</span>
            <strong>{{ dashboard.profile.username || "-" }}</strong>
          </div>
          <div class="item">
            <span>学号</span>
            <strong>{{ dashboard.profile.student_no || "-" }}</strong>
          </div>
          <div class="item">
            <span>班级</span>
            <strong>{{ dashboard.profile.class_name || "-" }}</strong>
          </div>
          <div class="item">
            <span>角色</span>
            <strong>{{ roleLabel(dashboard.profile.role) }}</strong>
          </div>
        </div>
      </article>

      <article class="card">
        <h3>进度概览</h3>
        <div class="summary-grid">
          <div class="summary-item">
            <span>实验总数</span>
            <strong>{{ dashboard.summary.total_experiments }}</strong>
          </div>
          <div class="summary-item">
            <span>已提交</span>
            <strong>{{ dashboard.summary.submitted_count }}</strong>
          </div>
          <div class="summary-item">
            <span>已通过</span>
            <strong>{{ dashboard.summary.passed_count }}</strong>
          </div>
          <div class="summary-item highlight">
            <span>未完成</span>
            <strong>{{ unfinishedCount }}</strong>
          </div>
        </div>
        <p class="summary-hint">
          未完成 = 实验总数 - 已通过（当前：{{ dashboard.summary.total_experiments }} - {{ dashboard.summary.passed_count }}）
        </p>
        <p class="summary-hint">
          待批阅 {{ dashboard.summary.pending_count }}，未通过 {{ dashboard.summary.failed_count }}，未开始
          {{ dashboard.summary.not_started_count }}
        </p>
      </article>

      <article class="card">
        <div class="section-head">
          <h3>最近实验</h3>
          <RouterLink class="exp-link" to="/experiments">进入实验列表</RouterLink>
        </div>

        <p v-if="dashboard.recent_items.length === 0" class="empty-text">暂无最近实验记录，先去实验列表开始练习吧。</p>

        <div v-else class="recent-list">
          <article v-for="item in dashboard.recent_items" :key="item.experiment_id" class="recent-item">
            <div class="recent-top">
              <h4>{{ item.title }}</h4>
              <span class="time-text">{{ formatTime(item.latest_updated_at) }}</span>
            </div>
            <div class="status-row">
              <span class="badge status">状态：{{ latestStatusLabel(item.latest_status) }}</span>
              <span :class="['badge', 'review', item.review_status]">批阅：{{ reviewStatusLabel(item.review_status) }}</span>
              <span class="badge mode">{{ modeLabel(item.interaction_mode) }}</span>
            </div>
            <div class="actions">
              <RouterLink class="btn primary" :to="continuePath(item)">继续实验</RouterLink>
              <RouterLink class="btn plain" :to="`/docs?experiment_id=${item.experiment_id}`">查看说明</RouterLink>
            </div>
          </article>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { getStudentDashboard } from "../api/student";
import { formatApiDateTime } from "../utils/datetime";

const dashboard = ref(null);
const isLoading = ref(false);
const errorMessage = ref("");

const unfinishedCount = computed(() => {
  const summary = dashboard.value?.summary;
  if (!summary) {
    return 0;
  }
  return Math.max((summary.total_experiments || 0) - (summary.passed_count || 0), 0);
});

function formatTime(value) {
  return formatApiDateTime(value);
}

function roleLabel(role) {
  if (role === "admin") {
    return "管理员";
  }
  return role === "teacher" ? "教师" : "学生";
}

function latestStatusLabel(status) {
  if (status === "submitted") {
    return "已提交";
  }
  if (status === "draft") {
    return "草稿";
  }
  return status || "-";
}

function reviewStatusLabel(status) {
  if (status === "passed") {
    return "通过";
  }
  if (status === "failed") {
    return "未通过";
  }
  return "待批阅";
}

function modeLabel(mode) {
  return mode === "guided_template" ? "引导式模板" : "原生模式";
}

function continuePath(item) {
  if (item?.interaction_mode === "guided_template") {
    return `/guided-experiment?experiment_id=${item.experiment_id}`;
  }
  return `/editor?experiment_id=${item.experiment_id}`;
}

async function loadDashboard() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    dashboard.value = await getStudentDashboard();
  } catch (error) {
    errorMessage.value = error.message || "个人中心加载失败";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadDashboard();
});
</script>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 14px;
}

.card {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}

.hero-card h2 {
  margin: 0;
}

.hero-card p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-head h3 {
  margin: 0;
}

.profile-link,
.exp-link {
  text-decoration: none;
  color: var(--brand-700);
  font-size: 14px;
  font-weight: 600;
}

.profile-grid,
.summary-grid {
  margin-top: 12px;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.profile-grid {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.item,
.summary-item {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px 12px;
  display: grid;
  gap: 4px;
}

.item span,
.summary-item span {
  color: var(--text-subtle);
  font-size: 14px;
}

.item strong,
.summary-item strong {
  color: var(--text-strong);
  font-size: 16px;
}

.summary-item.highlight {
  border-color: var(--brand-soft-2);
  background: var(--brand-soft);
}

.summary-hint {
  margin: 10px 0 0;
  color: var(--text-muted);
  font-size: 14px;
}

.empty-text {
  margin: 12px 0 0;
  color: var(--text-subtle);
}

.recent-list {
  margin-top: 12px;
  display: grid;
  gap: 10px;
}

.recent-item {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 12px;
  display: grid;
  gap: 10px;
}

.recent-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.recent-top h4 {
  margin: 0;
}

.time-text {
  color: var(--text-subtle);
  font-size: 14px;
}

.status-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 14px;
  font-weight: 600;
}

.badge.status {
  background: var(--brand-soft-2);
  color: var(--accent-indigo-strong);
}

.badge.review.pending {
  background: var(--warn-soft);
  color: var(--warn-strong);
}

.badge.review.passed {
  background: var(--success-soft);
  color: var(--success-strong);
}

.badge.review.failed {
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.badge.mode {
  background: var(--surface-2);
  color: var(--text-body);
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  text-decoration: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 600;
}

.btn.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}

.btn.plain {
  background: var(--brand-soft-2);
  color: var(--brand-700);
}

@media (max-width: 980px) {
  .section-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .profile-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .card {
    padding: 14px;
  }

  .profile-grid,
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .recent-top {
    align-items: flex-start;
    flex-direction: column;
  }

  .actions {
    display: grid;
    gap: 8px;
  }

  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>
