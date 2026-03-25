"""
小说文本转换器
针对小说文本特点的反检测策略
"""

import random
import re
from typing import List, Dict, Tuple, Optional


class DialogueTransformer:
    """对话转换器 - 变换对话格式和标记"""

    DIALOGUE_MARKERS = ['"', '"', '"', '"', '「', '」', '『', '』', '『', '』']
    THOUGHT_MARKERS = ['*', '～', '——', '「', '』']

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def alternate_dialogue_markers(self, text: str) -> str:
        """交替使用不同的对话标记"""
        result = text

        # 替换双引号为其他引号
        replacements = [
            ('"', '「'), ('"', '」'),
            ('"', '『'), ('"', '』'),
        ]

        for old, new in replacements:
            if old in text and random.random() < self.intensity:
                result = result.replace(old, new, 1)
                break

        return result

    def remove_dialogue_tags(self, text: str) -> str:
        """移除部分对话标签（如 XX说：）"""
        patterns = [
            r'\w+说[道称喊叫问]?[:：]',
            r'"\s*',
            r'\s*"',
            r'[「『]\s*',
            r'\s*[」』]',
        ]

        if random.random() < self.intensity * 0.5:
            for pattern in patterns[:2]:
                result = re.sub(pattern, '', text, count=1)
                if result != text:
                    return result

        return text

    def add_dialogue_tags(self, text: str) -> str:
        """为无标记对话添加标签"""
        speaker_tags = ['低声', '高声', '轻声', '喃喃', '缓缓', '突然', '平静']

        # 寻找独立句子并添加标签
        sentences = re.split(r'([。！？])', text)

        for i, sent in enumerate(sentences):
            if len(sent) > 10 and random.random() < self.intensity * 0.3:
                if '"' in sent or '「' in sent:
                    tag = random.choice(speaker_tags)
                    sentences[i] = f"{tag}，{sent}"
                    break

        return ''.join(sentences)

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            result = self.alternate_dialogue_markers(result)

        if random.random() < self.intensity * 0.5:
            if random.random() < 0.5:
                result = self.remove_dialogue_tags(result)
            else:
                result = self.add_dialogue_tags(result)

        return result


class NarrativePerspectiveTransformer:
    """叙事视角转换器 - 第一/第三人称切换"""

    FIRST_PERSON_WORDS = ['我', '我的', '我们', '我们的']
    THIRD_PERSON_WORDS = ['他', '她', '他们', '它的']

    def __init__(self, intensity: float = 0.15):
        self.intensity = intensity

    def flip_perspective(self, text: str) -> str:
        """翻转叙事视角"""
        result = text

        # 第一人称转第三人称
        for word in self.FIRST_PERSON_WORDS:
            if word in text and random.random() < self.intensity:
                replacements = {
                    '我': random.choice(['他', '她', '这个人']),
                    '我的': random.choice(['他的', '她的', '这个人的']),
                    '我们': random.choice(['他们', '大家', '这些人']),
                    '我们的': random.choice(['他们的', '大家的', '这些人的']),
                }
                result = result.replace(word, replacements[word], 1)
                break

        return result

    def add_perspective_markers(self, text: str) -> str:
        """添加视角标记"""
        markers = ['他注意到', '她心想', '他感觉到', '她看见', '他听到']

        sentences = text.split('。')
        for i, sent in enumerate(sentences):
            if len(sent) > 15 and random.random() < self.intensity * 0.2:
                if '他' in sent or '她' in sent:
                    sentences[i] = random.choice(markers) + sent
                    break

        return '。'.join(sentences)

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            result = self.flip_perspective(result)

        if random.random() < self.intensity * 0.5:
            result = self.add_perspective_markers(result)

        return result


class MetaphorTransformer:
    """比喻/修辞转换器"""

    METAPHOR_PATTERNS = [
        (r'(\w+)像(\w+)', r'\1仿佛\2'),
        (r'(\w+)如同(\w+)', r'\1像\2'),
        (r'(\w+)似的', r'\1一般'),
        (r'像(\w+)一样', r'如同\1'),
    ]

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def vary_metaphors(self, text: str) -> str:
        """变化比喻说法"""
        result = text

        for pattern, replacement in self.METAPHOR_PATTERNS:
            if random.random() < self.intensity:
                new_text = re.sub(pattern, replacement, result, count=1)
                if new_text != result:
                    return new_text

        return result

    def simplify_metaphors(self, text: str) -> str:
        """简化复杂比喻"""
        # 将"像...一样"简化为"像..."
        if '像' in text and '一样' in text and random.random() < self.intensity:
            text = text.replace('一样', '', 1)

        return text

    def expand_metaphors(self, text: str) -> str:
        """扩展简单比喻"""
        expansions = ['一样', '一般', '似的', '般']

        if random.random() < self.intensity * 0.5:
            # 在"像"后添加扩展词
            if '像' in text:
                idx = text.find('像')
                if idx > 0 and idx < len(text) - 1:
                    char_after = text[idx + 1]
                    if char_after not in expansions:
                        text = text[:idx + 1] + random.choice(expansions) + text[idx + 1:]

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            result = self.vary_metaphors(result)

        if random.random() < self.intensity * 0.5:
            if random.random() < 0.5:
                result = self.simplify_metaphors(result)
            else:
                result = self.expand_metaphors(result)

        return result


