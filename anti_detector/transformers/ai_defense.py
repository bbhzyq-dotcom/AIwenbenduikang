"""
AI检测器对抗策略
基于AI检测器工作原理的针对性对抗
"""

import random
import re
import jieba
import jieba.posseg as pseg
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class DetectionVulnerability:
    """检测器漏洞"""
    name: str
    description: str
    countermeasure: str
    effectiveness: str


class AIReIDDefense:
    """
    AI检测器对抗策略集

    基于AI检测器的工作原理，实现针对性的对抗策略：

    1. **困惑度(Perplexity)对抗**:
       - AI文本困惑度通常较低且稳定
       - 策略：增加词汇变化，引入低频词汇

    2. **突发性(Burstiness)对抗**:
       - AI句子长度变化小
       - 策略：故意制造长短句变化

    3. **正式度(Formality)对抗**:
       - AI文本过于正式
       - 策略：添加口语化表达、感叹词

    4. **N-gram分布对抗**:
       - AI使用高频N-gram组合
       - 策略：同义词替换，打破固定搭配

    5. **句子结构一致性对抗**:
       - AI句子结构过于规整
       - 策略：变化句式，主动被动交替
    """

    def __init__(self, intensity: float = 0.3):
        self.intensity = intensity

        self._colloquial_markers = [
            "说实话", "说真的", "实话说", "要我说", "按理说",
            "这么一看", "说起来", "你知道", "你知道吗",
            "我觉得", "我个人", "个人感觉", "说实话",
            "嗯", "啊", "嘛", "呢", "吧", "呀", "哦", "呃",
        ]

        self._sentence_openers = [
            "突然", "忽然", "猛然", "骤然", "陡然",
            "没想到", "不料", "谁知道", "说时迟那时快",
        ]

        self._sentence_connectors = [
            "可是", "但是", "然而", "不过", "只是", "偏",
            "于是", "就这么着", "结果", "没想到", "不料",
        ]

        self._interjections = [
            "哎呀", "哎哟", "哇", "嗯", "啊", "噢", "呃",
            "等等", "对了", "话说", "说起来", "你看",
        ]

        self._doubt_markers = [
            "难道", "岂不是", "何不", "何须", "不必",
            "难道说", "该不会", "该不会是", "说不定",
        ]

    def break_perplexity_pattern(self, text: str) -> str:
        """
        打破困惑度模式

        AI文本困惑度通常较低，通过以下方式增加变化：
        1. 引入低频词汇
        2. 增加词汇多样性
        """
        words = list(jieba.cut(text))
        result = []

        rare_word_replacements = {
            "重要": ["紧要", "举足轻重"],
            "非常": ["格外", "尤为"],
            "特别": ["格外", "尤为"],
            "认为": ["觉得", "以为"],
            "知道": ["清楚", "明白"],
            "因为": ["由于", "缘于"],
            "所以": ["于是", "因而"],
            "但是": ["可是", "只是"],
            "如果": ["倘若", "假如"],
        }

        for word in words:
            if word in rare_word_replacements and random.random() < self.intensity * 0.5:
                result.append(random.choice(rare_word_replacements[word]))
            else:
                result.append(word)

        return ''.join(result)

    def add_burstiness(self, text: str) -> str:
        """
        增加句子突发性

        人类写作句子长短不一，AI写作句子长度均匀
        """
        if len(text) < 50 or '。' not in text:
            return text

        sentences = re.split(r'([。！？])', text)
        result = []

        for i, part in enumerate(sentences):
            if part in '。！？':
                if random.random() < self.intensity * 0.3:
                    if random.random() < 0.5 and len(result) > 5:
                        result.append(part)
                        result.append(random.choice(self._sentence_openers))
                    else:
                        result.append(part)
                else:
                    result.append(part)
            elif part.strip():
                if random.random() < self.intensity * 0.2:
                    opener = random.choice(self._sentence_openers)
                    result.append(opener + part)
                else:
                    result.append(part)

        return ''.join(result)

    def add_colloquial_style(self, text: str) -> str:
        """
        添加口语化表达

        AI文本通常过于正式，添加口语化标记可以有效对抗
        """
        result = text

        for marker in self._colloquial_markers:
            if marker in result:
                continue

            if random.random() < self.intensity * 0.3:
                if '，' in result:
                    pos = result.find('，')
                    if pos > 0 and pos < len(result) - 1:
                        result = result[:pos + 1] + marker + "，" + result[pos + 1:]
                        break
                elif '。' in result:
                    pos = result.find('。')
                    if pos > 0:
                        result = result[:pos] + "，" + marker + result[pos:]
                        break

        if random.random() < self.intensity * 0.2:
            if not result.endswith('。'):
                result = result + random.choice(['嘛', '呢', '吧', '呀'])

        return result

    def add_interjections(self, text: str) -> str:
        """
        添加感叹词和插入语

        人类写作中常有无规律的感叹和插入
        """
        if len(text) < 20:
            return text

        result = []

        for char in text:
            result.append(char)
            if char == '，' and random.random() < self.intensity * 0.15:
                if random.random() < 0.5:
                    result.append(random.choice(self._interjections))
                    result.append('，')

        return ''.join(result)

    def break_ngram_patterns(self, text: str) -> str:
        """
        打破N-gram固定搭配

        AI写作倾向于使用高频N-gram组合，通过替换打破
        """
        replacements = {
            "首先": random.choice(["第一", "起先", "一开头"]),
            "其次": random.choice(["第二", "而后", "再者"]),
            "最后": random.choice(["最终", "临了", "到头来"]),
            "与此同时": random.choice(["这时", "那会儿", "正当这会儿"]),
            "总而言之": random.choice(["总之", "说到底", "要之"]),
            "综上所述": random.choice(["总之", "归根结底", "说到底"]),
            "因此": random.choice(["所以", "于是", "因而"]),
            "然而": random.choice(["可是", "但是", "不过"]),
            "而且": random.choice(["并且", "同时", "加之"]),
            "一方面": random.choice(["一则", "一头", "一面"]),
        }

        result = text
        for pattern, replacement in replacements.items():
            if pattern in result and random.random() < self.intensity * 0.5:
                result = result.replace(pattern, replacement, 1)
                break

        return result

    def vary_sentence_structure(self, text: str) -> str:
        """
        变化句子结构

        AI写作句子结构一致，通过拆分、合并、倒装等变化
        """
        sentences = re.split(r'([。！？])', text)
        result = []

        for i, part in enumerate(sentences):
            if part in '。！？':
                result.append(part)
            elif part.strip():
                if len(part) > 30 and random.random() < self.intensity * 0.3:
                    connectors = ['可是', '但是', '不过', '只是', '偏', '然而']
                    if any(c in part for c in connectors):
                        for c in connectors:
                            if c in part:
                                idx = part.find(c)
                                if idx > 0:
                                    front = part[:idx]
                                    back = part[idx:]
                                    result.append(back + front)
                                    break
                    else:
                        result.append(part)
                else:
                    result.append(part)

        return ''.join(result)

    def add_doubt_questions(self, text: str) -> str:
        """
        添加反问句

        人类写作常伴有思考和疑问
        """
        if len(text) < 30 or '。' not in text:
            return text

        doubt_phrases = [
            "难道不是吗？",
            "你说是不是？",
            "这事儿你怎么看？",
            "这难道不值得深思吗？",
            "你说呢？",
        ]

        if random.random() < self.intensity * 0.2:
            sentences = text.split('。')
            if len(sentences) >= 2:
                insert_pos = random.randint(1, len(sentences) - 1)
                sentences.insert(insert_pos, random.choice(doubt_phrases))
                return '。'.join(sentences)

        return text

    def remove_mechanical_structures(self, text: str) -> str:
        """
        移除机械性结构

        AI写作常见"首先...其次...最后"等机械结构
        """
        mechanical_patterns = [
            (r'首先([，。])', r'第一\1'),
            (r'其次([，。])', r'第二\1'),
            (r'最后([，。])', r'临了\1'),
            (r'第一([，])', r'首先\1'),
            (r'第二([，])', r'其次\1'),
        ]

        result = text
        for pattern, replacement in mechanical_patterns:
            if random.random() < self.intensity * 0.5:
                new_text = re.sub(pattern, replacement, result)
                if new_text != result:
                    result = new_text
                    break

        return result

    def transform(self, text: str) -> str:
        """综合变换 - 确保高强度时执行多种变换"""
        if not text:
            return text

        result = text

        # 确保关键变换一定执行
        result = self.break_ngram_patterns(result)

        result = self.remove_mechanical_structures(result)

        # 随机性变换
        if random.random() < self.intensity * 1.5:
            result = self.break_perplexity_pattern(result)

        if random.random() < self.intensity * 1.5:
            result = self.add_burstiness(result)

        if random.random() < self.intensity * 1.5:
            result = self.add_colloquial_style(result)

        if random.random() < self.intensity * 1.0:
            result = self.add_interjections(result)

        if random.random() < self.intensity * 0.8:
            result = self.add_doubt_questions(result)

        if random.random() < self.intensity * 1.0:
            result = self.vary_sentence_structure(result)

        return result


