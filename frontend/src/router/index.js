import { createRouter, createWebHistory } from "vue-router";
import { getAccessToken, getStoredCurrentUser, restoreSession } from "../api/auth";
import ExperimentListView from "../views/ExperimentListView.vue";
import CodeEditorView from "../views/CodeEditorView.vue";
import DocsView from "../views/DocsView.vue";
import TeacherExperimentOverviewView from "../views/TeacherExperimentOverviewView.vue";
import TeacherExperimentDetailView from "../views/TeacherExperimentDetailView.vue";
import TeacherStudentImportView from "../views/TeacherStudentImportView.vue";
import TeacherStudentManageView from "../views/TeacherStudentManageView.vue";
import LoginView from "../views/LoginView.vue";
import ChangePasswordView from "../views/ChangePasswordView.vue";
import ProfileView from "../views/ProfileView.vue";
import StudentDashboardView from "../views/StudentDashboardView.vue";
import AdminOverviewView from "../views/AdminOverviewView.vue";
import AdminUsersView from "../views/AdminUsersView.vue";
import AdminTeachersView from "../views/AdminTeachersView.vue";
import AdminAdminUsersView from "../views/AdminAdminUsersView.vue";
import AdminDocsView from "../views/AdminDocsView.vue";
import AdminExperimentsView from "../views/AdminExperimentsView.vue";
import AdminExperimentFormView from "../views/AdminExperimentFormView.vue";
import GuidedTemplateExperimentView from "../views/GuidedTemplateExperimentView.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: "/",
    redirect: "/experiments",
  },
  {
    path: "/experiments",
    name: "experiments",
    component: ExperimentListView,
    meta: { requiresAuth: true },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: StudentDashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: "/editor",
    name: "editor",
    component: CodeEditorView,
    meta: { requiresAuth: true },
  },
  {
    path: "/guided-experiment",
    name: "guided-experiment",
    component: GuidedTemplateExperimentView,
    meta: { requiresAuth: true },
  },
  {
    path: "/docs",
    name: "docs",
    component: DocsView,
    meta: { requiresAuth: true },
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: "/change-password",
    name: "change-password",
    component: ChangePasswordView,
    meta: { requiresAuth: true, allowWhenMustChange: true },
  },
  {
    path: "/teacher/experiments",
    name: "teacher-experiments",
    component: TeacherExperimentOverviewView,
    meta: { requiresAuth: true, requiresTeacher: true },
  },
  {
    path: "/teacher/experiment-detail",
    name: "teacher-experiment-detail",
    component: TeacherExperimentDetailView,
    meta: { requiresAuth: true, requiresTeacher: true },
  },
  {
    path: "/teacher/student-import",
    name: "teacher-student-import",
    component: TeacherStudentImportView,
    meta: { requiresAuth: true, requiresTeacher: true },
  },
  {
    path: "/teacher/students",
    name: "teacher-students",
    component: TeacherStudentManageView,
    meta: { requiresAuth: true, requiresTeacher: true },
  },
  {
    path: "/admin",
    name: "admin-overview",
    component: AdminOverviewView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/users",
    name: "admin-users",
    component: AdminUsersView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/teachers",
    name: "admin-teachers",
    component: AdminTeachersView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/docs",
    name: "admin-docs",
    component: AdminDocsView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/experiments",
    name: "admin-experiments",
    component: AdminExperimentsView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/experiments/new",
    name: "admin-experiment-new",
    component: AdminExperimentFormView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/experiments/:id/edit",
    name: "admin-experiment-edit",
    component: AdminExperimentFormView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/admin-users",
    name: "admin-admin-users",
    component: AdminAdminUsersView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { left: 0, top: 0 };
  },
});

let hasSessionBootstrapped = false;

function resolveDefaultHome(user) {
  if (user?.must_change_password) {
    return "/change-password";
  }
  const role = user?.role || "";
  if (role === "admin") {
    return "/admin";
  }
  return role === "teacher" ? "/teacher/experiments" : "/dashboard";
}

function normalizeRedirectTarget(target) {
  if (typeof target !== "string") {
    return "";
  }
  if (!target.startsWith("/") || target.startsWith("/login")) {
    return "";
  }
  return target;
}

router.beforeEach(async (to) => {
  const token = getAccessToken();

  const ensureSessionUser = async () => {
    if (!token) {
      return null;
    }
    if (!hasSessionBootstrapped) {
      hasSessionBootstrapped = true;
      return await restoreSession();
    }
    return getStoredCurrentUser() || (await restoreSession());
  };

  if (to.meta.guestOnly) {
    if (!token) {
      return true;
    }
    const user = await ensureSessionUser();
    if (!user) {
      return true;
    }
    const redirectTarget = normalizeRedirectTarget(to.query.redirect);
    if (user.must_change_password) {
      return "/change-password";
    }
    return redirectTarget || resolveDefaultHome(user);
  }

  if (!to.meta.requiresAuth) {
    return true;
  }

  if (!token) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  const currentUser = await ensureSessionUser();
  if (!currentUser) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (currentUser.must_change_password && !to.meta.allowWhenMustChange) {
    return { path: "/change-password" };
  }

  if (to.meta.requiresTeacher && currentUser.role !== "teacher") {
    return { path: resolveDefaultHome(currentUser) };
  }

  if (to.meta.requiresAdmin && currentUser.role !== "admin") {
    return { path: resolveDefaultHome(currentUser) };
  }

  return true;
});

export default router;
