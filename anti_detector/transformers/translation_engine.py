"""
翻译引擎模块
支持多种免费翻译API
"""

import random
import time
from typing import Optional, Dict, List
from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    """翻译器基类"""

    @abstractmethod
    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """翻译文本"""
        pass

    def back_translate(self, text: str, chain: tuple = ("en", "zh")) -> str:
        """回译"""
        if len(chain) < 2:
            return text

        current = text
        for i in range(len(chain) - 1):
            from_lang = chain[i]
            to_lang = chain[i + 1]
            result = self.translate(current, from_lang, to_lang)
            if result:
                current = result
            else:
                return text

        return current


class MyMemoryTranslator(BaseTranslator):
    """MyMemory免费翻译API"""

    def __init__(self, timeout: int = 30):
        self.api_url = "https://api.mymemory.translated.net/get"
        self.timeout = timeout
        self._cache: Dict[str, str] = {}

    def translate(self, text: str, from_lang: str = "zh-CN", to_lang: str = "en") -> Optional[str]:
        if not text:
            return text

        cache_key = f"{text}:{from_lang}:{to_lang}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            import requests
            params = {"q": text, "langpair": f"{from_lang}|{to_lang}"}
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    result = data["responseData"]["translatedText"]
                    self._cache[cache_key] = result
                    return result
        except Exception:
            pass

        return None


