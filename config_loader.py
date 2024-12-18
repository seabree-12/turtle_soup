import json
import os
from common.log import logger

class ConfigLoader:
    def __init__(self):
        self.config = {}
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # 默认配置
                self.config = {
                    "keywords": {
                        "start": "开始汤",
                        "end": "结束汤",
                        "tip": "提示"
                    },
                    "scoring": {
                        "penalty_per_question": 2,
                        "max_score": 100
                    },
                    "game_settings": {
                        "difficulty_levels": {
                            "简单": "easy",
                            "中等": "medium",
                            "高等": "hard",
                            "炼狱": "extreme"
                        }
                    }
                }
                # 保存默认配置
                self.save_config()
        except Exception as e:
            logger.error(f"[turtle_soup] Failed to load config: {e}")
            raise

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"[turtle_soup] Failed to save config: {e}")
            raise

    def get(self, section, key, default=None):
        """获取配置项"""
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception:
            return default
