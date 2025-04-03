<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-left">
        <img src="@/assets/logo.png" alt="Drive Logo" class="logo" />
        <span class="logo-text">文献管理</span>
      </div>
      <div class="header-center">
        <el-input
          v-model="searchQuery"
          placeholder="Search in Drive"
          prefix-icon="Search"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="header-right">
        <el-tooltip content="Settings" placement="bottom">
          <el-button circle>
            <el-icon><Setting /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="Apps" placement="bottom">
          <el-button circle>
            <el-icon><Grid /></el-icon>
          </el-button>
        </el-tooltip>
        <el-avatar :size="32" class="user-avatar">U</el-avatar>
      </div>
    </header>

    <!-- 主内容区域 -->
    <div class="app-main">
      <!-- 侧边栏导航 -->
      <aside class="app-sidebar">
        <div class="new-button-container">
          <el-button type="primary" class="new-button">
            <el-icon><Plus /></el-icon>
            New
          </el-button>
        </div>

        <!-- 文件夹树形导航 -->
        <FolderTree class="folder-tree" />

        <!-- 快捷导航菜单 -->
        <div class="quick-links">
          <el-menu default-active="1" class="sidebar-menu">
            <el-menu-item index="3">
              <el-icon><Monitor /></el-icon>
              <span>Computers</span>
            </el-menu-item>
            <el-menu-item index="4">
              <el-icon><Share /></el-icon>
              <span>Shared with me</span>
            </el-menu-item>
            <el-menu-item index="5">
              <el-icon><Clock /></el-icon>
              <span>Recent</span>
            </el-menu-item>
            <el-menu-item index="6">
              <el-icon><Star /></el-icon>
              <span>Starred</span>
            </el-menu-item>
          </el-menu>
        </div>
      </aside>

      <!-- 内容区域 -->
      <main class="app-content">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  Search,
  Setting,
  Grid,
  Plus,
  Monitor,
  Share,
  Clock,
  Star,
} from "@element-plus/icons-vue";
import FolderTree from "@/components/FolderTree.vue";

const searchQuery = ref("");
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #e0e0e0;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  width: 240px;
}

.logo {
  height: 40px;
  width: 40px;
}

.logo-text {
  font-size: 22px;
  font-weight: 500;
  margin-left: 8px;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.search-input {
  width: 60%;
  max-width: 720px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  cursor: pointer;
  background-color: #4285f4;
  color: white;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  width: 240px;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  padding-top: 16px;
}

.new-button-container {
  padding: 0 16px 16px 16px;
}

.new-button {
  width: 100%;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.sidebar-menu {
  border-right: none;
}

.folder-tree {
  margin-bottom: 16px;
}

.quick-links {
  border-top: 1px solid #e0e0e0;
  padding-top: 8px;
}

.app-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.el-menu-item {
  height: 40px;
  line-height: 40px;
}
</style>
