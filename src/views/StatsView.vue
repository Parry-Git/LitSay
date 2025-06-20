<template>
  <div class="stats-container">
    <a-row :gutter="16">
      <a-col :span="24">
        <a-page-header
          title="统计分析"
          sub-title="文献管理系统数据概览"
          :backIcon="false"
        />
      </a-col>
    </a-row>

    <!-- 加载状态 -->
    <a-spin :spinning="loading" tip="数据加载中...">
      <!-- 基本数据统计卡片 -->
      <a-row :gutter="16" style="margin-bottom: 16px">
        <a-col :xs="24" :sm="8">
          <a-card hoverable>
            <template #cover>
              <div
                class="stats-card-icon-wrapper"
                style="background-color: #e6f7ff"
              >
                <book-outlined class="stats-card-icon" style="color: #1890ff" />
              </div>
            </template>
            <a-card-meta title="文献总数">
              <template #description>
                <div class="stats-number">
                  {{ overviewData.documentsCount || 0 }}
                </div>
              </template>
            </a-card-meta>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="8">
          <a-card hoverable>
            <template #cover>
              <div
                class="stats-card-icon-wrapper"
                style="background-color: #f6ffed"
              >
                <folder-outlined
                  class="stats-card-icon"
                  style="color: #52c41a"
                />
              </div>
            </template>
            <a-card-meta title="文件夹数量">
              <template #description>
                <div class="stats-number">
                  {{ overviewData.foldersCount || 0 }}
                </div>
              </template>
            </a-card-meta>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="8">
          <a-card hoverable>
            <template #cover>
              <div
                class="stats-card-icon-wrapper"
                style="background-color: #fff2e8"
              >
                <user-outlined class="stats-card-icon" style="color: #fa8c16" />
              </div>
            </template>
            <a-card-meta title="收录作者数量">
              <template #description>
                <div class="stats-number">
                  {{ overviewData.authorsCount || 0 }}
                </div>
              </template>
            </a-card-meta>
          </a-card>
        </a-col>
      </a-row>

      <!-- 关键词统计图表 -->
      <a-row :gutter="16" style="margin-bottom: 16px">
        <a-col :span="24">
          <a-card title="关键词文献数量 TOP 5" :loading="loading">
            <template #extra> <tag-outlined /> 关键词分析 </template>
            <div ref="keywordsChartContainer" style="height: 400px"></div>
            <a-empty
              v-if="keywordsTop.length === 0 && !loading"
              description="暂无关键词数据"
            />
          </a-card>
        </a-col>
      </a-row>

      <!-- 作者星级统计图表 -->
      <a-row :gutter="16">
        <a-col :span="24">
          <a-card title="作者星级评分 TOP 5" :loading="loading">
            <template #extra> <star-outlined /> 星级分析 </template>
            <div ref="authorsChartContainer" style="height: 400px"></div>
            <div
              v-if="allAuthorsHaveNullStars && !loading"
              class="no-stars-warning"
            >
              <a-alert
                message="暂无星级评分数据"
                description="您尚未对任何文献进行星级评分，评分后将显示作者的星级统计"
                type="info"
                show-icon
              />
            </div>
          </a-card>
        </a-col>
      </a-row>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import {
  BookOutlined,
  FolderOutlined,
  UserOutlined,
  TagOutlined,
  StarOutlined,
} from "@ant-design/icons-vue";
import {
  getStatsOverview,
  getKeywordsTop,
  getAuthorsStarsTop,
} from "@/api/stats";
import * as echarts from "echarts/core";
import { BarChart, BarSeriesOption } from "echarts/charts";
import {
  TitleComponent,
  TitleComponentOption,
  TooltipComponent,
  TooltipComponentOption,
  GridComponent,
  GridComponentOption,
  LegendComponent,
  LegendComponentOption,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

// 注册必须的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  BarChart,
  CanvasRenderer,
]);

