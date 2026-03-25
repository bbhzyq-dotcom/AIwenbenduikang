"""
文本反检测系统核心引擎
提供多种文本扰动策略以对抗AI文本检测器
"""

import random
from typing import Optional, List, Callable, Dict, Any, Tuple
from .transformers import (
    SynonymTransformer,
    StructureTransformer,
    TenseTransformer,
    InterrogativeTransformer,
    UnicodeObfuscator,
    ZeroWidthInjector,
    SpacingManipulator,
    PunctuationManipulator,
    ParagraphFormatter,
    StyleMixer,
    SentenceFragmenter,
    BackTranslator,
    DialogueTransformer,
    NarrativePerspectiveTransformer,
    MetaphorTransformer,
    InnerMonologueTransformer,
    ActionDescriptionTransformer,
    SceneDescriptionTransformer,
    CharacterNameTransformer,
    EmotionalIntensityTransformer,
    NarrativeRhythmTransformer,
    AiPatternDetector,
    AIReIDDefense,
    TargetedDefense,
    SemanticDefense,
    TranslationChain,
    MultiTranslator,
    SmartParaphraser,
    MultiBackendTranslator,
    create_paraphraser,
    create_translator,
)


class AntiDetector:
    """文本反检测主引擎"""

    STRATEGY_MAPPING = {
        "synonym": SynonymTransformer,
        "structure": StructureTransformer,
        "tense": TenseTransformer,
        "interrogative": InterrogativeTransformer,
        "unicode": UnicodeObfuscator,
        "zerowidth": ZeroWidthInjector,
        "spacing": SpacingManipulator,
        "punctuation": PunctuationManipulator,
        "paragraph": ParagraphFormatter,
        "style": StyleMixer,
        "fragment": SentenceFragmenter,
        "backtranslate": BackTranslator,
        # 小说文本变换器
        "dialogue": DialogueTransformer,
        "narrative_perspective": NarrativePerspectiveTransformer,
        "metaphor": MetaphorTransformer,
        "inner_monologue": InnerMonologueTransformer,
        "action": ActionDescriptionTransformer,
        "scene": SceneDescriptionTransformer,
        "character_name": CharacterNameTransformer,
        "emotion": EmotionalIntensityTransformer,
        "rhythm": NarrativeRhythmTransformer,
        # AI检测器对抗
        "ai_defense": AIReIDDefense,
        "semantic": SemanticDefense,
        "backtranslate": BackTranslator,
        # 智能改写（翻译回译）
        "paraphrase": SmartParaphraser,
        "multitrans": MultiBackendTranslator,
    }

    def __init__(
        self,
        intensity: float = 0.3,
        strategy: Optional[List[str]] = None,
        use_advanced: bool = True
    ):
        """
        初始化反检测引擎

        Args:
            intensity: 扰动强度 0-1，值越高扰动越大
            strategy: 启用的策略列表，默认全部启用
            use_advanced: 是否启用高级策略（回译、LLM等）
        """
        self.intensity = intensity
        self.use_advanced = use_advanced

        default_strategy = [
            "synonym", "structure", "tense", "interrogative",
            "unicode", "spacing", "punctuation", "style"
        ]
        if use_advanced:
            default_strategy.extend(["fragment", "backtranslate"])

        self.strategy = strategy or default_strategy

        self.transformers: Dict[str, Any] = {}
        for name in self.strategy:
            if name in self.STRATEGY_MAPPING:
                transformer_class = self.STRATEGY_MAPPING[name]
                # 特殊处理不需要intensity参数的变换器
                if name in ["paraphraser", "multitrans"]:
                    self.transformers[name] = transformer_class()
                else:
                    self.transformers[name] = transformer_class(intensity)

    def transform(self, text: str, random_order: bool = True) -> str:
        """
        对文本进行反检测变换

        Args:
            text: 输入文本
            random_order: 是否随机顺序应用变换策略

        Returns:
            变换后的文本
        """
        if not text:
            return text

        current_text = text
        transformer_list = list(self.transformers.items())

        if random_order:
            random.shuffle(transformer_list)

        for name, transformer in transformer_list:
            if hasattr(transformer, 'transform'):
                current_text = transformer.transform(current_text)

        return current_text

    def transform_with_strategy(
        self,
        text: str,
        strategy: List[str],
        random_order: bool = True
    ) -> str:
        """
        使用指定策略进行变换

        Args:
            text: 输入文本
            strategy: 策略列表
            random_order: 是否随机顺序

        Returns:
            变换后的文本
        """
        current_text = text

        transformers_to_use = []
        for name in strategy:
            if name in self.transformers:
                transformers_to_use.append((name, self.transformers[name]))

        if random_order:
            random.shuffle(transformers_to_use)

        for _, transformer in transformers_to_use:
            if hasattr(transformer, 'transform'):
                current_text = transformer.transform(current_text)

        return current_text

    def batch_transform(self, texts: List[str], random_order: bool = True) -> List[str]:
        """批量变换文本"""
        return [self.transform(text, random_order) for text in texts]

    def add_transformer(self, name: str, transformer: Any) -> None:
        """添加自定义转换器"""
        self.transformers[name] = transformer

    def get_available_strategies(self) -> List[str]:
        """获取所有可用的策略"""
        return list(self.STRATEGY_MAPPING.keys())

    def evaluate_text(self, text: str) -> Dict[str, Any]:
        """
        评估文本的AI概率

        Returns:
            包含评估结果的字典
        """
        evaluator = AiPatternDetector()
        detection_result = evaluator.detect_ai_writing_markers(text)
        return {
            "ai_score": detection_result["ai_score"],
            "suggested_strategies": detection_result["suggestions"],
            "available_strategies": self.get_available_strategies(),
            "detection_details": detection_result,
        }

    def transform_long_text(self, text: str, min_length: int = 500) -> str:
        """
        处理长文本

        根据文本长度自动选择最优处理策略：
        - 小于min_length: 直接用transform处理
        - 大于min_length: 使用自适应长文本处理器

        Args:
            text: 输入文本
            min_length: 启用长文本处理的最小长度

        Returns:
            处理后的文本
        """
        from .transformers import create_adaptive_processor

        if len(text) < min_length:
            return self.transform(text)

        detector = AiPatternDetector()
        processor = create_adaptive_processor(self, detector)
        return processor.process(text)

    def transform_with_report(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        变换文本并生成详细报告

        Returns:
            (变换后的文本, 处理报告)
        """
        from .transformers import create_adaptive_processor

        detector = AiPatternDetector()
        original_detection = detector.detect_ai_writing_markers(text)

        if len(text) < 500:
            processed = self.transform(text)
        else:
            processor = create_adaptive_processor(self, detector)
            processed = processor.process(text)

        processed_detection = detector.detect_ai_writing_markers(processed)

        report = {
            "original_length": len(text),
            "processed_length": len(processed),
            "original_ai_score": original_detection["ai_score"],
            "processed_ai_score": processed_detection["ai_score"],
            "score_reduction": original_detection["ai_score"] - processed_detection["ai_score"],
            "reduction_percent": f"{(original_detection['ai_score'] - processed_detection['ai_score']) * 100:.1f}%",
            "detection_details": processed_detection,
        }

        return processed, report


class Pipeline:
    """文本处理管道，支持链式调用"""

    def __init__(self):
        self.steps: List[Tuple[Callable, dict]] = []

    def add(self, func: Callable, **kwargs) -> "Pipeline":
        """添加处理步骤"""
        self.steps.append((func, kwargs))
        return self

    def execute(self, text: str) -> str:
        """执行管道"""
        result = text
        for func, kwargs in self.steps:
            result = func(result, **kwargs)
        return result

    def then(self, func: Callable, **kwargs) -> "Pipeline":
        """链式添加步骤"""
        return self.add(func, **kwargs)


def create_engine(
    intensity: float = 0.3,
    preset: str = "balanced",
    use_advanced: bool = True
) -> AntiDetector:
    """
    工厂函数：创建预配置的反检测引擎

    Args:
        intensity: 扰动强度
        preset: 预设模式
            - "gentle": 轻度扰动，保留原文结构
            - "balanced": 均衡模式，同义词+结构变换
            - "aggressive": 强力模式，全策略启用
            - "stealth": 隐蔽模式，低强度多策略
        use_advanced: 是否启用高级策略
    """
    presets: Dict[str, List[str]] = {
        # 基础模式
        "gentle": ["synonym", "spacing"],
        "balanced": ["synonym", "structure", "tense", "punctuation", "paraphrase"],
        "aggressive": [
            "synonym", "structure", "tense", "interrogative",
            "style", "fragment", "ai_defense", "paraphrase"
        ],
        "stealth": [
            "synonym", "spacing", "punctuation", "style",
            "fragment", "paraphrase"
        ],
        # 翻译回译为核心模式
        "translate_heavy": [
            "paraphrase", "paraphrase", "paraphrase",
            "multitrans", "paraphrase", "multitrans"
        ],
        "ultimate": [
            "synonym", "structure", "tense", "interrogative",
            "style", "fragment", "ai_defense", "paraphrase", "multitrans"
        ],
        # 翻译回译模式（强化版）
        "translate": [
            "paraphrase", "paraphrase", "multitrans", "paraphrase"
        ],
        # LLM辅助模式（仅辅助，不生成）
        "llm_assisted": [
            "synonym", "structure", "paraphrase", "multitrans"
        ],
        # 小说文本预设
        "novel_balanced": [
            "dialogue", "narrative_perspective", "metaphor",
            "action", "scene", "rhythm", "synonym", "paraphrase"
        ],
        "novel_aggressive": [
            "dialogue", "narrative_perspective", "metaphor",
            "inner_monologue", "action", "scene", "character_name",
            "emotion", "rhythm", "synonym", "structure", "paraphrase"
        ],
        "novel_stealth": [
            "dialogue", "scene", "action", "metaphor",
            "spacing", "punctuation", "synonym", "paraphrase"
        ],
        # 学术文本预设
        "academic": [
            "synonym", "structure", "tense",
            "punctuation", "style", "fragment", "paraphrase"
        ],
        # 口语化预设
        "colloquial": [
            "tense", "interrogative", "style",
            "fragment", "emotion", "paraphrase"
        ],
    }
    strategy = presets.get(preset, presets["balanced"])
    return AntiDetector(intensity=intensity, strategy=strategy, use_advanced=use_advanced)


class HybridEngine:
    """
    混合引擎 - 结合多种变换策略的增强引擎

    支持多层变换、策略组合、自适应强度调整
    """

    def __init__(
        self,
        intensity: float = 0.3,
        layers: int = 2,
        use_defense: bool = True
    ):
        self.intensity = intensity
        self.layers = layers
        self.use_defense = use_defense

        self.base_engine = create_engine(intensity=intensity, preset="aggressive")
        self.ai_defense = AIReIDDefense(intensity) if use_defense else None

    def transform(self, text: str) -> str:
        """多层变换"""
        result = text

        # 基础多层变换
        for _ in range(self.layers):
            result = self.base_engine.transform(result)

        # 可选：AI检测器对抗
        if self.use_defense and self.ai_defense:
            result = self.ai_defense.transform(result)

        return result

    def adaptive_transform(self, text: str) -> str:
        """
        自适应变换 - 根据文本AI概率动态调整策略

        高AI概率文本使用更强力的变换
        """
        evaluator = AiPatternDetector()
        detection_result = evaluator.detect_ai_writing_markers(text)
        ai_score = detection_result["ai_score"]

        # 根据AI分数调整强度
        if ai_score > 0.5:
            self.base_engine.intensity = min(0.8, self.intensity + 0.3)
            self.layers = 3
        elif ai_score > 0.3:
            self.base_engine.intensity = self.intensity
            self.layers = 2
        else:
            self.base_engine.intensity = max(0.1, self.intensity - 0.1)
            self.layers = 1

        return self.transform(text)
