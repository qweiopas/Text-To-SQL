# from setting import MYSQL_PASSWORD, MYSQL_USER
import pymysql
import logging
import re

# 配置日志
logging.basicConfig(
    level=logging.DEBUG, # 日志级别DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='MySQLDataBaseMange.log',  # 日志文件名
    filemode='a',  # 追加模式
    encoding='utf-8'  # 设置编码为 UTF-8
)
logger = logging.getLogger(__name__)   # 获取当前模块的 logger

class MySQLDataBaseManage:
    def __init__(self, password: str, database: str, user: str, host: str = 'localhost', port: int = 3306, charset: str = 'utf8mb4') -> None:
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.user = user
        self.charset = charset
        # self.table = table
        self.conn = None
        self.sql = None
        logger.info(f"MySQLDataBaseManage 初始化: host={host}, database={database}, user={user}")

    # 上下文管理
    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logger.info("通过 self.__exit__() 关闭了数据库连接")

    def __del__(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logger.info("通过 self.__del__() 关闭了数据库连接")

    def initialize(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, charset=self.charset, database=self.database)
            logger.info(f"数据库连接成功: {self.database}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise ConnectionError(f"连接数据库失败{e}")

    def _validate_identifier(self, name: str) -> None:
        """校验标识符：只允许字母、数字、下划线，且非空"""
        if not name or not isinstance(name, str):
            logger.error(f"标识符校验失败: 标识符必须是非空字符串，实际为 {name}")
            raise ValueError("标识符必须是非空字符串")
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            logger.error(f"标识符校验失败: 非法标识符 '{name}'")
            raise ValueError(f"非法标识符: {name}")

    def insert(self, table: str, data: dict):
        self._validate_identifier(table)
        for col in data:
            self._validate_identifier(col)
        columns = list(data.keys())
        values = list(data.values())
        col_str = ', '.join(columns)
        placeholder = ', '.join(['%s'] * len(values))
        self.sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholder})"
        logger.debug(f"执行 SQL: {self.sql}, 参数: {values}")
        if self.conn is None:
            logger.error("数据库未连接")
            raise ConnectionError("数据库未连接")
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(self.sql, values)
                self.conn.commit()
                last_id = cursor.lastrowid
                logger.info(f"插入成功: 表={table}, ID={last_id}")
                return last_id
        except Exception as e:
            logger.error(f"插入数据失败: {e}, SQL: {self.sql}, 参数: {values}")
            self.conn.rollback()    # 回滚
            raise

    def update(self, table: str, data: dict, condition: dict):
        self._validate_identifier(table)
        for col in data.keys():
            self._validate_identifier(col)
        for col in condition.keys():
            self._validate_identifier(col)
        # SET 子句
        set_clause = ', '.join([f'{col} = %s' for col in data.keys()])
        # WHERE 子句
        where_clause = ' AND '.join([f'{col} = %s' for col in condition.keys()])

        params = list(data.values()) + list(condition.values())
        self.sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        logger.debug(f"执行 SQL: {self.sql}, 参数: {params}")
        if self.conn is None:
            logger.error("数据库未连接")
            raise ConnectionError("数据库未连接")
        try:
            with self.conn.cursor() as cursor:
                rows = cursor.execute(self.sql, params)
                self.conn.commit()
                logger.info(f"更新成功: 表={table}, 影响行数={rows}")
                return rows
        except Exception as e:
            logger.error(f"数据更新失败: {e}, SQL: {self.sql}, 参数: {params}")
            self.conn.rollback()
            raise

    def delete(self, table: str, condition: dict):
        self._validate_identifier(table)
        for col in condition.keys():
            self._validate_identifier(col)
        # WHERE 子句
        where_clause = ' AND '.join([f'{col} = %s' for col in condition.keys()])

        params = list(condition.values())
        self.sql = f"DELETE FROM {table} WHERE {where_clause}"
        logger.debug(f"执行 SQL: {self.sql}, 参数: {params}")
        if self.conn is None:
            logger.error("数据库未连接")
            raise ConnectionError("数据库未连接")
        try:
            with self.conn.cursor() as cursor:
                rows = cursor.execute(self.sql, params)
                self.conn.commit()
                logger.info(f"删除成功: 表={table}, 影响行数={rows}")
                return rows
        except Exception as e:
            logger.error(f"数据删除失败: {e}, SQL: {self.sql}, 参数: {params}")
            self.conn.rollback()
            raise

    def search(self, table: str, columns: list[str], condition: dict):
        self._validate_identifier(table)
        for col in columns:
            self._validate_identifier(col)
            if condition:
                for col in condition.keys():
                    self._validate_identifier(col)
        # SELECT 子句
        select_clause = ', '.join(columns)
        self.sql = f"SELECT {select_clause} FROM {table}"
        params = []
        if condition:
            # WHERE 子句
            where_clause = ' AND '.join([f'{col} = %s' for col in condition.keys()])
            self.sql += f" WHERE {where_clause}"
            params = list(condition.values())
        logger.debug(f"执行 SQL: {self.sql}, 参数: {params}")
        if self.conn is None:
            logger.error("数据库未连接")
            raise ConnectionError("数据库未连接")
        try:
            with self.conn.cursor() as cursor:
                rows = cursor.execute(self.sql, params)
                results = cursor.fetchall()
                logger.info(f"查询成功: 表={table}, 返回 {len(results)} 条记录")
                return results
            
        except Exception as e:
            logger.error(f"数据查询失败: {e}, SQL: {self.sql}, 参数: {params}")
            # self.conn.rollback()
            raise

    def execute_sql(self, sql: str, params: list = []) -> tuple:
        """
        执行只读的 SELECT 查询，支持参数化。
        - 只允许 SELECT 语句
        - 自动添加 LIMIT 1000（如果未指定）
        - 返回查询结果列表（每行是一个元组）
        """
        # 校验 SQL 类型
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            logger.error(f"不支持的 SQL 类型: {sql}")
            raise ValueError("只允许执行 SELECT 查询")

        statements = [s.strip() for s in sql.split(';') if s.strip()]
        if len(statements) > 1:
            logger.error(f"检测到多条 SQL 语句: {sql}")
            raise ValueError("只允许执行单条 SQL 语句")
        
        # 强制添加 LIMIT（防止全表扫描）
        if "LIMIT" not in sql_upper:
            sql += " LIMIT 1000"
        
        if self.conn is None:
            raise ConnectionError("数据库未连接")
        
        try:
            with self.conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                results = cursor.fetchall()
                logger.info(f"执行 SQL 成功: {sql}, 返回 {len(results)} 行")
                return results
        except Exception as e:
            logger.error(f"执行 SQL 失败: {e}, SQL: {sql}")
            raise

    def get_user_permissions(self):
        description = f"Grants for {self.user}@{self.host} \n"
        if self.conn is None:
            logger.error("数据库未连接")
            raise ConnectionError("数据库未连接")
        
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
            grants = cursor.fetchall()
            logger.info(f"获取用户权限成功: {grants}")
        description += "\n".join(grant[0] for grant in grants)
        return description
    
    def get_table_info_tool(self, table: str) -> str:
        """
        获取指定表的详细信息，包括列名、数据类型、主键、是否可为空等。
        返回格式化的描述文本。
        """
        if self.conn is None:
            logger.error("数据库未连接")
            raise ConnectionError("数据库未连接")
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                result = cursor.fetchone()
                if not result:
                    return f"表 '{table}' 不存在或您无权查看其定义。"
                # result 格式：(table_name, create_statement)
                create_sql = result[1]
                logger.info(f"获取表 {table} 的建表语句成功: {create_sql}")
                return f"表 {table} 的建表语句：\n{create_sql}"
        except Exception as e:
            logger.error(f"获取表 {table} 的建表语句失败: {e}")
            return f"获取建表语句失败: {e}"

    def conn_close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logger.info("通过 self.conn_close() 关闭了数据库")

