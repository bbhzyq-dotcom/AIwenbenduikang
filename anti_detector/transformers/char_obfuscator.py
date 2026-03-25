"""
字符级混淆转换器
通过Unicode字符替换、同形字混淆等技术对抗字符级检测
"""

import random
import unicodedata
from typing import Dict, List, Tuple, Optional


class UnicodeObfuscator:
    """Unicode字符混淆器"""

    # 常见ASCII相似字符映射
    HOMOGLYPHS: Dict[str, List[str]] = {
        'a': ['ɑ', 'α', 'а', '𝒶'],
        'b': ['ƅ', 'ь', '𝐛', '𝕓'],
        'c': ['ϲ', 'с', '𝒸', '𝓬'],
        'd': ['ԁ', 'ⅆ', '𝒹', '𝓭'],
        'e': ['е', 'ⅇ', '𝒆', '𝓮'],
        'o': ['ο', 'о', '𝒐', '𝑜'],
        'p': ['ρ', 'р', '𝒑', '𝓅'],
        's': ['ѕ', '𝒔', '𝓈', '𝓈'],
        'x': ['х', '𝒙', '𝓍', '𝕩'],
        'y': ['у', 'γ', 'у', '𝓎'],
        'w': ['ԝ', 'ѡ', '𝓌', '𝕨'],
        '0': ['ο', 'О', '𝟢', '𝟎'],
        '1': ['Ӏ', 'Ⅰ', '𝟣', '𝟭'],
    }

    # 全角转半角映射
    FULLWIDTH_MAP: Dict[str, str] = {
        '！': '!', '。': '.', '，': ',', '；': ';', '：': ':',
        '？': '?', '（': '(', '）': ')', '【': '[', '】': ']',
        '－': '-', '＋': '+', '＝': '=', '％': '%',
    }

    # 常见汉字形似字
    SIMILAR_CHARS: Dict[str, List[str]] = {
        '人': ['入', '八'],
        '日': ['曰', '目'],
        '了': ['乜', '孒'],
        '子': ['孑', '卆'],
        '大': ['太', '犬', '𠂉'],
        '小': ['少', '尒'],
        '千': ['干', '十'],
        '弓': ['吊', '𢎀'],
        '己': ['已', '巳'],
        '土': ['士', '圡'],
    }

    def __init__(self, intensity: float = 0.1):
        self.intensity = intensity

    def homoglyph_substitution(self, text: str) -> str:
        """
        同形字替换
        将英文字符替换为视觉相似的Unicode字符
        """
        result = []
        for char in text:
            if char.isascii() and char.isalpha() and char.lower() in self.HOMOGLYPHS:
                if random.random() < self.intensity:
                    replacements = self.HOMOGLYPHS[char.lower()]
                    result.append(random.choice(replacements))
                else:
                    result.append(char)
            else:
                result.append(char)
        return ''.join(result)

    def fullwidth_to_halfwidth(self, text: str) -> str:
        """全角转半角"""
        result = []
        for char in text:
            if char in self.FULLWIDTH_MAP:
                result.append(self.FULLWIDTH_MAP[char])
            elif '\uff01' <= char <= '\uff5e':
                result.append(chr(ord(char) - 0xfee0))
            else:
                result.append(char)
        return ''.join(result)

    def similar_char_substitution(self, text: str) -> str:
        """汉字形似字替换"""
        result = []
        for char in text:
            if char in self.SIMILAR_CHARS and random.random() < self.intensity * 2:
                result.append(random.choice(self.SIMILAR_CHARS[char]))
            else:
                result.append(char)
        return ''.join(result)

    def normalize_unicode(self, text: str) -> str:
        """Unicode正规化"""
        return unicodedata.normalize('NFKC', text)

    def transform(self, text: str) -> str:
        """执行字符级混淆"""
        if not text:
            return text

        result = text

        # 同形字替换
        if random.random() < self.intensity:
            result = self.homoglyph_substitution(result)

        # 全角半角转换
        if random.random() < self.intensity * 0.5:
            result = self.fullwidth_to_halfwidth(result)

        return result


