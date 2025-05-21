import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: { requiresAuth: true }, // 需要认证
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    meta: {
      guest: true, // 游客可访问
      fullScreen: true, // 设置为全屏页面 - 不使用AppLayout
    },
  },
  {
    path: "/about",
    name: "about",
    component: () => import("../views/AboutView.vue"),
    meta: { requiresAuth: true }, // 需要认证
  },
  {
    path: "/upload",
    name: "upload",
    component: () => import("../views/UploadView.vue"),
    meta: { requiresAuth: true }, // 需要认证
  },
  // 添加新的文件夹内容路由
  {
    path: "/folder/:id",
    name: "folder-content",
    component: () => import("../views/FolderContentView.vue"),
    meta: { requiresAuth: true }, // 需要认证
  },
  // 文档详情页面路由
  {
    path: "/document/:id",
    name: "document-detail",
    component: () => import("../views/DocumentDetailView.vue"),
    meta: { requiresAuth: true }, // 需要认证
  },
  // 文档编辑页面路由
  {
    path: "/document/:id/edit",
    name: "document-edit",
    component: () => import("../views/DocumentEditView.vue"),
    meta: { requiresAuth: true }, // 需要认证
  },
  // 添加搜索结果页面路由
  {
    path: "/search",
    name: "search-results",
    component: () => import("../views/SearchResultView.vue"),
    meta: { requiresAuth: true }, // 需要认证
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// 添加路由守卫
router.beforeEach((to, from, next) => {
  console.log("Navigating to:", to.path);
  console.log("From:", from.path);
  console.log("require or not:", to.meta.requiresAuth);
  const isAuthenticated = !!localStorage.getItem("token");

  console.log("Token:", localStorage.getItem("token"));

  console.log("Is authenticated:", isAuthenticated);

  // 需要登录但未登录时重定向到登录页
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({
      path: "/login",
      query: { redirect: to.fullPath },
    });
  }
  // 已登录用户访问登录页，重定向到首页
  else if (to.meta.guest && isAuthenticated) {
    next("/");
  }
  // 其他正常访问
  else {
    next();
  }
});

export default router;
