<template>
  <div class="layout">
    <header class="header">
      <h1>Edu Code Platform</h1>
      <div v-if="!isLoginPage" class="header-right">
        <nav ref="navRef" class="nav">
          <RouterLink v-if="isStudent" class="nav-rect-btn" to="/dashboard">我的主页</RouterLink>

          <template v-if="isAdmin">
            <div class="admin-nav-group">
              <RouterLink class="nav-rect-btn" to="/admin" @click="handleNavLinkClick">后台首页</RouterLink>

              <div class="nav-dropdown">
                <button
                  type="button"
                  :class="['nav-drop-trigger', openMenu === 'users' || usersGroupActive ? 'active' : '']"
                  @click.stop="toggleMenu('users')"
                >
                  用户管理
                  <span :class="['caret', openMenu === 'users' ? 'open' : '']">▾</span>
                </button>
                <div v-if="openMenu === 'users'" class="dropdown-menu">
                  <RouterLink to="/admin/users" @click="handleNavLinkClick">全部用户</RouterLink>
                  <RouterLink to="/admin/teachers" @click="handleNavLinkClick">教师管理</RouterLink>
                  <RouterLink to="/admin/admin-users" @click="handleNavLinkClick">管理员管理</RouterLink>
                </div>
              </div>

              <div class="nav-dropdown">
                <button
                  type="button"
                  :class="['nav-drop-trigger', openMenu === 'experiments' || experimentsGroupActive ? 'active' : '']"
                  @click.stop="toggleMenu('experiments')"
                >
                  实验管理
                  <span :class="['caret', openMenu === 'experiments' ? 'open' : '']">▾</span>
                </button>
                <div v-if="openMenu === 'experiments'" class="dropdown-menu">
                  <RouterLink to="/admin/experiments" @click="handleNavLinkClick">后台实验管理</RouterLink>
                  <RouterLink to="/experiments" @click="handleNavLinkClick">实验列表</RouterLink>
                </div>
              </div>

              <div class="nav-dropdown">
                <button
                  type="button"
                  :class="['nav-drop-trigger', openMenu === 'docs' || docsGroupActive ? 'active' : '']"
                  @click.stop="toggleMenu('docs')"
                >
                  文档管理
                  <span :class="['caret', openMenu === 'docs' ? 'open' : '']">▾</span>
                </button>
                <div v-if="openMenu === 'docs'" class="dropdown-menu">
                  <RouterLink to="/admin/docs" @click="handleNavLinkClick">后台文档管理</RouterLink>
                  <RouterLink to="/docs" @click="handleNavLinkClick">技术文档</RouterLink>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <RouterLink class="nav-rect-btn" to="/experiments" @click="handleNavLinkClick">实验列表</RouterLink>
            <RouterLink class="nav-rect-btn" to="/docs" @click="handleNavLinkClick">技术文档</RouterLink>
          </template>

          <RouterLink v-if="isTeacher" class="nav-rect-btn" to="/teacher/experiments" @click="handleNavLinkClick">教师看板</RouterLink>
          <RouterLink v-if="isTeacher" class="nav-rect-btn" to="/teacher/students" @click="handleNavLinkClick">学生管理</RouterLink>
        </nav>
        <div v-if="isLoggedIn" class="session-area">
          <span class="user-label">{{ userLabel }}</span>
          <RouterLink class="profile-link" to="/profile">个人中心</RouterLink>
          <button type="button" class="logout-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getAccessToken, getCurrentUserProfile, getStoredCurrentUser, logout } from "./api/auth";

const route = useRoute();
const router = useRouter();
const currentUser = ref(getStoredCurrentUser());
const hasToken = ref(Boolean(getAccessToken()));
const role = computed(() => currentUser.value?.role || "");
const isAdmin = computed(() => role.value === "admin");
const isTeacher = computed(() => role.value === "teacher");
const isStudent = computed(() => role.value === "student");
const isLoggedIn = computed(() => hasToken.value || Boolean(currentUser.value));
const isLoginPage = computed(() => route.path === "/login");
const navRef = ref(null);
const openMenu = ref("");
const usersGroupActive = computed(() => ["/admin/users", "/admin/teachers", "/admin/admin-users"].includes(route.path));
const experimentsGroupActive = computed(() => route.path === "/admin/experiments" || route.path === "/experiments");
const docsGroupActive = computed(() => route.path === "/admin/docs" || route.path === "/docs");
const userLabel = computed(() => {
  if (!currentUser.value) {
    return "";
  }
  const name = currentUser.value.full_name || currentUser.value.username || "用户";
  const roleText = currentUser.value.role === "admin" ? "管理员" : currentUser.value.role === "teacher" ? "教师" : "学生";
  const mustChangeHint = currentUser.value.must_change_password ? "，需改密" : "";
  return `${name}（${roleText}${mustChangeHint}）`;
});

