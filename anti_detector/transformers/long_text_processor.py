"""
长文本处理器
针对几千字长文本的优化处理
"""

import random
import re
from typing import List, Tuple, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass


@dataclass
class TextSegment:
    """文本段落"""
    content: str
    segment_type: str  # "normal", "dialogue", "title", "enum"
    position: int  # 在原文中的位置
    ai_score: float = 0.0


class LongTextProcessor:
    """
    长文本处理器

    优化策略：
    1. 智能分段 - 按段落、句子结构分段
    2. 选择性变换 - AI特征高的段落重点变换
    3. 结构保持 - 保留标题、列表等结构
    4. 分层处理 - 段内变换 + 段间变换
    """

    # AI高风险模式（需要重点变换）
    HIGH_RISK_PATTERNS = [
        r"综上所述",
        r"总而言之",
        r"首先[,，].*?其次[,，].*?最后",
        r"第一[,，].*?第二[,，].*?第三",
        r"一方面.*?另一方面",
        r"随着时代的发展",
        r"在当今社会",
        r"研究表明",
        r"实验数据表明",
        r"毫无疑问",
        r"不言而喻",
        r"显而易见",
        r"值得注意的是",
        r"更重要的是",
        r"本文旨在",
        r"本文将",
        r"本文通过",
    ]

    # 需要保留原样的结构
    STRUCTURE_PATTERNS = [
        (r"^#+\s+.+$", "title"),  # Markdown标题
        (r"^\d+\.\s+.+$", "enum"),  # 编号列表
        (r"^[a-zA-Z]\.\s+.+$", "enum"),  # 字母列表
        (r"^[A-Z]\.\s+.+$", "enum"),  # 大写字母列表
        (r"^\([a-zA-Z]\)\s+.+$", "enum"),  # (a) (b) 格式
        (r"^\d+[)、]\s+.+$", "enum"),  # 1)、2) 格式
        (r"^\-\s+.+$", "enum"),  # - 列表
        (r"^\*\s+.+$", "enum"),  # * 列表
    ]

    def __init__(self, engine, detector, min_segment_length: int = 50):
        """
        Args:
            engine: 反检测引擎
            detector: AI检测器
            min_segment_length: 最小段落长度，短于此的段落不单独处理
        """
        self.engine = engine
        self.detector = detector
        self.min_segment_length = min_segment_length

    def process(self, text: str, intensity: Optional[float] = None) -> str:
        """
        处理长文本

        Args:
            text: 输入文本
            intensity: 扰动强度，如果为None则使用引擎默认强度

        Returns:
            处理后的文本
        """
        if len(text) < 300:
            return self.engine.transform(text)

        # 1. 智能分段
        segments = self._split_segments(text)

        # 2. 对每个段落进行评估和变换
        result_segments = []
        for segment in segments:
            if segment.segment_type == "title":
                # 标题保持不变
                result_segments.append(segment.content)
            elif segment.segment_type == "enum":
                # 列表项轻度变换
                result_segments.append(self._light_transform(segment.content))
            elif len(segment.content) < self.min_segment_length:
                # 短段落直接变换
                result_segments.append(self.engine.transform(segment.content))
            elif segment.ai_score > 0.5:
                # AI概率高的段落重点变换
                result_segments.append(self._deep_transform(segment.content))
            else:
                # 正常段落标准变换
                result_segments.append(self.engine.transform(segment.content))

        return self._join_segments(result_segments, segments)

    def _split_segments(self, text: str) -> List[TextSegment]:
        """将文本智能分段"""
        segments = []
        lines = text.split('\n')
        current_para = []
        current_position = 0

        for line in lines:
            stripped = line.strip()

            if not stripped:
                # 空行 - 结束当前段落
                if current_para:
                    content = '\n'.join(current_para)
                    if len(content) > 0:
                        segments.append(TextSegment(
                            content=content,
                            segment_type=self._detect_segment_type(content),
                            position=current_position
                        ))
                    current_para = []
                current_position += len(line) + 1
                continue

            # 检测是否是特殊结构
            is_special, seg_type = self._is_special_structure(stripped)
            if is_special:
                # 先保存当前段落
                if current_para:
                    content = '\n'.join(current_para)
                    if len(content) > 0:
                        segments.append(TextSegment(
                            content=content,
                            segment_type=self._detect_segment_type(content),
                            position=current_position
                        ))
                    current_para = []

                # 添加特殊结构行
                segments.append(TextSegment(
                    content=stripped,
                    segment_type=seg_type,
                    position=current_position
                ))
                current_position += len(line) + 1
                continue

            # 检测段落类型
            seg_type = self._detect_segment_type(stripped)

            # 对话检测
            if '"' in stripped or '"' in stripped or '"' in stripped or '「' in stripped or '『' in stripped:
                if current_para:
                    content = '\n'.join(current_para)
                    if len(content) > 0:
                        segments.append(TextSegment(
                            content=content,
                            segment_type=self._detect_segment_type(content),
                            position=current_position
                        ))
                    current_para = []
                segments.append(TextSegment(
                    content=stripped,
                    segment_type="dialogue",
                    position=current_position
                ))
                current_position += len(line) + 1
                continue

            # 普通段落
            if seg_type == "normal" and len(stripped) > 200:
                # 长段落 - 可能需要进一步拆分
                sub_segments = self._split_long_paragraph(stripped, current_position)
                segments.extend(sub_segments)
            else:
                current_para.append(stripped)

            current_position += len(line) + 1

        # 处理最后一段
        if current_para:
            content = '\n'.join(current_para)
            if len(content) > 0:
                segments.append(TextSegment(
                    content=content,
                    segment_type=self._detect_segment_type(content),
                    position=current_position
                ))

        # 评估每个段的AI概率
        for segment in segments:
            if segment.segment_type == "title":
                segment.ai_score = 0.0
            else:
                detection = self.detector.detect_ai_writing_markers(segment.content)
                segment.ai_score = detection['ai_score']

        return segments

    def _split_long_paragraph(self, text: str, base_position: int) -> List[TextSegment]:
        """将长段落拆分为较短的段落"""
        segments = []

        # 按句子拆分
        sentences = re.split(r'([。！？；])', text)
        current = ""
        current_len = 0
        max_len = 300

        for i, part in enumerate(sentences):
            current_len += len(part)
            current += part

            # 在标点处可以考虑分段
            if part in '。！？；' and current_len > max_len:
                if current.strip():
                    segments.append(TextSegment(
                        content=current,
                        segment_type="normal",
                        position=base_position
                    ))
                current = ""
                current_len = 0

        # 处理最后一段
        if current.strip():
            segments.append(TextSegment(
                content=current,
                segment_type="normal",
                position=base_position
            ))

        return segments if segments else [TextSegment(
            content=text,
            segment_type="normal",
            position=base_position
        )]

    def _is_special_structure(self, line: str) -> Tuple[bool, str]:
        """检测是否是特殊结构"""
        for pattern, seg_type in self.STRUCTURE_PATTERNS:
            if re.match(pattern, line.strip()):
                return True, seg_type
        return False, ""

    def _detect_segment_type(self, text: str) -> str:
        """检测段落类型"""
        # 对话检测
        dialogue_markers = ['"', '"', '"', '"', '「', '」', '『', '』', '"', '"']
        if any(m in text for m in dialogue_markers):
            return "dialogue"

        # 检测是否是列表
        if re.match(r"^\s*[\d一二三四五六七八九十]+[、.．)]", text):
            return "enum"
        if re.match(r"^\s*[a-zA-Z][\.、)]", text):
            return "enum"

        return "normal"

    def _light_transform(self, text: str) -> str:
        """轻度变换 - 用于列表等结构"""
        # 只做少量变换
        engine = self.engine
        original_intensity = engine.intensity
        engine.intensity = original_intensity * 0.3
        result = engine.transform(text)
        engine.intensity = original_intensity
        return result

    def _deep_transform(self, text: str) -> str:
        """深度变换 - 用于AI概率高的段落"""
        engine = self.engine
        original_intensity = engine.intensity

        # 多次变换
        result = text
        for _ in range(2):
            engine.intensity = original_intensity * 1.5
            result = engine.transform(result)

        engine.intensity = original_intensity
        return result

    def _join_segments(self, results: List[str], segments: List[TextSegment]) -> str:
        """合并处理后的段落"""
        # 简化处理：直接用换行连接
        return '\n'.join(results)


