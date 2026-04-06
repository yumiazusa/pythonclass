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
        <div v-else>
          <div class="table-wrap desktop-only">
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
          <div class="mobile-only summary-mobile-list">
            <article v-for="item in classSummaryList" :key="`summary-${item.class_name}`" class="summary-mobile-card">
              <div class="summary-mobile-head">
                <h4>{{ item.class_name }}</h4>
                <span class="summary-mobile-rate">提交率 {{ formatSubmitRate(item.submitted_count, item.total_students) }}</span>
              </div>
              <div class="summary-mobile-metrics">
                <div>
                  <span>总人数</span>
                  <strong>{{ item.total_students }}</strong>
                </div>
                <div>
                  <span>已提交</span>
                  <strong>{{ item.submitted_count }}</strong>
                </div>
                <div>
                  <span>待批阅</span>
                  <strong>{{ item.pending_review_count }}</strong>
                </div>
                <div>
                  <span>通过</span>
                  <strong>{{ item.passed_count }}</strong>
                </div>
              </div>
              <p class="summary-mobile-foot">未提交 {{ item.not_submitted_count }} ｜ 未通过 {{ item.failed_count }}</p>
            </article>
          </div>
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
            <span class="batch-select-label">批量设为</span>
            <select
              v-model="batchReviewForm.review_status"
              class="batch-select"
              aria-label="批量批阅目标状态"
              title="批量批阅目标状态"
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
              placeholder="批量评语（可选）"
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
              {{ batchReviewing ? "执行中..." : "执行批量批阅" }}
            </button>
            <button type="button" class="btn return" :disabled="!canBatchReturn" @click="handleBatchReturn">
              {{ batchReturning ? "批量退回中..." : "批量退回" }}
            </button>
          </div>
        </div>
        <p v-if="studentsLoading" class="hint">正在加载学生状态...</p>
        <p v-else-if="studentsError" class="error-text">{{ studentsError }}</p>
        <p v-else-if="students.length === 0">当前条件下无数据</p>
        <div v-else>
          <div class="table-wrap desktop-only">
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
                    <span
                      :class="['status-tag', item.latest_status, 'compact']"
                      :title="formatLatestStatusText(item.latest_status)"
                      :aria-label="`提交状态：${formatLatestStatusText(item.latest_status)}`"
                    >
                      {{ formatLatestStatusShort(item.latest_status) }}
                    </span>
                  </td>
                  <td>
                    <span
                      :class="['review-tag', item.review_status, 'compact']"
                      :title="formatReviewBadgeText(item.review_status)"
                      :aria-label="`批阅状态：${formatReviewBadgeText(item.review_status)}`"
                    >
                      {{ formatReviewBadgeShort(item.review_status) }}
                    </span>
                  </td>
                  <td class="workspace-cell" :title="item.is_locked ? '已锁定' : '可编辑'">
                    {{ item.is_locked ? "锁" : "编" }}
                  </td>
                  <td>{{ formatTime(item.reviewed_at) }}</td>
                  <td>{{ formatTime(item.latest_updated_at) }}</td>
                  <td class="actions">
                    <button type="button" class="btn light" :disabled="!resolveUserId(item)" @click="openHistoryDrawer(item)">
                      查看历史
                    </button>
                    <button
                      type="button"
                      class="btn return"
                      :disabled="!resolveUserId(item) || !item.can_reopen || returningUserId === item.user_id || batchReturning"
                      @click="handleReturn(item)"
                    >
                      {{ returningUserId === item.user_id ? "退回中..." : "退回" }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-only students-mobile-list">
            <article v-for="item in students" :key="`student-${item.user_id}`" class="student-mobile-card">
              <div class="student-mobile-head">
                <label class="student-mobile-check">
                  <input
                    type="checkbox"
                    :checked="selectedUserIds.includes(item.user_id)"
                    :disabled="!canSelectStudent(item) || studentsLoading || batchReturning || batchReviewing"
                    :title="canSelectStudent(item) ? '可用于批量退回/批量批阅' : '当前没有可退回的最终提交'"
                    @change="toggleUserSelection(item.user_id, $event.target.checked)"
                  />
                </label>
                <div class="student-mobile-identity">
                  <h4>{{ item.full_name || item.username }}</h4>
                  <p>{{ item.username }}</p>
                </div>
                <span class="student-mobile-version">v{{ item.latest_version }}</span>
              </div>
              <div class="student-mobile-meta">
                <span>班级：{{ item.class_name || "未分班" }}</span>
                <span>学号：{{ item.student_no || "-" }}</span>
                <span>工作区：{{ item.is_locked ? "锁定" : "可编辑" }}</span>
              </div>
              <div class="student-mobile-statuses">
                <span :class="['status-tag', item.latest_status]">提交：{{ formatLatestStatusMobile(item.latest_status) }}</span>
                <span :class="['review-tag', item.review_status]">批阅：{{ formatReviewStatus(item.review_status) }}</span>
              </div>
              <p class="student-mobile-time">更新：{{ formatTime(item.latest_updated_at) }}</p>
              <div class="student-mobile-actions">
                <button type="button" class="btn light" :disabled="!resolveUserId(item)" @click="openHistoryDrawer(item)">
                  查看历史
                </button>
                <button
                  type="button"
                  class="btn return"
                  :disabled="!resolveUserId(item) || !item.can_reopen || returningUserId === item.user_id || batchReturning"
                  @click="handleReturn(item)"
                >
                  {{ returningUserId === item.user_id ? "退回中..." : "退回" }}
                </button>
              </div>
            </article>
          </div>
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
    <aside
      :class="['history-drawer', isHistoryDrawerDragging ? 'dragging' : '']"
      :style="historyDrawerStyle"
      role="dialog"
      aria-modal="true"
    >
      <div class="drawer-drag-handle" title="向下拖拽可关闭" @pointerdown="handleDrawerDragStart">
        <span></span>
      </div>
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
              <span class="history-item-main">v{{ item.version }} ｜ {{ item.status }}</span>
              <span class="history-item-time">{{ formatTime(item.updated_at) }}</span>
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
import { formatApiDateTime, toDateTimeLocalInput, toUtcIsoStringFromLocalInput } from "../utils/datetime";

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
const historyDrawerOffsetY = ref(0);
const isHistoryDrawerDragging = ref(false);
const historyDrawerDragStartY = ref(0);
const historyDrawerDragStartOffsetY = ref(0);

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
  students.value
    .filter((item) => canSelectStudent(item))
    .map((item) => resolveUserId(item))
    .filter((userId) => userId !== null),
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
    .filter((item) => {
      const itemUserId = resolveUserId(item);
      return itemUserId !== null && selectedIdSet.has(itemUserId) && item.latest_status === "submitted";
    })
    .map((item) => Number(item.latest_submission_id))
    .filter((id) => Number.isInteger(id) && id > 0);
});
const canBatchReview = computed(
  () => selectedSubmissionIds.value.length > 0 && !batchReviewing.value && !studentsLoading.value,
);
const experimentPublishLabel = computed(() => (experimentSettings.value?.is_published ? "已发布" : "未发布"));
const historyDrawerStyle = computed(() => ({
  transform: `translate3d(0, ${historyDrawerOffsetY.value}px, 0)`,
}));

