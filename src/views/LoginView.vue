<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-header">
        <img src="@/assets/logo3.png" alt="Logo" class="logo" />
        <h1 class="title">文献一言</h1>
        <h2 class="head2">在线智能文献管理系统</h2>
      </div>

      <a-card class="login-card">
        <a-tabs v-model:activeKey="activeKey" centered>
          <a-tab-pane key="login" tab="登录">
            <a-form
              :model="loginForm"
              :rules="loginRules"
              ref="loginFormRef"
              @finish="handleLogin"
              layout="vertical"
            >
              <a-form-item name="username" label="用户名">
                <a-input
                  v-model:value="loginForm.username"
                  placeholder="请输入用户名"
                  size="large"
                >
                  <template #prefix>
                    <user-outlined />
                  </template>
                </a-input>
              </a-form-item>

              <a-form-item name="password" label="密码">
                <a-input-password
                  v-model:value="loginForm.password"
                  placeholder="请输入密码"
                  size="large"
                >
                  <template #prefix>
                    <lock-outlined />
                  </template>
                </a-input-password>
              </a-form-item>

              <a-form-item>
                <a-checkbox v-model:checked="loginForm.remember"
                  >记住我</a-checkbox
                >
              </a-form-item>

              <a-form-item>
                <a-button
                  type="primary"
                  html-type="submit"
                  size="large"
                  block
                  :loading="loading"
                >
                  登录
                </a-button>
              </a-form-item>

              <div class="form-footer">
                还没有账号？
                <a @click="activeKey = 'register'">立即注册</a>
              </div>
            </a-form>
          </a-tab-pane>

          <a-tab-pane key="register" tab="注册">
            <a-form
              :model="registerForm"
              :rules="registerRules"
              ref="registerFormRef"
              @finish="handleRegister"
              layout="vertical"
            >
              <a-form-item name="username" label="用户名">
                <a-input
                  v-model:value="registerForm.username"
                  placeholder="请设置用户名"
                  size="large"
                >
                  <template #prefix>
                    <user-outlined />
                  </template>
                </a-input>
              </a-form-item>

              <a-form-item name="password" label="密码">
                <a-input-password
                  v-model:value="registerForm.password"
                  placeholder="请设置密码"
                  size="large"
                >
                  <template #prefix>
                    <lock-outlined />
                  </template>
                </a-input-password>
              </a-form-item>

              <a-form-item name="confirmPassword" label="确认密码">
                <a-input-password
                  v-model:value="registerForm.confirmPassword"
                  placeholder="请确认密码"
                  size="large"
                >
                  <template #prefix>
                    <lock-outlined />
                  </template>
                </a-input-password>
              </a-form-item>

              <a-form-item>
                <a-button
                  type="primary"
                  html-type="submit"
                  size="large"
                  block
                  :loading="loading"
                >
                  注册
                </a-button>
              </a-form-item>

              <div class="form-footer">
                已有账号？
                <a @click="activeKey = 'login'">立即登录</a>
              </div>
            </a-form>
          </a-tab-pane>
        </a-tabs>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { message } from "ant-design-vue";
import {
  UserOutlined,
  LockOutlined,
  CrownOutlined,
} from "@ant-design/icons-vue";
import { login, register } from "@/api/auth";

const router = useRouter();
const route = useRoute();
const activeKey = ref("login");
const loading = ref(false);

// 判断是否为开发环境
const isDev = computed(() => {
  return process.env.NODE_ENV === "development";
});

// 登录表单
const loginFormRef = ref();
const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

// 注册表单
const registerFormRef = ref();
const registerForm = reactive({
  username: "",
  password: "",
  confirmPassword: "",
});

// 登录表单验证规则
const loginRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, message: "用户名不能少于3个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码不能少于6个字符", trigger: "blur" },
  ],
};

// 注册表单验证规则
const registerRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, message: "用户名不能少于3个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码不能少于6个字符", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码", trigger: "blur" },
    {
      validator: (rule: any, value: string) => {
        if (!value || registerForm.password === value) {
          return Promise.resolve();
        }
        return Promise.reject("两次输入的密码不一致");
      },
      trigger: "blur",
    },
  ],
};

// 登录方法
const handleLogin = async () => {
  try {
    loading.value = true;

    // 在开发环境中，如果使用管理员账号，直接模拟登录成功
    if (
      isDev.value &&
      loginForm.username === "admin" &&
      loginForm.password === "admin123"
    ) {
      // 模拟存储token
      localStorage.setItem("token", "admin-mock-token");
      localStorage.setItem(
        "userInfo",
        JSON.stringify({
          username: "admin",
          role: "admin",
          id: "1",
        })
      );

      message.success("管理员登录成功");

      // 如果有重定向参数，跳转到对应页面，否则跳转到首页
      const redirectPath = (route.query.redirect as string) || "/";
      router.push(redirectPath);
      return;
    }

    // 正常登录流程
    const response = await login(loginForm.username, loginForm.password);
    // console.log("登录响应数据:", response); // 打印响应数据，方便调试

    // 确保 localStorage 中存储了 token 和用户信息
    const token = response.token || response.data?.token;
    const userData = response.user || response.data?.user;

    if (token) {
      localStorage.setItem("token", token);
      // console.log("Token 已存储:", token);
    }

    if (userData) {
      localStorage.setItem("userInfo", JSON.stringify(userData));
      // console.log("用户信息已存储:", userData);
    }

    message.success("登录成功");

    // 登录成功后将用户重定向到首页或指定页面
    const redirectPath = (route.query.redirect as string) || "/";
    console.log("重定向到:", redirectPath);
    router.push(redirectPath);
  } catch (error: any) {
    message.error(error.message || "登录失败，请重试");
    console.error("登录错误详情:", error);
  } finally {
    loading.value = false;
  }
};

// 注册方法
const handleRegister = async () => {
  try {
    loading.value = true;
    const response = await register(
      registerForm.username,
      registerForm.password
    );
    message.success("注册成功，请登录");

    // 注册成功后切换到登录页
    activeKey.value = "login";
    // 自动填充用户名到登录表单
    loginForm.username = registerForm.username;
    // 清空注册表单
    registerForm.password = "";
    registerForm.confirmPassword = "";
  } catch (error: any) {
    message.error(error.message || "注册失败，请重试");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  background-image: url("https://gw.alipayobjects.com/zos/rmsportal/TVYTbAXWheQpRcWDaDMu.svg");
  background-repeat: no-repeat;
  background-position: center 110px;
  background-size: 100%;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
  padding: 0 16px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  height: 44px;
  margin-bottom: 16px;
}

.title {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  font-size: 39px;
}

.head2 {
  color: rgba(0, 0, 0, 0.45);
  font-size: 18px;
  margin-bottom: 24px;
}

.login-card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.forget-link {
  float: right;
}

.form-footer {
  text-align: center;
  margin-top: 16px;
}

:deep(.ant-tabs-nav::before) {
  border-bottom: none !important;
}

/* 开发环境信息样式 */
.dev-info {
  margin-top: 20px;
  opacity: 0.8;
}
</style>
