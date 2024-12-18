from http import HTTPStatus
import dashscope
from openai import OpenAI
from common.log import logger
from plugins.turtle_soup.config_loader import ConfigLoader


class AIHandler:
    DEFAULT_MODELS = {
        "dashscope": "qwen-max",
        "openai": "gpt-3.5-turbo"
    }

    def __init__(self):
        config = ConfigLoader()
        self.dashscope_api_key = config.get('api_config', 'dashscope_api_key')
        self.open_ai_api_base = config.get('api_config', 'open_ai_api_base')
        self._initialize_provider()

    def _initialize_provider(self):
        """初始化 AI 提供商"""
        if self.dashscope_api_key:
            self.provider = "dashscope"
            dashscope.api_key = self.dashscope_api_key
            self.model = self.DEFAULT_MODELS["dashscope"]
        elif self.open_ai_api_base:
            self.provider = "openai"
            self.client = OpenAI(
                api_key=self.open_ai_api_base,
                base_url="https://api.openai.com/v1"
            )
            self.model = self.DEFAULT_MODELS["openai"]
        else:
            # 如果没有配置任何 API，报错
            logger.warning("[turtle_soup] No API configured, will use default responses")
            raise Exception("[turtle_soup] No API configured")

    def get_response(self, question: str, story: dict) -> str:
        """获取 AI 回答"""
        if self.provider == "dashscope":
            return self._get_dashscope_response(question, story)
        else:
            return self._get_openai_response(question, story)

    def _get_dashscope_response(self, question: str, story: dict) -> str:
        prompt = self._create_prompt(question, story)
        try:
            print(f"Calling Dashscope API with prompt: {prompt}")
            response = dashscope.Generation.call(
                model=self.model,  # 使用配置的模型
                prompt=prompt,
                result_format='message'
            )
            print(f"Dashscope API response: {response}")
            if response.status_code == HTTPStatus.OK:
                return response.output.choices[-1]['message']['content']
            else:
                print(f"Dashscope API error: {response.code} - {response.message}")
                return "调用 AI 接口失败"
        except Exception as e:
            print(f"Dashscope API error: {str(e)}")
            return "调用 AI 接口失败"

    def _get_openai_response(self, question: str, story: dict) -> str:
        prompt = self._create_prompt(question, story)
        response = self.client.chat.completions.create(
            model=self.model,  # 使用配置的模型
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _create_prompt(self, question: str, story: dict) -> str:
        return f"""
作为海龟汤游戏的主持人，你需要根据以下信息回答玩家的是/否问题：

故事情境：{story['situation']}
真相：{story['truth']}
背景：{story['background']}

玩家问题：{question}

请只回答"是"或"否", 必要时可以补充一句简短的解释。
"""