class ZeroWidthInjector:
    """零宽字符注入器"""

    # 零宽字符
    ZERO_WIDTH_CHARS = [
        '\u200b',      # Zero Width Space
        '\u200c',      # Zero Width Non-Joiner
        '\u200d',      # Zero Width Joiner
        '\ufeff',      # Zero Width No-Break Space
        '\u180e',      # Mongolian Free Variation Selector (deprecated)
    ]

    def __init__(self, intensity: float = 0.05):
        self.intensity = intensity

    def inject_random(self, text: str) -> str:
        """随机位置注入零宽字符"""
        if not text or len(text) < 5:
            return text

        chars = list(text)
        num_injections = max(1, int(len(text) * self.intensity))

        for _ in range(num_injections):
            pos = random.randint(0, len(chars))
            char = random.choice(self.ZERO_WIDTH_CHARS)
            chars.insert(pos, char)

        return ''.join(chars)

    def inject_after_char(self, text: str, target: str) -> str:
        """在特定字符后注入"""
        result = []
        for char in text:
            result.append(char)
            if char == target and random.random() < self.intensity:
                result.append(random.choice(self.ZERO_WIDTH_CHARS))
        return ''.join(result)

    def inject_word_boundaries(self, text: str) -> str:
        """在词语边界注入"""
        result = []
        boundaries = ['，', '。', '、', '；', '：', '！', '？', ' ', '\n']

        for char in text:
            result.append(char)
            if char in boundaries and random.random() < self.intensity * 0.5:
                result.append(random.choice(self.ZERO_WIDTH_CHARS))

        return ''.join(result)

    def transform(self, text: str) -> str:
        """执行零宽字符注入"""
        if random.random() > self.intensity:
            return text

        methods = [
            lambda: self.inject_random(text),
            lambda: self.inject_word_boundaries(text),
        ]
        return random.choice(methods)()


class SpacingManipulator:
    """空格操纵器"""

    def __init__(self, intensity: float = 0.1):
        self.intensity = intensity

    def add_extra_spaces(self, text: str) -> str:
        """添加额外空格"""
        result = []
        for char in text:
            result.append(char)
            if char in '，。！？；：' and random.random() < self.intensity:
                result.append(' ')
        return ''.join(result)

    def remove_spaces(self, text: str) -> str:
        """移除空格（在中文文本中添加空格是AI特征）"""
        return text.replace(' ', '')

    def mixed_spacing(self, text: str) -> str:
        """混合空格策略"""
        if random.random() < 0.5:
            return self.add_extra_spaces(text)
        else:
            return self.remove_spaces(text)

    def transform(self, text: str) -> str:
        """执行空格操纵"""
        if not text:
            return text

        return self.mixed_spacing(text)


class CharacterLeet:
    """字符Leet转换（数字/符号替换字母）"""

    LEET_MAP = {
        'a': ['4', '@'],
        'e': ['3', '€'],
        'i': ['1', '!', '|'],
        'o': ['0', 'Ω'],
        's': ['5', '$', 'z'],
        't': ['7', '+'],
        'l': ['1', '|'],
        'b': ['8', '6'],
    }

    def __init__(self, intensity: float = 0.05):
        self.intensity = intensity

    def to_leet(self, text: str) -> str:
        """转换为Leet风格"""
        result = []
        for char in text.lower():
            if char in self.LEET_MAP and random.random() < self.intensity:
                result.append(random.choice(self.LEET_MAP[char]))
            else:
                result.append(char)
        return ''.join(result)

    def transform(self, text: str) -> str:
        """执行Leet转换"""
        if random.random() > self.intensity * 2:
            return text
        return self.to_leet(text)


class EmojiInjection:
    """表情符号注入"""

    CONTEXTUAL_EMOJIS = {
        '开心': ['😊', '😄', '🙂', '😃'],
        '惊讶': ['😮', '😲', '🤔', '❓'],
        '思考': ['🤔', '💭', '🧐', '...'],
        '强调': ['❗', '❕', '❓', '⚡'],
        '疑问': ['🤔', '❓', '⁉️', '？'],
    }

    def __init__(self, intensity: float = 0.1):
        self.intensity = intensity

    def inject_contextual(self, text: str) -> str:
        """根据上下文注入表情"""
        result = text

        for keyword, emojis in self.CONTEXTUAL_EMOJIS.items():
            if keyword in text and random.random() < self.intensity:
                emoji = random.choice(emojis)
                result = result.replace(keyword, f"{keyword}{emoji}", 1)
                break

        return result

    def inject_random(self, text: str) -> str:
        """随机注入表情"""
        if len(text) < 20:
            return text

        emojis = ['🤔', '💭', '❓', '❗', '...', '（思考）', '（疑惑）']
        pos = random.randint(len(text) // 3, 2 * len(text) // 3)
        return text[:pos] + random.choice(emojis) + text[pos:]

    def transform(self, text: str) -> str:
        """执行表情注入"""
        if random.random() > self.intensity:
            return text

        if random.random() < 0.5:
            return self.inject_contextual(text)
        else:
            return self.inject_random(text)
