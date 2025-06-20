# 文献一言 (LitSay) - 文献管理系统

**文献一言 (LitSay)** Developed for `DATA130039.01` 项目旨在实现一个方便快捷、功能丰富的文献管理平台，让文献的上传、组织、查询和分析像“说一句话一样简单”。

| | |
| :--- | :--- |
| **GitHub 仓库** | **[https://github.com/Parry-Git/LitSay](https://github.com/Parry-Git/LitSay)** |
| **在线用户手册** | **[https://fcnhy5uwfpqk.feishu.cn/wiki/YK6Qwu0h5imbF1kgXVocKI6cnfe](https://fcnhy5uwfpqk.feishu.cn/wiki/YK6Qwu0h5imbF1kgXVocKI6cnfe)** |

---

## ✨ 核心功能

* **智能文献导入**: 支持单篇或批量拖拽上传PDF，提供“普通解析”和“AI解析”双模式，自动提取元数据。
* **灵活文献组织**: 提供无限层级的目录系统，支持自由创建、移动和重命名。
* **强大信息检索**: 提供覆盖多字段的基础搜索，以及支持逻辑（`AND`/`OR`）、范围和正则表达式的高级搜索。
* **精细元数据管理**: 支持手动编辑所有文献信息，并提供独特的“文献星级评分”和支持 Markdown 的“文献笔记”。
* **便捷数据迁移**: 支持从 CSV、JSON 格式批量导入文献数据，并支持一键导出数据和参考文献。
* **可视化统计分析**: 提供仪表盘，通过图表直观展示文献数量、关键词排行、作者排行等关键指标。

---

## 🖥️ 开发环境

* **操作系统**: Windows 11 (WSL2)
* **编程语言**:
    * 后端: Python 3.13.2
    * 前端: TypeScript / JavaScript (ES6)
* **核心框架**:
    * 后端: Flask 3.1.1
    * 前端: Vue.js 5.0.8
* **数据库**: OceanBase
* **依赖管理**:
    * 后端: Conda, Pip
    * 前端: Yarn
* **依赖文件**:
    * 后端: `LitSay/backend-test/requirements.txt`
    * 前端: `LitSay/package.json`

---

## 🛠️ 项目部署步骤与使用方法

通过以下步骤在本地环境中部署和运行本项目。

### 第 1 步：克隆源代码

```bash
git clone https://github.com/Parry-Git/LitSay.git
cd LitSay
```

### 第 2 步：配置并运行前端

1.  **安装依赖** (在 `LitSay` 根目录下执行):
    ```bash
    yarn install
    ```

2.  **启动开发服务器**:
    ```bash
    yarn serve
    ```
    > 成功启动后，前端应用即可在 `http://localhost:8080` (或终端提示的地址) 访问。

### 第 3 步：配置并运行后端

1.  **导航至后端目录**:
    ```bash
    cd backend-test
    ```

2.  **创建并激活 Conda 环境**:
    ```bash
    conda create -n LitSay python=3.13
    conda activate LitSay
    ```

3.  **安装 Python 依赖**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量 (关键)**:
    在 `backend-test` 目录下找到 `.env` 和 `.flaskenv` 两个文件。
    > **提示**: 为了方便测试，我们已将配置文件包含在仓库中，您可以使用默认配置，也可自行修改。

    **`.env` 文件内容:**
    ```ini
    # Flask 安全密钥 (请使用随机字符串)
    SECRET_KEY='your_very_secret_random_string_for_flask_sessions_and_cookies'
    JWT_SECRET_KEY='your_super_secret_key_for_jwt'

    # OceanBase 数据库连接信息 (默认数据库中包含了一些测试信息)
    OB_HOST="obmt6ljnxn8aacxs-mi.aliyun-cn-hangzhou-internet.oceanbase.cloud"
    OB_PORT=3306
    OB_USER="yu"
    OB_PASSWORD="iCNiD{@l~6;*-6D?,uu=SHBZ)y"
    OB_DATABASE="test_0613"
    TEST_OB_DATABASE="test_0613"

    # 文件上传路径 (确保目录存在且有写入权限)
    UPLOAD_FOLDER=uploads/
    
    # Gemini API Key (在批改期间应该是可用的，如果不可用，请联系我们或自行填补)
    GEMINI_KEY="AIzaSyDSBULm2E_tWhsygPl9OOwQhbQvGGRgXh8"
    ```

    **`.flaskenv` 文件内容:**
    ```ini
    FLASK_APP=run.py
    FLASK_ENV=development
    ```

5.  **运行后端服务**:
    ```bash
    flask run
    ```
    > 服务成功启动后，将监听 `http://127.0.0.1:5000`。

---

## 🗄️ 数据库初始化与测试数据

### 1. 数据库初始化流程

> **注意**: 如果您使用我们**提供的 OceanBase 测试数据库**，其表结构和部分数据已预设完毕，**可以跳过此步骤**。

此方法适用于您希望在自己部署的数据库中创建表结构。

1.  确保后端服务已停止，但 Conda 环境 `LitSay` 已激活。
2.  在后端目录 `backend-test` 下，运行以下命令：
    ```bash
    # 此命令会连接到 .env 文件中配置的数据库并创建所有表
    flask init-db
    ```
3.  命令执行成功后，数据库表结构即创建完毕。现在可以正常启动后端服务了。

### 2. 测试数据导入方法

我们提供了测试数据集，您可以通过系统的批量导入功能将其导入。

1.  **测试数据文件**:
    测试数据位于仓库的 `LitSay/examples/` 目录下：
    * `LitSay/examples/metadata_example.csv`
    * `LitSay/examples/metadata_example.json`

2.  **导入步骤**:
    * 首先，请确保前后端服务均已正常运行。
    * 在浏览器中打开前端页面 (`http://localhost:8080`) 并**注册/登录一个新用户**。
    * 在主界面的左侧菜单栏或顶部操作区找到 **“批量操作”** 或 **“导入数据”** 功能按钮。
    * 在弹出的导入界面中，选择对应的文件格式（JSON 或 CSV）。
    * 上传 `LitSay/examples/` 目录下的相应文件。
    * 系统将解析文件并将数据批量存入数据库。导入成功后，您将在文献列表中看到这些测试数据。

> **备用测试方案**: 您也可以直接登录我们预设的管理员账户进行测试。
> * **账号**: `Paul`
> * **密码**: `123456`
> 此账户下已有部分数据，可用于体验搜索、导出等功能。

---

## 📂 项目文件结构

### 后端 (`backend-test`)

```
backend-test/
├── .env
├── .flaskenv
├── app/
│   ├── __init__.py         # 应用工厂
│   ├── db.py               # 数据库连接
│   ├── config.py           # 配置管理
│   ├── auth/               # 用户认证蓝图
│   ├── documents/          # 文献管理蓝图
│   ├── folders/            # 目录管理蓝图
│   ├── search/             # 搜索功能蓝图
│   ├── stats/              # 统计分析蓝图
│   ├── upload/             # 文件上传蓝图
│   └── utils/              # 辅助工具 (装饰器等)
├── requirements.txt
└── run.py                  # 项目启动文件
```

### 前端 (`LitSay/` 根目录)

```
LitSay/
├── public/
├── src/
│   ├── api/                # API 请求封装
│   ├── assets/             # 静态资源
│   ├── components/         # 可复用UI组件
│   ├── router/             # 前端路由
│   ├── views/              # 页面级组件
│   ├── App.vue
│   └── main.ts
├── package.json
└── vue.config.js
```

---

## 👥 小组成员分工说明

| 成员     | 主要职责                        |
| :------- | :------------------------------ |
| **程琦** | `前端开发` `后端开发`           |
| **于翔** | `后端开发` `项目报告编写`       |
| **黄济川** | `后端开发` `用户手册编写`       |
| **武相如** | `PPT制作` `手册编写`          |

