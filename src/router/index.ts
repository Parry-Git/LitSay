import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/about",
    name: "about",
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/AboutView.vue"),
  },
  {
    path: "/upload",
    name: "upload",
    component: () =>
      import(/* webpackChunkName: "upload" */ "../views/UploadView.vue"),
  },
  // 添加新的文件夹内容路由
  {
    path: "/folder/:id",
    name: "folder-content",
    component: () =>
      import(/* webpackChunkName: "folder" */ "../views/FolderContentView.vue"),
  },
  // 文档详情页面路由
  {
    path: "/document/:id",
    name: "document-detail",
    component: () =>
      import(
        /* webpackChunkName: "document" */ "../views/DocumentDetailView.vue"
      ),
  },
  // 文档编辑页面路由
  {
    path: "/document/:id/edit",
    name: "document-edit",
    component: () =>
      import(
        /* webpackChunkName: "document-edit" */ "../views/DocumentEditView.vue"
      ),
  },
  // 添加搜索结果页面路由
  {
    path: "/search",
    name: "search-results",
    component: () =>
      import(/* webpackChunkName: "search" */ "../views/SearchResultView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
