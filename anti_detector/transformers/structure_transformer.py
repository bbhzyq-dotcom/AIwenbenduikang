"""
结构转换器
通过句子重组、拆分、合并等手段改变文本结构特征
"""

import random
import re
from typing import List, Tuple


class StructureTransformer:
    """结构扰动转换器 - 改变句式、长短句分布"""

    def __init__(self, intensity: float = 0.3):
        self.intensity = intensity

    def _split_sentences(self, text: str) -> List[str]:
        """将文本拆分为句子"""
        # 按中文标点拆分
        sentences = re.split(r'([。！？；\n])', text)
        result = []
        current = ""

        for part in sentences:
            if part in '。！？；\n':
                current += part
                if current.strip():
                    result.append(current)
                current = ""
            else:
                current += part

        if current.strip():
            result.append(current)

        return result

    def _merge_sentences(self, sentences: List[str]) -> List[str]:
        """合并相邻短句"""
        if len(sentences) < 2:
            return sentences

        merged = []
        buffer = sentences[0] if sentences else ""

        for i in range(1, len(sentences)):
            current = sentences[i]

            # 随机决定是否合并
            if len(buffer) < 50 and len(current) < 50 and random.random() < self.intensity:
                buffer += current
            else:
                if buffer.strip():
                    merged.append(buffer)
                buffer = current

        if buffer.strip():
            merged.append(buffer)

        return merged

    def _shuffle_segments(self, text: str) -> str:
        """打乱句段顺序"""
        segments = text.split('，')

        if len(segments) <= 2:
            return text

        if random.random() < self.intensity:
            # 保持首尾，中间打乱
            middle = segments[1:-1]
            random.shuffle(middle)
            segments = [segments[0]] + middle + [segments[-1]]

        return '，'.join(segments)

    def _insert_interruption(self, text: str) -> str:
        """插入思维中断（插入语或转折）"""
        interruptions = [
            "说到这里，",
            "实际上，",
            "不过，",
            "更重要的是，",
            "说起来，",
            "其实，",
            "但需要指出的是，",
        ]

        if len(text) > 20 and '，' in text and random.random() < self.intensity * 0.5:
            parts = text.split('，', 1)
            if len(parts) == 2:
                insertion = random.choice(interruptions)
                text = parts[0] + '，' + insertion + parts[1]

        return text

    def transform(self, text: str) -> str:
        """执行结构变换"""
        if not text:
            return text

        result = text

        # 策略1: 句段打乱
        if random.random() < self.intensity * 1.5:
            result = self._shuffle_segments(result)

        # 策略2: 插入思维中断
        result = self._insert_interruption(result)

        # 策略3: 句子拆分与合并
        sentences = self._split_sentences(result)
        if len(sentences) > 3:
            if random.random() < self.intensity * 1.5:
                sentences = self._merge_sentences(sentences)
            result = ''.join(sentences)

        return result


class SentenceSplitter:
    """句子拆分器 - 将长句拆分为短句"""

    @staticmethod
    def split_long_sentence(text: str, max_length: int = 20) -> str:
        """
        将长句拆分为短句（通过在适当位置添加标点）

        注意：这是一个简化实现，实际需要更复杂的NLP处理
        """
        if len(text) <= max_length * 2:
            return text

        result = []
        current_length = 0

        for char in text:
            result.append(char)
            current_length += 1

            # 在适当位置插入断句标记
            if current_length >= max_length and char in '，、；':
                result.append('。')
                current_length = 0

        return ''.join(result)
