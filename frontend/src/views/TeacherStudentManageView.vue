<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>学生账号管理</h2>
      <p class="header-desc">支持筛选、启停用、重置密码与导出账号清单。</p>
      <p class="header-hint">建议先导入学生名单，再进行筛选和批量操作。</p>
      <div class="toolbar">
        <RouterLink class="btn header-action back-nav" to="/teacher/experiments">返回教师看板</RouterLink>
        <RouterLink class="btn header-action import-nav" to="/teacher/student-import">去导入学生名单</RouterLink>
      </div>
    </article>

    <article v-if="isRoleChecking" class="panel">正在验证教师权限...</article>
    <article v-else-if="roleError" class="panel error">{{ roleError }}</article>
    <article v-else-if="!isTeacher" class="panel error">仅教师可访问当前页面</article>

    <template v-else>
      <article v-if="actionMessage" :class="['panel', actionError ? 'error' : 'success']">{{ actionMessage }}</article>

      <article class="panel filter-panel">
        <h3>筛选与查询</h3>
        <div class="filter-grid">
          <label class="filter-item">
            <span>关键字</span>
            <input
              v-model="filters.keyword"
              type="text"
              placeholder="用户名 / 姓名 / 学号"
              :disabled="isLoading"
              @keyup.enter="handleSearch"
            />
          </label>
          <label class="filter-item">
            <span>班级</span>
            <select v-model="filters.class_name" :disabled="isLoading || isClassOptionsLoading">
              <option value="">全部班级</option>
              <option v-for="name in classOptions" :key="name" :value="name">{{ name }}</option>
            </select>
          </label>
          <label class="filter-item">
            <span>学号</span>
            <input v-model="filters.student_no" type="text" placeholder="学号（可选）" :disabled="isLoading" @keyup.enter="handleSearch" />
          </label>
          <label class="filter-item">
            <span>账号状态</span>
            <select v-model="filters.is_enabled" :disabled="isLoading">
              <option value="all">全部</option>
              <option value="enabled">启用</option>
              <option value="disabled">停用</option>
            </select>
          </label>
          <label class="filter-item">
            <span>排序字段</span>
            <select v-model="filters.sort_by" :disabled="isLoading">
              <option value="created_at">created_at</option>
              <option value="username">username</option>
              <option value="full_name">full_name</option>
              <option value="student_no">student_no</option>
              <option value="class_name">class_name</option>
              <option value="is_enabled">is_enabled</option>
            </select>
          </label>
          <label class="filter-item">
            <span>排序方向</span>
            <select v-model="filters.sort_order" :disabled="isLoading">
              <option value="desc">desc</option>
              <option value="asc">asc</option>
            </select>
          </label>
        </div>
        <div class="filter-actions">
          <button type="button" class="btn light" :disabled="isLoading" @click="handleSearch">查询</button>
          <button type="button" class="btn gray" :disabled="isLoading" @click="handleResetFilters">重置</button>
          <button type="button" class="btn export" :disabled="isExporting || isLoading" @click="handleExport">
            {{ isExporting ? "导出中..." : "导出当前筛选" }}
          </button>
        </div>
      </article>

      <article class="panel">
        <div class="table-header">
          <h3>学生账号列表</h3>
          <div class="table-meta">共 {{ pagination.total }} 条，当前第 {{ pagination.page }} / {{ totalPagesText }} 页</div>
        </div>

        <div class="batch-ops">
          <span class="batch-meta">已选 {{ selectedCount }} 人</span>
          <div class="batch-actions">
            <button
              type="button"
              class="btn gray btn-batch-select-page"
              :disabled="isLoading || students.length === 0"
              @click="toggleSelectCurrentPage"
            >
              {{ isAllCurrentPageSelected ? "取消全选当前页" : "全选当前页" }}
            </button>
            <button
              type="button"
              class="btn gray btn-batch-clear"
              :disabled="selectedCount === 0 || isLoading"
              @click="clearSelection"
            >
              清空选择
            </button>
            <button
              type="button"
              class="btn manage btn-batch-enable"
              :disabled="selectedCount === 0 || isLoading || isActioning"
              @click="handleBatchEnable"
            >
              {{ isActioning ? "处理中..." : "批量启用" }}
            </button>
            <button
              type="button"
              class="btn disable btn-batch-disable"
              :disabled="selectedCount === 0 || isLoading || isActioning"
              @click="handleBatchDisable"
            >
              {{ isActioning ? "处理中..." : "批量停用" }}
            </button>
            <button
              type="button"
              class="btn reset btn-batch-reset"
              :disabled="selectedCount === 0 || isLoading || isActioning"
              @click="handleBatchResetPassword"
            >
              {{ isActioning ? "处理中..." : "批量重置密码" }}
            </button>
          </div>
        </div>

        <p v-if="isLoading" class="hint">正在加载学生账号...</p>
        <p v-else-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        <p v-else-if="students.length === 0" class="hint">当前筛选条件下无学生数据</p>
        <div v-else>
          <div class="table-wrap desktop-only">
            <table>
              <thead>
                <tr>
                  <th>选择</th>
                  <th>姓名</th>
                  <th>学号</th>
                  <th>班级</th>
                  <th>用户名</th>
                  <th>账号状态</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in students" :key="item.user_id">
                  <td>
                    <input
                      type="checkbox"
                      :checked="selectedUserIds.includes(item.user_id)"
                      :disabled="isLoading || isActioning"
                      @change="toggleUserSelection(item.user_id, $event.target.checked)"
                    />
                  </td>
                  <td>{{ item.full_name || "-" }}</td>
                  <td>{{ item.student_no || "-" }}</td>
                  <td>{{ item.class_name || "-" }}</td>
                  <td>{{ item.username }}</td>
                  <td>
                    <span :class="['status-tag', item.is_enabled ? 'enabled' : 'disabled']">
                      {{ item.is_enabled ? "启用" : "停用" }}
                    </span>
                  </td>
                  <td>{{ formatTime(item.created_at) }}</td>
                  <td class="actions">
                    <button type="button" class="btn manage" :disabled="item.is_enabled || isActioning" @click="handleSingleEnable(item)">
                      启用
                    </button>
                    <button type="button" class="btn disable" :disabled="!item.is_enabled || isActioning" @click="handleSingleDisable(item)">
                      停用
                    </button>
                    <button type="button" class="btn reset" :disabled="isActioning" @click="handleSingleResetPassword(item)">
                      重置密码
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mobile-only student-mobile-list">
            <article v-for="item in students" :key="`student-mobile-${item.user_id}`" class="student-mobile-card">
              <div class="student-mobile-head">
                <label class="student-mobile-check">
                  <input
                    type="checkbox"
                    :checked="selectedUserIds.includes(item.user_id)"
                    :disabled="isLoading || isActioning"
                    @change="toggleUserSelection(item.user_id, $event.target.checked)"
                  />
                </label>
                <div class="student-mobile-identity">
                  <h4>{{ item.full_name || item.username }}</h4>
                  <p>{{ item.username }}（#{{ item.user_id }}）</p>
                </div>
                <span :class="['status-tag', item.is_enabled ? 'enabled' : 'disabled']">
                  {{ item.is_enabled ? "启用" : "停用" }}
                </span>
              </div>

              <div class="student-mobile-meta">
                <span>学号：{{ item.student_no || "-" }}</span>
                <span>班级：{{ item.class_name || "-" }}</span>
              </div>
              <p class="student-mobile-time">创建：{{ formatTime(item.created_at) }}</p>

              <div class="student-mobile-actions">
                <button type="button" class="btn manage" :disabled="item.is_enabled || isActioning" @click="handleSingleEnable(item)">
                  启用
                </button>
                <button type="button" class="btn disable" :disabled="!item.is_enabled || isActioning" @click="handleSingleDisable(item)">
                  停用
                </button>
                <button type="button" class="btn reset" :disabled="isActioning" @click="handleSingleResetPassword(item)">
                  重置密码
                </button>
              </div>
            </article>
          </div>
        </div>

        <div class="pagination">
          <div class="page-size">
            <span>每页</span>
            <select v-model.number="pagination.page_size" :disabled="isLoading" @change="handlePageSizeChange">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span>条</span>
          </div>
          <div class="page-actions">
            <button type="button" class="btn gray" :disabled="isLoading || pagination.page <= 1" @click="goPrevPage">上一页</button>
            <span>第 {{ pagination.page }} / {{ totalPagesText }} 页</span>
            <button
              type="button"
              class="btn gray"
              :disabled="isLoading || pagination.page >= pagination.total_pages || pagination.total_pages === 0"
              @click="goNextPage"
            >
              下一页
            </button>
          </div>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { getCurrentUserProfile } from "../api/auth";