function formatTime(value) {
  return formatApiDateTime(value);
}

function toDateTimeLocalValue(value) {
  return toDateTimeLocalInput(value);
}

function toIsoDateTime(value) {
  return toUtcIsoStringFromLocalInput(value);
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

function formatLatestStatusText(value) {
  if (value === "submitted") {
    return "submitted";
  }
  if (value === "draft") {
    return "draft";
  }
  return value || "-";
}

function formatLatestStatusShort(value) {
  if (value === "submitted") {
    return "S";
  }
  if (value === "draft") {
    return "D";
  }
  return "-";
}

function formatLatestStatusMobile(value) {
  if (value === "submitted") {
    return "已提交";
  }
  if (value === "draft") {
    return "草稿";
  }
  return "-";
}

function formatSubmitRate(submittedCount, totalStudents) {
  const total = Number(totalStudents) || 0;
  const submitted = Number(submittedCount) || 0;
  if (total <= 0) {
    return "0%";
  }
  return `${Math.round((submitted / total) * 100)}%`;
}

function formatReviewBadgeShort(value) {
  if (value === "pending") {
    return "待";
  }
  return "批";
}

function formatReviewBadgeText(value) {
  if (value === "pending") {
    return "待批阅";
  }
  if (value === "passed") {
    return "已批阅（通过）";
  }
  if (value === "failed") {
    return "已批阅（未通过）";
  }
  return "待批阅";
}

function resolveUserId(value) {
  const rawUserId = value?.user_id ?? value?.userId ?? value?.id ?? null;
  const parsedUserId = Number(rawUserId);
  if (!Number.isInteger(parsedUserId) || parsedUserId <= 0) {
    return null;
  }
  return parsedUserId;
}

function normalizeStudentItem(item) {
  const normalizedUserId = resolveUserId(item);
  return {
    ...item,
    user_id: normalizedUserId,
  };
}

function getHistoryStudentUserId() {
  return resolveUserId(historyStudent.value);
}

function canSelectStudent(item) {
  return Boolean(item && resolveUserId(item) !== null && (item.has_final_submission || item.is_locked));
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

function clampNumber(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function resetHistoryDrawerDrag() {
  isHistoryDrawerDragging.value = false;
  historyDrawerOffsetY.value = 0;
  historyDrawerDragStartY.value = 0;
  historyDrawerDragStartOffsetY.value = 0;
}

function handleDrawerDragStart(event) {
  if (!isHistoryDrawerOpen.value) {
    return;
  }
  if (event.pointerType === "mouse" && event.button !== 0) {
    return;
  }
  isHistoryDrawerDragging.value = true;
  historyDrawerDragStartY.value = event.clientY;
  historyDrawerDragStartOffsetY.value = historyDrawerOffsetY.value;
  event.preventDefault();
}

function handleWindowPointerMove(event) {
  if (!isHistoryDrawerDragging.value) {
    return;
  }
  const deltaY = event.clientY - historyDrawerDragStartY.value;
  const maxOffset = typeof window !== "undefined" ? Math.max(260, Math.round(window.innerHeight * 0.88)) : 640;
  const nextOffset = historyDrawerDragStartOffsetY.value + Math.max(0, deltaY);
  historyDrawerOffsetY.value = clampNumber(nextOffset, 0, maxOffset);
  event.preventDefault();
}

function finishHistoryDrawerDrag() {
  if (!isHistoryDrawerDragging.value) {
    return;
  }
  const closeThreshold = typeof window !== "undefined" ? Math.max(120, Math.round(window.innerHeight * 0.16)) : 180;
  const shouldClose = historyDrawerOffsetY.value >= closeThreshold;
  isHistoryDrawerDragging.value = false;
  if (shouldClose) {
    historyDrawerOffsetY.value = 0;
    closeHistoryDrawer();
    return;
  }
  historyDrawerOffsetY.value = 0;
}

function handleWindowPointerUp() {
  finishHistoryDrawerDrag();
}

function handleWindowPointerCancel() {
  finishHistoryDrawerDrag();
}

function closeHistoryDrawer() {
  resetHistoryDrawerDrag();
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
    students.value = (data.items || []).map((item) => normalizeStudentItem(item));
    const currentUserIds = new Set(students.value.map((item) => resolveUserId(item)).filter((id) => id !== null));
    selectedUserIds.value = selectedUserIds.value.filter((id) => currentUserIds.has(id));
    pagination.total = data.total || 0;
    pagination.page = data.page || pagination.page;
    pagination.page_size = data.page_size || pagination.page_size;
    pagination.total_pages = data.total_pages || 0;
    if (isHistoryDrawerOpen.value && historyStudent.value) {
      const historyUserId = getHistoryStudentUserId();
      const updated =
        historyUserId === null ? null : students.value.find((item) => resolveUserId(item) === historyUserId);
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
    const historyUserId = getHistoryStudentUserId();
    if (isHistoryDrawerOpen.value && historyUserId !== null && targetUserIds.includes(historyUserId)) {
      const updated = students.value.find((item) => resolveUserId(item) === historyUserId);
      if (updated) {
        historyStudent.value = updated;
      }
      await loadHistoryList(historyUserId, true);
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
    const historyUserId = getHistoryStudentUserId();
    if (isHistoryDrawerOpen.value && historyUserId !== null) {
      await loadHistoryList(historyUserId, true);
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
  const normalizedUserId = Number(userId);
  if (!Number.isInteger(normalizedUserId) || normalizedUserId <= 0) {
    historyError.value = "历史记录加载失败：缺少有效的用户标识";
    historyList.value = [];
    if (requestToken === historyRequestToken.value) {
      historyLoading.value = false;
    }
    return;
  }
  try {
    const list = await getTeacherStudentHistory(experimentId.value, normalizedUserId);
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
  resetHistoryDrawerDrag();
  isHistoryDrawerOpen.value = true;
  const normalizedUserId = resolveUserId(student);
  historyStudent.value = normalizedUserId === null ? student : { ...student, user_id: normalizedUserId };
  historyList.value = [];
  selectedSubmissionId.value = null;
  detailError.value = "";
  submissionDetail.value = null;
  await loadHistoryList(normalizedUserId, false);
  await restorePageScrollPosition();
}

async function refreshHistory() {
  const historyUserId = getHistoryStudentUserId();
  if (!historyStudent.value || historyUserId === null) {
    return;
  }
  savePageScrollPosition();
  await loadHistoryList(historyUserId, true);
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
    const historyUserId = getHistoryStudentUserId();
    if (historyUserId !== null) {
      await loadHistoryList(historyUserId, true);
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
  const studentUserId = resolveUserId(student);
  if (!student || !student.can_reopen || studentUserId === null) {
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
  returningUserId.value = studentUserId;
  try {
    await returnTeacherStudentExperiment(experimentId.value, studentUserId);
    actionMessage.value = "已退回，该用户可继续修改并重新提交";
    await Promise.all([loadStudents(), loadClassSummary()]);
    const historyUserId = getHistoryStudentUserId();
    if (isHistoryDrawerOpen.value && historyUserId === studentUserId && historyStudent.value) {
      const updated = students.value.find((item) => resolveUserId(item) === studentUserId);
      if (updated) {
        historyStudent.value = updated;
      }
      await loadHistoryList(studentUserId, preserveSelection);
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
  window.addEventListener("pointermove", handleWindowPointerMove, { passive: false });
  window.addEventListener("pointerup", handleWindowPointerUp);
  window.addEventListener("pointercancel", handleWindowPointerCancel);
  await initializePage();
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydown);
  window.removeEventListener("pointermove", handleWindowPointerMove);
  window.removeEventListener("pointerup", handleWindowPointerUp);
  window.removeEventListener("pointercancel", handleWindowPointerCancel);
});
</script>

<style scoped>
.teacher-page {
  display: grid;
  gap: clamp(14px, 1.8vw, 22px);
}

.panel {
  background: color-mix(in srgb, var(--surface-1) 92%, var(--brand-soft) 8%);
  border: 1px solid color-mix(in srgb, var(--border-soft) 74%, var(--brand-border) 26%);
  border-radius: 14px;
  padding: clamp(14px, 1.8vw, 20px);
  box-shadow: 0 10px 24px color-mix(in srgb, var(--brand-border) 12%, transparent);
}

.header-panel h2 {
  margin: 0;
  font-size: clamp(24px, 2.1vw, 30px);
  line-height: 1.15;
  letter-spacing: 0.01em;
  color: color-mix(in srgb, var(--text-strong) 90%, var(--brand-700) 10%);
}

.header-panel p {
  margin: 8px 0;
  color: color-mix(in srgb, var(--text-muted) 86%, var(--brand-700) 14%);
  font-size: 14px;
  line-height: 1.45;
}

.back-link {
  color: color-mix(in srgb, var(--brand-700) 88%, var(--text-strong) 12%);
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.01em;
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

.error-text {
  color: var(--danger-strong);
}

.hint {
  color: var(--text-subtle);
}

.settings-panel h3 {
  margin: 0 0 14px;
  font-size: clamp(18px, 1.4vw, 22px);
  line-height: 1.2;
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
  border: 1px solid color-mix(in srgb, var(--border-strong) 72%, var(--brand-border) 28%);
  border-radius: 10px;
  padding: 8px 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-strong);
  font-size: 13px;
  background: color-mix(in srgb, var(--surface-1) 88%, var(--brand-soft) 12%);
}

.publish-control input {
  margin: 0;
}

.settings-meta {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--text-body);
  font-size: 13px;
  line-height: 1.35;
}

.settings-meta span {
  border: 1px solid color-mix(in srgb, var(--border-soft) 70%, var(--brand-border) 30%);
  border-radius: 999px;
  padding: 4px 10px;
  background: color-mix(in srgb, var(--surface-2) 84%, var(--brand-soft) 16%);
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
  margin: 0 0 14px;
  font-size: clamp(18px, 1.4vw, 22px);
  line-height: 1.2;
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
  color: var(--text-body);
  line-height: 1.35;
}

.filter-item input,
.filter-item select {
  border: 1px solid color-mix(in srgb, var(--border-strong) 72%, var(--brand-border) 28%);
  border-radius: 10px;
  padding: 9px 10px;
  font-size: 13px;
  color: var(--text-strong);
  background: color-mix(in srgb, var(--surface-1) 88%, var(--brand-soft) 12%);
}

.filter-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.table-header h3 {
  margin: 0;
  font-size: clamp(18px, 1.4vw, 22px);
  line-height: 1.2;
}

.table-meta {
  color: color-mix(in srgb, var(--text-subtle) 84%, var(--brand-700) 16%);
  font-size: 13px;
}

.batch-ops {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px;
  border: 1px solid color-mix(in srgb, var(--border-soft) 72%, var(--brand-border) 28%);
  border-radius: 12px;
  background: color-mix(in srgb, var(--surface-2) 84%, var(--brand-soft) 16%);
}

.batch-meta {
  color: var(--text-body);
  font-size: 13px;
  line-height: 1.35;
}

.batch-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.batch-select-label {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 2px;
  color: color-mix(in srgb, var(--text-body) 88%, var(--brand-700) 12%);
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.batch-select,
.batch-comment {
  border: 1px solid color-mix(in srgb, var(--border-strong) 72%, var(--brand-border) 28%);
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 13px;
  background: color-mix(in srgb, var(--surface-1) 88%, var(--brand-soft) 12%);
  color: var(--text-strong);
}

.batch-comment {
  min-width: 260px;
}

.table-wrap {
  position: relative;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x pan-y;
  overscroll-behavior-x: contain;
  border: 1px solid color-mix(in srgb, var(--border-soft) 74%, var(--brand-border) 26%);
  border-radius: 12px;
  background: color-mix(in srgb, var(--surface-1) 94%, var(--brand-soft) 6%);
  scrollbar-gutter: stable;
}

table {
  width: max-content;
  border-collapse: collapse;
  min-width: 1180px;
}

th,
td {
  border-bottom: 1px solid var(--border-soft);
  padding: 10px 9px;
  text-align: left;
  font-size: 13px;
  line-height: 1.35;
}

th {
  color: color-mix(in srgb, var(--text-body) 88%, var(--brand-700) 12%);
  font-weight: 700;
  position: sticky;
  top: 0;
  z-index: 2;
  background: color-mix(in srgb, var(--surface-2) 88%, var(--brand-soft) 12%);
}

tbody tr {
  transition: background-color 0.2s ease;
}

tbody tr:hover {
  background: color-mix(in srgb, var(--brand-soft) 42%, var(--surface-1) 58%);
}

.actions {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.actions .btn {
  padding: 6px 8px;
  font-size: 12px;
  line-height: 1.1;
  border-radius: 7px;
  white-space: nowrap;
}

.workspace-cell {
  text-align: center;
  font-weight: 700;
  color: var(--text-body);
}

.btn {
  border: none;
  border-radius: 10px;
  min-height: 38px;
  padding: 8px 11px;
  cursor: pointer;
  color: var(--surface-1);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.01em;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    filter 0.18s ease;
}

.btn.light {
  background: var(--brand-600);
}

.btn.return {
  background: var(--accent-indigo-strong);
}

.btn.review {
  background: var(--accent-teal-strong);
}

.btn.gray {
  background: var(--text-muted);
}

.btn.export {
  background: var(--accent-teal-strong);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn:hover {
  transform: translateY(-1px);
  filter: saturate(1.03);
}

.btn:focus-visible,
.back-link:focus-visible,
.filter-item input:focus-visible,
.filter-item select:focus-visible,
.batch-select:focus-visible,
.batch-comment:focus-visible,
.publish-control:focus-within {
  outline: none;
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.status-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 13px;
  font-weight: 700;
}

.status-tag.compact,
.review-tag.compact {
  width: 30px;
  min-width: 30px;
  height: 30px;
  padding: 0;
  font-size: 13px;
  line-height: 1;
}

.status-tag.draft {
  color: var(--brand-700);
  background: var(--brand-soft-2);
}

.status-tag.submitted {
  color: var(--accent-indigo-strong);
  background: var(--accent-indigo-soft);
}

.review-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 13px;
  font-weight: 700;
}

.review-tag.pending {
  color: var(--warn-strong);
  background: var(--warn-soft);
}

.review-tag.passed {
  color: var(--success-strong);
  background: var(--success-soft);
}

.review-tag.failed {
  color: var(--danger-strong);
  background: var(--danger-soft);
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
  color: var(--text-body);
  font-size: 14px;
}

.page-size select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 6px 8px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-body);
  font-size: 13px;
}

.desktop-only {
  display: block;
}

.mobile-only {
  display: none;
}

.summary-mobile-list,
.students-mobile-list {
  gap: 10px;
}

.summary-mobile-card,
.student-mobile-card {
  border: 1px solid color-mix(in srgb, var(--border-soft) 74%, var(--brand-border) 26%);
  border-radius: 12px;
  padding: 11px;
  background: color-mix(in srgb, var(--surface-1) 94%, var(--brand-soft) 6%);
  box-shadow: 0 8px 18px color-mix(in srgb, var(--brand-border) 10%, transparent);
}

.summary-mobile-head,
.student-mobile-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.summary-mobile-head h4,
.student-mobile-identity h4 {
  margin: 0;
  font-size: 14px;
  line-height: 1.25;
  color: var(--text-strong);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-mobile-rate {
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--brand-border) 74%, var(--border-soft) 26%);
  background: color-mix(in srgb, var(--surface-2) 82%, var(--brand-soft) 18%);
  color: var(--brand-700);
  font-size: 12px;
  font-weight: 700;
  padding: 3px 9px;
  white-space: nowrap;
  flex: 0 0 auto;
}

.summary-mobile-metrics {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.summary-mobile-metrics > div {
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--border-soft) 76%, var(--brand-border) 24%);
  background: color-mix(in srgb, var(--surface-1) 88%, var(--brand-soft) 12%);
  padding: 8px;
  display: grid;
  gap: 2px;
}

.summary-mobile-metrics span {
  font-size: 11px;
  color: var(--text-subtle);
}

.summary-mobile-metrics strong {
  font-size: 15px;
  color: var(--text-strong);
}

.summary-mobile-foot {
  margin: 8px 0 0;
  font-size: 11px;
  color: var(--text-subtle);
}

.student-mobile-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
}

.student-mobile-identity {
  flex: 1;
  min-width: 0;
}

.student-mobile-identity p {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.3;
  color: var(--text-subtle);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-mobile-version {
  font-size: 12px;
  font-weight: 700;
  color: var(--brand-700);
  white-space: nowrap;
}

.student-mobile-meta {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.student-mobile-meta span {
  font-size: 11px;
  line-height: 1.2;
  color: var(--text-subtle);
  border: 1px solid color-mix(in srgb, var(--border-soft) 78%, var(--brand-border) 22%);
  border-radius: 999px;
  background: color-mix(in srgb, var(--surface-1) 90%, var(--brand-soft) 10%);
  padding: 3px 7px;
}

.student-mobile-statuses {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.student-mobile-statuses .status-tag,
.student-mobile-statuses .review-tag {
  font-size: 12px;
  min-height: 24px;
  padding: 3px 9px;
}

.student-mobile-time {
  margin: 8px 0 0;
  font-size: 11px;
  color: var(--text-subtle);
}

.student-mobile-actions {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.student-mobile-actions .btn {
  width: 100%;
}

@media (max-width: 1024px) {
  .desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: grid;
  }
}

@media (max-width: 1180px) {
  .filter-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .batch-actions {
    width: 100%;
  }

  .batch-comment {
    min-width: min(280px, 100%);
    flex: 1 1 240px;
  }
}

@media (max-width: 860px) {
  .settings-grid,
  .filter-grid {
    grid-template-columns: 1fr;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-actions {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .batch-ops {
    padding: 10px;
  }

  .batch-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
  }

  .batch-select,
  .batch-comment {
    width: 100%;
    min-width: 0;
  }

  .batch-select-label {
    min-height: 0;
    padding: 2px 0;
  }

  .pagination {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .panel {
    padding: 12px;
  }

  .filter-actions,
  .batch-actions {
    grid-template-columns: 1fr;
  }

  .student-mobile-actions {
    grid-template-columns: 1fr;
  }
}

.drawer-mask {
  position: fixed;
  inset: 0;
  background: color-mix(in srgb, var(--overlay-soft) 86%, var(--brand-soft) 14%);
  backdrop-filter: blur(3px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 8px 8px 0;
  z-index: var(--z-drawer);
}

.history-drawer {
  width: min(1520px, 99vw);
  height: calc(100dvh - 8px);
  background: var(--surface-1);
  display: grid;
  grid-template-rows: auto auto auto;
  box-shadow: var(--shadow-elevated);
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  border-left: 1px solid color-mix(in srgb, var(--border-soft) 72%, var(--brand-border) 28%);
  border-radius: 16px 16px 0 0;
  transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
}

.history-drawer.dragging {
  transition: none;
}

.drawer-drag-handle {
  height: 24px;
  display: grid;
  place-items: center;
  touch-action: none;
  cursor: grab;
  position: sticky;
  top: 0;
  z-index: 6;
  background: color-mix(in srgb, var(--surface-1) 88%, var(--brand-soft) 12%);
  border-bottom: 1px solid color-mix(in srgb, var(--border-soft) 74%, var(--brand-border) 26%);
}

.drawer-drag-handle:active {
  cursor: grabbing;
}

.drawer-drag-handle span {
  width: clamp(64px, 9vw, 92px);
  height: 6px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--brand-border) 62%, var(--border-strong) 38%);
}

.drawer-head {
  border-bottom: 1px solid var(--border-soft);
  padding: clamp(14px, 1.8vw, 20px) clamp(14px, 1.9vw, 22px);
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  position: sticky;
  top: 24px;
  z-index: 5;
  background: color-mix(in srgb, var(--surface-1) 92%, var(--brand-soft) 8%);
}

.drawer-title h3 {
  margin: 0;
  font-size: clamp(20px, 1.4vw, 24px);
  line-height: 1.2;
  letter-spacing: 0.01em;
}

.drawer-title p {
  margin: 6px 0 0;
  color: color-mix(in srgb, var(--text-muted) 86%, var(--brand-700) 14%);
  font-size: 14px;
  line-height: 1.45;
}

.drawer-status-line {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--text-body);
  font-size: 13px;
  line-height: 1.35;
  align-items: center;
}

.return-hint {
  margin: 8px 0 0;
}

.drawer-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.drawer-body {
  min-height: auto;
  display: grid;
  grid-template-columns: clamp(278px, 25vw, 348px) minmax(0, 1fr);
  align-items: start;
}

.history-column {
  border-right: 1px solid var(--border-soft);
  padding: clamp(12px, 1.4vw, 16px);
  min-height: auto;
  display: grid;
  grid-template-rows: auto auto;
  gap: 10px;
  overflow: visible;
}

.history-list {
  display: grid;
  gap: 10px;
  max-height: min(72dvh, 760px);
  min-height: 120px;
  min-width: 0;
  height: auto;
  align-content: start;
  grid-auto-rows: max-content;
  overflow-y: auto;
  padding-right: 6px;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.history-item {
  border: 1px solid color-mix(in srgb, var(--border-strong) 70%, var(--brand-border) 30%);
  border-radius: 10px;
  background: color-mix(in srgb, var(--surface-3) 90%, var(--brand-soft) 10%);
  text-align: left;
  min-height: 58px;
  padding: 11px 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 5px;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
  color: var(--text-body);
  font-size: 13px;
  line-height: 1.35;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    box-shadow 0.2s ease;
}

.history-item:hover {
  border-color: var(--brand-border-strong);
  background: color-mix(in srgb, var(--brand-soft-2) 58%, var(--surface-2) 42%);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--brand-soft) 40%, transparent);
}

.history-item.active {
  border-color: var(--brand-600);
  background: color-mix(in srgb, var(--brand-soft) 66%, var(--surface-2) 34%);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--brand-soft) 54%, transparent);
}

.history-item-main,
.history-item-time {
  display: block;
  width: 100%;
  min-width: 0;
}

.history-item-main {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.01em;
  line-height: 1.32;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.history-item-time {
  font-size: 12px;
  line-height: 1.38;
  color: color-mix(in srgb, var(--text-muted) 88%, var(--brand-700) 12%);
  overflow-wrap: anywhere;
  word-break: break-word;
}

.detail-column {
  padding: clamp(12px, 1.4vw, 16px);
  min-height: auto;
  overflow: visible;
}

.detail-wrap {
  height: auto;
  display: grid;
  grid-template-rows: auto auto auto;
  gap: 12px;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--text-body);
  font-size: 13px;
  line-height: 1.35;
}

.detail-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--border-soft) 70%, var(--brand-border) 30%);
  background: color-mix(in srgb, var(--surface-2) 84%, var(--brand-soft) 16%);
}

.review-panel {
  border: 1px solid color-mix(in srgb, var(--border-soft) 74%, var(--brand-border) 26%);
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 10px;
  background: color-mix(in srgb, var(--surface-2) 86%, var(--brand-soft) 14%);
}

.review-panel h4 {
  margin: 0;
  font-size: 16px;
  line-height: 1.25;
}

.review-item {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: var(--text-body);
  line-height: 1.35;
}

.review-item select,
.review-item textarea {
  border: 1px solid color-mix(in srgb, var(--border-strong) 72%, var(--brand-border) 28%);
  border-radius: 10px;
  padding: 9px 11px;
  font-size: 13px;
  color: var(--text-strong);
  background: color-mix(in srgb, var(--surface-1) 88%, var(--brand-soft) 12%);
}

.review-actions {
  display: flex;
  justify-content: flex-end;
}

.detail-scroll {
  min-height: auto;
  overflow: visible;
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  padding-right: 4px;
}

.io-block {
  border: 1px solid color-mix(in srgb, var(--border-soft) 72%, var(--brand-border) 28%);
  border-radius: 12px;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 0;
  background: color-mix(in srgb, var(--surface-1) 90%, var(--brand-soft) 10%);
}

.io-title {
  background: color-mix(in srgb, var(--surface-2) 80%, var(--brand-soft) 20%);
  border-bottom: 1px solid color-mix(in srgb, var(--border-soft) 72%, var(--brand-border) 28%);
  padding: 10px 12px;
  font-weight: 700;
  font-size: 13px;
  line-height: 1.3;
  color: color-mix(in srgb, var(--brand-800) 92%, var(--text-strong) 8%);
}

.io-block pre {
  margin: 0;
  padding: 12px 14px;
  min-height: clamp(420px, 58vh, 860px);
  max-height: clamp(520px, 76vh, 1040px);
  overflow: auto;
  background: color-mix(in srgb, var(--surface-1) 92%, var(--brand-soft) 8%);
  color: var(--text-strong);
  font-size: 13px;
  line-height: 1.58;
  letter-spacing: 0.01em;
  font-family: var(--font-mono);
  tab-size: 2;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.history-list,
.io-block pre {
  scrollbar-width: thin;
  scrollbar-color: color-mix(in srgb, var(--brand-border) 64%, var(--border-strong) 36%) transparent;
}

.history-list::-webkit-scrollbar,
.io-block pre::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.history-list::-webkit-scrollbar-thumb,
.io-block pre::-webkit-scrollbar-thumb {
  border-radius: 999px;
  border: 2px solid transparent;
  background-clip: padding-box;
  background: color-mix(in srgb, var(--brand-border) 64%, var(--border-strong) 36%);
}

.history-list::-webkit-scrollbar-track,
.io-block pre::-webkit-scrollbar-track {
  background: transparent;
}

@media (max-width: 1200px) {
  .history-drawer {
    width: min(1280px, 99vw);
  }

  .detail-scroll {
    padding-right: 2px;
  }
}

@media (min-width: 961px) {
  .history-drawer {
    overflow: hidden;
  }

  .drawer-body {
    min-height: 0;
    height: 100%;
    overflow: hidden;
  }

  .history-column,
  .detail-column {
    min-height: 0;
  }

  .history-column {
    grid-template-rows: auto minmax(0, 1fr);
    overflow: hidden;
  }

  .history-list {
    height: 100%;
    max-height: none;
  }

  .detail-scroll {
    min-height: 0;
    max-height: 100%;
    overflow: auto;
    padding-right: 6px;
  }
}

@media (max-width: 960px) {
  .history-drawer {
    width: 100vw;
    height: 100dvh;
    border-radius: 0;
  }

  .drawer-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .drawer-actions {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .drawer-body {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .history-column {
    border-right: 0;
    border-bottom: 1px solid var(--border-soft);
  }

  .history-list {
    max-height: 30vh;
    overflow-y: auto;
  }

  .history-item {
    min-height: 0;
    padding: 9px 10px;
    gap: 4px;
  }

  .detail-scroll {
    max-height: none;
    overflow: visible;
    padding-right: 2px;
  }

  .io-block pre {
    min-height: 360px;
    max-height: 68vh;
  }
}

@media (max-width: 680px) {
  .drawer-actions {
    grid-template-columns: 1fr;
  }

  .drawer-title p,
  .drawer-status-line,
  .detail-meta,
  .review-item {
    font-size: 12px;
  }

}
</style>