# if __name__ == "__main__":
#     # db = MySQLDataBaseManage(password=str(MYSQL_PASSWORD), database='test_db_1')
#     # db.initialize()

#     # table = "users"
#     # # user = {"name": "test_user_1", "email": "1@a.com", "age": 21}
#     # # # 插入数据
#     # # new_id = db.insert(table=table, data=user)
#     # # # 修改数据
#     # # rows = db.update(table=table, data={"email": "2@a.com"}, condition={"id": 26})
#     # # # 查询数据
#     # # res = db.search(table=table, columns=["name", "email", "age"], condition={"age": 20})
#     # # print(res)
#     # # # 删除数据
#     # # db.delete(table=table, condition={"id": new_id})

#     # # # 测试校验
#     # # db.insert("users; DROP TABLE users; --", {"name": "test"})   # 会抛出 ValueError
#     # # db.search("users", ["id", "name; DROP"], {})                 # 会抛出 ValueError
#     # db.conn_close()
#     with MySQLDataBaseManage(user=str(MYSQL_USER), password=str(MYSQL_PASSWORD), database='test_db_1') as db:
#         # table = "users"
#         # user = {"name": "test_user_1", "email": "1@a.com", "age": 21}
#         # # 插入数据
#         # new_id = db.insert(table=table, data=user)
#         # # 修改数据
#         # rows = db.update(table=table, data={"email": "2@a.com"}, condition={"id": 26})
#         # # 查询数据
#         # res = db.search(table=table, columns=["name", "email", "age"], condition={"age": 20})
#         # print(res)
#         # # 删除数据
#         # db.delete(table=table, condition={"id": new_id})

#         # # 测试校验
#         # db.insert("users; DROP TABLE users; --", {"name": "test"})   # 会抛出 ValueError
#         # db.search("users", ["id", "name; DROP"], {})                 # 会抛出 ValueError
#         # print(db.get_user_permissions())
#         print(db.get_table_info_tool("users"))