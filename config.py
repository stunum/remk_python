"""
配置模块 - 使用单例模式和结构化模型读取YAML配置文件
"""
import os
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


# 定义与config.yaml对应的结构模型类
@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    user: str
    password: str
    dbname: str
    sslmode: str
    timezone: str
    max_idle_conns: int
    max_open_conns: int
    conn_max_lifetime: int
    log_level: str


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str
    port: int


@dataclass
class ThirdPartyConfig:
    """第三方服务配置"""
    base_url: str
    port: int
    timeout: int
    retry_count: int


@dataclass
class JWTConfig:
    """JWT配置"""
    secret_key: str
    token_expire_hours: int


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str
    format: str
    output: str
    file_path: str
    report_caller: bool
    rotation: str
    retention: str
    compression: str

@dataclass
class AppConfig:
    """应用总配置"""
    database: DatabaseConfig
    server: ServerConfig
    third_party: ThirdPartyConfig
    jwt: JWTConfig
    logging: LoggingConfig
    save_folder_path: str


class ConfigError(Exception):
    """配置错误异常"""
    pass


class Config:
    """
    配置类 - 单例模式
    使用PyYAML读取config.yaml文件，确保全局唯一实例
    使用结构化模型提供类型安全的配置访问
    """
    _instance = None
    _config: Optional[AppConfig] = None
    _config_file_path: str = "config.yaml"
    
    def __new__(cls, config_file_path: Optional[str] = None):
        """
        单例模式实现
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            if config_file_path:
                cls._config_file_path = config_file_path
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """
        从YAML文件加载配置到结构化模型
        当配置值缺失时抛出错误
        """
        try:
            # 获取当前文件所在目录的绝对路径
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建配置文件的绝对路径
            config_path = os.path.join(base_dir, self._config_file_path)
            
            # 检查文件是否存在
            if not os.path.exists(config_path):
                raise ConfigError(f"配置文件不存在: {config_path}")
            
            # 读取并解析YAML文件
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                
            # 将配置数据映射到结构化模型
            self._update_config_from_dict(config_data)
                
        except ConfigError as e:
            # 直接重新抛出配置错误
            raise
        except Exception as e:
            # 将其他异常包装为配置错误
            raise ConfigError(f"加载配置文件失败: {str(e)}")
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """
        将字典数据更新到结构化配置模型
        当必要的配置值缺失时抛出错误
        """
        # 检查必要的顶级配置项
        required_sections = ['database', 'server', 'third_party', 'jwt', 'logging', 'save_folder_path']
        missing_sections = [section for section in required_sections if section not in config_data]
        if missing_sections:
            raise ConfigError(f"配置文件缺少必要的配置项: {', '.join(missing_sections)}")
        
        try:
            # 数据库配置
            db_config = config_data['database']
            self._config = AppConfig(
                database=DatabaseConfig(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    dbname=db_config['dbname'],
                    sslmode=db_config['sslmode'],
                    timezone=db_config['timezone'],
                    max_idle_conns=db_config['max_idle_conns'],
                    max_open_conns=db_config['max_open_conns'],
                    conn_max_lifetime=db_config['conn_max_lifetime'],
                    log_level=db_config['log_level']
                ),
                server=ServerConfig(
                    host=config_data['server']['host'],
                    port=config_data['server']['port']
                ),
                third_party=ThirdPartyConfig(
                    base_url=config_data['third_party']['base_url'],
                    port=config_data['third_party']['port'],
                    timeout=config_data['third_party']['timeout'],
                    retry_count=config_data['third_party']['retry_count']
                ),
                jwt=JWTConfig(
                    secret_key=config_data['jwt']['secret_key'],
                    token_expire_hours=config_data['jwt']['token_expire_hours']
                ),
                logging=LoggingConfig(
                    level=config_data['logging']['level'],
                    format=config_data['logging']['format'],
                    output=config_data['logging']['output'],
                    file_path=config_data['logging']['file_path'],
                    report_caller=config_data['logging']['report_caller'],
                    rotation=config_data['logging']['rotation'],
                    retention=config_data['logging']['retention'],
                    compression=config_data['logging']['compression']
                ),
                save_folder_path=config_data['save_folder_path']
            )
        except KeyError as e:
            # 当缺少必要的配置项时抛出错误
            raise ConfigError(f"配置文件缺少必要的配置项: {str(e)}")
    
    @property
    def config(self) -> AppConfig:
        """
        获取结构化配置对象
        """
        if self._config is None:
            raise ConfigError("配置未加载或加载失败")
        return self._config
    
    def save(self):
        """
        将当前配置保存到YAML文件
        """
        if self._config is None:
            raise ConfigError("配置未加载或加载失败，无法保存")
            
        try:
            # 获取当前文件所在目录的绝对路径
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建配置文件的绝对路径
            config_path = os.path.join(base_dir, self._config_file_path)
            
            # 将结构化配置转换为字典
            config_dict = self._config_to_dict()
            
            # 写入YAML文件
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config_dict, file, default_flow_style=False, sort_keys=False)
                
            return True
        except Exception as e:
            raise ConfigError(f"保存配置文件失败: {str(e)}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """
        将结构化配置转换为字典
        """
        if self._config is None:
            raise ConfigError("配置未加载或加载失败，无法转换为字典")
        return asdict(self._config)
    
    def reload(self):
        """
        重新加载配置文件
        """
        self._load_config()


# 创建全局配置实例，方便导入使用
try:
    config = Config()
except ConfigError as e:
    print(f"配置初始化失败: {str(e)}")
    # 在实际应用中，可能需要在这里进行适当的错误处理
    # 例如退出程序或使用备用配置
    raise


# 使用示例
if __name__ == "__main__":
    try:
        # 访问数据库配置
        print(f"数据库主机: {config.config.database.host}")
        print(f"数据库端口: {config.config.database.port}")
        
        # 访问日志配置
        print(f"日志级别: {config.config.logging.level}")
        
        # 修改配置
        config.config.database.host = "127.0.0.1"
        config.config.logging.level = "debug"
        
        # 保存修改后的配置
        config.save()
        print("配置已保存")
        
        # 重新加载配置
        config.reload()
        print(f"重新加载后的数据库主机: {config.config.database.host}")
    except ConfigError as e:
        print(f"配置错误: {str(e)}")