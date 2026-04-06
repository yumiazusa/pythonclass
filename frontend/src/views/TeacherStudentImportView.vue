<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>导入学生名单</h2>
      <p>仅支持 .xlsx，模板必须包含：班级、学号、姓名。序号列可存在但会被忽略。</p>
      <RouterLink class="back-link" to="/teacher/experiments">返回教师看板</RouterLink>
    </article>

    <article v-if="isRoleChecking" class="panel">正在验证教师权限...</article>
    <article v-else-if="roleError" class="panel error">{{ roleError }}</article>
    <article v-else-if="!isTeacher" class="panel error">仅教师可访问当前页面</article>

    <template v-else>
      <article class="panel">
        <h3>上传文件</h3>
        <p class="upload-rules">支持 .xlsx，模板必须包含：班级、学号、姓名。</p>
        <div class="uploader">
          <input ref="fileInputRef" type="file" accept=".xlsx" @change="handleSelectFile" />
          <button
            type="button"
            class="btn download"
            :disabled="isDownloadingTemplate"
            @click="handleDownloadTemplate"
          >
            {{ isDownloadingTemplate ? "下载中..." : "下载模板" }}
          </button>
          <button type="button" class="btn upload" :disabled="isUploading || !selectedFile" @click="handleImport">
            {{ isUploading ? "导入中..." : "开始导入" }}
          </button>
        </div>
        <p class="hint">
          当前文件：<span>{{ selectedFile ? selectedFile.name : "未选择文件" }}</span>
        </p>
      </article>

      <article v-if="message" :class="['panel', messageIsError ? 'error' : 'success']">{{ message }}</article>

      <article v-if="importResult" class="panel">
        <h3>导入结果</h3>
        <div class="summary-grid">
          <div>总行数：{{ importResult.total_rows }}</div>
          <div>新建：{{ importResult.created_count }}</div>
          <div>更新：{{ importResult.updated_count }}</div>
          <div>跳过：{{ importResult.skipped_count }}</div>
          <div>错误：{{ importResult.failed_items.length }}</div>
        </div>
        <div v-if="importResult.failed_items.length > 0" class="failed-wrap">
          <h4>错误明细（前 10 条）</h4>
          <ul>
            <li v-for="item in previewFailedItems" :key="`${item.row}-${item.student_no}-${item.reason}`">
              第 {{ item.row }} 行｜学号：{{ item.student_no || "-" }}｜原因：{{ item.reason }}
            </li>
          </ul>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { getCurrentUserProfile } from "../api/auth";
import { downloadTeacherStudentImportTemplate, importTeacherStudents } from "../api/teacher";

const isRoleChecking = ref(false);
const roleError = ref("");
const isTeacher = ref(false);
const selectedFile = ref(null);
const fileInputRef = ref(null);
const isUploading = ref(false);
const isDownloadingTemplate = ref(false);
const importResult = ref(null);
const message = ref("");
const messageIsError = ref(false);

const previewFailedItems = computed(() => (importResult.value?.failed_items || []).slice(0, 10));

async function verifyTeacherRole() {
  isRoleChecking.value = true;
  roleError.value = "";
  try {
    const user = await getCurrentUserProfile();
    isTeacher.value = user?.role === "teacher";
  } catch (error) {
    isTeacher.value = false;
    roleError.value = `权限验证失败：${error.message}`;
  } finally {
    isRoleChecking.value = false;
  }
}

function handleSelectFile(event) {
  const file = event?.target?.files?.[0] || null;
  selectedFile.value = file;
  importResult.value = null;
  message.value = "";
  messageIsError.value = false;
}

async function handleImport() {
  if (!selectedFile.value) {
    message.value = "请先选择 .xlsx 文件";
    messageIsError.value = true;
    return;
  }
  if (!selectedFile.value.name.toLowerCase().endsWith(".xlsx")) {
    message.value = "仅支持 .xlsx 文件";
    messageIsError.value = true;
    return;
  }
  isUploading.value = true;
  message.value = "";
  messageIsError.value = false;
  importResult.value = null;
  try {
    const result = await importTeacherStudents(selectedFile.value);
    importResult.value = result;
    message.value = result.message || "导入完成";
    messageIsError.value = false;
    if (fileInputRef.value) {
      fileInputRef.value.value = "";
    }
    selectedFile.value = null;
  } catch (error) {
    message.value = `导入失败：${error.message}`;
    messageIsError.value = true;
  } finally {
    isUploading.value = false;
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
  message.value = "";
  messageIsError.value = false;
  try {
    const blob = await downloadTeacherStudentImportTemplate();
    triggerFileDownload(blob, "学生名单导入模板.xlsx");
  } catch (error) {
    message.value = `模板下载失败：${error.message}`;
    messageIsError.value = true;
  } finally {
    isDownloadingTemplate.value = false;
  }
}

onMounted(async () => {
  await verifyTeacherRole();
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
  margin: 8px 0 12px;
  color: var(--text-subtle);
}

.back-link {
  color: var(--brand-600);
  text-decoration: none;
  font-weight: 600;
}

.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.success {
  border-color: var(--success-border);
  background: var(--success-soft);
  color: var(--success-strong);
}

.uploader {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.upload-rules {
  margin: 8px 0 12px;
  color: var(--text-muted);
}

.btn.upload {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 8px;
  background: var(--text-strong);
  color: var(--surface-1);
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn.download {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 8px;
  background: var(--brand-600);
  color: var(--surface-1);
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn.upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.download:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hint {
  margin-top: 12px;
  color: var(--text-muted);
}

.summary-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.failed-wrap {
  margin-top: 14px;
}

.failed-wrap h4 {
  margin: 0 0 8px;
}

.failed-wrap ul {
  margin: 0;
  padding-left: 18px;
}

.failed-wrap li {
  color: var(--text-body);
  margin-bottom: 6px;
}
</style>
