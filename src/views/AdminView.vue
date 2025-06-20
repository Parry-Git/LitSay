<template>
  <div class="admin-container">
    <a-page-header
      title="用户管理"
      sub-title="管理系统用户"
      :back-icon="false"
    />

    <a-alert
      v-if="errorMsg"
      :message="errorMsg"
      type="error"
      show-icon
      class="admin-alert"
      closable
      @close="errorMsg = ''"
    />

    <a-alert
      v-if="successMsg"
      :message="successMsg"
      type="success"
      show-icon
      class="admin-alert"
      closable
      @close="successMsg = ''"
    />

    <a-card class="admin-card">
      <template #title>
        <div class="card-title-with-actions">
          <span>用户列表</span>
          <a-button type="primary" @click="fetchUsers">
            <template #icon><reload-outlined /></template>
            刷新
          </a-button>
        </div>
      </template>

      <a-spin :spinning="loading">
        <a-table
          :dataSource="users"
          :columns="columns"
          :pagination="{ pageSize: 10 }"
          :scroll="{ x: 800 }"
          rowKey="user_id"
        >
          <!-- 角色列 -->
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'role'">
              <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
                {{ record.role === "admin" ? "管理员" : "普通用户" }}
              </a-tag>
            </template>

            <!-- 操作列 -->
            <template v-else-if="column.dataIndex === 'actions'">
              <a-space>
                <!-- 角色切换按钮 -->
                <a-button
                  v-if="record.role !== 'admin' || currentUserRole === 'admin'"
                  :type="record.role === 'admin' ? 'danger' : 'primary'"
                  :disabled="record.user_id === currentUserId"
                  @click="toggleUserRole(record)"
                  size="small"
                >
                  {{
                    record.role === "admin" ? "降级为普通用户" : "升级为管理员"
                  }}
                </a-button>

                <!-- 删除按钮 -->
                <a-popconfirm
                  title="确定要删除此用户吗？"
                  description="删除后将无法恢复，所有相关数据都将被删除"
                  ok-text="确定"
                  cancel-text="取消"
                  @confirm="deleteUser(record.user_id)"
                >
                  <a-button
                    danger
                    size="small"
                    :disabled="
                      record.user_id === currentUserId ||
                      record.role === 'admin'
                    "
                  >
                    <template #icon><delete-outlined /></template>
                    删除
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { message } from "ant-design-vue";
import {
  UserOutlined,
  ReloadOutlined,
  DeleteOutlined,
} from "@ant-design/icons-vue";
import { getAllUsers, updateUserRole, deleteUserAccount } from "@/api/admin";

// 状态变量
const loading = ref(false);
const users = ref<any[]>([]);
const errorMsg = ref("");
const successMsg = ref("");

// 获取当前用户信息
const userInfo = JSON.parse(localStorage.getItem("userInfo") || "{}");
const currentUserId = userInfo.id;
const currentUserRole = userInfo.role;

// 表格列定义
const columns = [
  {
    title: "用户ID",
    dataIndex: "user_id",
    key: "user_id",
    width: 100,
  },
  {
    title: "用户名",
    dataIndex: "username",
    key: "username",
    width: 150,
  },
  {
    title: "角色",
    dataIndex: "role",
    key: "role",
    width: 100,
    filters: [
      { text: "管理员", value: "admin" },
      { text: "普通用户", value: "user" },
    ],
    onFilter: (value: string, record: any) => record.role === value,
  },
  {
    title: "操作",
    dataIndex: "actions",
    key: "actions",
    fixed: "right",
    width: 240,
  },
];

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return "-";
  try {
    const date = new Date(dateString);
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (e) {
    return dateString;
  }
};

// 获取所有用户
const fetchUsers = async () => {
  loading.value = true;
  errorMsg.value = "";
  successMsg.value = "";

  try {
    const response = await getAllUsers();
    if (response.data.code === 0) {
      users.value = response.data.data;
    } else {
      errorMsg.value = response.data.message || "获取用户列表失败";
    }
  } catch (error) {
    console.error("获取用户列表错误:", error);
    errorMsg.value = "无法加载用户列表，请检查网络连接";
  } finally {
    loading.value = false;
  }
};

// 切换用户角色
const toggleUserRole = async (user: any) => {
  const newRole = user.role === "admin" ? "user" : "admin";
  const actionText = user.role === "admin" ? "降级为普通用户" : "升级为管理员";

  try {
    const response = await updateUserRole(user.user_id, newRole);
    if (response.data.code === 0) {
      successMsg.value = `已将用户 ${user.username} ${actionText}`;
      fetchUsers(); // 刷新用户列表
    } else {
      errorMsg.value = response.data.message || "更新用户角色失败";
    }
  } catch (error) {
    console.error("更新用户角色错误:", error);
    errorMsg.value = "无法更新用户角色，请检查网络连接";
  }
};

// 删除用户
const deleteUser = async (userId: number) => {
  try {
    const response = await deleteUserAccount(userId);
    if (response.data.code === 0) {
      successMsg.value = "用户已成功删除";
      fetchUsers(); // 刷新用户列表
    } else {
      errorMsg.value = response.data.message || "删除用户失败";
    }
  } catch (error) {
    console.error("删除用户错误:", error);
    errorMsg.value = "无法删除用户，请检查网络连接";
  }
};

// 组件挂载时获取用户列表
onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.admin-container {
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-alert {
  margin-bottom: 16px;
}

.admin-card {
  margin-bottom: 24px;
}

.card-title-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

:deep(.ant-table-column-sorter) {
  margin-left: 4px;
}

:deep(.ant-tag) {
  margin-right: 0;
}
</style>
