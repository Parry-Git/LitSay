const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

// 显示当前目录
console.log("当前目录:", process.cwd());

// 确保 package.json 存在
const packageJsonPath = path.join(process.cwd(), "package.json");
if (!fs.existsSync(packageJsonPath)) {
  console.error("错误: 找不到 package.json 文件");
  process.exit(1);
}

// 读取 package.json
const packageJson = require(packageJsonPath);
console.log("当前项目:", packageJson.name);

try {
  // 卸载当前 ant-design-vue
  console.log("正在卸载 ant-design-vue...");
  execSync("npm uninstall ant-design-vue", { stdio: "inherit" });

  // 清除缓存
  console.log("清除 npm 缓存...");
  execSync("npm cache clean --force", { stdio: "inherit" });

  // 安装特定版本
  console.log("安装 ant-design-vue v3.2.20 (稳定版)...");
  execSync("npm install ant-design-vue@3.2.20 --save", { stdio: "inherit" });

  // 安装相关依赖
  console.log("安装 markdown-it 相关依赖...");
  execSync("npm install markdown-it markdown-it-katex katex --save", {
    stdio: "inherit",
  });

  console.log("完成! 所有依赖已成功安装。");
} catch (error) {
  console.error("安装过程中发生错误:", error.message);
  process.exit(1);
}
