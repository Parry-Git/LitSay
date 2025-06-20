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

        <!-- 名人名言副标题 -->
        <div class="quote-section">
          <p class="famous-quote">{{ currentQuote.text }}</p>
          <p class="quote-author">— {{ currentQuote.author }}</p>
        </div>
      </div>

      <!-- 功能介绍卡片 -->
      <div class="features-section">
        <a-row :gutter="[32, 32]" justify="center">
          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <cloud-upload-outlined class="feature-icon upload-icon" />
                </div>
              </template>
              <a-card-meta title="智能文献上传">
                <template #description>
                  支持PDF文件拖拽上传，AI自动解析元数据，包括标题、作者、期刊等关键信息
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <folder-open-outlined class="feature-icon organize-icon" />
                </div>
              </template>
              <a-card-meta title="分层文件夹管理">
                <template #description>
                  创建多级文件夹结构，按学科、主题或项目分类整理您的学术资料
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <search-outlined class="feature-icon search-icon" />
                </div>
              </template>
              <a-card-meta title="高级搜索引擎">
                <template #description>
                  全文检索、关键词筛选、作者查找，支持正则表达式和多条件组合搜索
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <star-outlined class="feature-icon rating-icon" />
                </div>
              </template>
              <a-card-meta title="文献评分与笔记">
                <template #description>
                  为重要文献打星评分，添加个人笔记，支持Markdown格式的富文本编辑
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <bar-chart-outlined class="feature-icon stats-icon" />
                </div>
              </template>
              <a-card-meta title="统计分析视图">
                <template #description>
                  可视化展示您的研究数据，包括关键词分布、作者统计等学术洞察
                </template>
              </a-card-meta>
            </a-card>
          </a-col>

          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable class="feature-card">
              <template #cover>
                <div class="feature-icon-container">
                  <book-outlined class="feature-icon reference-icon" />
                </div>
              </template>
              <a-card-meta title="参考文献生成">
                <template #description>
                  一键生成符合GB/T
                  7714-2015或APA格式的参考文献列表，导出多种格式
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

    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
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
  } else if (hour >= 14 && hour < 22) {
    return {
      text: "下午好！",
      icon: "☕",
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

// 名人名言库
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
/* 导入 Google Fonts */
@import url("https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap");

.welcome-container {
  min-height: calc(100vh - 140px);
  padding: 60px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.welcome-content {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

/* 问候部分样式 */
.greeting-section {
  text-align: center;
  margin-bottom: 80px;
}

.greeting-title {
  font-size: 4rem;
  font-weight: 600;
  margin-bottom: 32px;
  color: #ffffff;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  line-height: 1.2;
}

.greeting-text,
.username {
  margin-right: 16px;
}

.greeting-icon {
  font-size: 4.5rem;
  margin: 0 16px;
  display: inline-block;
  animation: bounce 2s infinite;
}

.username {
  color: #ffd700;
  font-weight: 700;
}

/* 名言部分样式 */
.quote-section {
  margin-top: 40px;
}

.famous-quote {
  font-family: "EB Garamond", serif;
  font-size: 1.8rem;
  color: #f8f9fa;
  margin-bottom: 12px;
  line-height: 1.6;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.quote-author {
  font-family: "EB Garamond", serif;
  font-size: 1.2rem;
  color: #e9ecef;
  font-weight: 500;
}

/* 功能卡片样式 */
.features-section {
  margin-bottom: 80px;
}

.feature-card {
  height: 100%;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transition: all 0.3s ease;
  border: none;
  background: #ffffff;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.16);
}

.feature-icon-container {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 16px 16px 0 0;
}

.feature-icon {
  font-size: 3rem;
  color: #ffffff;
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

/* 不同功能图标的特色配色 */
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

.feature-card .feature-icon-container {
  background: linear-gradient(
    135deg,
    var(--icon-color, #667eea) 0%,
    var(--icon-color-end, #764ba2) 100%
  );
}

/* CTA 部分样式 */
.cta-section {
  text-align: center;
}

.get-started-btn {
  font-size: 1.4rem;
  height: 64px;
  padding: 0 48px;
  border-radius: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  font-weight: 600;
}

.get-started-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.cta-subtitle {
  margin-top: 16px;
  font-size: 1.1rem;
  color: #f8f9fa;
  opacity: 0.9;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

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
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-container {
    padding: 40px 16px;
  }

  .greeting-title {
    font-size: 2.5rem;
  }

  .greeting-icon {
    font-size: 3rem;
  }

  .famous-quote {
    font-size: 1.4rem;
  }

  .quote-author {
    font-size: 1rem;
  }

  .get-started-btn {
    font-size: 1.2rem;
    height: 56px;
    padding: 0 32px;
  }

  .features-section {
    margin-bottom: 60px;
  }
}

@media (max-width: 480px) {
  .greeting-title {
    font-size: 2rem;
  }

  .greeting-icon {
    font-size: 2.5rem;
  }

  .famous-quote {
    font-size: 1.2rem;
  }

  .feature-icon-container {
    height: 100px;
  }

  .feature-icon {
    font-size: 2.5rem;
  }
}

/* Ant Design 样式覆盖 */
:deep(.ant-card-meta-title) {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
}

:deep(.ant-card-meta-description) {
  font-size: 1rem;
  line-height: 1.6;
  color: #5a6c7d;
}

:deep(.ant-card-body) {
  padding: 24px;
}
</style>