type ECOption = echarts.ComposeOption<
  | BarSeriesOption
  | TitleComponentOption
  | TooltipComponentOption
  | GridComponentOption
  | LegendComponentOption
>;

// 状态变量
const loading = ref(true);
const overviewData = ref({
  documentsCount: 0,
  foldersCount: 0,
  authorsCount: 0,
});
const keywordsTop = ref<Array<{ keyword: string; count: number }>>([]);
const authorsStarsTop = ref<Array<{ author: string; stars: number | null }>>(
  []
);

// 添加计算属性，检查是否所有作者都没有星级评分
const allAuthorsHaveNullStars = computed(() => {
  // console.log("检查作者星级数据:", authorsStarsTop.value);
  return (
    authorsStarsTop.value.length > 0 &&
    authorsStarsTop.value.every((item) => item.stars === null)
  );
});

// Chart refs
const keywordsChartContainer = ref<HTMLElement | null>(null);
const authorsChartContainer = ref<HTMLElement | null>(null);
let keywordsChart: echarts.ECharts | null = null;
let authorsChart: echarts.ECharts | null = null;

// 获取统计数据 - 通过API获取
const fetchStatsData = async () => {
  try {
    loading.value = true;
    console.log("开始获取统计数据...");

    // 并行请求各项数据
    try {
      const [overviewResp, keywordsResp, authorsResp] = await Promise.all([
        getStatsOverview(),
        getKeywordsTop(),
        getAuthorsStarsTop(),
      ]);

      console.log("统计概览数据:", overviewResp);
      console.log("关键词TOP5数据:", keywordsResp);
      console.log("作者星级TOP5数据:", authorsResp);

      // 解析返回的数据
      if (overviewResp && overviewResp.code === 0) {
        overviewData.value = overviewResp.data.overview || overviewResp.data;
      }

      if (keywordsResp && keywordsResp.code === 0) {
        keywordsTop.value = keywordsResp.data.keywordsTop || keywordsResp.data;
      }

      if (authorsResp && authorsResp.code === 0) {
        authorsStarsTop.value =
          authorsResp.data.authorsStarsTop || authorsResp.data;
      }
    } catch (error) {
      console.error("获取统计数据失败:", error);

      // 如果并行请求失败，尝试单独调用获取所有数据
      try {
        const statsResponse = await getStatsOverview();

        if (statsResponse && statsResponse.code === 0) {
          const data = statsResponse.data;

          overviewData.value = data.overview || {
            documentsCount: 0,
            foldersCount: 0,
            authorsCount: 0,
          };

          keywordsTop.value = data.keywordsTop || [];
          authorsStarsTop.value = data.authorsStarsTop || [];
        }
      } catch (fallbackError) {
        console.error("获取统计数据彻底失败:", fallbackError);
      }
    }

    console.log("处理后的统计数据:", {
      overview: overviewData.value,
      keywordsTop: keywordsTop.value,
      authorsStarsTop: authorsStarsTop.value,
    });

    // 初始化图表
    setTimeout(() => {
      initCharts();
    }, 100);
  } catch (error) {
    console.error("获取统计数据失败:", error);
  } finally {
    loading.value = false;
  }
};

// 处理空数据或null值
const processAuthorsStarsData = () => {
  // 为空值设置默认值，这样图表可以正常显示
  return authorsStarsTop.value.map((item) => ({
    author: item.author,
    // 如果stars为null，则设置为0并在界面提示
    stars: item.stars === null ? 0 : item.stars,
  }));
};

