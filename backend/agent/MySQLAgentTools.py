from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_community.tools import StructuredTool
from agent.MySQLDataBaseManage import MySQLDataBaseManage
from langchain.agents import create_agent

# ---------- 输入参数模型 ----------
class InsertInput(BaseModel):
    table: str = Field(description="要插入数据的表名")
    data: Dict[str, Any] = Field(description="要插入的字段和值，如 {'name':'Alice','age':25}")

class UpdateInput(BaseModel):
    table: str = Field(description="要更新数据的表名")
    data: Dict[str, Any] = Field(description="要更新的字段和值")
    condition: Dict[str, Any] = Field(description="更新条件，如 {'id':1}")

class DeleteInput(BaseModel):
    table: str = Field(description="要删除数据的表名")
    condition: Dict[str, Any] = Field(description="删除条件，如 {'id':1}")

class SearchInput(BaseModel):
    table: str = Field(description="要查询数据的表名")
    columns: List[str] = Field(description="要查询的列名列表，如 ['id','name']")
    condition: Optional[Dict[str, Any]] = Field(default=None, description="查询条件，如 {'age':25}，可省略")

class CreateTableInput(BaseModel):
    table: str = Field(description="要获取建表语句的表名")

class ExecuteSQLInput(BaseModel):
    sql: str = Field(description="要执行的 SELECT SQL 语句，支持占位符 %s，例如 'SELECT * FROM users WHERE age > %s'")
    params: Optional[List[Any]] = Field(default=[], description="参数列表，顺序对应占位符 %s，例如 [25]")

class MySQLAgentTools:
    """封装 MySQL CRUD 工具，供 LangChain Agent 调用"""
    def __init__(
        self,
        user: str,
        password: str,
        database: str,
        host: str = 'localhost',
        port: int = 3306,
        charset: str = 'utf8mb4'
    ):
        """
        初始化数据库连接并建立连接。
        """
        self.db = MySQLDataBaseManage(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port,
            charset=charset
        )
        # 建立数据库连接
        self.db.initialize()

    def get_tools(self):
        """返回工具列表，使用 StructuredTool 构建"""
        db = self.db  # 捕获引用

        def insert_tool(table: str, data: Dict[str, Any]) -> str:
            try:
                new_id = db.insert(table, data)
                return f"插入成功，新记录ID: {new_id}"
            except Exception as e:
                return f"插入失败: {e}"

        def update_tool(table: str, data: Dict[str, Any], condition: Dict[str, Any]) -> str:
            try:
                rows = db.update(table, data, condition)
                return f"更新成功，影响行数: {rows}"
            except Exception as e:
                return f"更新失败: {e}"

        def delete_tool(table: str, condition: Dict[str, Any]) -> str:
            try:
                rows = db.delete(table, condition)
                return f"删除成功，影响行数: {rows}"
            except Exception as e:
                return f"删除失败: {e}"

        def search_tool(table: str, columns: List[str], condition: Optional[Dict[str, Any]] = None) -> str:
            try:
                results = db.search(table, columns, condition if condition else {})
                if results:
                    return f"查询成功，共 {len(results)} 条记录:\n" + "\n".join(str(row) for row in results)
                else:
                    return "查询成功，但未找到匹配记录"
            except Exception as e:
                return f"查询失败: {e}"

        def get_create_table_tool(table: str) -> str:
            try:
                create_sql = db.get_table_info_tool(table)
                return f"建表语句:\n{create_sql}"
            except Exception as e:
                return f"获取建表语句失败: {e}"

        def execute_sql_tool(sql: str, params: List[Any] = []) -> str:
            try:
                results = db.execute_sql(sql, params)
                if results:
                    return f"查询成功，共 {len(results)} 条记录:\n" + "\n".join(str(row) for row in results)
                else:
                    return "查询成功，但无匹配记录"
            except Exception as e:
                return f"查询失败: {e}"

        tools = [
            StructuredTool.from_function(
                func=insert_tool,
                name="insert_record",
                description="向指定的数据库表中插入一条新记录。",
                args_schema=InsertInput
            ),
            StructuredTool.from_function(
                func=update_tool,
                name="update_record",
                description="更新数据库表中符合条件的一条或多条记录。",
                args_schema=UpdateInput
            ),
            StructuredTool.from_function(
                func=delete_tool,
                name="delete_record",
                description="删除数据库表中符合条件的一条或多条记录。",
                args_schema=DeleteInput
            ),
            StructuredTool.from_function(
                func=search_tool,
                name="search_records",
                description="查询数据库表中符合条件的数据，返回指定列的值。",
                args_schema=SearchInput
            ),
            StructuredTool.from_function(
                func=get_create_table_tool,
                name="get_create_table",
                description="获取指定表的完整建表语句，包括列定义、索引、约束、引擎、字符集等。",
                args_schema=CreateTableInput
            ),
                StructuredTool.from_function(
            func=execute_sql_tool,
            name="execute_sql",
            description="执行复杂的只读 SQL 查询（仅 SELECT），支持 JOIN、聚合、子查询等。必须使用参数化占位符 %s 并提供对应的参数列表。",
            args_schema=ExecuteSQLInput
        ),
        ]
        return tools
        

    def create_agent(self, llm, system_prompt: Optional[str] = None):
        """
        便捷方法：直接基于当前工具创建 LangChain Agent。
        :param llm: 大语言模型实例（如 ChatOpenAI, DeepSeek)
        :param system_prompt: 系统提示词（可选）
        """
        tools = self.get_tools()
        permission = self.db.get_user_permissions()
        if system_prompt is None:
            system_prompt = f"你是一个数据库助手，能够执行对指定表的增删改查操作。当前用户权限: {permission}"
        else:
            system_prompt += f" 当前用户权限: {permission}"
        return create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt
        )