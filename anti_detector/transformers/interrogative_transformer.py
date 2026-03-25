"""
设问/插入转换器
通过添加人类写作特征来打破AI文本的模式
"""

import random
from typing import List


class InterrogativeTransformer:
    """设问转换器 - 添加人类写作的思维跳跃特征"""

    # 反问句式
    RHETORICAL_QUESTIONS = [
        "这难道不值得深思吗？",
        "还有什么比这更重要的呢？",
        "难道不是这样吗？",
        "你说是不是？",
        "这事儿你怎么看？",
        "这里面有没有什么门道？",
    ]

    # 自我提问（模拟思考过程）
    SELF_QUESTIONS = [
        "为什么要这么说呢？",
        "问题的关键在哪？",
        "这么说来是怎么回事？",
        "等等，让我理一理...",
        "这里面有个问题需要说清楚：",
    ]

    # 插入语/过渡语
    TRANSITIONS = [
        "说起来，",
        "话说回来，",
        "你还真别说，",
        "说实在的，",
        "坦白讲，",
        "实话说，",
        "按理说，",
        "这么一想，",
        "回头看看，",
        "综合来看，",
    ]

    # 观点陈述
    PERSONAL_VIEWS = [
        "我觉得吧，",
        "依我看，",
        "个人感觉，",
        "说真的，",
        "实话实说，",
        "我寻思着，",
        "要我说啊，",
    ]

    def __init__(self, intensity: float = 0.3):
        self.intensity = intensity

    def _add_rhetorical_question(self, text: str) -> str:
        """在合适位置添加反问"""
        if len(text) < 20 or '。' not in text:
            return text

        if random.random() < self.intensity * 0.3:
            sentences = text.split('。')
            if len(sentences) >= 3:
                insert_idx = random.randint(1, len(sentences) - 2)
                question = random.choice(self.RHETORICAL_QUESTIONS)
                sentences.insert(insert_idx, question)
                return '。'.join(sentences)

        return text

    def _add_self_question(self, text: str) -> str:
        """在段落开头添加自我提问"""
        if len(text) > 30 and random.random() < self.intensity * 0.2:
            question = random.choice(self.SELF_QUESTIONS)
            text = question + text

        return text

    def _add_transition(self, text: str) -> str:
        """在句中添加过渡语"""
        if '，' not in text or len(text) < 15:
            return text

        if random.random() < self.intensity * 0.4:
            parts = text.split('，', 1)
            if len(parts) == 2:
                transition = random.choice(self.TRANSITIONS)
                text = parts[0] + '，' + transition + parts[1]

        return text

    def _add_personal_view(self, text: str) -> str:
        """添加个人观点"""
        if len(text) > 50 and '。' in text and random.random() < self.intensity * 0.2:
            sentences = text.split('。')
            if len(sentences) >= 2:
                view = random.choice(self.PERSONAL_VIEWS)
                # 在第二句或第三句开头添加
                insert_idx = random.randint(1, min(2, len(sentences) - 1))
                sentences[insert_idx] = view + sentences[insert_idx]
                return '。'.join(sentences)

        return text

    def transform(self, text: str) -> str:
        """执行设问变换"""
        if not text:
            return text

        result = text

        # 添加自我提问
        result = self._add_self_question(result)

        # 添加过渡语
        result = self._add_transition(result)

        # 添加反问
        result = self._add_rhetorical_question(result)

        # 添加个人观点
        result = self._add_personal_view(result)

        return result
