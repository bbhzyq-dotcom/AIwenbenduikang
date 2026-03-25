"""
LLM辅助变换模块

核心设计原则：
1. LLM只做辅助，不生成大段文本
2. LLM用于扩展同义词库
3. LLM用于生成局部变换建议
4. 回译/多语言变换作为主要手段
"""

import random
import re
import json
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class SynonymCandidate:
    """同义词候选"""
    original: str
    replacement: str
    confidence: float = 0.8
    source: str = "rule"  # "rule" or "llm"


@dataclass
class TransformSuggestion:
    """变换建议"""
    start: int
    end: int
    original: str
    replacement: str
    reason: str
    confidence: float = 0.5


class LLMAssistedThesaurus:
    """
    LLM辅助同义词库扩展器

    核心功能：
    1. 接收种子词汇，LLM生成更多同义词候选
    2. 管理同义词库，支持动态扩展
    3. 不生成大段文本，只扩展词库
    """

    EXPANSION_PROMPT = """给定一个中文词汇，生成5-10个同义词或近义词。

要求：
- 只输出词汇列表，每行一个
- 不要解释，不要标号，不要任何其他内容
- 只输出中文词汇
- 词汇应该自然、口语化，避免过于书面的词汇

词汇：{word}

同义词："""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.expanded_synonyms: Dict[str, Set[str]] = {}
        self._cache: Dict[str, List[str]] = {}

    def expand_synonyms(self, word: str) -> List[str]:
        """
        扩展同义词

        优先使用LLM扩展，如果不可用则返回空列表
        """
        if word in self.expanded_synonyms:
            return list(self.expanded_synonyms[word])

        cache_key = f"expand_{word}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.llm_client:
            try:
                expanded = self._llm_expand(word)
                self.expanded_synonyms[word] = set(expanded)
                self._cache[cache_key] = expanded
                return expanded
            except Exception:
                pass

        return []

    def _llm_expand(self, word: str) -> List[str]:
        """使用LLM扩展同义词"""
        if not self.llm_client:
            return []
        prompt = self.EXPANSION_PROMPT.format(word=word)

        try:
            response = self.llm_client.generate(prompt, "")
            lines = response.strip().split('\n')
            synonyms = [line.strip() for line in lines if line.strip()]
            return synonyms[:10]
        except Exception:
            return []

    def get_expanded_thesaurus(self, base_thesaurus: Dict[str, list]) -> Dict[str, list]:
        """
        获取扩展后的同义词库

        对基础同义词库的每个词，用LLM尝试扩展
        """
        result = dict(base_thesaurus)

        if not self.llm_client:
            return result

        for word, synonyms in base_thesaurus.items():
            expanded = self.expand_synonyms(word)
            if expanded:
                combined = list(set(synonyms + expanded))
                result[word] = combined

        return result