async function refreshCurrentUser() {
  const token = getAccessToken();
  hasToken.value = Boolean(token);
  if (!token) {
    currentUser.value = null;
    return;
  }
  try {
    currentUser.value = await getCurrentUserProfile();
  } catch (error) {
    currentUser.value = null;
    hasToken.value = Boolean(getAccessToken());
  }
}

async function handleLogout() {
  logout();
  currentUser.value = null;
  hasToken.value = false;
  if (route.path !== "/login") {
    await router.replace("/login");
  }
}

function closeMenus() {
  openMenu.value = "";
}

function toggleMenu(menuName) {
  openMenu.value = openMenu.value === menuName ? "" : menuName;
}

function handleNavLinkClick() {
  closeMenus();
}

function handleDocumentClick(event) {
  if (!navRef.value) {
    closeMenus();
    return;
  }
  const target = event.target;
  if (!(target instanceof Node) || !navRef.value.contains(target)) {
    closeMenus();
  }
}

watch(
  () => route.fullPath,
  async () => {
    closeMenus();
    await refreshCurrentUser();
  },
);

onMounted(async () => {
  await refreshCurrentUser();
  document.addEventListener("click", handleDocumentClick);
  window.addEventListener("storage", refreshCurrentUser);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleDocumentClick);
  window.removeEventListener("storage", refreshCurrentUser);
});
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f7f8fc;
}

.header {
  padding: 16px 24px;
  border-bottom: 1px solid #e5e8f0;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.header h1 {
  margin: 0;
  font-size: 20px;
}

.nav {
  display: flex;
  gap: 14px;
  align-items: center;
  flex-wrap: wrap;
}

.nav > a {
  color: #2b5cff;
  text-decoration: none;
  padding: 6px 0;
}

.nav > a.router-link-active {
  font-weight: 600;
}

.admin-nav-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-dropdown {
  position: relative;
}

.nav-rect-btn,
.nav-drop-trigger {
  border: 1px solid #d9e2ff;
  background: #f8faff;
  color: #2b5cff;
  width: 112px;
  height: 36px;
  border-radius: 8px;
  padding: 0 10px;
  font-size: 13px;
  line-height: 36px;
  text-decoration: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-sizing: border-box;
  white-space: nowrap;
}

.nav-rect-btn {
  display: inline-flex;
}

.nav a.nav-rect-btn {
  padding: 0 10px;
}

.nav-rect-btn.router-link-active,
.nav-drop-trigger.active {
  border-color: #93c5fd;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
}

.caret {
  transition: transform 0.2s ease;
}

.caret.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 170px;
  z-index: 20;
  background: #fff;
  border: 1px solid #dbe1f1;
  border-radius: 10px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  padding: 8px;
  display: grid;
  gap: 6px;
}

.dropdown-menu a {
  color: #1f2937;
  text-decoration: none;
  padding: 7px 9px;
  border-radius: 6px;
  font-size: 13px;
}

.dropdown-menu a:hover {
  background: #f3f4f6;
}

.dropdown-menu a.router-link-active {
  font-weight: 600;
  color: #1d4ed8;
  background: #eff6ff;
}

.session-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-label {
  color: #374151;
  font-size: 13px;
}

.profile-link {
  text-decoration: none;
}

.logout-btn {
  border: 0;
  cursor: pointer;
}

.profile-link,
.logout-btn {
  border-radius: 8px;
  height: 36px;
  min-width: 92px;
  padding: 0 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  font-size: 13px;
  font-weight: 600;
  line-height: 36px;
}

.profile-link {
  background: #e0e7ff;
  color: #1d4ed8;
}

.logout-btn {
  background: #ef4444;
  color: #fff;
}

.main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
</style>
