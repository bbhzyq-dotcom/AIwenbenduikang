#!/usr/bin/env python3
"""
文本反检测系统完整示例
演示所有功能和策略
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anti_detector import AntiDetector, create_engine, HybridEngine
from anti_detector.transformers import (
    AiPatternDetector,
    UnicodeObfuscator,
    ZeroWidthInjector,
    PunctuationManipulator,
    StyleMixer,
    SentenceFragmenter,
    BackTranslator,
)


def demo_all_transformers():
    """演示所有基础转换器"""
    print("=" * 70)
    print("所有转换器演示")
    print("=" * 70)

    text = "综上所述，提高系统的安全性是非常重要的，我们需要深入分析这个问题。"

    transformers = {
        "同义词替换": lambda: AntiDetector(strategy=["synonym"]).transform(text),
        "结构变换": lambda: AntiDetector(strategy=["structure"]).transform(text),
        "语气转换": lambda: AntiDetector(strategy=["tense"]).transform(text),
        "设问插入": lambda: AntiDetector(strategy=["interrogative"]).transform(text),
        "Unicode混淆": lambda: UnicodeObfuscator(0.2).transform(text),
        "零宽字符": lambda: ZeroWidthInjector(0.1).transform(text),
        "标点操纵": lambda: PunctuationManipulator(0.2).transform(text),
        "风格混合": lambda: StyleMixer(0.3).transform(text),
        "句子碎片化": lambda: SentenceFragmenter(0.3).transform(text),
    }

    for name, func in transformers.items():
        result = func()
        print(f"\n[{name}]")
        print(f"  {result}")


def demo_presets():
    """演示不同预设模式"""
    print("\n" + "=" * 70)
    print("预设模式对比")
    print("=" * 70)

    text = ("毫无疑问，在当今社会，科学技术的发展对于提高生产效率具有重要作用。"
            "首先，我们需要明确研究的目标。其次，通过实验数据验证假设。最后，总结结论并提出建议。")

    presets = ["gentle", "balanced", "aggressive", "stealth"]

    evaluator = AiPatternDetector()

    for preset in presets:
        engine = create_engine(preset=preset, intensity=0.4)
        result = engine.transform(text)
        detection = evaluator.detect_ai_writing_markers(result)
        score = detection["ai_score"]

        print(f"\n[{preset.upper()}] (AI概率: {score:.2%})")
        print(f"  {result[:80]}...")


def demo_ai_score_evaluation():
    """演示AI概率评估"""
    print("\n" + "=" * 70)
    print("AI概率评估")
    print("=" * 70)

    texts = [
        "首先，我们需要明确研究的目标。",
        "综上所述，本文通过深入分析表明，提高系统的安全性对于保障数据安全具有重要意义。",
        "我觉得吧，这个事儿吧，确实挺重要的。你说是不是？",
        "随着时代的发展，科技的进步日新月异。综上所述，我们应该加强创新驱动。",
    ]

    evaluator = AiPatternDetector()

    for text in texts:
        detection = evaluator.detect_ai_writing_markers(text)
        print(f"\n文本: {text[:50]}...")
        print(f"  AI概率: {detection['ai_score']:.2%}")
        print(f"  正式度: {detection['formality_score']:.2%}")
        print(f"  突发性: {detection['burstiness']:.2%}")
        print(f"  词汇丰富度: {detection['vocabulary_richness']:.2%}")
        print(f"  建议: {', '.join(detection['suggestions'])}")


def demo_hybrid_engine():
    """演示混合引擎"""
    print("\n" + "=" * 70)
    print("混合引擎演示")
    print("=" * 70)

    text = "提高系统的安全性是非常重要的一环，我们需要深入分析这个问题。"

    evaluator = AiPatternDetector()

    # 自适应混合引擎
    engine = HybridEngine(intensity=0.4, layers=2)

    print(f"\n原文: {text}")

    # 基础变换
    result1 = engine.transform(text)
    print(f"\n多层变换后: {result1}")

    # 自适应变换
    engine2 = HybridEngine(intensity=0.3, layers=3)
    result2 = engine2.adaptive_transform(text)
    print(f"\n自适应变换后: {result2}")

    # 评估
    orig_detection = evaluator.detect_ai_writing_markers(text)
    result1_detection = evaluator.detect_ai_writing_markers(result1)
    result2_detection = evaluator.detect_ai_writing_markers(result2)

    print(f"\n原文AI概率: {orig_detection['ai_score']:.2%}")
    print(f"多层变换后: {result1_detection['ai_score']:.2%}")
    print(f"自适应变换后: {result2_detection['ai_score']:.2%}")


def demo_backtranslation():
    """演示回译功能"""
    print("\n" + "=" * 70)
    print("回译功能演示 (需要网络)")
    print("=" * 70)

    text = "人工智能技术的发展正在改变我们的生活方式。"

    translator = BackTranslator(intensity=0.5)

    print(f"\n原文: {text}")

    # 智能回译
    result = translator.smart_back_translate(text)
    print(f"\n回译后: {result}")


def demo_batch_transform():
    """演示批量变换"""
    print("\n" + "=" * 70)
    print("批量变换演示")
    print("=" * 70)

    texts = [
        "首先，我们需要明确研究的目标。",
        "其次，通过实验数据验证假设。",
        "最后，总结结论并提出建议。",
        "综上所述，本文的研究具有重要的理论价值和实践意义。",
    ]

    engine = create_engine(preset="balanced", intensity=0.4)

    print("\n原文列表:")
    for i, t in enumerate(texts, 1):
        print(f"  [{i}] {t}")

    results = engine.batch_transform(texts)

    print("\n变换后:")
    for i, t in enumerate(results, 1):
        print(f"  [{i}] {t}")


def demo_strategy_comparison():
    """演示策略对比"""
    print("\n" + "=" * 70)
    print("策略对比")
    print("=" * 70)

    text = ("毫无疑问，在当今社会，科学技术的发展对于提高生产效率具有重要作用。"
            "首先，我们需要明确研究的目标。其次，通过实验数据验证假设。最后，总结结论并提出建议。")

    evaluator = AiPatternDetector()
    orig_detection = evaluator.detect_ai_writing_markers(text)
    orig_score = orig_detection["ai_score"]

    print(f"\n原文: {text[:60]}...")
    print(f"原文AI概率: {orig_score:.2%}\n")

    strategies = [
        ["synonym"],
        ["synonym", "structure"],
        ["synonym", "structure", "tense", "interrogative"],
        ["synonym", "punctuation", "style", "fragment"],
    ]

    for strategy in strategies:
        engine = AntiDetector(intensity=0.4, strategy=strategy)
        result = engine.transform(text)
        detection = evaluator.detect_ai_writing_markers(result)
        new_score = detection["ai_score"]

        print(f"策略: {' + '.join(strategy)}")
        print(f"  AI概率: {new_score:.2%} (变化: {(orig_score - new_score):.2%})")
        print()


def demo_custom_engine():
    """演示自定义引擎"""
    print("\n" + "=" * 70)
    print("自定义引擎演示")
    print("=" * 70)

    text = "毫无疑问，在当今社会，科学技术的发展对于提高生产效率具有重要作用。"

    engine = AntiDetector(intensity=0.35)

    def my_transform(text):
        import random
        return text.replace("毫无疑问", random.choice(["不用说", "明摆着", "显然"]))

    engine.add_transformer("my_custom", my_transform)

    print(f"\n原文: {text}")
    print(f"\n自定义变换: {my_transform(text)}")
    print(f"\n完整变换: {engine.transform(text)}")


def main():
    """主函数"""
    print("=" * 70)
    print("文本反检测系统 - 功能演示")
    print("=" * 70)
    print("\n注意：本工具仅供技术研究和学习使用")

    demo_all_transformers()
    demo_presets()
    demo_ai_score_evaluation()
    demo_hybrid_engine()
    demo_batch_transform()
    demo_strategy_comparison()
    demo_custom_engine()
    demo_backtranslation()

    print("\n" + "=" * 70)
    print("演示结束")
    print("=" * 70)


if __name__ == "__main__":
    main()
