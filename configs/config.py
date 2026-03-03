import json
from pathlib import Path
from typing import Any


class Config:
    """配置管理类，用于加载和管理项目配置"""
    _instance = None
    _config_data: dict[str, Any] = {}
    _schema_data: dict[str, Any] = {}
    
    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not self._config_data:
            self.load_config()
        if not self._schema_data:
            self.load_schema()
    
    def load_config(self) -> None:
        """加载配置文件"""
        config_path = Path(__file__).parent / "config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config_data = json.load(f)
        except FileNotFoundError:
            self._config_data = {}
            print(f"警告：配置文件 {config_path} 未找到")
        except json.JSONDecodeError as e:
            self._config_data = {}
            print(f"警告：配置文件格式错误 - {e}")
    
    def load_schema(self) -> None:
        """加载 schema 文件"""
        schema_path = Path(__file__).parent / "schema.json"
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                self._schema_data = json.load(f)
        except FileNotFoundError:
            self._schema_data = {}
            print(f"警告：schema 文件 {schema_path} 未找到")
        except json.JSONDecodeError as e:
            self._schema_data = {}
            print(f"警告：schema 文件格式错误 - {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持嵌套键（如 'models.claude.api_key'）"""
        keys = key.split(".")
        value = self._config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值，支持嵌套键"""
        keys = key.split(".")
        config = self._config_data
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """保存配置到文件"""
        config_path = Path(__file__).parent / "config.json"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败：{e}")
            return False

    @property
    def schema(self) -> dict[str, Any]:
        """获取 schema 配置"""
        return self._schema_data


