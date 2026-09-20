# Text-to-SQL Agent

基于 LangChain + LangGraph + DeepSeek 的智能数据库查询助手。

## ✨ 功能特性
- 🗣️ 自然语言查询 MySQL 数据库
- 🔧 支持 CRUD、复杂 SQL 查询
- 🛡️ 三层安全防护（参数化 + 标识符校验 + 权限隔离）
- 🔄 LangGraph Agent 架构，支持多轮对话
- 📊 提供 React 前端界面

## 🛠️ 技术栈
Python | LangChain | LangGraph | DeepSeek | MySQL | FastAPI | React

## 🚀 快速开始

1. 克隆项目
   \`\`\`bash
   git clone https://github.com/your-username/text2sql-agent.git
   cd text2sql-agent
   \`\`\`

2. 配置环境变量
   \`\`\`bash
   cp backend/.env.example backend/.env
   # 编辑 .env，填入你的密码和 API Key
   \`\`\`

3. 安装依赖
   \`\`\`bash
   pip install -r backend/requirements.txt
   \`\`\`

4. 启动服务
   \`\`\`bash
   cd backend
   langgraph dev
   \`\`\`

## 📁 项目结构
\`\`\`
├── backend/         # LangGraph 后端
│   ├── agent/       # Agent 核心逻辑
│   └── .env.example # 配置模板
├── scripts/         # 工具脚本
└── SQL_Scripts/     # 数据库初始化
\`\`\`

## 📝 License
MIT