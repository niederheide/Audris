import os
from typing import Dict, Any, Optional

class Config:
    """
    Configuration manager for the DORA Assessment Agent.
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        "app_name": "DORA Assessment Agent",
        "app_version": "0.1.0",
        "database_path": "dora_register.db",
        "log_level": "INFO",
        "log_file": "dora_assessment.log",
        "max_upload_size_mb": 10,
        "enable_advanced_nlp": True,
        "enable_openai": True,
        "openai_model": "gpt-4o" # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    }
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "APP_NAME": "app_name",
            "APP_VERSION": "app_version",
            "DATABASE_PATH": "database_path",
            "LOG_LEVEL": "log_level",
            "LOG_FILE": "log_file",
            "MAX_UPLOAD_SIZE_MB": "max_upload_size_mb",
            "ENABLE_ADVANCED_NLP": "enable_advanced_nlp",
            "ENABLE_OPENAI": "enable_openai",
            "OPENAI_MODEL": "openai_model"
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Handle type conversion
                if config_key == "max_upload_size_mb":
                    self.config[config_key] = int(env_value)
                elif config_key in ["enable_advanced_nlp", "enable_openai"]:
                    self.config[config_key] = env_value.lower() in ["true", "1", "yes"]
                else:
                    self.config[config_key] = env_value
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary with all configuration values
        """
        return self.config.copy()
    
    def get_sensitive_keys(self) -> Dict[str, bool]:
        """
        Get keys that should be treated as sensitive/confidential.
        
        Returns:
            Dictionary with sensitive keys and True values
        """
        return {
            "openai_api_key": True
        }
    
    def get_openai_api_key(self) -> Optional[str]:
        """
        Get the OpenAI API key from environment variable.
        
        Returns:
            OpenAI API key or None if not found
        """
        return os.getenv("OPENAI_API_KEY")
    
    def is_openai_enabled(self) -> bool:
        """
        Check if OpenAI integration is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self.get("enable_openai", False) and self.get_openai_api_key() is not None

# Create a global configuration instance
config = Config()