import {
  batchDisableTeacherStudents,
  batchEnableTeacherStudents,
  batchResetTeacherStudentPasswords,
  disableTeacherStudent,
  enableTeacherStudent,
  exportTeacherStudents,
  getTeacherStudentClassOptions,
  getTeacherStudents,
} from "../api/teacher";

const isRoleChecking = ref(false);
const roleError = ref("");
const isTeacher = ref(false);
const students = ref([]);
const isLoading = ref(false);
const isActioning = ref(false);
const isExporting = ref(false);
const isClassOptionsLoading = ref(false);
const errorMessage = ref("");
const actionMessage = ref("");
const actionError = ref(false);
const selectedUserIds = ref([]);
const classOptions = ref([]);

const filters = ref({
  keyword: "",
  class_name: "",
  student_no: "",
  is_enabled: "all",
  sort_by: "created_at",
  sort_order: "desc",
});

const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
});

const totalPagesText = computed(() => (pagination.value.total_pages > 0 ? pagination.value.total_pages : 1));
const selectedCount = computed(() => selectedUserIds.value.length);
const isAllCurrentPageSelected = computed(
  () => students.value.length > 0 && students.value.every((item) => selectedUserIds.value.includes(item.user_id)),
);

function formatTime(value) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

function buildListQueryParams() {
  const params = {
    page: pagination.value.page,
    page_size: pagination.value.page_size,
    keyword: filters.value.keyword.trim(),
    class_name: filters.value.class_name.trim(),
    student_no: filters.value.student_no.trim(),
    sort_by: filters.value.sort_by,
    sort_order: filters.value.sort_order,
  };
  if (filters.value.is_enabled === "enabled") {
    params.is_enabled = true;
  } else if (filters.value.is_enabled === "disabled") {
    params.is_enabled = false;
  }
  return params;
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

function resetActionMessage() {
  actionMessage.value = "";
  actionError.value = false;
}

function setActionMessage(text, isError = false) {
  actionMessage.value = text;
  actionError.value = isError;
}

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

async function loadStudents({ preserveSelection = true } = {}) {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const data = await getTeacherStudents(buildListQueryParams());
    students.value = data.items || [];
    pagination.value.total = data.total || 0;
    pagination.value.total_pages = data.total_pages || 0;
    if (preserveSelection) {
      const allCurrentIds = new Set((students.value || []).map((item) => item.user_id));
      selectedUserIds.value = selectedUserIds.value.filter((id) => allCurrentIds.has(id));
    } else {
      selectedUserIds.value = [];
    }
  } catch (error) {
    errorMessage.value = `学生列表加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

async function loadClassOptions() {
  isClassOptionsLoading.value = true;
  try {
    const options = await getTeacherStudentClassOptions();
    classOptions.value = Array.isArray(options) ? options : [];
  } catch (error) {
    classOptions.value = [];
    setActionMessage(`班级选项加载失败：${error.message}`, true);
  } finally {
    isClassOptionsLoading.value = false;
  }
}

async function handleSearch() {
  pagination.value.page = 1;
  await loadStudents({ preserveSelection: false });
}

async function handleResetFilters() {
  filters.value = {
    keyword: "",
    class_name: "",
    student_no: "",
    is_enabled: "all",
    sort_by: "created_at",
    sort_order: "desc",
  };
  pagination.value.page = 1;
  await loadStudents({ preserveSelection: false });
}

function toggleUserSelection(userId, checked) {
  if (checked) {
    if (!selectedUserIds.value.includes(userId)) {
      selectedUserIds.value = [...selectedUserIds.value, userId];
    }
    return;
  }
  selectedUserIds.value = selectedUserIds.value.filter((id) => id !== userId);
}

function toggleSelectCurrentPage() {
  const currentIds = students.value.map((item) => item.user_id);
  if (isAllCurrentPageSelected.value) {
    selectedUserIds.value = selectedUserIds.value.filter((id) => !currentIds.includes(id));
    return;
  }
  const merged = new Set([...selectedUserIds.value, ...currentIds]);
  selectedUserIds.value = Array.from(merged);
}

function clearSelection() {
  selectedUserIds.value = [];
}

function promptNewPassword() {
  const value = window.prompt("请输入新密码（不少于6位）", "123456");
  if (value === null) {
    return null;
  }
  const cleaned = value.trim();
  if (cleaned.length < 6) {
    window.alert("密码长度不能少于 6 位");
    return null;
  }
  return cleaned;
}

async function handleSingleEnable(item) {
  if (!window.confirm(`确认启用账号：${item.username}（#${item.user_id}）？`)) {
    return;
  }
  isActioning.value = true;
  resetActionMessage();
  try {
    await enableTeacherStudent(item.user_id);
    setActionMessage(`账号已启用：${item.username}`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`启用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleSingleDisable(item) {
  if (!window.confirm(`确认停用账号：${item.username}（#${item.user_id}）？`)) {
    return;
  }
  isActioning.value = true;
  resetActionMessage();
  try {
    await disableTeacherStudent(item.user_id);
    setActionMessage(`账号已停用：${item.username}`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`停用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleSingleResetPassword(item) {
  const newPassword = promptNewPassword();
  if (!newPassword) {
    return;
  }
  if (!window.confirm(`确认重置账号 ${item.username} 的密码？`)) {
    return;
  }
  isActioning.value = true;
  resetActionMessage();
  try {
    const result = await batchResetTeacherStudentPasswords({
      user_ids: [item.user_id],
      new_password: newPassword,
    });
    setActionMessage(`已成功重置 ${result.success_count} 个账号密码`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`重置密码失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleBatchEnable() {
  if (selectedUserIds.value.length === 0) {
    return;
  }
  if (!window.confirm(`确认批量启用已选 ${selectedUserIds.value.length} 个账号？`)) {
    return;
  }
  isActioning.value = true;
  resetActionMessage();
  try {
    const result = await batchEnableTeacherStudents({ user_ids: selectedUserIds.value });
    setActionMessage(`批量启用完成：成功 ${result.success_count} 个，失败 ${result.failed_count} 个`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`批量启用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleBatchDisable() {
  if (selectedUserIds.value.length === 0) {
    return;
  }
  if (!window.confirm(`确认批量停用已选 ${selectedUserIds.value.length} 个账号？`)) {
    return;
  }
  isActioning.value = true;
  resetActionMessage();
  try {
    const result = await batchDisableTeacherStudents({ user_ids: selectedUserIds.value });
    setActionMessage(`批量停用完成：成功 ${result.success_count} 个，失败 ${result.failed_count} 个`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`批量停用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleBatchResetPassword() {
  if (selectedUserIds.value.length === 0) {
    return;
  }
  const newPassword = promptNewPassword();
  if (!newPassword) {
    return;
  }
  if (!window.confirm(`确认批量重置已选 ${selectedUserIds.value.length} 个账号密码？`)) {
    return;
  }
  isActioning.value = true;
  resetActionMessage();
  try {
    const result = await batchResetTeacherStudentPasswords({
      user_ids: selectedUserIds.value,
      new_password: newPassword,
    });
    setActionMessage(`已成功重置 ${result.success_count} 个账号密码，失败 ${result.failed_count} 个`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`批量重置密码失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleExport() {
  isExporting.value = true;
  resetActionMessage();
  try {
    const query = buildListQueryParams();
    delete query.page;
    delete query.page_size;
    const blob = await exportTeacherStudents(query);
    triggerFileDownload(blob, "学生账号清单.xlsx");
    setActionMessage("导出成功");
  } catch (error) {
    setActionMessage(`导出失败：${error.message}`, true);
  } finally {
    isExporting.value = false;
  }
}

async function handlePageSizeChange() {
  pagination.value.page = 1;
  await loadStudents({ preserveSelection: false });
}

async function goPrevPage() {
  if (pagination.value.page <= 1) {
    return;
  }
  pagination.value.page -= 1;
  await loadStudents({ preserveSelection: false });
}

async function goNextPage() {
  if (pagination.value.page >= pagination.value.total_pages) {
    return;
  }
  pagination.value.page += 1;
  await loadStudents({ preserveSelection: false });
}

onMounted(async () => {
  await verifyTeacherRole();
  if (!isTeacher.value) {
    return;
  }
  await loadClassOptions();
  await loadStudents({ preserveSelection: false });
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
  margin: 12px 0 0;
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

.btn.back-nav {
  background: var(--text-strong);
  color: var(--surface-1);
}

.btn.import-nav {
  background: var(--accent-teal-strong);
  color: var(--surface-1);
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

.filter-panel h3 {
  margin-top: 0;
}

.filter-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.filter-item {
  display: grid;
  gap: 6px;
  color: var(--text-body);
}

.filter-item span {
  font-size: 14px;
  color: var(--text-muted);
}

.filter-item input,
.filter-item select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
}

.filter-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.table-header h3 {
  margin: 0;
}

.table-meta {
  color: var(--text-subtle);
  font-size: 14px;
}

.desktop-only {
  display: block !important;
}

.mobile-only {
  display: none !important;
}

.batch-ops {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.batch-meta {
  color: var(--text-body);
}

.batch-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.table-wrap {
  margin-top: 12px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 980px;
}

th,
td {
  border-bottom: 1px solid var(--border-soft);
  text-align: left;
  padding: 10px 8px;
  font-size: 14px;
}

th {
  color: var(--text-body);
  background: var(--surface-3);
}

th:nth-child(7),
td:nth-child(7) {
  width: 190px;
  white-space: nowrap;
}

th:nth-child(8),
td:nth-child(8) {
  width: 248px;
  white-space: nowrap;
}

th:nth-child(8),
td:nth-child(8) {
  padding-right: 0;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.status-tag.enabled {
  background: var(--success-soft);
  color: var(--success-strong);
}

.status-tag.disabled {
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.actions {
  display: flex;
  justify-content: flex-start;
  gap: 8px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.actions .btn {
  min-height: 34px;
  padding: 7px 10px;
  font-size: 13px;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 8px 12px;
  min-height: 36px;
  line-height: 1.2;
  color: var(--surface-1);
  cursor: pointer;
  font-weight: 600;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.light {
  background: var(--brand-600);
}

.btn.gray {
  background: var(--text-muted);
}

.btn.manage {
  background: var(--accent-teal-strong);
}

.btn.disable {
  background: var(--danger-strong);
}

.btn.reset {
  background: var(--accent-indigo-strong);
}

.btn.export {
  background: var(--accent-teal-strong);
}

.hint {
  color: var(--text-subtle);
}

.error-text {
  color: var(--danger-strong);
}

.pagination {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.page-size {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-body);
}

.page-size select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 6px 8px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Mobile card list (same interaction rhythm as teacher dashboard cards) */
.student-mobile-list {
  margin-top: 12px;
  gap: 10px;
}

.student-mobile-card {
  border: 1px solid color-mix(in srgb, var(--border-soft) 72%, var(--brand-border) 28%);
  border-radius: 12px;
  padding: 11px;
  background: color-mix(in srgb, var(--surface-1) 94%, var(--brand-soft) 6%);
  box-shadow: 0 8px 18px color-mix(in srgb, var(--brand-border) 10%, transparent);
  min-width: 0;
}

.student-mobile-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.student-mobile-check {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  padding-top: 0;
}

.student-mobile-check input[type="checkbox"] {
  width: 18px;
  height: 18px;
  min-height: 0;
  margin: 0;
}

.student-mobile-identity {
  display: grid;
  gap: 0;
  min-width: 0;
  flex: 1 1 auto;
}

.student-mobile-identity h4 {
  margin: 0;
  color: var(--text-strong);
  font-size: 15px;
  line-height: 1.25;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.student-mobile-identity p {
  margin: 0;
  color: var(--text-subtle);
  font-size: 12px;
  line-height: 1.35;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.student-mobile-meta {
  margin-top: 2px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.student-mobile-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--border-soft) 74%, var(--brand-border) 26%);
  background: color-mix(in srgb, var(--surface-2) 86%, var(--brand-soft) 14%);
  color: color-mix(in srgb, var(--text-body) 88%, var(--brand-700) 12%);
  padding: 3px 9px;
  font-size: 12px;
  line-height: 1.25;
}

.student-mobile-time {
  margin: 8px 0 0;
  color: var(--text-subtle);
  font-size: 12px;
  line-height: 1.35;
}

.student-mobile-actions {
  margin-top: 8px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}

.student-mobile-actions .btn {
  width: 100%;
  min-height: 30px;
  padding: 5px 6px;
  font-size: 12px;
  line-height: 1.15;
  font-weight: 600;
}

@media (max-width: 1180px) {
  .filter-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .header-panel h2 {
    font-size: clamp(27px, 4.6vw, 37px);
  }

  .table-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .batch-ops {
    align-items: stretch;
    flex-direction: column;
  }

  .batch-actions {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 6px;
  }

  .batch-actions .btn {
    width: 100%;
    min-height: 34px;
    padding: 6px 8px;
    font-size: 12px;
    line-height: 1.2;
    border-radius: 9px;
  }

  .btn-batch-select-page {
    grid-row: 1;
    grid-column: 1 / span 2;
  }

  .btn-batch-clear {
    grid-row: 1;
    grid-column: 3 / span 2;
  }

  .btn-batch-reset {
    grid-row: 1;
    grid-column: 5 / span 2;
  }

  .btn-batch-enable {
    grid-row: 2;
    grid-column: 1 / span 3;
  }

  .btn-batch-disable {
    grid-row: 2;
    grid-column: 4 / span 3;
  }
}

@media (max-width: 960px) {
  .desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: grid !important;
  }

  .teacher-page {
    gap: 12px;
  }

  .panel {
    padding: 14px;
  }

  .header-panel h2 {
    font-size: clamp(24px, 6vw, 32px);
  }

  .filter-grid {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filter-actions .btn {
    width: 100%;
  }

  .filter-actions .btn.export {
    grid-column: 1 / -1;
  }

  .pagination {
    align-items: stretch;
    flex-direction: column;
  }

  .page-actions {
    width: 100%;
    justify-content: space-between;
  }

  .student-mobile-actions {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .toolbar {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    grid-template-columns: 1fr;
  }

  .batch-actions {
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 6px;
  }

  .page-size,
  .page-actions {
    width: 100%;
    justify-content: space-between;
  }

  .student-mobile-actions {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .header-desc,
  .header-hint {
    font-size: 13px;
  }

  .batch-actions .btn {
    min-height: 32px;
    padding: 5px 6px;
    font-size: 11px;
  }
}
</style>
