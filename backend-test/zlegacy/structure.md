## project structure
\paperdb\
├── backend/                 # Python后端
│   ├── app.py               # Flask主应用
│   ├── requirements.txt     # Python依赖
│   ├── config.py            # 应用配置 (数据库, 密钥, 存储, API Key等)
│   ├── api/
│   │   ├── __init__.py      # API模块初始化
│   │   ├── paper_api.py     # 文献相关API
│   │   ├── file_api.py      # 文件上传API
│   │   ├── directory_api.py # 目录管理API
│   │   └── search_api.py    # 搜索API
│   ├── tests/               # 后端测试
│   │   └── ...
│   ├── utils/
│   │   ├── __init__.py      # 工具模块初始化
│   │   ├── parser.py        # 文献解析工具
│   │   └── config.py        # 配置文件
│   └── database/            # Ocean Base模块
│       ├── __init__.py      # 数据库模块初始化
│       ├── connect.py       # Ocean base数据库连接
│       ├── models.py        # 数据模型定义
│       └── operations.py    # 数据库操作封装
├── frontend/                # Vue前端
│   ├── public/
│   ├── src/
│   │   ├── api/             # 前端API调用封装
│   │   ├── assets/          # 静态资源
│   │   ├── components/      # 公共Vue组件
│   │   ├── router/          # 路由配置
│   │   ├── store/           # Vuex状态管理
│   │   ├── services/        # 前端复杂逻辑/服务
│   │   ├── utils/           # 前端工具函数
│   │   ├── views/           # 页面视图
│   │   └── main.js          # Vue应用入口
│   ├── tests/               # 前端测试
│   │   └── ...
│   ├── package.json
│   └── vue.config.js
├── docker-compose.yml       # (可选) Docker配置
├── Dockerfile               # (可选) 后端和前端的Dockerfile
└── README.md


## 1. 引言

本md旨在阐述 PaperDB 文献管理系统的核心软件架构设计。我们将介绍架构模式、技术选型及模块划分，论证其在满足项目需求方面的合理性、可行性与技术优势。

## 2. 整体架构设计：前后端分离 (SPA + RESTful API)

采用业界成熟的**前后端分离**架构：

*   **前端 (Frontend):** **Vue.js** 构建的**单页面应用 (SPA)**，负责 UI 渲染与用户交互。
*   **后端 (Backend):** **Python Flask** 构建的 **RESTful API 服务**，负责业务逻辑、数据持久化、文件处理。
*   **通信:** 通过 **HTTP/S** + **JSON** 进行数据交换，遵循 **RESTful** 规范。

**优势:**

*   **关注点分离:** UI 与业务逻辑解耦，易于维护。
*   **技术栈灵活:** 前后端可独立选型优化。
*   **并行开发 & 部署:** 基于 API 契约，可并行工作，独立部署和扩展。
*   **跨平台潜力:** API 便于未来接入其他客户端。

## 3. 后端架构 (`backend/`) 详解

基于 **Flask** 微框架，利用 Python 生态进行数据处理与 API 开发。

*   **`api/` (API 接口层):** 使用 Flask Blueprints 按功能组织 API (文件、文献、目录、搜索)。
    *   **关键点 (文件上传):** 实现**分块上传 (Chunking)** 及合并逻辑，支持断点续传，处理校验、限制与加密。
    *   **关键点 (目录管理):** 提供目录结构的 CRUD 及移动接口，调用 `database/` 维护层级关系。
*   **`database/` (数据持久层):**
    *   **ORM:** 使用 **SQLAlchemy** 定义数据模型 (`models.py`)。
    *   **核心设计 (目录):** 采用 **Closure Table (闭包表)** 模式 (`directory_closures` 表) 高效管理和查询复杂的目录层级关系（祖先、子孙、移动子树）。
    *   **数据操作:** 封装原子性数据库操作 (`operations.py`)，供 API 层调用。
    *   **数据库选型:** **PostgreSQL** 或 **MySQL** (提供事务支持)。
*   **`utils/` (工具与服务层):**
    *   **`parser.py` (核心解析):** 集成 PDF 文本提取库 (e.g., PyMuPDF)、OCR 工具/服务、文献 API (e.g., CrossRef) 和未来可能的 AI 模型 API，实现元数据自动提取。
    *   包含其他通用工具函数 (加密、文件辅助等)。
*   **`config.py`:** 集中管理配置信息。
*   **`tests/`:** 单元测试与集成测试。

## 4. 前端架构 (`frontend/`) 详解

基于 **Vue.js** 构建交互式用户界面。

*   **核心:** Vue Router (路由), Vuex/Pinia (全局状态管理)。
*   **`api/`:** 封装对后端 API 的调用 (e.g., using `axios`)。
*   **`components/`:** 可复用 UI 组件库。
    *   **关键组件:** 文件上传组件 (拖拽、进度条)、树形目录组件 (懒加载、拖拽)、富文本编辑器 (笔记功能)、数据展示组件。
*   **`views/`:** 页面级组件，组合 `components/` 构建完整界面。
*   **`services/`:** 处理复杂前端逻辑，如**文件分块上传的协调**（切割、上传、重试、合并通知）。
*   **`store/`:** 管理全局状态 (用户、上传进度、当前项等)。
*   **`utils/` & `assets/`:** 通用工具函数与静态资源。
*   **`tests/`:** 前端测试。

## 5. 技术栈总结

*   **后端:** Python, Flask, SQLAlchemy, Oceanbase.
*   **前端:** Vue.js, Vue Router, Vuex/Pinia, Axios.
*   **(可选):** Celery (异步任务), Redis (缓存), Docker (容器化).

## 6. 合理性与可行性评估

*   **需求覆盖:** 架构设计能有效支撑所有核心需求（上传、解析、目录管理、搜索、笔记、关联、去重等）。
    *   **分块上传** 解决大文件/网络问题。
    *   **Closure Table** 高效处理目录层级。
    *   **模块化解析** 支持多种方式和扩展。
*   **技术成熟度:** 主流技术栈，社区支持良好，风险可控。
*   **模块化优势:**
    *   **可扩展性:** 易于增加新功能或替换模块 (e.g., 新解析源)。
    *   **可维护性:** 代码结构清晰，易于理解和修改。
    *   **可测试性:** 各层级易于进行单元和集成测试。

## 7. 结论

所设计的 PaperDB 软件架构采用成熟的前后端分离模式，技术选型合理，模块划分清晰。关键技术点（如分块上传、Closure Table）针对性地解决了核心需求中的难点。该架构具备良好的可行性、可扩展性、可维护性和可测试性，为项目后续的成功开发奠定了坚实基础。