class GoogleTranslator(BaseTranslator):
    """Google Translate API (使用非官方免费接口)"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._cache: Dict[str, str] = {}

    def translate(self, text: str, from_lang: str = "zh-CN", to_lang: str = "en") -> Optional[str]:
        if not text:
            return text

        cache_key = f"{text}:{from_lang}:{to_lang}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            import requests

            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": from_lang,
                "tl": to_lang,
                "dt": "t",
                "q": text
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    result = "".join(item[0] for item in data[0] if item[0])
                    self._cache[cache_key] = result
                    return result
        except Exception:
            pass

        return None


class DeepLTranslator(BaseTranslator):
    """DeepL免费API"""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or "0" * 36
        self.api_url = "https://api-free.deepl.com/v2/translate" if not api_key else "https://api.deepl.com/v2/translate"
        self.timeout = timeout
        self._cache: Dict[str, str] = {}

    def translate(self, text: str, from_lang: str = "ZH", to_lang: str = "EN") -> Optional[str]:
        if not text:
            return text

        cache_key = f"{text}:{from_lang}:{to_lang}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            import requests

            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            data = {
                "text": text,
                "source_lang": from_lang,
                "target_lang": to_lang
            }

            response = requests.post(self.api_url, headers=headers, data=data, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()["translations"][0]["text"]
                self._cache[cache_key] = result
                return result
        except Exception:
            pass

        return None


class LibreTranslator(BaseTranslator):
    """LibreTranslate免费开源翻译API"""

    def __init__(self, api_url: str = "https://libretranslate.com/translate", timeout: int = 30):
        self.api_url = api_url
        self.timeout = timeout
        self._cache: Dict[str, str] = {}

    def translate(self, text: str, from_lang: str = "zh", to_lang: str = "en") -> Optional[str]:
        if not text:
            return text

        cache_key = f"{text}:{from_lang}:{to_lang}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            import requests

            data = {
                "q": text,
                "source": from_lang,
                "target": to_lang,
                "format": "text"
            }

            response = requests.post(self.api_url, json=data, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()["translatedText"]
                self._cache[cache_key] = result
                return result
        except Exception:
            pass

        return None


class TranslationChain:
    """翻译链管理器 - 核心回译策略"""

    CHAINS = {
        "en": ("en-US", "EN-US"),
        "de": ("de-DE", "DE-DE"),
        "ja": ("ja-JP", "JA-JP"),
        "fr": ("fr-FR", "FR-FR"),
        "es": ("es-ES", "ES-ES"),
        "ko": ("ko-KR", "KO-KR"),
        "ru": ("ru-RU", "RU-RU"),
        "it": ("it-IT", "IT-IT"),
        "pt": ("pt-PT", "PT-PT"),
        "ar": ("ar-SA", "AR-SA"),
    }

    BACKTRANSLATION_PATHS = [
        ("zh-CN", "en", "zh-CN"),
        ("zh-CN", "ja", "zh-CN"),
        ("zh-CN", "de", "zh-CN"),
        ("zh-CN", "fr", "zh-CN"),
        ("zh-CN", "ko", "zh-CN"),
        ("zh-CN", "ru", "zh-CN"),
        ("zh-CN", "es", "zh-CN"),
        ("zh-CN", "it", "zh-CN"),
        ("zh-CN", "pt", "zh-CN"),
        ("zh-CN", "en", "de", "zh-CN"),
        ("zh-CN", "en", "fr", "zh-CN"),
        ("zh-CN", "en", "ja", "zh-CN"),
        ("zh-CN", "ja", "en", "zh-CN"),
        ("zh-CN", "de", "en", "zh-CN"),
        ("zh-CN", "fr", "en", "zh-CN"),
        ("zh-CN", "en", "es", "zh-CN"),
        ("zh-CN", "en", "ko", "zh-CN"),
        ("zh-CN", "ja", "ko", "zh-CN"),
        ("zh-CN", "de", "fr", "zh-CN"),
        ("zh-CN", "en", "ru", "zh-CN"),
    ]

    LONG_TEXT_PATHS = [
        ("zh-CN", "en", "de", "zh-CN"),
        ("zh-CN", "en", "fr", "zh-CN"),
        ("zh-CN", "ja", "en", "zh-CN"),
        ("zh-CN", "en", "ja", "zh-CN"),
        ("zh-CN", "de", "en", "zh-CN"),
        ("zh-CN", "fr", "en", "zh-CN"),
        ("zh-CN", "en", "es", "fr", "zh-CN"),
        ("zh-CN", "en", "de", "fr", "zh-CN"),
    ]

    def __init__(self):
        self.translators: List[BaseTranslator] = []
        self._init_translators()

    def _init_translators(self):
        """初始化可用的翻译器"""
        self.translators.append(MyMemoryTranslator())

        try:
            self.translators.append(GoogleTranslator())
        except Exception:
            pass

        try:
            self.translators.append(LibreTranslator())
        except Exception:
            pass

    def get_translator(self, name: str = "mymemory") -> Optional[BaseTranslator]:
        """获取指定翻译器"""
        translators = {
            "mymemory": MyMemoryTranslator,
            "google": GoogleTranslator,
            "libre": LibreTranslator,
            "deepl": DeepLTranslator,
        }

        translator_class = translators.get(name)
        if translator_class:
            return translator_class()
        return None

    def back_translate_multi(
        self,
        text: str,
        target_langs: Optional[List[str]] = None,
        iterations: int = 2
    ) -> str:
        """
        多语言回译

        Args:
            text: 原文
            target_langs: 目标语言列表
            iterations: 迭代次数
        """
        if not target_langs:
            target_langs = ["en", "de", "ja"]

        result = text

        for _ in range(iterations):
            lang = random.choice(target_langs)
            chain = (lang, "zh-CN")

            for translator in self.translators:
                translated = translator.translate(text, chain[0], chain[1])
                if translated and translated != text:
                    result = translated
                    break

        return result

    def smart_back_translate(self, text: str, intensity: float = 0.5) -> str:
        """
        智能回译

        根据文本长度和内容选择最优翻译链
        """
        if random.random() > intensity:
            return text

        # 根据长度选择翻译策略
        if len(text) < 30:
            chain = ("en", "zh-CN")
        elif len(text) < 80:
            chain = random.choice([("en", "zh-CN"), ("de", "zh-CN"), ("ja", "zh-CN")])
        else:
            chain = random.choice([
                ("en", "zh-CN"), ("de", "zh-CN"),
                ("ja", "zh-CN"), ("fr", "zh-CN")
            ])

        for translator in self.translators:
            result = translator.translate(text, chain[0], chain[1])
            if result and result != text:
                return result

        return text

    def back_translate_v2(self, text: str, iterations: int = 1) -> str:
        """
        增强版回译 - 使用更多翻译路径

        Args:
            text: 原文
            iterations: 回译次数
        """
        result = text

        for _ in range(iterations):
            if len(text) < 50:
                path = random.choice(self.BACKTRANSLATION_PATHS[:6])
            elif len(text) < 200:
                path = random.choice(self.BACKTRANSLATION_PATHS[:12])
            else:
                path = random.choice(self.BACKTRANSLATION_PATHS + self.LONG_TEXT_PATHS)

            current = result
            for i in range(len(path) - 1):
                for translator in self.translators:
                    translated = translator.translate(current, path[i], path[i + 1])
                    if translated and translated != current:
                        current = translated
                        break
            result = current

        return result


class MultiTranslator:
    """
    多翻译器聚合
    自动选择可用翻译器并实现故障转移
    """

    def __init__(self):
        self.translators: List[BaseTranslator] = []
        self._init_translators()

    def _init_translators(self):
        """初始化所有可用的翻译器"""
        translator_configs = [
            ("MyMemory", MyMemoryTranslator),
            ("Google", GoogleTranslator),
            ("Libre", LibreTranslator),
        ]

        for name, translator_class in translator_configs:
            try:
                translator = translator_class()
                self.translators.append(translator)
            except Exception:
                pass

    def translate_with_fallback(
        self,
        text: str,
        from_lang: str = "zh-CN",
        to_lang: str = "en"
    ) -> Optional[str]:
        """故障转移翻译"""
        for translator in self.translators:
            try:
                result = translator.translate(text, from_lang, to_lang)
                if result and result != text:
                    return result
            except Exception:
                continue

        return None

    def multi_hop_translate(self, text: str, hops: List[tuple]) -> str:
        """
        多跳翻译

        Args:
            text: 原文
            hops: 翻译跳序列，如 [("zh-CN", "en"), ("en", "de"), ("de", "zh-CN")]
        """
        result = text
        for from_lang, to_lang in hops:
            translated = self.translate_with_fallback(result, from_lang, to_lang)
            if translated:
                result = translated
            else:
                break
            time.sleep(0.1)

        return result

    def back_translate(self, text: str, via_lang: str = "en") -> str:
        """回译"""
        return self.multi_hop_translate(text, [(text[:2] if text else "zh", via_lang), (via_lang, "zh-CN")])


def create_translation_chain() -> TranslationChain:
    """创建翻译链"""
    return TranslationChain()


def create_multi_translator() -> MultiTranslator:
    """创建多翻译器"""
    return MultiTranslator()
