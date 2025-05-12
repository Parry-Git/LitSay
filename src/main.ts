import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
// 正确导入 Ant Design Vue
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css"; // 新版本使用 reset.css

// 配置 dayjs 以解决日期组件错误
import dayjs from "dayjs"; // 确保已安装: npm install dayjs
import "dayjs/locale/zh-cn";
dayjs.locale("zh-cn"); // 全局使用中文

// 导入KaTeX样式（用于数学公式渲染）
import "katex/dist/katex.min.css";

const app = createApp(App);
app.use(router);
app.use(ElementPlus);
app.use(Antd); // 使用Ant Design Vue
app.mount("#app");