class ParagraphAwareTransformer:
    """
    段落感知变换器

    在保持段落结构的同时进行深度变换
    """

    def __init__(self, base_transformer: Callable, min_paragraph_len: int = 100):
        """
        Args:
            base_transformer: 基础变换函数
            min_paragraph_len: 最小段落长度
        """
        self.base_transformer = base_transformer
        self.min_paragraph_len = min_paragraph_len

    def transform(self, text: str) -> str:
        """变换长文本"""
        if len(text) < self.min_paragraph_len:
            return self.base_transformer(text)

        paragraphs = text.split('\n\n')
        result = []

        for para in paragraphs:
            if not para.strip():
                continue

            # 判断段落类型
            para_type = self._classify_paragraph(para)

            if para_type == "title":
                # 标题不变换
                result.append(para)
            elif para_type == "short":
                # 短段落轻度变换
                result.append(self._light_transform(para))
            elif para_type == "dialogue":
                # 对话段落 - 只变换叙述部分
                result.append(self._transform_dialogue(para))
            else:
                # 正常段落标准变换
                result.append(self.base_transformer(para))

        return '\n\n'.join(result)

    def _classify_paragraph(self, para: str) -> str:
        """分类段落"""
        lines = para.strip().split('\n')

        # 单行可能是标题
        if len(lines) == 1 and len(para) < 100 and not any('。' in l for l in lines):
            return "title"

        # 对话段落
        dialogue_lines = 0
        for line in lines:
            if any(d in line for d in ['"', '"', '"', '「', '『', '"']):
                dialogue_lines += 1

        if dialogue_lines > len(lines) * 0.3:
            return "dialogue"

        # 短段落
        if len(para) < self.min_paragraph_len:
            return "short"

        return "normal"

    def _light_transform(self, text: str) -> str:
        """轻度变换"""
        # 只做同义词替换
        from anti_detector.transformers import SynonymTransformer
        transformer = SynonymTransformer(intensity=0.2)
        return transformer.transform(text)

    def _transform_dialogue(self, text: str) -> str:
        """变换对话段落 - 保持对话，只变换叙述"""
        # 简化处理：整体轻度变换
        return self._light_transform(text)


