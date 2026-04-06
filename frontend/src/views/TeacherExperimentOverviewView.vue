<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>教师实验看板</h2>
      <p class="header-desc">统计口径：当前统计在该实验下“每个学生最新最终提交（status=submitted）”的批阅状态。</p>
      <p class="header-hint">学生名单模板必须包含：班级、学号、姓名（仅支持 .xlsx）。</p>
      <div class="toolbar">
        <RouterLink class="btn header-action import" to="/teacher/student-import">上传学生名单</RouterLink>
        <RouterLink class="btn header-action manage" to="/teacher/students">学生管理</RouterLink>
        <button type="button" class="btn header-action download" :disabled="isDownloadingTemplate" @click="handleDownloadTemplate">
          {{ isDownloadingTemplate ? "下载中..." : "下载模板" }}
        </button>
      </div>
    </article>

    <article v-if="isRoleChecking" class="panel">正在验证教师权限...</article>
    <article v-else-if="roleError" class="panel error">{{ roleError }}</article>
    <article v-else-if="!isTeacher" class="panel error">仅教师可访问当前页面</article>

    <template v-else>
      <article v-if="isLoading" class="panel">正在加载实验概览...</article>
      <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>
      <article v-else-if="overviewList.length === 0" class="panel">暂无实验数据</article>
      <div v-else class="list-wrap">
        <article v-for="item in overviewList" :key="item.experiment_id" class="panel overview-card">
          <div class="overview-head">
            <h3>{{ item.title }}</h3>
            <RouterLink class="btn detail" :to="`/teacher/experiment-detail?experiment_id=${item.experiment_id}`">
              查看详情
            </RouterLink>
          </div>
          <div class="meta-grid desktop-only">
            <div>实验ID：{{ item.experiment_id }}</div>
            <div>发布状态：{{ item.is_published ? "已发布" : "未发布" }}</div>
            <div>开放时间：{{ formatTime(item.open_at) }}</div>
            <div>截止时间：{{ formatTime(item.due_at) }}</div>
            <div>记录学生数：{{ item.total_students_with_records }}</div>
            <div>已提交数：{{ item.submitted_count }}</div>
            <div>草稿数：{{ item.draft_count }}</div>
            <div>锁定数：{{ item.locked_count }}</div>
            <div>已批阅：{{ item.reviewed_count }}</div>
            <div>已通过：{{ item.passed_count }}</div>
            <div>未通过：{{ item.failed_count }}</div>
            <div>待批阅：{{ item.pending_review_count }}</div>
            <div>最近更新：{{ formatTime(item.updated_at) }}</div>
          </div>
          <div class="overview-mobile mobile-only">
            <div class="overview-mobile-badges">
              <span class="metric-pill">实验ID {{ item.experiment_id }}</span>
              <span :class="['metric-pill', item.is_published ? 'published' : 'unpublished']">
                {{ item.is_published ? "已发布" : "未发布" }}
              </span>
            </div>

            <div class="overview-mobile-times">
              <div>
                <span>开放时间</span>
                <strong>{{ formatTime(item.open_at) }}</strong>
              </div>
              <div>
                <span>截止时间</span>
                <strong>{{ formatTime(item.due_at) }}</strong>
              </div>
            </div>

            <div class="overview-mobile-kpis">
              <div>
                <span>记录学生</span>
                <strong>{{ item.total_students_with_records }}</strong>
              </div>
              <div>
                <span>已提交</span>
                <strong>{{ item.submitted_count }}</strong>
              </div>
              <div>
                <span>待批阅</span>
                <strong>{{ item.pending_review_count }}</strong>
              </div>
            </div>

            <p class="overview-mobile-subtle">
              草稿 {{ item.draft_count }} · 锁定 {{ item.locked_count }} · 已批阅 {{ item.reviewed_count }}
            </p>
            <p class="overview-mobile-subtle">通过 {{ item.passed_count }} · 未通过 {{ item.failed_count }}</p>
            <p class="overview-mobile-updated">最近更新：{{ formatTime(item.updated_at) }}</p>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getCurrentUserProfile } from "../api/auth";
import { downloadTeacherStudentImportTemplate, getTeacherExperimentOverview } from "../api/teacher";
import { formatApiDateTime } from "../utils/datetime";

const overviewList = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const isRoleChecking = ref(false);
const roleError = ref("");
const isTeacher = ref(false);
const isDownloadingTemplate = ref(false);

function formatTime(value) {
  return formatApiDateTime(value);
}

async function verifyTeacherRole() {
  isRoleChecking.value = true;
  roleError.value = "";
  try {
    const user = await getCurrentUserProfile();
    isTeacher.value = user?.role === "teacher";
    if (!isTeacher.value) {
      roleError.value = "";
    }
  } catch (error) {
    isTeacher.value = false;
    roleError.value = `权限验证失败：${error.message}`;
  } finally {
    isRoleChecking.value = false;
  }
}