class TargetedDefense:
    """
    针对特定检测器的专项对抗

    已知AI检测器的检测原理：
    - **GPTZero**: 基于困惑度(perplexity)和突发性(burstiness)
    - **朱雀**: 基于词汇分布、句子结构、语义连贯性
    - **Originality.ai**: 基于N-gram分布和词汇丰富度
    """

    def __init__(self, intensity: float = 0.3):
        self.intensity = intensity

    def against_gptzero(self, text: str) -> str:
        """
        对抗GPTZero

        GPTZero主要检测:
        1. Perplexity (困惑度): AI文本困惑度低
        2. Burstiness (突发性): AI句子长度均匀
        """
        defense = AIReIDDefense(self.intensity)
        text = defense.break_perplexity_pattern(text)
        text = defense.add_burstiness(text)
        text = defense.add_colloquial_style(text)
        return text

    def against_zhuque(self, text: str) -> str:
        """
        对抗朱雀检测

        朱雀检测主要关注:
        1. 词汇分布异常
        2. 句子结构过于规整
        3. 语义连贯性过于完美
        """
        defense = AIReIDDefense(self.intensity)
        text = defense.break_ngram_patterns(text)
        text = defense.vary_sentence_structure(text)
        text = defense.remove_mechanical_structures(text)
        text = defense.add_interjections(text)
        return text

    def against_originality(self, text: str) -> str:
        """
        对抗Originality.ai

        Originality.ai主要检测:
        1. N-gram分布
        2. 词汇丰富度
        3. 特定短语频率
        """
        defense = AIReIDDefense(self.intensity)
        text = defense.break_perplexity_pattern(text)
        text = defense.break_ngram_patterns(text)
        text = defense.add_colloquial_style(text)
        return text

    def transform(self, text: str, target: str = "all") -> str:
        """
        通用变换接口

        Args:
            text: 输入文本
            target: 目标检测器，可选 "gptzero", "zhuque", "originality", "all"
        """
        if target == "gptzero":
            return self.against_gptzero(text)
        elif target == "zhuque":
            return self.against_zhuque(text)
        elif target == "originality":
            return self.against_originality(text)
        else:
            defense = AIReIDDefense(self.intensity)
            return defense.transform(text)


