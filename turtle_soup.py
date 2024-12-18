import json
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
import plugins
from plugins.plugin import Plugin
from plugins.event import EventContext, EventAction, Event
from plugins.turtle_soup.config_loader import ConfigLoader
from plugins.turtle_soup.game_engine import GameEngine
from plugins.turtle_soup.ai_handler import AIHandler

@plugins.register(
    name="turtle_soup",
    title="海龟汤游戏",
    desc="一个有趣的海龟汤文字推理游戏",
    version="1.0",
    author="yuehj-ww",
    desire_priority=0,
    namecn="海龟汤",
    hidden=False
)
class TurtleSoupPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.config = ConfigLoader()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        self.game = GameEngine()
        
        # 获取关键词配置
        self.start_keyword = self.config.get('keywords', 'start', default="开始汤")
        self.end_keyword = self.config.get('keywords', 'end', default="结束汤")
        self.tip_keyword = self.config.get('keywords', 'tip', default="提示")
        
    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        
        content = e_context['context'].content.strip()
        
        # 添加自定义故事命令处理
        if content.startswith("添加故事"):
            try:
                # 期望格式: 添加故事 难度 {"title": "标题", ...}
                parts = content.split(maxsplit=2)
                if len(parts) != 3:
                    raise ValueError("格式错误")
                
                difficulty = parts[1]
                story_data = json.loads(parts[2])
                
                if self.game.add_custom_story(story_data, difficulty):
                    reply = "添加自定义故事成功！"
                else:
                    reply = "添加自定义故事失败，请检查格式是否正确。"
                
            except Exception as e:
                reply = f"添加故事失败: {str(e)}"
                
            e_context['reply'] = Reply(ReplyType.TEXT, reply)
            e_context.action = EventAction.BREAK_PASS
            return
        
        # 删除自定义故事命令处理
        elif content.startswith("删除故事"):
            try:
                story_id = content.split()[1]
                if self.game.remove_custom_story(story_id):
                    reply = "删除自定义故事成功！"
                else:
                    reply = "删除故事失败，可能故事ID不存在或不是自定义故事。"
                
            except Exception as e:
                reply = f"删除故事失败: {str(e)}"
                
            e_context['reply'] = Reply(ReplyType.TEXT, reply)
            e_context.action = EventAction.BREAK_PASS
            return
        
        if content.startswith(self.start_keyword):
            # 解析难度等级
            parts = content.split()
            difficulty = None
            if len(parts) > 1:
                difficulty_map = self.config.get('game_settings', 'difficulty_levels')
                difficulty = difficulty_map.get(parts[1])
            
            reply = self.game.start_game(difficulty)
            e_context['reply'] = Reply(ReplyType.TEXT, reply)
            e_context.action = EventAction.BREAK_PASS
            
        elif content == self.end_keyword:
            reply = self.game.end_game()
            e_context['reply'] = Reply(ReplyType.TEXT, reply)
            e_context.action = EventAction.BREAK_PASS
            
        elif content == self.tip_keyword:
            reply = self.game.get_hint()
            e_context['reply'] = Reply(ReplyType.TEXT, reply)
            e_context.action = EventAction.BREAK_PASS
            
        elif self.game.is_gaming:
            # 处理问题并扣分
            self.game.score -= self.config.get('scoring', 'penalty_per_question', default=2)
            # 调用 AI 接口处理题
            try:
                ai = AIHandler()
                response = ai.get_response(content, self.game.current_game)
                e_context['reply'] = Reply(ReplyType.TEXT, response)
            except Exception as e:
                logger.error(f"[turtle_soup] AI response failed: {e}")
                e_context['reply'] = Reply(ReplyType.TEXT, "抱歉，AI 回答出现问题")
            e_context.action = EventAction.BREAK_PASS
        
    def get_help_text(self, **kwargs):
        help_text = """海龟汤文字推理游戏帮助：
1. 发送"开始汤 [难度]"开始游戏，难度可选：简单、中等、高等、炼狱
2. 通过是/否问题来推理故事真相
3. 发送"提示"获取提示
4. 发送"结束汤"结束游戏

自定义故事：
5. 发送"添加故事 [难度] {故事数据}"添加自定义故事
6. 发送"删除故事 [故事ID]"删除自定义故事

故事数据格式例：
{
    "title": "标题",
    "situation": "情境描述",
    "truth": "真相",
    "background": "背景故事",
    "hints": ["提示1", "提示2", "提示3"]
}
"""
        return help_text