async function loadOverview() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    overviewList.value = await getTeacherExperimentOverview();
  } catch (error) {
    errorMessage.value = `实验概览加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

function triggerFileDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

async function handleDownloadTemplate() {
  if (isDownloadingTemplate.value) {
    return;
  }
  isDownloadingTemplate.value = true;
  try {
    const blob = await downloadTeacherStudentImportTemplate();
    triggerFileDownload(blob, "学生名单导入模板.xlsx");
  } catch (error) {
    errorMessage.value = `模板下载失败：${error.message}`;
  } finally {
    isDownloadingTemplate.value = false;
  }
}

onMounted(async () => {
  await verifyTeacherRole();
  if (!isTeacher.value) {
    return;
  }
  await loadOverview();
});
</script>

<style scoped>
.teacher-page {
  display: grid;
  gap: 16px;
}

.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}

.header-panel h2 {
  margin: 0;
  font-size: clamp(30px, 2.45vw, 43px);
  line-height: 1.2;
  letter-spacing: 0.01em;
}

.header-desc {
  margin: 8px 0 0;
  color: var(--text-subtle);
  line-height: 1.45;
}

.header-hint {
  margin-top: 12px;
  color: var(--text-muted);
  line-height: 1.45;
}

.toolbar {
  margin-top: 12px;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.header-panel .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 44px;
  border-radius: 10px;
  padding: 9px 12px;
  text-decoration: none;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.btn.import {
  background: var(--text-strong);
  color: var(--surface-1);
}

.btn.download {
  border: 0;
  background: var(--brand-600);
  color: var(--surface-1);
  cursor: pointer;
}

.btn.manage {
  background: var(--accent-teal-strong);
  color: var(--surface-1);
}

.btn.download:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.list-wrap {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(0, 1fr);
}

.overview-card {
  display: grid;
  gap: 10px;
  width: 100%;
}

.overview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.overview-head h3 {
  margin: 0;
  min-width: 0;
  line-height: 1.28;
}

.desktop-only {
  display: grid;
}

.mobile-only {
  display: none;
}

.meta-grid {
  display: grid;
  gap: 6px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  color: var(--text-body);
  font-size: 14px;
}

.btn.detail {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--brand-600);
  color: var(--surface-1);
  padding: 8px 12px;
  text-decoration: none;
  font-weight: 600;
  min-height: 38px;
  white-space: nowrap;
  flex: 0 0 auto;
}

.overview-mobile {
  display: grid;
  gap: 10px;
}

.overview-mobile-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.metric-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 9px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--border-soft) 72%, var(--brand-border) 28%);
  background: color-mix(in srgb, var(--surface-2) 86%, var(--brand-soft) 14%);
  color: color-mix(in srgb, var(--text-body) 90%, var(--brand-700) 10%);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.25;
}

.metric-pill.published {
  background: color-mix(in srgb, var(--success-soft) 70%, var(--surface-1) 30%);
  color: var(--success-strong);
}

.metric-pill.unpublished {
  background: color-mix(in srgb, var(--danger-soft) 66%, var(--surface-1) 34%);
  color: var(--danger-strong);
}

.overview-mobile-times {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.overview-mobile-times > div {
  border: 1px solid color-mix(in srgb, var(--border-soft) 76%, var(--brand-border) 24%);
  border-radius: 10px;
  padding: 8px;
  background: color-mix(in srgb, var(--surface-1) 92%, var(--brand-soft) 8%);
  min-width: 0;
}

.overview-mobile-times span {
  display: block;
  font-size: 11px;
  color: var(--text-subtle);
}

.overview-mobile-times strong {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.35;
  color: var(--text-body);
  overflow-wrap: anywhere;
  word-break: break-word;
}

.overview-mobile-kpis {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.overview-mobile-kpis > div {
  border: 1px solid color-mix(in srgb, var(--border-soft) 78%, var(--brand-border) 22%);
  border-radius: 10px;
  padding: 8px 6px;
  background: color-mix(in srgb, var(--surface-1) 88%, var(--brand-soft) 12%);
  text-align: center;
}

.overview-mobile-kpis span {
  display: block;
  font-size: 11px;
  color: var(--text-subtle);
}

.overview-mobile-kpis strong {
  display: block;
  margin-top: 3px;
  font-size: 18px;
  line-height: 1.1;
  color: var(--text-strong);
}

.overview-mobile-subtle {
  margin: 0;
  font-size: 12px;
  line-height: 1.35;
  color: var(--text-subtle);
}

.overview-mobile-updated {
  margin: 0;
  font-size: 12px;
  line-height: 1.35;
  color: color-mix(in srgb, var(--text-muted) 88%, var(--brand-700) 12%);
}

@media (max-width: 1024px) {
  .header-panel h2 {
    font-size: clamp(27px, 4.6vw, 37px);
  }
}

@media (max-width: 960px) {
  .teacher-page {
    gap: 12px;
  }

  .panel {
    padding: 14px;
  }

  .header-panel h2 {
    font-size: clamp(24px, 6vw, 32px);
  }

  .desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: grid;
  }

  .overview-card {
    gap: 12px;
  }

  .overview-head {
    gap: 10px;
    flex-direction: column;
  }

  .overview-head h3 {
    font-size: clamp(18px, 4.9vw, 24px);
    line-height: 1.3;
  }

  .btn.detail {
    width: 100%;
    min-height: 42px;
    font-size: 15px;
  }
}

@media (max-width: 680px) {
  .toolbar {
    grid-template-columns: 1fr;
  }

  .header-desc,
  .header-hint {
    font-size: 13px;
  }

  .overview-mobile-times {
    grid-template-columns: 1fr;
  }
}
</style>
