<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>教师实验看板</h2>
      <p>统计口径：当前统计在该实验下“每个学生最新最终提交（status=submitted）”的批阅状态。</p>
      <p class="import-hint">学生名单模板必须包含：班级、学号、姓名（仅支持 .xlsx）。</p>
      <div class="toolbar">
        <RouterLink class="btn import" to="/teacher/student-import">上传学生名单</RouterLink>
        <RouterLink class="btn manage" to="/teacher/students">学生管理</RouterLink>
        <button type="button" class="btn download" :disabled="isDownloadingTemplate" @click="handleDownloadTemplate">
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
          <div class="meta-grid">
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
}

.header-panel p {
  margin: 8px 0 0;
  color: var(--text-subtle);
}

.import-hint {
  margin-top: 12px;
  color: var(--text-muted);
}

.toolbar {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn.import {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--text-strong);
  color: var(--surface-1);
  padding: 8px 12px;
  text-decoration: none;
  font-weight: 600;
}

.btn.download {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: 0;
  background: var(--brand-600);
  color: var(--surface-1);
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn.manage {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--accent-teal-strong);
  color: var(--surface-1);
  padding: 8px 12px;
  text-decoration: none;
  font-weight: 600;
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
}

.overview-card {
  display: grid;
  gap: 10px;
}

.overview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.overview-head h3 {
  margin: 0;
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
}
</style>
