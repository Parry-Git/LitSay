<template>
  <div class="welcome-container">
    <!-- 主要内容区域 -->
    <div class="welcome-content">
      <!-- 问候标题 -->
      <div class="greeting-section">
        <h1 class="greeting-title">
          <span class="greeting-text">{{ greetingText }}</span>
          <span class="greeting-icon">{{ greetingIcon }}</span>
          <span class="username">{{ currentUser }}</span>
        </h1>

        <!-- 副标题 -->
        <div class="quote-section">
          <p class="famous-quote">{{ currentQuote.text }}</p>
          <p class="quote-author">— {{ currentQuote.author }}</p>
        </div>
      </div>

      <!-- 功能介绍卡片 -->
      <div class="features-section">
        <a-row :gutter="[24, 24]" justify="center">
          <a-col :xs="12" :sm="8" :lg="6">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <cloud-upload-outlined class="feature-icon upload-icon" />
                </div>
              </template>
              <a-card-meta title="智能文献上传">
                <template #description>
                  支持PDF文件拖拽上传，AI自动解析元数据
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="12" :sm="8" :lg="6">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <folder-open-outlined class="feature-icon organize-icon" />
                </div>
              </template>
              <a-card-meta title="分层文件夹管理">
                <template #description>
                  创建多级文件夹结构，按学科分类整理
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="12" :sm="8" :lg="6">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <search-outlined class="feature-icon search-icon" />
                </div>
              </template>
              <a-card-meta title="高级搜索引擎">
                <template #description>
                  全文检索、关键词筛选、正则表达式搜索
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="12" :sm="8" :lg="6">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <star-outlined class="feature-icon rating-icon" />
                </div>
              </template>
              <a-card-meta title="文献评分与笔记">
                <template #description>
                  打星评分，添加Markdown格式笔记
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="12" :sm="8" :lg="6">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <bar-chart-outlined class="feature-icon stats-icon" />
                </div>
              </template>
              <a-card-meta title="统计分析视图">
                <template #description>
                  可视化展示研究数据和关键词分布
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="12" :sm="8" :lg="6">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <book-outlined class="feature-icon reference-icon" />
                </div>
              </template>
              <a-card-meta title="参考文献生成">
                <template #description>
                  一键生成GB/T 7714或APA格式参考文献
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
        </a-row>
      </div>

      <!-- Get Started 按钮 -->
      <div class="cta-section">
        <a-button
          type="primary"
          size="large"
          class="get-started-btn"
          @click="goToUpload"
        >
          <template #icon>
            <rocket-outlined />
          </template>
          Get Started!
        </a-button>
        <p class="cta-subtitle">开始构建您的学术知识库</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  CloudUploadOutlined,
  FolderOpenOutlined,
  SearchOutlined,
  StarOutlined,
  BarChartOutlined,
  BookOutlined,
  RocketOutlined,
} from "@ant-design/icons-vue";

const router = useRouter();

// 当前用户信息
const currentUser = ref("");

// 获取当前用户名
const getCurrentUser = () => {
  const userInfo = localStorage.getItem("userInfo");
  if (userInfo) {
    try {
      const parsedInfo = JSON.parse(userInfo);
      currentUser.value = parsedInfo.username || "用户";
    } catch (e) {
      currentUser.value = "用户";
    }
  } else {
    currentUser.value = "用户";
  }
};

// 问候语和图标
const greetingData = computed(() => {
  const hour = new Date().getHours();

  if (hour >= 5 && hour < 12) {
    return {
      text: "早上好！",
      icon: "☀️",
    };
  } else if (hour >= 12 && hour < 14) {
    return {
      text: "中午好！",
      icon: "🌈",
    };
  } else if (hour >= 14 && hour < 19) {
    return {
      text: "下午好！",
      icon: "☕",
    };
  } else if (hour >= 19 && hour < 22) {
    return {
      text: "晚上好！",
      icon: "🌆",
    };
  } else {
    return {
      text: "夜深了...",
      icon: "🌙",
    };
  }
});

const greetingText = computed(() => greetingData.value.text);
const greetingIcon = computed(() => greetingData.value.icon);

const famousQuotes = [
  {
    text: "The only way to do great work is to love what you do.",
    author: "Steve Jobs",
  },
  {
    text: "Innovation distinguishes between a leader and a follower.",
    author: "Steve Jobs",
  },
  {
    text: "Knowledge is power. Information is liberating.",
    author: "Kofi Annan",
  },
  {
    text: "The beautiful thing about learning is that no one can take it away from you.",
    author: "B.B. King",
  },
  {
    text: "Education is the most powerful weapon which you can use to change the world.",
    author: "Nelson Mandela",
  },
  {
    text: "The future belongs to those who believe in the beauty of their dreams.",
    author: "Eleanor Roosevelt",
  },
  {
    text: "It is during our darkest moments that we must focus to see the light.",
    author: "Aristotle",
  },
  {
    text: "The way to get started is to quit talking and begin doing.",
    author: "Walt Disney",
  },
  {
    text: "Don't be afraid to give up the good to go for the great.",
    author: "John D. Rockefeller",
  },
  {
    text: "If you look at what you have in life, you'll always have more.",
    author: "Oprah Winfrey",
  },
];