// 初始化图表
const initCharts = () => {
  // 确保DOM元素已经挂载
  if (!keywordsChartContainer.value || !authorsChartContainer.value) {
    console.error("图表容器DOM元素未找到");
    return;
  }

  console.log("初始化关键词图表...");
  // 初始化关键词图表
  keywordsChart = echarts.init(keywordsChartContainer.value);
  const keywordsOption: ECOption = {
    title: {
      text: "关键词文献分布",
      subtext: "基于文献关键词统计",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      formatter: "{b}: {c} 篇文献",
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: keywordsTop.value.map((item) => item.keyword),
      axisTick: {
        alignWithLabel: true,
      },
      axisLabel: {
        rotate: 45,
        interval: 0,
      },
    },
    yAxis: {
      type: "value",
      name: "文献数量",
    },
    series: [
      {
        name: "文献数量",
        type: "bar",
        barWidth: "60%",
        data: keywordsTop.value.map((item) => item.count),
        itemStyle: {
          color: "#1890ff",
        },
        label: {
          show: true,
          position: "top",
          formatter: "{c}",
        },
        emphasis: {
          itemStyle: {
            color: "#40a9ff",
          },
        },
      },
    ],
  };

  // console.log("关键词图表配置:", keywordsOption);
  keywordsChart.setOption(keywordsOption);

  // console.log("初始化作者星级图表...");
  // 处理作者星级数据，替换null值
  const processedAuthorsData = processAuthorsStarsData();
  // console.log("处理后的作者星级数据:", processedAuthorsData);

  // 初始化作者星级图表
  authorsChart = echarts.init(authorsChartContainer.value);
  const authorsOption: ECOption = {
    title: {
      text: "作者星级评分",
      subtext: allAuthorsHaveNullStars.value
        ? "暂无星级评分数据"
        : "基于用户对文献的评分",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      formatter: function (params: any) {
        const value = params[0].value;
        const name = params[0].name;
        if (value === 0 && allAuthorsHaveNullStars.value) {
          return `${name}: 暂无评分`;
        }
        return `${name}: ${value} 星`;
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: processedAuthorsData.map((item) => item.author),
      axisTick: {
        alignWithLabel: true,
      },
    },
    yAxis: {
      type: "value",
      name: "星级总数",
      min: 0,
      max: function (value: { max: number }) {
        return allAuthorsHaveNullStars.value
          ? 5
          : Math.ceil(value.max * 1.2 || 5);
      },
    },
    series: [
      {
        name: "星级评分",
        type: "bar",
        barWidth: "60%",
        data: processedAuthorsData.map((item) => item.stars),
        itemStyle: {
          color: function (params: any) {
            // 如果所有作者都没有星级，使用灰色
            return allAuthorsHaveNullStars.value ? "#d9d9d9" : "#fa8c16";
          },
        },
        label: {
          show: true,
          position: "top",
          formatter: function (params: any) {
            const value = params.value;
            if (value === 0 && allAuthorsHaveNullStars.value) {
              return "暂无";
            }
            return value;
          },
        },
        emphasis: {
          itemStyle: {
            color: function (params: any) {
              return allAuthorsHaveNullStars.value ? "#bfbfbf" : "#ffa940";
            },
          },
        },
      },
    ],
  };

  console.log("作者星级图表配置:", authorsOption);
  authorsChart.setOption(authorsOption);
};

// 窗口大小变化时调整图表大小
const handleResize = () => {
  keywordsChart?.resize();
  authorsChart?.resize();
};

onMounted(() => {
  // console.log("StatsView组件已挂载，开始获取数据...");
  fetchStatsData();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  keywordsChart?.dispose();
  authorsChart?.dispose();
});
</script>

<style scoped>
.stats-container {
  padding: 16px;
}

.stats-card-icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 120px;
  border-radius: 2px 2px 0 0;
  padding: 24px;
}

.stats-card-icon {
  font-size: 64px;
}

.stats-number {
  font-size: 36px;
  font-weight: 600;
  color: #262626;
  line-height: 1.2;
  margin-top: 8px;
}

.no-stars-warning {
  margin-top: 20px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .stats-number {
    font-size: 28px;
  }

  .stats-card-icon {
    font-size: 48px;
  }

  .stats-card-icon-wrapper {
    height: 100px;
  }
}
</style>
