# Text-to-SQL Agent

基于 **LangChain + LangGraph + DeepSeek** 的智能数据库查询助手。通过自然语言对话即可完成对 MySQL 数据库的增删改查、复杂聚合查询。

---

``` bash
git clone https://github.com/qweiopas/Text-To-SQL.git
```
``` bash
cd Text-To-SQL/backend
pip install -r requirements.txt
# 需要 Python >= 3.11。
pip install --upgrade "langgraph-cli[inmem]"
langgraph dev
```

## ✨ 功能特性

- 🗣️ **自然语言交互** — 用日常语言描述需求，Agent 自动生成并执行 SQL
- 🔧 **完整的 CRUD 能力** — 支持 `SELECT`、`INSERT`、`UPDATE`、`DELETE`
- 📊 **复杂查询支持** — 支持 `JOIN`、`GROUP BY`、聚合、子查询等
- 🛡️ **三层安全防护**
  - 应用层：参数化查询 + 标识符白名单校验 + 强制 `LIMIT`
  - 数据库层：表级权限隔离（Agent 只能操作授权表）
  - 审计层：结构化日志记录每一次 SQL 调用
- 🔄 **LangGraph Agent 架构** — 支持多轮对话、工具调用、状态管理
- 📈 **可观测性** — 集成 LangSmith，全链路追踪 Token 消耗与响应延迟


---

## 🛠️ 技术栈

| 分类 | 技术 |
|------|------|
| **语言** | Python 3.11+ |
| **Agent 框架** | LangChain 1.0+ / LangGraph 1.0+ |
| **大语言模型** | DeepSeek（兼容 OpenAI 接口） |
| **数据库** | MySQL 8.0+ |
| **数据库驱动** | PyMySQL |
| **配置管理** | Pydantic Settings + python-dotenv |
| **日志** | Python logging |