// 随机选择名言
const currentQuote = ref(famousQuotes[0]);

const selectRandomQuote = () => {
  const randomIndex = Math.floor(Math.random() * famousQuotes.length);
  currentQuote.value = famousQuotes[randomIndex];
};

// 跳转到上传页面
const goToUpload = () => {
  router.push("/upload");
};

// 组件挂载时执行
onMounted(() => {
  getCurrentUser();
  selectRandomQuote();
});
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap");

.welcome-container {
  min-height: calc(100vh - 140px);
  padding: 40px 24px;
  background: #ffffff;
  position: relative;
  overflow: hidden;
}

.welcome-content {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.greeting-section {
  text-align: center;
  margin-bottom: 60px;
}

.greeting-title {
  font-size: 3.5rem;
  font-weight: 600;
  margin-bottom: 32px;
  color: #2c3e50;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
}

.greeting-text,
.username {
  margin-right: 16px;
}

.greeting-icon {
  font-size: 4rem;
  margin: 0 16px;
  display: inline-block;
  animation: bounce 2s infinite;
}

.username {
  color: #667eea; /* 调整为主题色 */
  font-weight: 700;
}

.quote-section {
  margin-top: 40px;
}

.famous-quote {
  font-family: "EB Garamond", serif;
  font-size: 1.6rem;
  font-style: italic;
  color: #5a6c7d;
  margin-bottom: 12px;
  line-height: 1.6;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.quote-author {
  font-family: "EB Garamond", serif;
  font-size: 1.1rem;
  color: #8492a6;
  font-weight: 500;
}

.features-section {
  margin-bottom: 60px;
}

.feature-card {
  height: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* 减轻阴影 */
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  background: #ffffff;
}

.feature-card:hover {
  transform: translateY(-4px); /* 减小悬浮效果 */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.feature-icon-container {
  height: 80px; /* 减小高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    #f8f9ff 0%,
    #e6f7ff 100%
  ); /* 调整为浅色渐变 */
  border-radius: 12px 12px 0 0;
}

.feature-icon {
  font-size: 2rem; /* 减小图标尺寸 */
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

/* 不同功能图标的特色配色 - 调整为适应白色背景的颜色 */
.upload-icon {
  color: #4facfe !important;
}

.organize-icon {
  color: #43e97b !important;
}

.search-icon {
  color: #fa709a !important;
}

.rating-icon {
  color: #ffa726 !important;
}

.stats-icon {
  color: #ab47bc !important;
}

.reference-icon {
  color: #26c6da !important;
}

/* CTA 部分样式 */
.cta-section {
  text-align: center;
}

.get-started-btn {
  font-size: 1.3rem;
  height: 56px; /* 稍微减小按钮高度 */
  padding: 0 40px;
  border-radius: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3); /* 减轻阴影 */
  transition: all 0.3s ease;
  font-weight: 600;
}

.get-started-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.cta-subtitle {
  margin-top: 16px;
  font-size: 1rem;
  color: #5a6c7d; /* 调整为深灰色 */
  opacity: 0.8;
}

/* 移除背景装饰元素，因为现在是纯白背景 */

/* 动画效果 */
@keyframes bounce {
  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px); /* 减小动画幅度 */
  }
  60% {
    transform: translateY(-4px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-container {
    padding: 30px 16px;
  }

  .greeting-title {
    font-size: 2.2rem;
  }

  .greeting-icon {
    font-size: 2.8rem;
  }

  .famous-quote {
    font-size: 1.3rem;
  }

  .quote-author {
    font-size: 1rem;
  }

  .get-started-btn {
    font-size: 1.1rem;
    height: 48px;
    padding: 0 28px;
  }

  .features-section {
    margin-bottom: 40px;
  }

  .feature-icon-container {
    height: 70px;
  }

  .feature-icon {
    font-size: 1.8rem;
  }
}

@media (max-width: 480px) {
  .greeting-title {
    font-size: 1.8rem;
  }

  .greeting-icon {
    font-size: 2.2rem;
  }

  .famous-quote {
    font-size: 1.1rem;
  }

  .feature-icon-container {
    height: 60px;
  }

  .feature-icon {
    font-size: 1.6rem;
  }
}

:deep(.ant-card-meta-title) {
  font-size: 1.1rem; /* 减小标题字体 */
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

:deep(.ant-card-meta-description) {
  font-size: 0.9rem; /* 减小描述字体 */
  line-height: 1.5;
  color: #5a6c7d;
}

:deep(.ant-card-body) {
  padding: 16px; /* 减小内边距 */
}
</style>
