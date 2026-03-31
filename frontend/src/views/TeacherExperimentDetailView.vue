<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>教师实验详情</h2>
      <p>实验ID：{{ hasValidExperimentId ? experimentId : "-" }} ｜ 实验标题：{{ experimentTitle }}</p>
      <RouterLink class="back-link" to="/teacher/experiments">返回实验看板</RouterLink>
    </article>

    <article v-if="isRoleChecking" class="panel">正在验证教师权限...</article>
    <article v-else-if="roleError" class="panel error">{{ roleError }}</article>
    <article v-else-if="!isTeacher" class="panel error">仅教师可访问当前页面</article>
    <article v-else-if="!hasValidExperimentId" class="panel error">缺少有效 experiment_id</article>
    <template v-else>
      <article v-if="actionMessage" :class="['panel', actionError ? 'error' : 'success']">{{ actionMessage }}</article>

      <article class="panel settings-panel">
        <h3>实验设置</h3>
        <div class="settings-grid">
          <label class="filter-item switch-item settings-publish">
            <span>发布状态</span>
            <div class="publish-control">
              <input v-model="settingsForm.is_published" type="checkbox" :disabled="settingsSaving" />
              <span>{{ settingsForm.is_published ? "已发布" : "未发布" }}</span>
            </div>
          </label>
          <label class="filter-item">
            <span>开放时间</span>
            <input v-model="settingsForm.open_at_local" type="datetime-local" :disabled="settingsSaving" />
          </label>
          <label class="filter-item">
            <span>截止时间</span>
            <input v-model="settingsForm.due_at_local" type="datetime-local" :disabled="settingsSaving" />
          </label>
        </div>
        <div class="settings-meta">
          <span>当前状态：{{ experimentPublishLabel }}</span>
          <span>开放：{{ formatTime(experimentSettings.open_at) }}</span>
          <span>截止：{{ formatTime(experimentSettings.due_at) }}</span>
        </div>
        <div class="filter-actions">
          <button type="button" class="btn review" :disabled="settingsSaving" @click="handleSaveExperimentSettings">
            {{ settingsSaving ? "保存中..." : "保存设置" }}
          </button>
        </div>
      </article>

      <article class="panel">
        <div class="table-header">
          <h3>班级统计</h3>
          <button type="button" class="btn gray" :disabled="classSummaryLoading" @click="loadClassSummary">
            {{ classSummaryLoading ? "加载中..." : "刷新统计" }}
          </button>
        </div>
        <p class="hint">统计口径：按系统内学生账号（role=student）所属班级汇总该实验的最新提交与批阅状态。</p>
        <p v-if="classSummaryLoading" class="hint">正在加载班级统计...</p>
        <p v-else-if="classSummaryError" class="error-text">{{ classSummaryError }}</p>
        <p v-else-if="classSummaryList.length === 0" class="hint">暂无班级统计数据</p>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>班级</th>
                <th>总人数</th>
                <th>已提交</th>
                <th>通过</th>
                <th>未通过</th>
                <th>待批阅</th>
                <th>未提交</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in classSummaryList" :key="item.class_name">
                <td>{{ item.class_name }}</td>
                <td>{{ item.total_students }}</td>
                <td>{{ item.submitted_count }}</td>
                <td>{{ item.passed_count }}</td>
                <td>{{ item.failed_count }}</td>
                <td>{{ item.pending_review_count }}</td>
                <td>{{ item.not_submitted_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="panel filter-panel">
        <h3>筛选与查询</h3>
        <div class="filter-grid">
          <label class="filter-item">
            <span>关键字</span>
            <input v-model="filters.keyword" type="text" placeholder="用户名 / 学号" @keyup.enter="handleSearch" />
          </label>
          <label class="filter-item">
            <span>状态</span>
            <select v-model="filters.status">
              <option value="all">all</option>
              <option value="draft">draft</option>
              <option value="submitted">submitted</option>
            </select>
          </label>
          <label class="filter-item">
            <span>批阅</span>
            <select v-model="filters.review_status">
              <option value="all">全部</option>
              <option value="pending">待批阅</option>
              <option value="passed">通过</option>
              <option value="failed">未通过</option>
            </select>
          </label>
          <label class="filter-item">
            <span>班级</span>
            <select v-model="filters.class_name">
              <option value="">全部班级</option>
              <option v-for="name in classFilterOptions" :key="name" :value="name">{{ name }}</option>
            </select>
          </label>
          <label class="filter-item">
            <span>学号</span>
            <input v-model="filters.student_no" type="text" placeholder="学号（可选）" @keyup.enter="handleSearch" />
          </label>
          <label class="filter-item">
            <span>排序字段</span>
            <select v-model="filters.sort_by">
              <option value="latest_updated_at">latest_updated_at</option>
              <option value="username">username</option>
              <option value="latest_version">latest_version</option>
            </select>
          </label>
          <label class="filter-item">
            <span>排序方向</span>
            <select v-model="filters.sort_order">
              <option value="desc">desc</option>
              <option value="asc">asc</option>
            </select>
          </label>
        </div>
        <div class="filter-actions">
          <button type="button" class="btn light" :disabled="studentsLoading" @click="handleSearch">查询</button>
          <button type="button" class="btn gray" :disabled="studentsLoading" @click="handleResetFilters">重置</button>
          <button type="button" class="btn export" :disabled="isExportingResults || studentsLoading" @click="handleExportCurrentResults">
            {{ isExportingResults ? "导出中..." : "导出当前结果" }}
          </button>
        </div>
      </article>

      <article class="panel">
        <div class="table-header">
          <h3>学生最新提交状态</h3>
          <div class="table-meta">共 {{ pagination.total }} 条，当前第 {{ pagination.page }} / {{ totalPagesText }} 页</div>
        </div>
        <div class="batch-ops">
          <span class="batch-meta">已选 {{ selectedCount }} 人，可批量批阅 {{ selectedSubmissionIds.length }} 条提交</span>
          <div class="batch-actions">
            <select
              v-model="batchReviewForm.review_status"
              class="batch-select"
              :disabled="studentsLoading || batchReturning || batchReviewing"
            >
              <option value="pending">待批阅</option>
              <option value="passed">通过</option>
              <option value="failed">未通过</option>
            </select>
            <input
              v-model="batchReviewForm.review_comment"
              class="batch-comment"
              type="text"
              maxlength="500"
              placeholder="批量批阅评语（可选）"
              :disabled="studentsLoading || batchReturning || batchReviewing"
            />
            <button
              type="button"
              class="btn gray"
              :disabled="selectableUserIds.length === 0 || studentsLoading || batchReturning || batchReviewing"
              @click="handleToggleSelectCurrentPage"
            >
              {{ isAllSelectableChecked ? "取消全选当前页" : "全选当前页" }}
            </button>
            <button
              type="button"
              class="btn gray"
              :disabled="selectedCount === 0 || studentsLoading || batchReturning || batchReviewing"
              @click="clearSelectedUsers"
            >
              清空选择
            </button>
            <button type="button" class="btn review" :disabled="!canBatchReview" @click="handleBatchReview">
              {{ batchReviewing ? "批量批阅中..." : "批量批阅" }}
            </button>
            <button type="button" class="btn return" :disabled="!canBatchReturn" @click="handleBatchReturn">
              {{ batchReturning ? "批量退回中..." : "批量退回" }}
            </button>
          </div>
        </div>
        <p v-if="studentsLoading" class="hint">正在加载学生状态...</p>
        <p v-else-if="studentsError" class="error-text">{{ studentsError }}</p>
        <p v-else-if="students.length === 0">当前条件下无数据</p>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>选择</th>
                <th>学生</th>
                <th>姓名</th>
                <th>学号</th>
                <th>班级</th>
                <th>版本</th>
                <th>状态</th>
                <th>批阅</th>
                <th>工作区</th>
                <th>批阅时间</th>
                <th>更新时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in students" :key="item.user_id">
                <td>
                  <input
                    type="checkbox"
                    :checked="selectedUserIds.includes(item.user_id)"
                    :disabled="!canSelectStudent(item) || studentsLoading || batchReturning || batchReviewing"
                    :title="canSelectStudent(item) ? '可用于批量退回/批量批阅' : '当前没有可退回的最终提交'"
                    @change="toggleUserSelection(item.user_id, $event.target.checked)"
                  />
                </td>
                <td>{{ item.username }}（#{{ item.user_id }}）</td>
                <td>{{ item.full_name || "-" }}</td>
                <td>{{ item.student_no || "-" }}</td>
                <td>{{ item.class_name || "-" }}</td>
                <td>v{{ item.latest_version }}</td>
                <td>
                  <span :class="['status-tag', item.latest_status]">{{ item.latest_status }}</span>
                </td>
                <td>
                  <span :class="['review-tag', item.review_status]">{{ formatReviewStatus(item.review_status) }}</span>
                </td>
                <td>{{ item.is_locked ? "已锁定" : "可编辑" }}</td>
                <td>{{ formatTime(item.reviewed_at) }}</td>
                <td>{{ formatTime(item.latest_updated_at) }}</td>
                <td class="actions">
                  <button type="button" class="btn light" @click="openHistoryDrawer(item)">查看历史</button>
                  <button
                    type="button"
                    class="btn return"
                    :disabled="!item.can_reopen || returningUserId === item.user_id || batchReturning"
                    @click="handleReturn(item)"
                  >
                    {{ returningUserId === item.user_id ? "退回中..." : "退回" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination">
          <div class="page-size">
            <span>每页</span>
            <select v-model.number="pagination.page_size" :disabled="studentsLoading" @change="handlePageSizeChange">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span>条</span>
          </div>
          <div class="page-actions">
            <button type="button" class="btn gray" :disabled="studentsLoading || pagination.page <= 1" @click="goPrevPage">
              上一页
            </button>
            <span>第 {{ pagination.page }} / {{ totalPagesText }} 页</span>
            <button
              type="button"
              class="btn gray"
              :disabled="studentsLoading || pagination.page >= pagination.total_pages || pagination.total_pages === 0"
              @click="goNextPage"
            >
              下一页
            </button>
          </div>
        </div>
      </article>
    </template>
  </section>

  <div v-show="isHistoryDrawerOpen" class="drawer-mask" @click.self="closeHistoryDrawer">
    <aside class="history-drawer" role="dialog" aria-modal="true">
      <div class="drawer-head">
        <div class="drawer-title">
          <h3>历史记录</h3>
          <p>
            实验：{{ experimentTitle }} ｜ 用户：{{ historyStudent?.username || "-" }}
            <span v-if="historyStudent?.full_name">｜ 姓名：{{ historyStudent.full_name }}</span>
            <span v-if="historyStudent?.student_no">（{{ historyStudent.student_no }}）</span>
          </p>
          <div class="drawer-status-line">
            <span>
              当前状态：
              <span :class="['status-tag', historyLatestStatus]">{{ historyLatestStatus }}</span>
            </span>
            <span>工作区：{{ historyLockText }}</span>
          </div>
          <p v-if="historyStudent && !historyCanReopen" class="hint return-hint">当前没有可退回的最终提交</p>
        </div>
        <div class="drawer-actions">
          <button
            type="button"
            class="btn return"
            :disabled="
              !historyStudent ||
              !historyCanReopen ||
              batchReturning ||
              (historyStudent && returningUserId === historyStudent.user_id)
            "
            @click="handleReturn(historyStudent, { preserveSelection: true, preserveDetail: true })"
          >
            {{ historyStudent && returningUserId === historyStudent.user_id ? "退回中..." : "退回" }}
          </button>
          <button type="button" class="btn light" :disabled="historyLoading || !historyStudent" @click="refreshHistory">
            刷新历史
          </button>
          <button type="button" class="btn gray" @click="closeHistoryDrawer">关闭</button>
        </div>
      </div>
      <div class="drawer-body">
        <div class="history-column">
          <p v-if="historyLoading" class="hint">历史记录加载中...</p>
          <p v-else-if="historyError" class="error-text">{{ historyError }}</p>
          <p v-else-if="historyList.length === 0" class="hint">暂无历史记录</p>
          <div v-else class="history-list">
            <button
              v-for="item in historyList"
              :key="item.id"
              type="button"
              :class="['history-item', selectedSubmissionId === item.id ? 'active' : '']"
              @click="loadSubmissionDetail(item.id)"
            >
              <div>v{{ item.version }} ｜ {{ item.status }}</div>
              <div>{{ formatTime(item.updated_at) }}</div>
            </button>
          </div>
        </div>
        <div class="detail-column">
          <p v-if="detailLoading" class="hint">提交详情加载中...</p>
          <p v-else-if="detailError" class="error-text">{{ detailError }}</p>
          <p v-else-if="!submissionDetail" class="hint">请选择历史版本查看详情</p>
          <div v-else class="detail-wrap">
            <div class="detail-meta">
              <span>提交ID：{{ submissionDetail.id }}</span>
              <span>状态：{{ submissionDetail.status }}</span>
              <span>版本：v{{ submissionDetail.version }}</span>
              <span>批阅：{{ formatReviewStatus(submissionDetail.review_status) }}</span>
              <span>批阅时间：{{ formatTime(submissionDetail.reviewed_at) }}</span>
              <span>更新时间：{{ formatTime(submissionDetail.updated_at) }}</span>
            </div>
            <div class="review-panel">
              <h4>批阅</h4>
              <label class="review-item">
                <span>批阅状态</span>
                <select v-model="reviewForm.review_status" :disabled="reviewSaving || !submissionDetail">
                  <option value="pending">待批阅</option>
                  <option value="passed">通过</option>
                  <option value="failed">未通过</option>
                </select>
              </label>
              <label class="review-item">
                <span>教师评语</span>
                <textarea
                  v-model="reviewForm.review_comment"
                  :disabled="reviewSaving || !submissionDetail"
                  rows="3"
                  placeholder="请输入批阅意见（可选）"
                />
              </label>
              <div class="review-actions">
                <button
                  type="button"
                  class="btn review"
                  :disabled="reviewSaving || !submissionDetail"
                  @click="saveReview"
                >
                  {{ reviewSaving ? "保存中..." : "保存批阅" }}
                </button>
              </div>
            </div>
            <div class="detail-scroll">
              <div class="io-block">
                <div class="io-title">代码</div>
                <pre>{{ submissionDetail.code || "（空）" }}</pre>
              </div>
              <div class="io-block">
                <div class="io-title">运行结果</div>
                <pre>{{ submissionDetail.run_output || "（空）" }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { getExperimentById } from "../api/experiment";
import { getCurrentUserProfile } from "../api/auth";
import {
  batchReviewTeacherSubmissions,
  batchReturnTeacherStudents,
  exportTeacherExperimentResults,
  getTeacherExperimentClassSummary,
  getTeacherExperimentStudents,
  getTeacherStudentHistory,
  getTeacherSubmissionDetail,
  reviewTeacherSubmission,
  returnTeacherStudentExperiment,
  updateTeacherExperimentSettings,
} from "../api/teacher";

const route = useRoute();

const isRoleChecking = ref(false);
const roleError = ref("");
const isTeacher = ref(false);

const students = ref([]);
const studentsLoading = ref(false);
const studentsError = ref("");

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
});

const filters = reactive({
  keyword: "",
  status: "all",
  review_status: "all",
  class_name: "",
  student_no: "",
  sort_by: "latest_updated_at",
  sort_order: "desc",
});

const isHistoryDrawerOpen = ref(false);
const historyStudent = ref(null);
const historyList = ref([]);
const historyLoading = ref(false);
const historyError = ref("");
const selectedSubmissionId = ref(null);
const detailLoading = ref(false);
const detailError = ref("");
const submissionDetail = ref(null);
const reviewSaving = ref(false);
const reviewForm = reactive({
  review_status: "pending",
  review_comment: "",
});
const studentsRequestToken = ref(0);
const historyRequestToken = ref(0);
const detailRequestToken = ref(0);
const pageScrollTop = ref(0);

const returningUserId = ref(null);
const batchReturning = ref(false);
const selectedUserIds = ref([]);
const actionMessage = ref("");
const actionError = ref(false);
const experimentTitle = ref("-");
const experimentSettings = ref({
  is_published: false,
  open_at: null,
  due_at: null,
});
const settingsForm = reactive({
  is_published: false,
  open_at_local: "",
  due_at_local: "",
});
const settingsSaving = ref(false);
const batchReviewing = ref(false);
const batchReviewForm = reactive({
  review_status: "passed",
  review_comment: "",
});
const classSummaryList = ref([]);
const classSummaryLoading = ref(false);
const classSummaryError = ref("");
const isExportingResults = ref(false);

const experimentId = computed(() => Number(route.query.experiment_id));
const hasValidExperimentId = computed(() => Number.isInteger(experimentId.value) && experimentId.value > 0);
const totalPagesText = computed(() => (pagination.total_pages > 0 ? pagination.total_pages : 0));
const classFilterOptions = computed(() => {
  const classNameSet = new Set();
  students.value.forEach((item) => {
    if (item.class_name) {
      classNameSet.add(item.class_name);
    }
  });
  return Array.from(classNameSet);
});
const historyLatestStatus = computed(() => historyStudent.value?.latest_status || "-");
const historyLockText = computed(() => (historyStudent.value?.is_locked ? "已锁定" : "可编辑"));
const historyCanReopen = computed(() => Boolean(isTeacher.value && historyStudent.value?.can_reopen));
const selectableUserIds = computed(() =>
  students.value.filter((item) => canSelectStudent(item)).map((item) => item.user_id),
);
const selectedCount = computed(() => selectedUserIds.value.length);
const isAllSelectableChecked = computed(
  () => selectableUserIds.value.length > 0 && selectableUserIds.value.every((userId) => selectedUserIds.value.includes(userId)),
);
const canBatchReturn = computed(
  () => selectedCount.value > 0 && !batchReturning.value && !batchReviewing.value && !studentsLoading.value,
);
const selectedSubmissionIds = computed(() => {
  const selectedIdSet = new Set(selectedUserIds.value);
  return students.value
    .filter((item) => selectedIdSet.has(item.user_id) && item.latest_status === "submitted")
    .map((item) => Number(item.latest_submission_id))
    .filter((id) => Number.isInteger(id) && id > 0);
});
const canBatchReview = computed(
  () => selectedSubmissionIds.value.length > 0 && !batchReviewing.value && !studentsLoading.value,
);
const experimentPublishLabel = computed(() => (experimentSettings.value?.is_published ? "已发布" : "未发布"));

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

function toDateTimeLocalValue(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  const pad = (num) => `${num}`.padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toIsoDateTime(value) {
  if (!value) {
    return null;
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return date.toISOString();
}

function formatReviewStatus(value) {
  if (value === "passed") {
    return "通过";
  }
  if (value === "failed") {
    return "未通过";
  }
  return "待批阅";
}

function canSelectStudent(item) {
  return Boolean(item && (item.has_final_submission || item.is_locked));
}

function clearSelectedUsers() {
  selectedUserIds.value = [];
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

function handleToggleSelectCurrentPage() {
  if (isAllSelectableChecked.value) {
    selectedUserIds.value = selectedUserIds.value.filter((id) => !selectableUserIds.value.includes(id));
    return;
  }
  const merged = new Set(selectedUserIds.value);
  selectableUserIds.value.forEach((id) => merged.add(id));
  selectedUserIds.value = Array.from(merged);
}

function formatFailedItemsSummary(failedItems) {
  if (!Array.isArray(failedItems) || failedItems.length === 0) {
    return "";
  }
  const preview = failedItems.slice(0, 3).map((item) => `#${item.user_id}：${item.reason}`);
  const moreCount = failedItems.length - preview.length;
  if (moreCount > 0) {
    return `${preview.join("；")}；其余 ${moreCount} 人请查看列表状态`;
  }
  return preview.join("；");
}

function savePageScrollPosition() {
  pageScrollTop.value = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
}

async function restorePageScrollPosition() {
  await nextTick();
  window.scrollTo(0, pageScrollTop.value);
}

function resetHistoryState() {
  historyStudent.value = null;
  historyList.value = [];
  historyLoading.value = false;
  historyError.value = "";
  selectedSubmissionId.value = null;
  detailLoading.value = false;
  detailError.value = "";
  submissionDetail.value = null;
  reviewSaving.value = false;
  reviewForm.review_status = "pending";
  reviewForm.review_comment = "";
}

function closeHistoryDrawer() {
  savePageScrollPosition();
  historyRequestToken.value += 1;
  detailRequestToken.value += 1;
  isHistoryDrawerOpen.value = false;
  resetHistoryState();
  void restorePageScrollPosition();
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

async function loadExperimentMeta() {
  if (!hasValidExperimentId.value) {
    experimentTitle.value = "-";
    return;
  }
  try {
    const experiment = await getExperimentById(experimentId.value);
    experimentTitle.value = experiment?.title || "-";
    experimentSettings.value = {
      is_published: Boolean(experiment?.is_published),
      open_at: experiment?.open_at || null,
      due_at: experiment?.due_at || null,
    };
    settingsForm.is_published = Boolean(experiment?.is_published);
    settingsForm.open_at_local = toDateTimeLocalValue(experiment?.open_at);
    settingsForm.due_at_local = toDateTimeLocalValue(experiment?.due_at);
  } catch (error) {
    experimentTitle.value = "加载失败";
  }
}

async function handleSaveExperimentSettings() {
  if (!hasValidExperimentId.value || settingsSaving.value) {
    return;
  }
  const openAt = toIsoDateTime(settingsForm.open_at_local);
  const dueAt = toIsoDateTime(settingsForm.due_at_local);
  if (openAt && dueAt && new Date(dueAt).getTime() < new Date(openAt).getTime()) {
    actionError.value = true;
    actionMessage.value = "截止时间不能早于开放时间";
    return;
  }
  actionMessage.value = "";
  actionError.value = false;
  settingsSaving.value = true;
  try {
    const updated = await updateTeacherExperimentSettings(experimentId.value, {
      is_published: settingsForm.is_published,
      open_at: openAt,
      due_at: dueAt,
    });
    experimentSettings.value = {
      is_published: Boolean(updated?.is_published),
      open_at: updated?.open_at || null,
      due_at: updated?.due_at || null,
    };
    settingsForm.is_published = Boolean(updated?.is_published);
    settingsForm.open_at_local = toDateTimeLocalValue(updated?.open_at);
    settingsForm.due_at_local = toDateTimeLocalValue(updated?.due_at);
    actionMessage.value = "实验设置已更新";
    await Promise.all([loadStudents(), loadClassSummary()]);
  } catch (error) {
    actionError.value = true;
    actionMessage.value = `实验设置保存失败：${error.message}`;
  } finally {
    settingsSaving.value = false;
  }
}

function buildStudentFilterParams() {
  return {
    keyword: filters.keyword,
    status: filters.status,
    review_status: filters.review_status,
    class_name: filters.class_name,
    student_no: filters.student_no,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
  };
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

async function loadClassSummary() {
  if (!hasValidExperimentId.value) {
    classSummaryList.value = [];
    classSummaryError.value = "";
    return;
  }
  classSummaryLoading.value = true;
  classSummaryError.value = "";
  try {
    classSummaryList.value = await getTeacherExperimentClassSummary(experimentId.value);
  } catch (error) {
    classSummaryList.value = [];
    classSummaryError.value = `班级统计加载失败：${error.message}`;
  } finally {
    classSummaryLoading.value = false;
  }
}

async function handleExportCurrentResults() {
  if (!hasValidExperimentId.value || isExportingResults.value) {
    return;
  }
  savePageScrollPosition();
  actionMessage.value = "";
  actionError.value = false;
  isExportingResults.value = true;
  try {
    const blob = await exportTeacherExperimentResults(experimentId.value, buildStudentFilterParams());
    triggerFileDownload(blob, `实验${experimentId.value}_结果导出.xlsx`);
    actionMessage.value = "导出成功";
  } catch (error) {
    actionError.value = true;
    actionMessage.value = `导出失败：${error.message}`;
  } finally {
    isExportingResults.value = false;
    await restorePageScrollPosition();
  }
}

async function loadStudents() {
  if (!hasValidExperimentId.value) {
    students.value = [];
    pagination.total = 0;
    pagination.total_pages = 0;
    return;
  }
  const requestToken = studentsRequestToken.value + 1;
  studentsRequestToken.value = requestToken;
  savePageScrollPosition();
  studentsLoading.value = true;
  studentsError.value = "";
  try {
    const data = await getTeacherExperimentStudents(experimentId.value, {
      page: pagination.page,
      page_size: pagination.page_size,
      ...buildStudentFilterParams(),
    });
    if (requestToken !== studentsRequestToken.value) {
      return;
    }
    students.value = data.items || [];
    const currentUserIds = new Set(students.value.map((item) => item.user_id));
    selectedUserIds.value = selectedUserIds.value.filter((id) => currentUserIds.has(id));
    pagination.total = data.total || 0;
    pagination.page = data.page || pagination.page;
    pagination.page_size = data.page_size || pagination.page_size;
    pagination.total_pages = data.total_pages || 0;
    if (isHistoryDrawerOpen.value && historyStudent.value) {
      const updated = students.value.find((item) => item.user_id === historyStudent.value.user_id);
      if (updated) {
        historyStudent.value = updated;
      }
    }
  } catch (error) {
    if (requestToken !== studentsRequestToken.value) {
      return;
    }
    studentsError.value = `学生状态加载失败：${error.message}`;
    students.value = [];
    pagination.total = 0;
    pagination.total_pages = 0;
  } finally {
    if (requestToken === studentsRequestToken.value) {
      studentsLoading.value = false;
    }
    await restorePageScrollPosition();
  }
}

async function handleBatchReturn() {
  if (!canBatchReturn.value) {
    return;
  }
  const confirmed = window.confirm(
    `确认批量退回当前选中的 ${selectedUserIds.value.length} 位学生吗？退回后这些学生将可继续修改并重新提交。`,
  );
  if (!confirmed) {
    return;
  }
  savePageScrollPosition();
  actionMessage.value = "";
  actionError.value = false;
  batchReturning.value = true;
  const targetUserIds = [...selectedUserIds.value];
  try {
    const result = await batchReturnTeacherStudents(experimentId.value, { user_ids: targetUserIds });
    const summary = `批量退回完成：成功 ${result.success_count} 人，失败 ${result.failed_count} 人`;
    const failedSummary = formatFailedItemsSummary(result.failed_items);
    actionMessage.value = failedSummary ? `${summary}。失败示例：${failedSummary}` : summary;
    actionError.value = result.success_count === 0 && result.failed_count > 0;
    await Promise.all([loadStudents(), loadClassSummary()]);
    clearSelectedUsers();
    if (isHistoryDrawerOpen.value && historyStudent.value && targetUserIds.includes(historyStudent.value.user_id)) {
      const updated = students.value.find((item) => item.user_id === historyStudent.value.user_id);
      if (updated) {
        historyStudent.value = updated;
      }
      await loadHistoryList(historyStudent.value.user_id, true);
      if (selectedSubmissionId.value) {
        const stillExists = historyList.value.some((item) => item.id === selectedSubmissionId.value);
        if (stillExists) {
          await loadSubmissionDetail(selectedSubmissionId.value);
        }
      }
    }
  } catch (error) {
    actionError.value = true;
    actionMessage.value = `批量退回失败：${error.message}`;
  } finally {
    batchReturning.value = false;
    await restorePageScrollPosition();
  }
}

async function handleBatchReview() {
  if (!canBatchReview.value) {
    return;
  }
  const confirmed = window.confirm(`确认批量批阅当前选中的 ${selectedSubmissionIds.value.length} 条提交吗？`);
  if (!confirmed) {
    return;
  }
  savePageScrollPosition();
  actionMessage.value = "";
  actionError.value = false;
  batchReviewing.value = true;
  try {
    const result = await batchReviewTeacherSubmissions({
      submission_ids: selectedSubmissionIds.value,
      review_status: batchReviewForm.review_status,
      review_comment: batchReviewForm.review_comment,
    });
    const summary = `批量批阅完成：成功 ${result.success_count} 条，失败 ${result.failed_count} 条`;
    actionMessage.value = summary;
    actionError.value = result.success_count === 0 && result.failed_count > 0;
    await Promise.all([loadStudents(), loadClassSummary()]);
    if (isHistoryDrawerOpen.value && historyStudent.value?.user_id) {
      await loadHistoryList(historyStudent.value.user_id, true);
      if (selectedSubmissionId.value) {
        const stillExists = historyList.value.some((item) => item.id === selectedSubmissionId.value);
        if (stillExists) {
          await loadSubmissionDetail(selectedSubmissionId.value);
        }
      }
    }
  } catch (error) {
    actionError.value = true;
    actionMessage.value = `批量批阅失败：${error.message}`;
  } finally {
    batchReviewing.value = false;
    await restorePageScrollPosition();
  }
}

async function loadHistoryList(userId, preserveSelection = false) {
  const requestToken = historyRequestToken.value + 1;
  historyRequestToken.value = requestToken;
  historyLoading.value = true;
  historyError.value = "";
  const previousSelectedId = preserveSelection ? selectedSubmissionId.value : null;
  try {
    const list = await getTeacherStudentHistory(experimentId.value, userId);
    if (requestToken !== historyRequestToken.value) {
      return;
    }
    historyList.value = list;
    if (previousSelectedId) {
      const stillExists = list.some((item) => item.id === previousSelectedId);
      if (!stillExists) {
        selectedSubmissionId.value = null;
        detailError.value = "";
        submissionDetail.value = null;
      }
    }
  } catch (error) {
    if (requestToken !== historyRequestToken.value) {
      return;
    }
    historyError.value = `历史记录加载失败：${error.message}`;
    historyList.value = [];
  } finally {
    if (requestToken === historyRequestToken.value) {
      historyLoading.value = false;
    }
  }
}

async function openHistoryDrawer(student) {
  savePageScrollPosition();
  isHistoryDrawerOpen.value = true;
  historyStudent.value = student;
  historyList.value = [];
  selectedSubmissionId.value = null;
  detailError.value = "";
  submissionDetail.value = null;
  await loadHistoryList(student.user_id, false);
  await restorePageScrollPosition();
}

async function refreshHistory() {
  if (!historyStudent.value) {
    return;
  }
  savePageScrollPosition();
  await loadHistoryList(historyStudent.value.user_id, true);
  await restorePageScrollPosition();
}

async function loadSubmissionDetail(submissionId) {
  const requestToken = detailRequestToken.value + 1;
  detailRequestToken.value = requestToken;
  savePageScrollPosition();
  selectedSubmissionId.value = submissionId;
  detailLoading.value = true;
  detailError.value = "";
  try {
    const detail = await getTeacherSubmissionDetail(submissionId);
    if (requestToken !== detailRequestToken.value) {
      return;
    }
    submissionDetail.value = detail;
    reviewForm.review_status = detail.review_status || "pending";
    reviewForm.review_comment = detail.review_comment || "";
  } catch (error) {
    if (requestToken !== detailRequestToken.value) {
      return;
    }
    detailError.value = `提交详情加载失败：${error.message}`;
    submissionDetail.value = null;
  } finally {
    if (requestToken === detailRequestToken.value) {
      detailLoading.value = false;
    }
    await restorePageScrollPosition();
  }
}

async function saveReview() {
  if (!submissionDetail.value) {
    return;
  }
  savePageScrollPosition();
  actionMessage.value = "";
  actionError.value = false;
  reviewSaving.value = true;
  try {
    const detail = await reviewTeacherSubmission(submissionDetail.value.id, {
      review_status: reviewForm.review_status,
      review_comment: reviewForm.review_comment,
    });
    submissionDetail.value = detail;
    reviewForm.review_status = detail.review_status || "pending";
    reviewForm.review_comment = detail.review_comment || "";
    actionMessage.value = "批阅已保存";
    await Promise.all([loadStudents(), loadClassSummary()]);
    if (historyStudent.value?.user_id) {
      await loadHistoryList(historyStudent.value.user_id, true);
    }
  } catch (error) {
    actionError.value = true;
    actionMessage.value = `批阅保存失败：${error.message}`;
  } finally {
    reviewSaving.value = false;
    await restorePageScrollPosition();
  }
}

async function handleReturn(student, options = {}) {
  const { preserveSelection = false, preserveDetail = false } = options;
  if (!student || !student.can_reopen) {
    return;
  }
  const confirmed = window.confirm(
    "确认退回该用户当前实验的最终提交吗？退回后该用户将可继续修改并重新提交。",
  );
  if (!confirmed) {
    return;
  }
  savePageScrollPosition();
  actionMessage.value = "";
  actionError.value = false;
  returningUserId.value = student.user_id;
  try {
    await returnTeacherStudentExperiment(experimentId.value, student.user_id);
    actionMessage.value = "已退回，该用户可继续修改并重新提交";
    await Promise.all([loadStudents(), loadClassSummary()]);
    if (isHistoryDrawerOpen.value && historyStudent.value?.user_id === student.user_id && historyStudent.value) {
      const updated = students.value.find((item) => item.user_id === student.user_id);
      if (updated) {
        historyStudent.value = updated;
      }
      await loadHistoryList(student.user_id, preserveSelection);
      if (preserveDetail && selectedSubmissionId.value) {
        const stillExists = historyList.value.some((item) => item.id === selectedSubmissionId.value);
        if (stillExists) {
          await loadSubmissionDetail(selectedSubmissionId.value);
        }
      }
    }
  } catch (error) {
    actionError.value = true;
    actionMessage.value = `退回失败：${error.message}`;
  } finally {
    returningUserId.value = null;
    await restorePageScrollPosition();
  }
}

async function handleSearch() {
  pagination.page = 1;
  await loadStudents();
}

async function handleResetFilters() {
  filters.keyword = "";
  filters.status = "all";
  filters.review_status = "all";
  filters.class_name = "";
  filters.student_no = "";
  filters.sort_by = "latest_updated_at";
  filters.sort_order = "desc";
  pagination.page = 1;
  await loadStudents();
}

async function handlePageSizeChange() {
  pagination.page = 1;
  await loadStudents();
}

async function goPrevPage() {
  if (pagination.page <= 1) {
    return;
  }
  pagination.page -= 1;
  await loadStudents();
}

async function goNextPage() {
  if (pagination.page >= pagination.total_pages) {
    return;
  }
  pagination.page += 1;
  await loadStudents();
}

function handleKeydown(event) {
  if (event.key === "Escape" && isHistoryDrawerOpen.value) {
    closeHistoryDrawer();
  }
}

async function initializePage() {
  await verifyTeacherRole();
  if (!isTeacher.value || !hasValidExperimentId.value) {
    return;
  }
  pagination.page = 1;
  await Promise.all([loadExperimentMeta(), loadStudents(), loadClassSummary()]);
}

watch(
  () => route.query.experiment_id,
  async () => {
    actionMessage.value = "";
    closeHistoryDrawer();
    await initializePage();
  },
);

onMounted(async () => {
  window.addEventListener("keydown", handleKeydown);
  await initializePage();
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydown);
});
</script>

<style scoped>
.teacher-page {
  display: grid;
  gap: 16px;
}

.panel {
  background: #fff;
  border: 1px solid #e5e8f0;
  border-radius: 12px;
  padding: 18px;
}

.header-panel h2 {
  margin: 0;
}

.header-panel p {
  margin: 8px 0;
  color: #4b5563;
}

.back-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}

.error {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.success {
  border-color: #bbf7d0;
  background: #f0fdf4;
  color: #166534;
}

.error-text {
  color: #b91c1c;
}

.hint {
  color: #6b7280;
}

.settings-panel h3 {
  margin: 0 0 12px;
}

.settings-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-items: end;
}

.switch-item {
  align-content: start;
}

.settings-publish {
  min-width: 200px;
}

.publish-control {
  min-height: 42px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #111827;
  font-size: 14px;
}

.publish-control input {
  margin: 0;
}

.settings-meta {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #374151;
  font-size: 13px;
}

@media (max-width: 1100px) {
  .settings-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

.filter-panel h3 {
  margin: 0 0 12px;
}

.filter-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.filter-item {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: #374151;
}

.filter-item input,
.filter-item select {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
}

.filter-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.table-header h3 {
  margin: 0;
}

.table-meta {
  color: #6b7280;
  font-size: 13px;
}

.batch-ops {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.batch-meta {
  color: #374151;
  font-size: 14px;
}

.batch-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.batch-select,
.batch-comment {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 14px;
}

.batch-comment {
  min-width: 260px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1180px;
}

th,
td {
  border-bottom: 1px solid #e5e7eb;
  padding: 10px 8px;
  text-align: left;
  font-size: 14px;
}

th {
  color: #374151;
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 7px 10px;
  cursor: pointer;
  color: #fff;
  font-weight: 600;
}

.btn.light {
  background: #2563eb;
}

.btn.return {
  background: #7c3aed;
}

.btn.review {
  background: #0f766e;
}

.btn.gray {
  background: #4b5563;
}

.btn.export {
  background: #0f766e;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 700;
}

.status-tag.draft {
  color: #1d4ed8;
  background: #dbeafe;
}

.status-tag.submitted {
  color: #5b21b6;
  background: #ede9fe;
}

.review-tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 700;
}

.review-tag.pending {
  color: #92400e;
  background: #fef3c7;
}

.review-tag.passed {
  color: #166534;
  background: #dcfce7;
}

.review-tag.failed {
  color: #991b1b;
  background: #fee2e2;
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.page-size {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #374151;
  font-size: 14px;
}

.page-size select {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 6px 8px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
  font-size: 14px;
}

.drawer-mask {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.35);
  display: flex;
  justify-content: flex-end;
  z-index: 1200;
}

.history-drawer {
  width: min(980px, 92vw);
  height: 100vh;
  background: #fff;
  display: grid;
  grid-template-rows: auto 1fr;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.16);
}

.drawer-head {
  border-bottom: 1px solid #e5e7eb;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.drawer-title h3 {
  margin: 0;
}

.drawer-title p {
  margin: 6px 0 0;
  color: #4b5563;
  font-size: 13px;
}

.drawer-status-line {
  margin-top: 6px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: #374151;
  font-size: 13px;
  align-items: center;
}

.return-hint {
  margin: 6px 0 0;
}

.drawer-actions {
  display: flex;
  gap: 8px;
}

.drawer-body {
  min-height: 0;
  display: grid;
  grid-template-columns: 320px 1fr;
}

.history-column {
  border-right: 1px solid #e5e7eb;
  padding: 12px;
  min-height: 0;
}

.history-list {
  display: grid;
  gap: 8px;
  max-height: calc(100vh - 170px);
  overflow-y: auto;
  padding-right: 2px;
}

.history-item {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #f8fafc;
  text-align: left;
  padding: 8px 10px;
  cursor: pointer;
  display: grid;
  gap: 4px;
}

.history-item.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.detail-column {
  padding: 12px;
  min-height: 0;
}

.detail-wrap {
  height: 100%;
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 10px;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #374151;
  font-size: 13px;
}

.review-panel {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px;
  display: grid;
  gap: 8px;
}

.review-panel h4 {
  margin: 0;
}

.review-item {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: #374151;
}

.review-item select,
.review-item textarea {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
}

.review-actions {
  display: flex;
  justify-content: flex-end;
}

.detail-scroll {
  min-height: 0;
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  display: grid;
  gap: 10px;
  padding-right: 2px;
}

.io-block {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
}

.io-title {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  padding: 8px 10px;
  font-weight: 700;
  font-size: 13px;
}

pre {
  margin: 0;
  padding: 10px;
  max-height: 320px;
  overflow: auto;
  background: #ffffff;
}
</style>
