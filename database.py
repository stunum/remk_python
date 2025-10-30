"""
数据库连接模块 - 使用SQLAlchemy和psycopg-binary连接PostgreSQL数据库
实现连接池、单例模式和自动断线重连功能
"""
import time
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from contextlib import contextmanager

from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.pool import QueuePool

from config import config, ConfigError
from models.base import Base

# 定义泛型类型变量，用于ORM操作方法的类型提示
T = TypeVar('T', bound=Base)


class DatabaseError(Exception):
    """数据库错误异常"""
    pass


class Database:
    """
    数据库连接类 - 单例模式
    使用SQLAlchemy和psycopg-binary连接PostgreSQL数据库
    实现连接池、单例模式和自动断线重连功能
    """
    _instance = None
    _engine = None
    _session_factory = None
    _max_retries = 3
    _retry_interval = 1  # 重试间隔（秒）

    def __new__(cls):
        """
        单例模式实现
        """
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        初始化数据库连接
        """
        try:
            # 从配置中获取数据库连接信息
            db_config = config.config.database
            
            # 构建数据库连接URL
            db_url = f"postgresql+psycopg://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.dbname}"
            
            # 创建引擎，配置连接池
            self._engine = create_engine(
                db_url,
                pool_size=db_config.max_idle_conns,  # 最小连接数
                max_overflow=db_config.max_open_conns - db_config.max_idle_conns,  # 最大溢出连接数
                pool_timeout=30,  # 连接池获取连接的超时时间
                pool_recycle=db_config.conn_max_lifetime,  # 连接回收时间
                pool_pre_ping=True,  # 自动检测连接是否有效，实现自动重连
                echo=db_config.log_level.lower() == "debug",  # 是否打印SQL语句
                poolclass=QueuePool  # 使用队列连接池
            )
            
            # 创建会话工厂
            self._session_factory = scoped_session(sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            ))
            
        except (ConfigError, Exception) as e:
            raise DatabaseError(f"数据库初始化失败: {str(e)}")

    @contextmanager
    def session(self):
        """
        创建数据库会话的上下文管理器
        自动处理异常和会话关闭
        实现自动断线重连
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except exc.DBAPIError as e:
            session.rollback()
            # 检查是否是连接错误
            if self._is_connection_error(e):
                # 尝试重新连接
                if self._reconnect():
                    # 重新创建会话并重试
                    session = self._session_factory()
                    try:
                        yield session
                        session.commit()
                    except Exception as retry_e:
                        session.rollback()
                        raise DatabaseError(f"数据库操作失败（重试后）: {str(retry_e)}")
                else:
                    raise DatabaseError(f"数据库连接失败，无法重新连接: {str(e)}")
            else:
                # 非连接错误，直接抛出
                raise DatabaseError(f"数据库操作失败: {str(e)}")
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"数据库操作失败: {str(e)}")
        finally:
            session.close()

    def _is_connection_error(self, error):
        """
        判断是否是连接错误
        """
        error_str = str(error).lower()
        connection_errors = [
            "connection", "timeout", "timed out", "lost connection",
            "broken pipe", "connection refused", "connection reset"
        ]
        return any(err in error_str for err in connection_errors)

    def _reconnect(self):
        """
        尝试重新连接数据库
        """
        for attempt in range(self._max_retries):
            try:
                # 尝试执行简单查询来测试连接
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return True
            except Exception:
                # 等待一段时间后重试
                time.sleep(self._retry_interval * (attempt + 1))
        
        # 所有重试都失败
        return False

    def create_tables(self):
        """
        创建所有模型对应的数据库表
        """
        try:
            Base.metadata.create_all(self._engine)
        except Exception as e:
            raise DatabaseError(f"创建数据库表失败: {str(e)}")

    def drop_tables(self):
        """
        删除所有模型对应的数据库表
        """
        try:
            Base.metadata.drop_all(self._engine)
        except Exception as e:
            raise DatabaseError(f"删除数据库表失败: {str(e)}")

    # ORM基本操作方法
    def get_by_id(self, model_class: Type[T], id: Any) -> Optional[T]:
        """
        根据ID获取记录
        """
        try:
            with self.session() as session:
                return session.query(model_class).filter(model_class.id == id).first()
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"查询记录失败: {str(e)}")

    def get_all(self, model_class: Type[T]) -> List[T]:
        """
        获取所有记录
        """
        try:
            with self.session() as session:
                return session.query(model_class).all()
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"查询所有记录失败: {str(e)}")

    def find(self, model_class: Type[T], **filters) -> List[T]:
        """
        根据过滤条件查询记录
        """
        try:
            with self.session() as session:
                query = session.query(model_class)
                for attr, value in filters.items():
                    query = query.filter(getattr(model_class, attr) == value)
                return query.all()
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"查询记录失败: {str(e)}")

    def create(self, model: T) -> T:
        """
        创建记录
        """
        try:
            with self.session() as session:
                session.add(model)
                session.flush()
                session.refresh(model)
                return model
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"创建记录失败: {str(e)}")

    def update(self, model: T) -> T:
        """
        更新记录
        """
        try:
            with self.session() as session:
                session.merge(model)
                session.flush()
                session.refresh(model)
                return model
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"更新记录失败: {str(e)}")

    def delete(self, model: T) -> bool:
        """
        删除记录
        """
        try:
            with self.session() as session:
                session.delete(model)
                return True
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"删除记录失败: {str(e)}")

    def delete_by_id(self, model_class: Type[T], id: Any) -> bool:
        """
        根据ID删除记录
        """
        try:
            with self.session() as session:
                model = session.query(model_class).filter(model_class.id == id).first()
                if model:
                    session.delete(model)
                    return True
                return False
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"删除记录失败: {str(e)}")

    def execute_raw_sql(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        执行原始SQL查询
        """
        try:
            with self.session() as session:
                result = session.execute(text(sql), params or {})
                return [dict(row) for row in result]
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"执行SQL查询失败: {str(e)}")


# 创建全局数据库实例，方便导入使用
try:
    db = Database()
except DatabaseError as e:
    print(f"数据库初始化失败: {str(e)}")
    # 在实际应用中，可能需要在这里进行适当的错误处理
    # 例如退出程序或使用备用数据库
    raise


# 使用示例
if __name__ == "__main__":
    from models.user import User
    
    try:
        # 创建表
        db.create_tables()
        
        # 创建用户
        new_user = User(
            username="admin",
            password_hash="hashed_password",
            email="admin@example.com",
            full_name="Administrator",
            user_type="admin",
            status="active"
        )
        created_user = db.create(new_user)
        print(f"创建用户成功: ID={created_user.id}, 用户名={created_user.username}")
        
        # 查询用户
        user = db.get_by_id(User, created_user.id)
        print(f"查询用户成功: ID={user.id}, 用户名={user.username}")
        
        # 更新用户
        user.email = "updated@example.com"
        updated_user = db.update(user)
        print(f"更新用户成功: ID={updated_user.id}, 邮箱={updated_user.email}")
        
        # 查询所有用户
        all_users = db.get_all(User)
        print(f"查询所有用户成功: 用户数量={len(all_users)}")
        
        # 根据条件查询用户
        admin_users = db.find(User, user_type="admin")
        print(f"查询管理员用户成功: 用户数量={len(admin_users)}")
        
        # 删除用户
        deleted = db.delete_by_id(User, created_user.id)
        print(f"删除用户{'成功' if deleted else '失败'}")
        
        # 执行原始SQL查询
        result = db.execute_raw_sql("SELECT COUNT(*) as user_count FROM users")
        print(f"用户总数: {result[0]['user_count']}")
        
    except DatabaseError as e:
        print(f"数据库操作失败: {str(e)}")