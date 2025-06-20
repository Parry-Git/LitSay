import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import HomeView from "../views/HomeView.vue";
import { ElMessage } from "element-plus";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: () => import("../views/WelcomeView.vue"),
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
  // 添加统计页面路由
  {
    path: "/stats",
    name: "stats",
    component: () => import("../views/StatsView.vue"),
    meta: {
      requiresAuth: true, // 需要认证
      title: "统计分析",
    },
  },
  {
    path: "/author/:id",
    name: "AuthorDetail",
    component: () => import("../views/AuthorDetailView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/institution/:id",
    name: "InstitutionDetail",
    component: () => import("../views/InstitutionDetailView.vue"),
    meta: { requiresAuth: true },
  },
  // 添加期刊详情页路由
  {
    path: "/journal/:id",
    name: "JournalDetail",
    component: () => import("../views/JournalDetailView.vue"),
    meta: { requiresAuth: true },
  },
  // 添加会议详情页路由
  {
    path: "/conference/:id",
    name: "ConferenceDetail",
    component: () => import("../views/ConferenceDetailView.vue"),
    meta: { requiresAuth: true },
  },
  // 添加用户管理页面路由
  {
    path: "/admin",
    name: "admin",
    component: () => import("../views/AdminView.vue"),
    meta: {
      requiresAuth: true,
      requiresAdmin: true, // 添加管理员权限要求
    },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// 修改路由守卫，增加管理员验证
router.beforeEach((to, from, next) => {
  // console.log("Navigating to:", to.path);
  const isAuthenticated = !!localStorage.getItem("token");

  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin) {
    const userInfo = localStorage.getItem("userInfo");
    const isAdmin = userInfo ? JSON.parse(userInfo).role : false;

    if (!isAdmin) {
      // 不是管理员，重定向到首页
      ElMessage.error("您没有访问此页面的权限");
      next("/");
      return;
    }
  }

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
