import json
import os
from pathlib import Path

def load_config():
    """Загрузка конфигурации приложения"""
    config_path = Path(__file__).parent.parent / 'config.json'
    
    if not config_path.exists():
        raise FileNotFoundError("Config file not found")
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Проверка обязательных параметров
    required_keys = ['database']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    return config