class AdaptiveLongTextProcessor:
    """
    自适应长文本处理器

    根据文本内容自动选择最优处理策略
    """

    def __init__(self, engine, detector):
        self.engine = engine
        self.detector = detector
        self.long_processor = LongTextProcessor(engine, detector)
        self.paragraph_transformer = ParagraphAwareTransformer(engine.transform)

    def process(self, text: str) -> str:
        """
        自适应处理长文本

        策略：
        1. 小于500字：直接用引擎处理
        2. 500-2000字：段落感知处理
        3. 大于2000字：长文本处理器 + 段落感知
        """
        text = text.strip()
        if not text:
            return text

        length = len(text)

        if length < 500:
            # 短文本直接处理
            return self.engine.transform(text)

        elif length < 2000:
            # 中等文本段落感知处理
            return self.paragraph_transformer.transform(text)

        else:
            # 长文本多层处理
            # 第一步：长文本处理器分段处理
            result = self.long_processor.process(text)

            # 第二步：段落感知再处理
            result = self.paragraph_transformer.transform(result)

            return result

    def process_with_report(self, text: str) -> Tuple[str, dict]:
        """
        处理并生成报告

        Returns:
            (处理后的文本, 处理报告)
        """
        original_score = self.detector.detect_ai_writing_markers(text)['ai_score']

        processed = self.process(text)
        processed_score = self.detector.detect_ai_writing_markers(processed)['ai_score']

        report = {
            "original_length": len(text),
            "processed_length": len(processed),
            "original_ai_score": original_score,
            "processed_ai_score": processed_score,
            "score_reduction": original_score - processed_score,
            "reduction_percent": f"{(original_score - processed_score) * 100:.1f}%"
        }

        return processed, report


def create_long_text_processor(engine, detector) -> LongTextProcessor:
    """创建长文本处理器"""
    return LongTextProcessor(engine, detector)


def create_adaptive_processor(engine, detector) -> AdaptiveLongTextProcessor:
    """创建自适应处理器"""
    return AdaptiveLongTextProcessor(engine, detector)