class SemanticDefense:
    """
    语义级对抗策略

    在保持语义基本不变的情况下进行深层变换
    """

    def __init__(self, intensity: float = 0.3):
        self.intensity = intensity

    def paraphrase_simple(self, text: str) -> str:
        """简单 paraphrase"""
        patterns = [
            (r'(\w+)很(\w+)', r'\1\2得很'),
            (r'非常(\w+)', r'极其\1'),
            (r'特别(\w+)', r'格外\1'),
        ]

        for pattern, replacement in patterns:
            if random.random() < self.intensity * 0.3:
                new_text = re.sub(pattern, replacement, text)
                if new_text != text:
                    return new_text

        return text

    def split_long_sentences(self, text: str) -> str:
        """拆分长句"""
        if len(text) < 50:
            return text

        result = []
        for sentence in re.split(r'([。！？；])', text):
            if len(sentence) > 40 and random.random() < self.intensity:
                mid = len(sentence) // 2
                for sep in ['，', '、', ';', '：']:
                    pos = sentence.rfind(sep, 0, mid)
                    if pos > 0:
                        result.append(sentence[:pos + 1])
                        result.append('。')
                        result.append(sentence[pos + 1:])
                        break
                    else:
                        result.append(sentence)
            else:
                result.append(sentence)

        return ''.join(result)

    def merge_short_sentences(self, text: str) -> str:
        """合并短句"""
        sentences = re.split(r'([。！？])', text)
        sentences = [s for s in sentences if s.strip()]

        if len(sentences) < 3:
            return text

        merged = [sentences[0]]
        for i in range(1, len(sentences)):
            if len(sentences[i]) < 15 and random.random() < self.intensity * 0.5:
                merged[-1] = merged[-1] + '，' + sentences[i]
            else:
                merged.append(sentences[i])

        return '。'.join(merged) + '。'

    def transform(self, text: str) -> str:
        """综合语义变换"""
        result = text

        if random.random() < self.intensity:
            result = self.paraphrase_simple(result)

        if random.random() < self.intensity * 0.6:
            if len(text) > 50:
                result = self.split_long_sentences(result)

        if random.random() < self.intensity * 0.4:
            result = self.merge_short_sentences(result)

        return result
