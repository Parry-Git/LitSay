import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";

import dayjs from "dayjs";
import "dayjs/locale/zh-cn";
dayjs.locale("zh-cn");

import "katex/dist/katex.min.css";

const app = createApp(App);
app.use(router);
app.use(ElementPlus);
app.use(Antd);
app.mount("#app");
