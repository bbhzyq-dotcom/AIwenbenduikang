"""
LLM接口模块
支持多种LLM后端，用于辅助去AI味
"""

import os
import json
import random
import re
from typing import Optional, List, Dict, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM配置"""
    model: str = "gpt-3.5-turbo"
    api_base: str = "https://api.openai.com/v1"
    api_key: Optional[str] = None
    timeout: int = 60
    max_tokens: int = 2000
    temperature: float = 0.7


class BaseLLMClient(ABC):
    """LLM客户端基类"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文本"""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        pass


class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI兼容接口（支持OpenAI、vLLM、LocalAI等）"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()

    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """发送请求"""
        try:
            import requests

            headers = {
                "Content-Type": "application/json",
            }
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"

            data = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }

            response = requests.post(
                f"{self.config.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")

        except ImportError:
            raise ImportError("requests library is required. Install with: pip install requests")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        result = self._make_request(messages, **kwargs)
        return result["choices"][0]["message"]["content"]


class OllamaClient(BaseLLMClient):
    """Ollama本地模型接口"""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        timeout: int = 120
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文本"""
        try:
            import requests

            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
            if system_prompt:
                data["system"] = system_prompt

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()["response"]
            else:
                raise Exception(f"Ollama Error: {response.status_code}")

        except ImportError:
            raise ImportError("requests library is required")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        try:
            import requests

            # Ollama使用不同的API格式
            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                raise Exception(f"Ollama Error: {response.status_code}")

        except ImportError:
            raise ImportError("requests library is required")


class LLMDeAIFier:
    """
    LLM去AI味处理器

    专门用于对AI生成的文本进行润色，使其更像人类写作
    """

    # 去AI味的系统提示词
    SYSTEM_PROMPT = """你是一位资深的人类写作润色专家。你的任务是将AI生成的文本改写成更像人类自然写作的风格。

重要原则：
1. 保持原文的核心含义不变
2. 增加人类写作的自然不规则性
3. 适当打破完美句式结构
4. 添加合理的语言变化
5. 移除过于机械化的表达
6. 不要添加新的实质性内容

具体技巧：
- 将部分长句拆分成短句
- 添加人类常见的思考停顿（嗯、这个、话说回来）
- 打破AI过于一致的句子长度
- 使用更口语化或多样化的连接词
- 引入轻微的逻辑跳跃模拟人类思维
- 保持适度的冗余和重复（人类写作特征）"""

    # 针对不同场景的提示词
    SCENE_PROMPTS = {
        "academic": """你是一位资深的人类学术写作者。润色学术文本，使其更像经验丰富的学者在咖啡馆里写的随笔，而非AI生成的正式论文。

特点：
- 可以使用轻微的口语化表达
- 句式可以稍微松散
- 允许一个段落内偶尔的思维跳跃
- 使用更人性化的过渡""",

        "novel": """你是一位资深的小说作家。润色小说文本，使其更生动自然，像是在咖啡馆里向你讲述的故事。

特点：
- 对话可以更自然
- 描述可以更随性
- 允许使用感叹词和口语
- 心理描写可以更跳跃
- 添加合理的语气词""",

        "general": """将文本改写得更加自然、有人情味。
        
要点：
- 打破AI的完美句式
- 添加自然的停顿和语气
- 模拟人类写作的不完美但真实的风格"""
    }

    def __init__(self, llm_client: BaseLLMClient, scene: str = "general"):
        self.llm = llm_client
        self.scene = scene

    def polish(self, text: str, intensity: str = "medium") -> str:
        """
        润色文本去AI味

        Args:
            text: 待润色的文本
            intensity: 润色强度 ("light", "medium", "strong")

        Returns:
            润色后的文本
        """
        if not text or len(text.strip()) < 10:
            return text

        if intensity == "light":
            prompt = self._build_light_prompt(text)
        elif intensity == "strong":
            prompt = self._build_strong_prompt(text)
        else:
            prompt = self._build_medium_prompt(text)

        try:
            result = self.llm.generate(prompt, self._get_system_prompt())
            return result.strip()
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return text

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        base = self.SYSTEM_PROMPT
        if self.scene in self.SCENE_PROMPTS:
            base += "\n\n" + self.SCENE_PROMPTS[self.scene]
        return base

    def _build_light_prompt(self, text: str) -> str:
        """轻度润色提示词"""
        return f"""请对以下文本进行轻微润色，保持原意，只做必要的调整：

原文：
{text}

要求：
- 只改变明显的AI特征
- 保持原有句式结构
- 不添加新内容
- 输出润色后的文本"""

    def _build_medium_prompt(self, text: str) -> str:
        """中度润色提示词"""
        return f"""请对以下文本进行中等程度润色，改变其AI写作特征：

原文：
{text}

要求：
- 打破过于规整的句子结构
- 增加自然的语言变化
- 可以拆分部分长句
- 保持核心含义
- 输出润色后的文本"""

    def _build_strong_prompt(self, text: str) -> str:
        """强力润色提示词"""
        return f"""请对以下文本进行强力润色，彻底改变其AI写作风格：

