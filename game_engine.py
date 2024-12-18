import json
import time
import os
from typing import Dict
import random
from common.log import logger
from plugins.turtle_soup.config_loader import ConfigLoader

class GameEngine:
    def __init__(self):
        self.config = ConfigLoader()
        self.current_game: Dict = {}
        self.start_time: float = 0
        self.score: int = self.config.get('scoring', 'max_score', default=100)
        self.is_gaming: bool = False
        self.stories = {}
        self._load_stories()
        
    def _load_stories(self):
        """加载故事池"""
        stories_file = os.path.join(os.path.dirname(__file__), "stories.json")
        
        try:
            if os.path.exists(stories_file):
                with open(stories_file, "r", encoding="utf-8") as f:
                    self.stories = json.load(f)
            else:
                self.stories = self._get_empty_story_structure()
                
        except Exception as e:
            logger.error(f"[turtle_soup] Failed to load stories: {e}")
            self.stories = self._get_empty_story_structure()
            
    @staticmethod
    def _get_empty_story_structure() -> Dict:
        """获取空的故事结构"""
        return {
            "easy": [],
            "medium": [],
            "hard": [],
            "extreme": []
        }
        
    def add_custom_story(self, story: Dict, difficulty: str = "medium") -> bool:
        """添加自定义故事"""
        try:
            # 验证故事格式
            required_fields = ["title", "situation", "truth", "background", "hints"]
            if not all(field in story for field in required_fields):
                return False
                
            # 生成唯一ID
            story_id = f"custom_{int(time.time())}"
            story["id"] = story_id
            
            # 确保难度级别存在
            if difficulty not in self.stories:
                self.stories[difficulty] = []
                
            # 添加到故事池
            self.stories[difficulty].append(story)
            
            # 保存所有故事
            try:
                stories_file = os.path.join(os.path.dirname(__file__), "stories.json")
                with open(stories_file, "w", encoding="utf-8") as f:
                    json.dump(self.stories, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                logger.error(f"[turtle_soup] Failed to save story: {e}")
                return False
                
        except Exception as e:
            logger.error(f"[turtle_soup] Failed to add story: {e}")
            return False
            
    def remove_custom_story(self, story_id: str) -> bool:
        """删除自定义故事"""
        try:
            # 从内存中删除
            for difficulty in self.stories:
                self.stories[difficulty] = [
                    story for story in self.stories[difficulty] 
                    if story["id"] != story_id or not story["id"].startswith("custom_")
                ]
                
            # 从文件中删除
            try:
                custom_pool = os.path.join(os.path.dirname(__file__), "stories", "custom.json")
                if not os.path.exists(custom_pool):
                    return False
                    
                with open(custom_pool, "r", encoding="utf-8") as f:
                    custom_stories = json.load(f)
                    
                modified = False
                for difficulty in custom_stories:
                    original_length = len(custom_stories[difficulty])
                    custom_stories[difficulty] = [
                        story for story in custom_stories[difficulty]
                        if story["id"] != story_id
                    ]
                    if len(custom_stories[difficulty]) != original_length:
                        modified = True
                        
                if modified:
                    with open(custom_pool, "w", encoding="utf-8") as f:
                        json.dump(custom_stories, f, ensure_ascii=False, indent=2)
                        
                return modified
            except FileNotFoundError:
                return False
                
        except Exception as e:
            logger.error(f"[turtle_soup] Failed to remove custom story: {e}")
            return False

    def start_game(self, difficulty: str = "medium") -> str:
        """开始新游戏"""
        if difficulty not in self.stories:
            difficulty = "medium"
            
        story = random.choice(self.stories[difficulty])
        self.current_game = story
        self.start_time = time.time()
        self.score = 100
        self.is_gaming = True
        
        return f"【海龟汤】\n\n{story['situation']}\n\n请开始提问吧！记住只能问是/否问题。"
    
    def end_game(self) -> str:
        """结束游戏"""
        if not self.is_gaming:
            return "当前没有进行中的游戏！"
            
        result = f"""
游戏结束！
最终得分：{self.score}分

【真相揭秘】
{self.current_game['truth']}

【背景故事】
{self.current_game['background']}
"""
        self.is_gaming = False
        return result
    
    def get_hint(self) -> str:
        """获取提示"""
        if not self.is_gaming:
            return "当前没有进行中的游戏！"
            
        hint = random.choice(self.current_game['hints'])
        self.score -= 5  # 使用提示扣5分
        return f"提示：{hint}\n当前得分：{self.score}"
    
    def update_score(self) -> None:
        """更新分数"""
        elapsed_minutes = (time.time() - self.start_time) / 60
        penalty_factor = self.config.get('scoring', 'penalty_time_factor', default=0.5)
        time_penalty = int(elapsed_minutes * penalty_factor)
        self.score = max(0, self.score - time_penalty) 
