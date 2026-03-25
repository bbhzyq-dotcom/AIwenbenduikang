"""
语义保持变换器
在不改变原文含义的前提下进行深层语义变换
"""

import random
import re
from typing import List, Tuple, Optional, Set


class NegationInverter:
    """否定翻转器 - 巧妙翻转否定意义"""

    NEGATION_WORDS = ['不', '没', '无', '非', '未', '别', '莫', '勿']

    def __init__(self, intensity: float = 0.05):
        self.intensity = intensity

    def flip_negation(self, text: str) -> str:
        """翻转否定词"""
        result = text

        for neg in self.NEGATION_WORDS:
            if neg in text and random.random() < self.intensity:
                # 寻找否定词后的动词，进行简单的"肯定/否定"翻转
                idx = text.find(neg)
                if idx >= 0:
                    remaining = text[idx + 1:]
                    # 简化处理：在动词前添加"能"或移除
                    if remaining:
                        result = text[:idx] + ("能" if neg in ['不', '没'] else "") + remaining
                break

        return result

    def transform(self, text: str) -> str:
        return self.flip_negation(text)


class SentenceFragmenter:
    """句子碎片化器 - 将完整句子拆分成碎片"""

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def split_by_conjunction(self, text: str) -> str:
        """通过连接词拆分"""
        conjunctions = ['并且', '而且', '同时', '此外', '但是', '然而', '所以', '因此']

        for conj in conjunctions:
            if conj in text and random.random() < self.intensity:
                parts = text.split(conj, 1)
                if len(parts) == 2:
                    return parts[0] + '。' + conj + parts[1]
                break

        return text

    def split_long_sentence(self, text: str, min_length: int = 40) -> str:
        """拆分长句"""
        if len(text) < min_length:
            return text

        # 在适当位置拆分
        split_points = ['，', '；', '：']

        for point in split_points:
            if point in text:
                parts = text.split(point, 1)
                if len(parts[0]) > min_length // 2:
                    return parts[0] + '。' + point.join(['']) + parts[1] if len(parts) > 1 else text

        return text

    def add_abrupt_break(self, text: str) -> str:
        """添加突兀的断句"""
        breaks = ['...', '——', '（停顿）', '（话说）', '等等', '呃']

        for i, char in enumerate(text):
            if char == '，' and len(text) > 20 and random.random() < self.intensity * 0.3:
                text = text[:i + 1] + random.choice(breaks) + text[i + 1:]
                break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            result = self.split_by_conjunction(result)

        if random.random() < self.intensity * 0.7:
            result = self.add_abrupt_break(result)

        return result


class StyleMixer:
    """风格混合器 - 混合正式与非正式表达"""

    FORMAL_TO_INFORMAL: dict[str, List[str]] = {
        '因此': ['所以', '这不'],
        '然而': ['可是', '但是'],
        '虽然': ['虽说', '就算'],
        '此外': ['另外', '还有'],
        '根据': ['按照', '照着'],
        '表明': ['说明', '看得出'],
        '认为': ['觉得', '寻思'],
        '重要': ['要紧', '关键'],
        '问题': ['事儿', '麻烦'],
        '情况': ['事儿', '样子'],
    }

    INFORMAL_TO_FORMAL: dict[str, List[str]] = {
        '所以': ['因此', '因而'],
        '但是': ['然而', '不过'],
        '觉得': ['认为', '觉得'],
        '事儿': ['事情', '事务'],
        '这不': ['因此', '于是'],
    }

    def __init__(self, intensity: float = 0.25):
        self.intensity = intensity

    def formal_to_informal(self, text: str) -> str:
        """正式转非正式"""
        result = text

        for formal, informal_list in self.FORMAL_TO_INFORMAL.items():
            if formal in text and random.random() < self.intensity:
                result = result.replace(formal, random.choice(informal_list), 1)
                break

        return result

    def informal_to_formal(self, text: str) -> str:
        """非正式转正式"""
        result = text

        for informal, formal_list in self.INFORMAL_TO_FORMAL.items():
            if informal in text and random.random() < self.intensity:
                result = result.replace(informal, random.choice(formal_list), 1)
                break

        return result

    def mixed_style(self, text: str) -> str:
        """混合风格"""
        if random.random() < 0.5:
            return self.formal_to_informal(text)
        else:
            return self.informal_to_formal(text)

    def transform(self, text: str) -> str:
        if not text:
            return text

        return self.mixed_style(text)


class PassiveToActiveConverter:
    """主动/被动语态转换器"""

    def __init__(self, intensity: float = 0.15):
        self.intensity = intensity

    def to_passive(self, text: str) -> str:
        """转被动语态"""
        passive_markers = ['被', '受到', '遭到', '为...所']

        for marker in passive_markers:
            if marker in text and random.random() < self.intensity:
                # 简化处理
                return text

        return text

    def to_active(self, text: str) -> str:
        """转主动语态"""
        passive_phrases = [
            '被发现', '被认定', '被认为', '被接受',
            '受到重视', '得到解决', '加以改进'
        ]

        for phrase in passive_phrases:
            if phrase in text and random.random() < self.intensity:
                # 简化处理：移除"被"
                text = text.replace('被', '', 1)
                break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        if random.random() < 0.5:
            return self.to_active(text)
        else:
            return self.to_passive(text)


class SynonymContextualReplacer:
    """上下文感知同义词替换器 - 根据上下文选择最合适的同义词"""

    CONTEXTUAL_SYNONYMS: dict[str, List[Tuple[str, List[str]]]] = {
        '重要': [
            ('safety', ['安全', '保障']),
            ('key', ['关键', '核心']),
            ('significance', ['意义', '价值']),
        ],
        '提高': [
            ('level', ['提升', '抬高']),
            ('quality', ['提升', '改进']),
            ('quantity', ['增加', '增长']),
        ],
        '分析': [
            ('data', ['分析', '解析']),
            ('problem', ['分析', '剖析']),
            ('situation', ['研判', '判断']),
        ],
    }

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def replace_with_context(self, text: str) -> str:
        """根据上下文替换同义词"""
        result = text

        for word, contexts in self.CONTEXTUAL_SYNONYMS.items():
            if word in text:
                if random.random() < self.intensity:
                    # 随机选择替换
                    _, replacements = random.choice(contexts)
                    result = result.replace(word, random.choice(replacements), 1)
                    break

        return result

    def transform(self, text: str) -> str:
        return self.replace_with_context(text)