原文：
{text}

要求：
- 完全打破AI的机械感
- 重写成更自然的人类写作风格
- 增加适度的口语化和不完美
- 可以添加轻微的思维跳跃
- 保持原文的核心信息和结构
- 输出润色后的文本"""


class LLMTextRepair:
    """
    LLM文本修复器

    专门用于修复变换过程中可能引入的语法错误或不通顺的句子
    """

    SYSTEM_PROMPT = """你是一位资深的中文文本校对专家。你的任务是修复文本中的语法错误和不通顺的句子，同时保持原文的风格和含义。

重要原则：
1. 只修复错误，不改变正确的内容
2. 保持原文的语气和风格
3. 不要过度修改
4. 特别关注：
   - 主谓宾搭配不当
   - 标点符号错误
   - 句式杂糅
   - 语义不通顺
5. 如果原文没有问题，直接输出原文"""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm = llm_client

    def repair(self, text: str) -> str:
        """
        修复文本

        Args:
            text: 待修复的文本

        Returns:
            修复后的文本
        """
        if not text or len(text.strip()) < 10:
            return text

        prompt = f"""请检查并修复以下文本中的语法错误和不通顺的句子：

原文：
{text}

要求：
- 只修复错误，不改变正确的内容
- 保持原文风格
- 不添加新内容
- 输出修复后的文本，如果原文没有问题则直接输出原文"""

        try:
            result = self.llm.generate(prompt, self.SYSTEM_PROMPT)
            return result.strip()
        except Exception as e:
            print(f"LLM修复失败: {e}")
            return text


class HybridAntiAI:
    """
    混合反AI系统

    结合传统变换方法和LLM润色，达到最佳效果
    """

    def __init__(
        self,
        traditional_engine,  # AntiDetector引擎
        llm_client: Optional[BaseLLMClient] = None,
        use_llm: bool = True,
        llm_strategy: str = "repair"  # "polish" | "repair" | "both"
    ):
        self.traditional_engine = traditional_engine
        self.llm_client = llm_client
        self.use_llm = use_llm and (llm_client is not None)
        self.llm_strategy = llm_strategy

        if self.use_llm:
            self.de_aifier = LLMDeAIFier(llm_client)
            self.repairer = LLMTextRepair(llm_client)

    def transform(self, text: str, use_llm: bool = None) -> str:
        """
        变换文本

        Args:
            text: 输入文本
            use_llm: 是否使用LLM（覆盖初始化设置）

        Returns:
            变换后的文本
        """
        # 步骤1: 传统变换
        result = self.traditional_engine.transform(text)

        # 步骤2: LLM润色/修复
        if use_llm if use_llm is not None else self.use_llm:
            strategy = self.llm_strategy

            if strategy in ["polish", "both"]:
                result = self.de_aifier.polish(result, intensity="medium")

            if strategy in ["repair", "both"]:
                result = self.repairer.repair(result)

        return result

    def transform_long_text(
        self,
        text: str,
        min_length: int = 500,
        paragraph_llm: bool = False
    ) -> str:
        """
        变换长文本

        Args:
            text: 输入文本
            min_length: 启用长文本处理的最小长度
            paragraph_llm: 是否对每个段落单独使用LLM

        Returns:
            变换后的文本
        """
        # 短文本直接处理
        if len(text) < min_length:
            return self.transform(text)

        # 长文本分段处理
        paragraphs = text.split('\n\n')
        results = []

        for para in paragraphs:
            if len(para.strip()) < 50:
                # 短段落只做传统变换
                results.append(self.traditional_engine.transform(para))
            elif paragraph_llm and self.use_llm:
                # 较长段落使用混合方法
                transformed = self.traditional_engine.transform(para)
                transformed = self.de_aifier.polish(transformed, intensity="light")
                results.append(transformed)
            else:
                # 标准处理
                results.append(self.transform(para))

        return '\n\n'.join(results)


def create_ollama_client(
    model: str = "llama3.2",
    base_url: str = "http://localhost:11434"
) -> OllamaClient:
    """创建Ollama客户端"""
    return OllamaClient(model=model, base_url=base_url)


def create_openai_client(
    api_key: Optional[str] = None,
    api_base: str = "https://api.openai.com/v1",
    model: str = "gpt-3.5-turbo"
) -> OpenAICompatibleClient:
    """创建OpenAI兼容客户端"""
    config = LLMConfig(
        api_key=api_key or os.environ.get("OPENAI_API_KEY"),
        api_base=api_base,
        model=model
    )
    return OpenAICompatibleClient(config)


def create_vllm_client(
    api_base: str = "http://localhost:8000",
    model: str = "meta-llama/Llama-3.2"
) -> OpenAICompatibleClient:
    """创建vLLM客户端"""
    config = LLMConfig(
        api_base=api_base,
        model=model
    )
    return OpenAICompatibleClient(config)