class InnerMonologueTransformer:
    """内心独白转换器"""

    def __init__(self, intensity: float = 0.25):
        self.intensity = intensity

    def format_as_thought(self, text: str) -> str:
        """将句子格式化为内心独白"""
        thought_prefixes = [
            '心想：', '想着：', '暗自道：', '心中暗想：',
            '不由得想：', '不禁思索：', '思绪飘向：',
        ]

        # 寻找适合转为内心独白的陈述句
        sentences = text.split('。')
        for i, sent in enumerate(sentences):
            if len(sent) > 10 and '说' not in sent and '想' not in sent:
                if random.random() < self.intensity * 0.3:
                    prefix = random.choice(thought_prefixes)
                    sentences[i] = f"她{prefix}「{sent}」"
                    break

        return '。'.join(sentences)

    def remove_thought_markers(self, text: str) -> str:
        """移除内心独白标记"""
        patterns = [
            r'心想[：:][「『]',
            r'想着[：:][「『]',
            r'[」』]$',
            r'^[「『]',
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                text = re.sub(pattern, '', text, count=1)
                break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            if random.random() < 0.5:
                result = self.format_as_thought(result)
            else:
                result = self.remove_thought_markers(result)

        return result


class ActionDescriptionTransformer:
    """动作描写转换器"""

    ACTION_VERBS = [
        '走', '跑', '站', '坐', '躺', '看', '听', '说',
        '想', '笑', '哭', '生气', '害怕', '惊讶',
    ]

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def expand_actions(self, text: str) -> str:
        """扩展简单动作描写"""
        expansions = {
            '走': ['缓缓走去', '一步步走向', '信步走到'],
            '看': ['目光落在', '眼神飘向', '定睛看'],
            '说': ['开口道', '低声说', '喃喃道'],
            '笑': ['嘴角上扬', '露出微笑', '轻笑一声'],
            '哭': ['眼眶泛红', '泪水滑落', '低声啜泣'],
        }

        for verb, exps in expansions.items():
            if verb in text and random.random() < self.intensity:
                text = text.replace(verb, random.choice(exps), 1)
                break

        return text

    def shorten_actions(self, text: str) -> str:
        """简化冗长动作描写"""
        shortenings = [
            ('缓缓', ''),
            ('慢慢地', ''),
            ('一步步', ''),
            ('轻轻地', ''),
            ('静静地', ''),
        ]

        for old, new in shortenings:
            if old in text and random.random() < self.intensity:
                text = text.replace(old, new, 1)
                break

        return text

    def add_physical_details(self, text: str) -> str:
        """添加身体细节"""
        details = [
            '手指微微颤抖，',
            '眉头紧锁，',
            '深吸一口气，',
            '不禁后退一步，',
            '眼眶微红，',
        ]

        if random.random() < self.intensity * 0.3:
            for detail in details:
                if detail.strip('，') in text:
                    continue
                # 在句首添加
                text = detail + text
                break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            if random.random() < 0.5:
                result = self.expand_actions(result)
            else:
                result = self.shorten_actions(result)

        if random.random() < self.intensity * 0.5:
            result = self.add_physical_details(result)

        return result


class SceneDescriptionTransformer:
    """场景描写转换器"""

    SCENE_OPENERS = [
        '夜幕降临，', '清晨的阳光', '房间里，', '街道上，',
        '微风拂过，', '雨声淅沥，', '月光如水，',
    ]

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def add_scene_opener(self, text: str) -> str:
        """添加场景开头"""
        if random.random() < self.intensity * 0.3:
            opener = random.choice(self.SCENE_OPENERS)
            text = opener + text

        return text

    def remove_scene_opener(self, text: str) -> str:
        """移除场景描写"""
        for opener in self.SCENE_OPENERS:
            if opener in text and random.random() < self.intensity:
                text = text.replace(opener, '', 1)
                break

        return text

    def vary_scene_elements(self, text: str) -> str:
        """变化场景元素词汇"""
        variations = {
            '夜幕': '夜色', '黄昏': '傍晚', '清晨': '早晨',
            '阳光': '日光', '微风': '轻风', '雨声': '雨滴',
        }

        for old, new in variations.items():
            if old in text and random.random() < self.intensity:
                text = text.replace(old, new, 1)
                break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            if random.random() < 0.5:
                result = self.add_scene_opener(result)
            else:
                result = self.remove_scene_opener(result)

        if random.random() < self.intensity * 0.5:
            result = self.vary_scene_elements(result)

        return result


class CharacterNameTransformer:
    """人物称呼转换器"""

    NAME_VARIATIONS = {
        '小明': ['小名', '那孩子', '少年', '他'],
        '小红': ['小丫头', '那姑娘', '少女', '她'],
        '老人': ['老者', '老先生', '那老人', '他'],
        '老板': ['掌柜', '那人', '主管', '他'],
    }

    def __init__(self, intensity: float = 0.15):
        self.intensity = intensity

    def vary_names(self, text: str) -> str:
        """变化人物称呼"""
        for name, variations in self.NAME_VARIATIONS.items():
            if name in text and random.random() < self.intensity:
                text = text.replace(name, random.choice(variations), 1)
                break

        return text

    def add_name_suffixes(self, text: str) -> str:
        """添加称呼后缀"""
        suffixes = ['先生', '女士', '小姐', '同志', '同学']

        # 检测人名并添加后缀
        # 这是一个简化实现
        for suffix in suffixes:
            if suffix not in text and random.random() < self.intensity * 0.2:
                # 寻找句尾的人名并添加后缀
                match = re.search(r'([李王张刘陈杨黄赵周吴徐孙马朱胡郭何高林郑])老师', text)
                if match:
                    old = match.group(0)
                    new = match.group(1) + '老师'
                    text = text.replace(old, new, 1)
                    break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            result = self.vary_names(result)

        if random.random() < self.intensity * 0.3:
            result = self.add_name_suffixes(result)

        return result


class EmotionalIntensityTransformer:
    """情感强度转换器"""

    INTENSIFIERS = ['非常', '十分', '极其', '格外', '相当', '颇为']
    DEINTENSIFIERS = ['有些', '有点', '略微', '稍稍', '一点']

    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity

    def intensify_emotion(self, text: str) -> str:
        """增强情感强度"""
        for word in ['喜欢', '讨厌', '害怕', '高兴', '悲伤', '生气']:
            if word in text and random.random() < self.intensity:
                intensifier = random.choice(self.INTENSIFIERS)
                text = text.replace(word, f"{intensifier}{word}", 1)
                break

        return text

    def deintensify_emotion(self, text: str) -> str:
        """减弱情感强度"""
        for word in ['非常喜欢', '十分讨厌', '极其害怕', '格外高兴']:
            if word in text and random.random() < self.intensity:
                deintensifier = random.choice(self.DEINTENSIFIERS)
                text = text.replace(word, word.replace('非常', '').replace('十分', ''))
                if text != word:
                    text = text.replace(word, deintensifier + word[2:])
                break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            if random.random() < 0.5:
                result = self.intensify_emotion(result)
            else:
                result = self.deintensify_emotion(result)

        return result


class NarrativeRhythmTransformer:
    """叙事节奏转换器 - 变化句子长短"""

    SHORT_SENTENCE_STARTERS = ['突然', '忽然', '猛然', '骤然', '陡然']

    def __init__(self, intensity: float = 0.25):
        self.intensity = intensity

    def break_long_sentences(self, text: str) -> str:
        """拆分长句"""
        # 寻找超过30字符的句子并在中间拆分
        if len(text) > 50:
            for sep in ['，', '。', '；']:
                idx = text.find(sep, len(text) // 2)
                if idx > 0 and idx < len(text) - 5:
                    if random.random() < self.intensity:
                        text = text[:idx + 1] + '。' + text[idx + 1:]
                        break

        return text

    def merge_short_sentences(self, text: str) -> str:
        """合并短句"""
        sentences = text.split('。')
        if len(sentences) > 2:
            merged = [sentences[0]]
            buffer = sentences[1]

            for i in range(2, len(sentences)):
                if len(sentences[i]) < 15 and random.random() < self.intensity:
                    buffer += sentences[i]
                else:
                    merged.append(buffer)
                    buffer = sentences[i]

            if buffer:
                merged.append(buffer)

            return '。'.join(merged)

        return text

    def add_sudden_changes(self, text: str) -> str:
        """添加突然变化"""
        starters = self.SHORT_SENTENCE_STARTERS

        for starter in starters:
            if starter not in text and random.random() < self.intensity * 0.3:
                # 在适当位置添加
                sentences = text.split('。')
                if len(sentences) >= 2:
                    idx = random.randint(1, len(sentences) - 1)
                    sentences[idx] = starter + sentences[idx]
                    return '。'.join(sentences)
                break

        return text

    def transform(self, text: str) -> str:
        if not text:
            return text

        result = text

        if random.random() < self.intensity:
            if random.random() < 0.5:
                result = self.break_long_sentences(result)
            else:
                result = self.merge_short_sentences(result)

        if random.random() < self.intensity * 0.5:
            result = self.add_sudden_changes(result)

        return result
