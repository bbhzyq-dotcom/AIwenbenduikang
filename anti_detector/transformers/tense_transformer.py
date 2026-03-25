"""
语气/语态转换器
通过改变表达方式来打破AI写作的固有模式
"""

import random
import re


class TenseTransformer:
    """语气语态转换器"""

    # 书面语到口语的表达映射
    WRITTEN_TO_SPOKEN = {
        "因此": ["所以", "于是", "这一来", "就这么着"],
        "然而": ["可是", "但是", "不过", "只是"],
        "虽然": ["虽说", "虽说", "尽管", "就算"],
        "此外": ["另外", "还有", "再说", "加之"],
        "并且": ["而且", "同时", "一边...一边"],
        "由于": ["因为", "因为...所以", "既然"],
        "从而": ["就这么着", "于是", "因此"],
        "综上所述": ["总的来说", "反正", "说到底"],
        "由此可见": ["可见", "这么看", "看来"],
        "值得注意的是": ["要我说", "重点是", "关键在于"],
        "毫无疑问": ["明摆着", "不用说", "肯定"],
        "在很大程度上": ["多半", "很大程度上", "主要"],
    }

    # 陈述句转疑问句的关键词
    STATEMENT_TO_QUESTION = {
        "重要": "重要吗",
        "必要": "必要吗",
        "需要": "需要吗",
        "应该": "应该吗",
        "可以": "可以吗",
        "可能": "可能吗",
    }

    def __init__(self, intensity: float = 0.3):
        self.intensity = intensity

    def _spoken_transform(self, text: str) -> str:
        """将书面语转为口语化表达"""
        result = text

        for written, spoken_list in self.WRITTEN_TO_SPOKEN.items():
            if written in result and random.random() < self.intensity:
                spoken = random.choice(spoken_list)
                result = result.replace(written, spoken, 1)
                break

        return result

    def _add_hesitation(self, text: str) -> str:
        """添加犹豫语气（嗯、啊、嘛、呢）"""
        hesitations = ["嗯", "啊", "嘛", "呢", "呃", "这个"]
        result = text

        if len(text) > 10 and random.random() < self.intensity * 0.3:
            # 在句首添加
            if random.random() < 0.5:
                result = random.choice(hesitations) + "，" + result
            # 在句中插入
            else:
                for i, char in enumerate(result):
                    if char == '，' and i > 3 and i < len(result) - 5:
                        insert_pos = i + 1
                        result = result[:insert_pos] + random.choice(hesitations) + "，" + result[insert_pos:]
                        break

        return result

    def _add_rhetorical_question(self, text: str) -> str:
        """将部分陈述转为反问"""
        result = text

        # 寻找可以转换的关键词
        for statement, question in self.STATEMENT_TO_QUESTION.items():
            if statement in result and random.random() < self.intensity * 0.2:
                # 在关键词后添加"吗"或替换
                if f"{statement}的" in result:
                    result = result.replace(f"{statement}的", f"{statement}的吗", 1)
                elif statement in result:
                    idx = result.find(statement)
                    if idx >= 0:
                        result = result[:idx] + f"真的{statement}吗？" + result[idx+len(statement):]
                break

        return result

    def _shorten_long_statements(self, text: str) -> str:
        """简化过长的陈述"""
        # 移除冗余的修饰词
        fillers = ["非常", "特别", "相当", "极其", "十分"]

        for filler in fillers:
            if filler in text and len(text) > 30 and random.random() < self.intensity:
                text = text.replace(filler, "", 1)
                break

        return text

    def transform(self, text: str) -> str:
        """执行语气变换"""
        if not text:
            return text

        result = text

        # 书面语转口语 - 确保执行
        result = self._spoken_transform(result)

        # 添加犹豫语气
        result = self._add_hesitation(result)

        # 添加反问
        if random.random() < self.intensity * 1.5:
            result = self._add_rhetorical_question(result)

        # 简化冗长陈述
        result = self._shorten_long_statements(result)

        return result
