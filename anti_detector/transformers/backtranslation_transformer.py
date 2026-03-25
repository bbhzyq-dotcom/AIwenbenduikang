"""
回译转换器
通过中英互译打乱原始语序，是对抗检测最有效的方法之一
"""

import random
import re
from typing import Optional, Callable, Dict

import requests  # type: ignore


class BackTranslationConfig:
    """回译配置"""

    TRANSLATION_CHAINS = [
        ("en", "zh"),      # 中 -> 英 -> 中
        ("de", "zh"),      # 中 -> 德 -> 中
        ("ja", "zh"),      # 中 -> 日 -> 中
        ("fr", "zh"),      # 中 -> 法 -> 中
        ("en", "de", "zh"), # 中 -> 英 -> 德 -> 中
    ]

    def __init__(
        self,
        api_url: str = "https://api.mymemory.translated.net/get",
        timeout: int = 30,
        source_lang: str = "zh-CN",
        target_langs: Optional[list] = None
    ):
        self.api_url = api_url
        self.timeout = timeout
        self.source_lang = source_lang
        self.target_langs = target_langs or ["en", "de"]


class BackTranslator:
    """回译转换器 - 通过翻译重排打破AI文本模式"""

    def __init__(
        self,
        config: Optional[BackTranslationConfig] = None,
        intensity: float = 0.2
    ):
        self.config = config or BackTranslationConfig()
        self.intensity = intensity
        self._cache: Dict[str, str] = {}

    def _translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """调用翻译API"""
        cache_key = f"{text}:{from_lang}:{to_lang}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            params = {
                "q": text,
                "langpair": f"{from_lang}|{to_lang}"
            }
            response = requests.get(
                self.config.api_url,
                params=params,
                timeout=self.config.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    result = data["responseData"]["translatedText"]
                    self._cache[cache_key] = result
                    return result
        except Exception:
            pass

        return None

    def _translate_with_cache(self, text: str, from_lang: str, to_lang: str) -> str:
        """带缓存的翻译，失败时返回原文"""
        result = self._translate(text, from_lang, to_lang)
        return result if result else text

    def back_translate(self, text: str, chain: tuple = ("en", "zh")) -> str:
        """
        执行回译

        Args:
            text: 原文
            chain: 翻译链，如 ("en", "zh") 表示中->英->中

        Returns:
            回译后的文本
        """
        if len(chain) < 2:
            return text

        current = text
        for i in range(len(chain) - 1):
            from_lang = chain[i]
            to_lang = chain[i + 1]
            current = self._translate_with_cache(current, from_lang, to_lang)

        return current

    def smart_back_translate(self, text: str) -> str:
        """
        智能选择翻译链进行回译

        根据文本长度和内容特点选择最合适的翻译路径
        """
        if random.random() > self.intensity:
            return text

        # 根据文本长度选择翻译链
        if len(text) < 50:
            chain = ("en", "zh")
        elif len(text) < 150:
            chain = random.choice([("en", "zh"), ("de", "zh")])
        else:
            chain = random.choice(self.config.TRANSLATION_CHAINS)

        return self.back_translate(text, chain)

    def batch_back_translate(
        self,
        texts: list,
        chain: tuple = ("en", "zh"),
        progress_callback: Optional[Callable] = None
    ) -> list:
        """批量回译"""
        results = []
        for i, text in enumerate(texts):
            result = self.back_translate(text, chain)
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, len(texts))

        return results

    def clear_cache(self) -> None:
        """清空翻译缓存"""
        self._cache.clear()