class LLMAssistedTransform:
    """
    LLM辅助局部变换

    核心功能：
    1. 分析文本中的AI模式
    2. 给出局部修改建议（不生成完整文本）
    3. 建议同义词替换
    4. 建议结构变化
    """

    ANALYSIS_PROMPT = """分析以下文本中的AI写作特征，给出具体的修改建议。

要求：
- 指出机械化的表达（如"首先、其次、最后"）
- 指出过于规整的句式
- 指出AI高频词汇
- 每条建议要具体到原文中的词或短语

输出格式（JSON数组）：
[
  {
    "start": 起始位置,
    "end": 结束位置,
    "original": "原词/短语",
    "suggestion": "建议替换为",
    "reason": "修改原因"
  }
]

文本：{text}

只输出JSON，不要其他内容。"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self._cache: Dict[str, List[TransformSuggestion]] = {}

    def get_suggestions(self, text: str, max_suggestions: int = 3) -> List[TransformSuggestion]:
        """
        获取局部变换建议

        优先使用LLM，不可用时返回基于规则的建议
        """
        cache_key = text[:100]
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.llm_client:
            try:
                suggestions = self._llm_analyze(text)
                self._cache[cache_key] = suggestions
                return suggestions[:max_suggestions]
            except Exception:
                pass

        return self._rule_based_suggestions(text)

    def _llm_analyze(self, text: str) -> List[TransformSuggestion]:
        """使用LLM分析文本"""
        if not self.llm_client:
            return []
        prompt = self.ANALYSIS_PROMPT.format(text=text)

        try:
            response = self.llm_client.generate(prompt, "")
            suggestions = self._parse_suggestions(response)
            return suggestions
        except Exception:
            return []

    def _parse_suggestions(self, response: str) -> List[TransformSuggestion]:
        """解析LLM响应"""
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return [
                    TransformSuggestion(
                        start=s.get("start", 0),
                        end=s.get("end", 0),
                        original=s.get("original", ""),
                        replacement=s.get("suggestion", ""),
                        reason=s.get("reason", ""),
                        confidence=0.7
                    )
                    for s in data if isinstance(s, dict)
                ]
        except Exception:
            pass
        return []

    def _rule_based_suggestions(self, text: str) -> List[TransformSuggestion]:
        """基于规则的变换建议"""
        suggestions = []
        ai_phrases = {
            "首先": "第一",
            "其次": "第二",
            "最后": "最终",
            "因此": "所以",
            "但是": "可是",
            "因为": "由于",
            "虽然": "尽管",
            "重要": "关键",
            "提高": "提升",
            "发展": "推进",
        }

        for phrase, replacement in ai_phrases.items():
            start = text.find(phrase)
            if start >= 0:
                suggestions.append(TransformSuggestion(
                    start=start,
                    end=start + len(phrase),
                    original=phrase,
                    replacement=replacement,
                    reason="替换AI高频短语",
                    confidence=0.6
                ))
                if len(suggestions) >= 3:
                    break

        return suggestions

    def apply_suggestions(self, text: str, suggestions: List[TransformSuggestion]) -> str:
        """应用变换建议"""
        if not suggestions:
            return text

        result = text
        offset = 0

        for sug in suggestions:
            if sug.start < len(result) and sug.end <= len(result):
                result = result[:sug.start + offset] + sug.replacement + result[sug.end + offset:]
                offset += len(sug.replacement) - (sug.end - sug.start)

        return result


class TranslationChainV2:
    """
    增强版翻译链 - 核心策略

    支持多种翻译路径，用于打破AI文本的固有模式
    """

    CHAINS = [
        ("zh-CN", "en", "zh-CN"),
        ("zh-CN", "ja", "zh-CN"),
        ("zh-CN", "de", "zh-CN"),
        ("zh-CN", "fr", "zh-CN"),
        ("zh-CN", "ko", "zh-CN"),
        ("zh-CN", "ru", "zh-CN"),
        ("zh-CN", "es", "zh-CN"),
        ("zh-CN", "it", "zh-CN"),
        ("zh-CN", "pt", "zh-CN"),
        ("zh-CN", "ar", "zh-CN"),
        ("zh-CN", "en", "ja", "zh-CN"),
        ("zh-CN", "en", "de", "zh-CN"),
        ("zh-CN", "en", "fr", "zh-CN"),
        ("zh-CN", "ja", "ko", "zh-CN"),
        ("zh-CN", "en", "es", "zh-CN"),
        ("zh-CN", "de", "fr", "zh-CN"),
        ("zh-CN", "en", "ru", "zh-CN"),
        ("zh-CN", "en", "ko", "zh-CN"),
    ]

    LONG_TEXT_CHAINS = [
        ("zh-CN", "en", "de", "zh-CN"),
        ("zh-CN", "en", "fr", "zh-CN"),
        ("zh-CN", "ja", "en", "zh-CN"),
        ("zh-CN", "en", "ja", "zh-CN"),
        ("zh-CN", "de", "en", "zh-CN"),
        ("zh-CN", "fr", "en", "zh-CN"),
        ("zh-CN", "en", "es", "fr", "zh-CN"),
    ]

    def __init__(self, api_url: str = "https://api.mymemory.translated.net/get", timeout: int = 30):
        self.api_url = api_url
        self.timeout = timeout
        self.cache: Dict[str, str] = {}

    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """单次翻译"""
        cache_key = f"{text}:{from_lang}:{to_lang}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            import requests
            params = {"q": text, "langpair": f"{from_lang}|{to_lang}"}
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    result = data["responseData"]["translatedText"]
                    self.cache[cache_key] = result
                    return result
        except Exception:
            pass
        return None

    def back_translate(self, text: str, chain: Optional[Tuple[str, ...]] = None) -> str:
        """回译"""
        if chain is None:
            chain = random.choice(self.CHAINS)

        if len(chain) < 2:
            return text

        result = text
        for i in range(len(chain) - 1):
            translated = self.translate(result, chain[i], chain[i + 1])
            if translated:
                result = translated
            else:
                break

        return result

    def smart_back_translate(self, text: str, intensity: float = 1.0) -> str:
        """
        智能回译 - 核心方法

        根据文本长度自动选择翻译链
        """
        if random.random() > intensity:
            return text

        if len(text) < 30:
            chain = random.choice(self.CHAINS[:6])
        elif len(text) < 100:
            chain = random.choice(self.CHAINS[:12])
        elif len(text) < 300:
            chain = random.choice(self.CHAINS[6:] + self.LONG_TEXT_CHAINS[:4])
        else:
            chain = random.choice(self.LONG_TEXT_CHAINS)

        return self.back_translate(text, chain)

    def multi_hop_translate(self, text: str, hops: int = 2) -> str:
        """多次翻译"""
        chains = [c for c in self.CHAINS if len(c) == hops + 1]
        if chains:
            chain = random.choice(chains)
            return self.back_translate(text, chain)
        chain = random.choice(self.CHAINS)
        return self.back_translate(text, chain)


class SmartParaphraser:
    """
    智能改写器 - 以翻译回译为核心

    策略优先级：
    1. 翻译回译（最高优先级）
    2. LLM辅助局部变换（次要）
    3. 规则变换（辅助）
    """

    def __init__(self, llm_client=None, intensity: float = 0.5):
        self.llm_client = llm_client
        self.intensity = intensity
        self.translator = TranslationChainV2()
        self.llm_transform = LLMAssistedTransform(llm_client) if llm_client else None

    def paraphrase(self, text: str, intensity: Optional[float] = None) -> str:
        """
        智能改写 - 核心入口

        策略：
        1. 翻译回译（必执行，用于打破固有模式）
        2. LLM辅助局部变换（可选）
        3. 保持原文长度和核心含义
        """
        if not text:
            return text

        intensity = intensity or self.intensity
        result = text

        result = self._translation_paraphrase(result, intensity)

        return result

    def _translation_paraphrase(self, text: str, intensity: float) -> str:
        """翻译回译 - 核心策略"""
        chain_count = 1 if len(text) < 100 else 2 if len(text) < 300 else 3

        for _ in range(chain_count):
            result = self.translator.smart_back_translate(text, intensity=1.0)
            if result and result != text:
                text = result

        return text

    def paraphrase_with_llm(self, text: str) -> str:
        """
        带LLM辅助的改写

        适用于对质量要求更高的场景
        """
        if not text:
            return text

        result = text

        result = self._translation_paraphrase(result, intensity=1.0)

        if self.llm_transform and random.random() < 0.3:
            suggestions = self.llm_transform.get_suggestions(result)
            result = self.llm_transform.apply_suggestions(result, suggestions[:2])

        return result


class MultiBackendTranslator:
    """
    多后端翻译器

    优先级：
    1. MyMemory (免费，无需密钥)
    2. Google Translate (非官方)
    """

    def __init__(self):
        self.backends = []
        self._init_backends()

    def _init_backends(self):
        try:
            self.backends.append(("mymemory", MyMemoryBackend()))
        except:
            pass

        try:
            self.backends.append(("google", GoogleBackend()))
        except:
            pass

    def translate(self, text: str, from_lang: str = "zh-CN", to_lang: str = "en") -> Optional[str]:
        for name, backend in self.backends:
            try:
                result = backend.translate(text, from_lang, to_lang)
                if result and result != text:
                    return result
            except:
                continue
        return None

    def back_translate(self, text: str) -> str:
        for name, backend in self.backends:
            try:
                en_text = backend.translate(text, "zh-CN", "en")
                if not en_text:
                    continue
                zh_text = backend.translate(en_text, "en", "zh-CN")
                if zh_text and zh_text != text:
                    return zh_text
            except:
                continue
        return text


class MyMemoryBackend:
    def __init__(self, api_url: str = "https://api.mymemory.translated.net/get"):
        self.api_url = api_url

    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        try:
            import requests
            params = {"q": text, "langpair": f"{from_lang}|{to_lang}"}
            response = requests.get(self.api_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    return data["responseData"]["translatedText"]
        except:
            pass
        return None


class GoogleBackend:
    def __init__(self):
        self.url = "https://translate.googleapis.com/translate_a/single"

    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        try:
            import requests
            params = {
                "client": "gtx",
                "sl": from_lang,
                "tl": to_lang,
                "dt": "t",
                "q": text
            }
            response = requests.get(self.url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    return "".join(item[0] for item in data[0] if item[0])
        except:
            pass
        return None


def create_paraphraser(llm_client=None, intensity: float = 0.5) -> SmartParaphraser:
    """创建智能改写器"""
    return SmartParaphraser(llm_client, intensity)


def create_translator() -> MultiBackendTranslator:
    """创建多后端翻译器"""
    return MultiBackendTranslator()


def create_llm_thesaurus(llm_client=None) -> LLMAssistedThesaurus:
    """创建LLM辅助同义词库"""
    return LLMAssistedThesaurus(llm_client)


def create_llm_transform(llm_client=None) -> LLMAssistedTransform:
    """创建LLM辅助变换器"""
    return LLMAssistedTransform(llm_client)