"""
标点符号与格式转换器
通过标点符号操纵对抗基于标点模式的检测
"""

import random
import re
from typing import List, Tuple, Optional


class PunctuationManipulator:
    """标点符号操纵器"""

    # 标点符号映射
    PUNCTUATION_ALTERNATIVES: dict[str, List[str]] = {
        '，': ['，', '、', '；', '，'],
        '。': ['。', '！', '？', '。'],
        '！': ['！', '！', '❗', '❕'],
        '？': ['？', '？', '⁉️', '❓'],
        '；': ['；', '，', '、', '；'],
        '：': ['：', '——', '——', '：'],
        '、': ['、', '，', '、', '，'],
    }

    # 句子结尾标点
    END_PUNCTUATION = ['。', '！', '？', '...', '～']

    def __init__(self, intensity: float = 0.15):
        self.intensity = intensity

    def randomize_punctuation(self, text: str) -> str:
        """随机化标点符号"""
        result = []
        i = 0
        while i < len(text):
            char = text[i]

            if char in self.PUNCTUATION_ALTERNATIVES:
                if random.random() < self.intensity:
                    alternatives = self.PUNCTUATION_ALTERNATIVES[char]
                    result.append(random.choice(alternatives))
                else:
                    result.append(char)
            else:
                result.append(char)
            i += 1

        return ''.join(result)

    def add_redundant_punctuation(self, text: str) -> str:
        """添加冗余标点"""
        result = []
        for char in text:
            result.append(char)
            if char in '，。；：' and random.random() < self.intensity * 0.3:
                result.append(char)
        return ''.join(result)

    def remove_punctuation(self, text: str) -> str:
        """移除部分标点"""
        result = []
        for char in text:
            if char in '，。；：、' and random.random() < self.intensity:
                continue
            result.append(char)
        return ''.join(result)

    def vary_sentence_ends(self, text: str) -> str:
        """变化句子结尾"""
        sentences = re.split(r'([。！？\n])', text)
        result = []

        for i, part in enumerate(sentences):
            if part in '。！？':
                if random.random() < self.intensity:
                    result.append(random.choice(self.END_PUNCTUATION))
                else:
                    result.append(part)
            else:
                result.append(part)

        return ''.join(result)

    def transform(self, text: str) -> str:
        """执行标点操纵"""
        if not text:
            return text

        result = text

        # 随机化标点
        if random.random() < self.intensity:
            result = self.randomize_punctuation(result)

        # 变化句子结尾
        if random.random() < self.intensity * 0.7:
            result = self.vary_sentence_ends(result)

        return result


class ParagraphFormatter:
    """段落格式化器"""

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def split_long_paragraphs(self, text: str, max_length: int = 100) -> str:
        """拆分过长段落"""
        result = []
        for para in text.split('\n'):
            if len(para) > max_length and '，' in para:
                parts = para.split('，')
                current = []
                current_len = 0

                for part in parts:
                    if current_len + len(part) > max_length and current:
                        result.append('，'.join(current) + '。')
                        current = [part]
                        current_len = len(part)
                    else:
                        current.append(part)
                        current_len += len(part)

                if current:
                    result.append('，'.join(current))
            else:
                result.append(para)

        return '\n'.join(result)

    def merge_short_paragraphs(self, text: str, min_length: int = 30) -> str:
        """合并过短段落"""
        paragraphs = text.split('\n\n')
        result = []
        buffer = ""

        for para in paragraphs:
            if len(para.strip()) < min_length:
                buffer += para.strip() + ' '
            else:
                if buffer:
                    result.append(buffer.strip())
                    buffer = ""
                result.append(para)

        if buffer:
            result.append(buffer.strip())

        return '\n\n'.join(result)

    def add_empty_lines(self, text: str) -> str:
        """添加空行"""
        sentences = re.split(r'([。！？])', text)
        result = []

        for i, part in enumerate(sentences):
            result.append(part)
            if part in '。！？' and random.random() < self.intensity * 0.2:
                result.append('\n')

        return ''.join(result)

    def remove_all_line_breaks(self, text: str) -> str:
        """移除所有换行"""
        return text.replace('\n', '').replace('\r', '')

    def transform(self, text: str) -> str:
        """执行段落格式化"""
        if not text:
            return text

        result = text

        # 随机选择格式化策略
        if random.random() < self.intensity:
            result = self.split_long_paragraphs(result)
        elif random.random() < self.intensity:
            result = self.add_empty_lines(result)

        return result


class CapitalizationMixer:
    """大小写混合器（针对英文）"""

    def __init__(self, intensity: float = 0.1):
        self.intensity = intensity

    def random_case(self, text: str) -> str:
        """随机大小写"""
        result = []
        for char in text:
            if char.isascii() and char.isalpha():
                if random.random() < self.intensity:
                    result.append(char.upper() if random.random() < 0.5 else char.lower())
                else:
                    result.append(char)
            else:
                result.append(char)
        return ''.join(result)

    def title_case_mixed(self, text: str) -> str:
        """混合标题大小写"""
        words = text.split()
        result = []

        for word in words:
            if word.isascii() and word.isalpha():
                if random.random() < self.intensity:
                    result.append(word.title())
                else:
                    result.append(word.lower() if random.random() < 0.5 else word)
            else:
                result.append(word)

        return ' '.join(result)

    def transform(self, text: str) -> str:
        """执行大小写混合"""
        if random.random() > self.intensity * 2:
            return text

        methods = [self.random_case, self.title_case_mixed]
        return random.choice(methods)(text)
