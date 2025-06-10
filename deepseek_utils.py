from openai import OpenAI
import urllib3
import httpx
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

class ChatBot:
    def __init__(self,
                 system_prompt: str,
                 model: str = "deepseek-chat",
                 temperature: float = 0.7,
                 max_tokens: int = 8192,
                 **kwargs):
        """
        初始化 ChatBot 实例。

        参数:
        - system_prompt: 系统初始化提示，用于设置对话的上下文。
        - model: 使用的模型名称，默认 "deepseek-chat"。
        - temperature: 控制回答的随机性，默认为 0.7。
        - max_tokens: 生成回答的最大 token 数量，默认为 150。
        - kwargs: 其他可能传递给 openai.ChatCompletion.create 的参数.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_params = kwargs

        self.client = OpenAI(
            api_key=API_KEY,
            base_url="https://api.deepseek.com",
            http_client=httpx.Client(verify=False)

        )

        # 初始消息列表中加入 system 提示
        self.reasoning_contents = []
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]

    def chat(self, s: str) -> str:
        """
        发送用户消息并获取模型响应.

        参数:
        - s: 用户输入的字符串.

        返回:
        - 模型生成的响应内容字符串.
        """
        # 添加用户的消息到对话历史中
        self.messages.append({"role": "user", "content": s})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **self.extra_params
            )

            # 获取模型的回复内容
            reply_content = response.choices[0].message.content
            if hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning_content = response.choices[0].message.reasoning_content
                self.reasoning_contents.append(reasoning_content)
            # 将模型回复加入对话历史便于上下文延续
            self.messages.append({"role": "assistant", "content": reply_content})

            return reply_content
        except Exception as e:
            # 捕获异常并返回错误消息
            return f"调用 ChatCompletion API 时出错: {str(e)}"
