from common.log import logger

try:
    logger.info("[turtle_soup] Loading plugin module...")
    from plugins.turtle_soup.turtle_soup import TurtleSoupPlugin
    from plugins.turtle_soup.config_loader import ConfigLoader
    from plugins.turtle_soup.game_engine import GameEngine
    from plugins.turtle_soup.ai_handler import AIHandler
    
    __all__ = ["TurtleSoupPlugin", "ConfigLoader", "GameEngine", "AIHandler"]
    logger.info("[turtle_soup] Plugin module loaded successfully")
except Exception as e:
    logger.error(f"[turtle_soup] Failed to import plugin: {e}")
    raise
