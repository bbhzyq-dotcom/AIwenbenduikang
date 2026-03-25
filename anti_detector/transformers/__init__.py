"""转换器模块 - 所有文本变换策略"""
from .synonym_transformer import SynonymTransformer
from .structure_transformer import StructureTransformer
from .tense_transformer import TenseTransformer
from .interrogative_transformer import InterrogativeTransformer
from .backtranslation_transformer import BackTranslator, BackTranslationConfig
from .char_obfuscator import (
    UnicodeObfuscator,
    ZeroWidthInjector,
    SpacingManipulator,
    CharacterLeet,
    EmojiInjection,
)
from .format_transformer import (
    PunctuationManipulator,
    ParagraphFormatter,
    CapitalizationMixer,
)
from .semantic_transformer import (
    NegationInverter,
    SentenceFragmenter,
    StyleMixer,
    PassiveToActiveConverter,
    SynonymContextualReplacer,
)
from .novel_transformer import (
    DialogueTransformer,
    NarrativePerspectiveTransformer,
    MetaphorTransformer,
    InnerMonologueTransformer,
    ActionDescriptionTransformer,
    SceneDescriptionTransformer,
    CharacterNameTransformer,
    EmotionalIntensityTransformer,
    NarrativeRhythmTransformer,
)
from .translation_engine import (
    TranslationChain,
    MultiTranslator,
    create_translation_chain,
    create_multi_translator,
)
from .thesaurus_manager import (
    ThesaurusManager,
    AiPatternDetector,
    create_thesaurus_manager,
    create_ai_detector,
)
from .ai_defense import (
    AIReIDDefense,
    TargetedDefense,
    SemanticDefense,
)
from .long_text_processor import (
    LongTextProcessor,
    ParagraphAwareTransformer,
    AdaptiveLongTextProcessor,
    create_long_text_processor,
    create_adaptive_processor,
)
from .llm_paraphrase import (
    TranslationChainV2,
    SmartParaphraser,
    MultiBackendTranslator,
    create_paraphraser,
    create_translator,
    create_llm_thesaurus,
    create_llm_transform,
    LLMAssistedThesaurus,
    LLMAssistedTransform,
)

__all__ = [
    # 基础变换器
    "SynonymTransformer",
    "StructureTransformer",
    "TenseTransformer",
    "InterrogativeTransformer",
    # 回译
    "BackTranslator",
    "BackTranslationConfig",
    # 字符级混淆
    "UnicodeObfuscator",
    "ZeroWidthInjector",
    "SpacingManipulator",
    "CharacterLeet",
    "EmojiInjection",
    # 格式变换
    "PunctuationManipulator",
    "ParagraphFormatter",
    "CapitalizationMixer",
    # 语义变换
    "NegationInverter",
    "SentenceFragmenter",
    "StyleMixer",
    "PassiveToActiveConverter",
    "SynonymContextualReplacer",
    # 小说文本变换器
    "DialogueTransformer",
    "NarrativePerspectiveTransformer",
    "MetaphorTransformer",
    "InnerMonologueTransformer",
    "ActionDescriptionTransformer",
    "SceneDescriptionTransformer",
    "CharacterNameTransformer",
    "EmotionalIntensityTransformer",
    "NarrativeRhythmTransformer",
    # 翻译引擎
    "TranslationChain",
    "MultiTranslator",
    "create_translation_chain",
    "create_multi_translator",
    # 同义词库
    "ThesaurusManager",
    "AiPatternDetector",
    "create_thesaurus_manager",
    "create_ai_detector",
    # AI检测器对抗
    "AIReIDDefense",
    "TargetedDefense",
    "SemanticDefense",
    # 长文本处理
    "LongTextProcessor",
    "ParagraphAwareTransformer",
    "AdaptiveLongTextProcessor",
    "create_long_text_processor",
    "create_adaptive_processor",
    # LLM辅助变换
    "TranslationChainV2",
    "SmartParaphraser",
    "MultiBackendTranslator",
    "create_paraphraser",
    "create_translator",
    "create_llm_thesaurus",
    "create_llm_transform",
    "LLMAssistedThesaurus",
    "LLMAssistedTransform",
]
