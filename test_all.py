#!/usr/bin/env python3
"""
文本反检测系统完整测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anti_detector import AntiDetector, create_engine, HybridEngine
from anti_detector.transformers import AiPatternDetector


def test_ai_detection():
    """测试AI检测功能"""
    print("=" * 70)
    print("AI检测功能测试")
    print("=" * 70)

    texts = [
        "首先，我们需要明确研究的目标。其次，通过实验数据验证假设。最后，总结结论并提出建议。",
        "综上所述，本文通过深入分析表明，提高系统的安全性对于保障数据安全具有重要意义。",
        "我觉得吧，这个事儿吧，确实挺重要的。你说是不是？",
        "毫无疑问，在当今社会，科学技术的发展对于提高生产效率具有重要作用。",
    ]

    detector = AiPatternDetector()

    for text in texts:
        result = detector.detect_ai_writing_markers(text)
        print(f"\n文本: {text[:50]}...")
        print(f"  AI概率: {result['ai_score']:.0%}")
        print(f"  正式度: {result['formality_score']:.0%}")
        print(f"  突发性: {result['burstiness']:.0%}")
        print(f"  词汇丰富度: {result['vocabulary_richness']:.0%}")
        print(f"  建议: {result['suggestions']}")


def test_translation_backends():
    """测试翻译后端"""
    print("\n" + "=" * 70)
    print("翻译后端测试")
    print("=" * 70)

    from anti_detector.transformers import TranslationChain, MultiTranslator

    text = "人工智能技术正在改变世界。"

    # 测试多翻译器
    multi = MultiTranslator()
    print(f"\n原文: {text}")
    print(f"可用翻译器数量: {len(multi.translators)}")

    result = multi.translate_with_fallback(text, "zh-CN", "en")
    print(f"翻译(中->英): {result}")


def test_all_presets():
    """测试所有预设"""
    print("\n" + "=" * 70)
    print("所有预设模式测试")
    print("=" * 70)

    text = "综上所述，本文通过深入分析表明，提高系统的安全性对于保障数据安全具有重要意义。首先，我们需要明确研究的目标。其次，通过实验数据验证假设。最后，总结结论并提出建议。"

    presets = [
        "gentle", "balanced", "aggressive", "stealth",
        "ultimate", "novel_balanced", "novel_aggressive",
        "academic", "colloquial"
    ]

    detector = AiPatternDetector()
    orig_result = detector.detect_ai_writing_markers(text)
    orig_score = orig_result["ai_score"]

    print(f"\n原文: {text[:50]}...")
    print(f"原文AI概率: {orig_score:.0%}\n")

    for preset in presets:
        engine = create_engine(preset=preset, intensity=0.4)
        result = engine.transform(text)
        detection = detector.detect_ai_writing_markers(result)
        new_score = detection["ai_score"]
        reduction = orig_score - new_score

        print(f"[{preset:20s}] AI概率: {new_score:.0%} (降低: {reduction:+.0%})")


def test_targeted_defense():
    """测试针对性防御"""
    print("\n" + "=" * 70)
    print("针对性防御测试")
    print("=" * 70)

    from anti_detector.transformers import TargetedDefense

    text = "首先，我们需要明确研究的目标。其次，通过实验数据验证假设。最后，总结结论并提出建议。"

    detector = AiPatternDetector()
    defense = TargetedDefense(intensity=0.5)

    print(f"\n原文: {text}")
    orig_detection = detector.detect_ai_writing_markers(text)
    print(f"原文AI概率: {orig_detection['ai_score']:.0%}")

    targets = ["gptzero", "zhuque", "originality", "all"]

    for target in targets:
        defense_engine = TargetedDefense(intensity=0.5)
        transformed = defense_engine.transform(text, target)
        detection = detector.detect_ai_writing_markers(transformed)
        print(f"\n[{target}] AI概率: {detection['ai_score']:.0%}")
        print(f"  文本: {transformed[:60]}...")


def test_ai_defense():
    """测试AI检测器对抗"""
    print("\n" + "=" * 70)
    print("AI检测器对抗策略测试")
    print("=" * 70)

    from anti_detector.transformers import AIReIDDefense

    text = "综上所述，本文通过深入分析表明，提高系统的安全性对于保障数据安全具有重要意义。"

    detector = AiPatternDetector()
    defense = AIReIDDefense(intensity=0.6)

    print(f"\n原文: {text}")
    orig_detection = detector.detect_ai_writing_markers(text)
    print(f"原文AI概率: {orig_detection['ai_score']:.0%}")

    for _ in range(3):
        transformed = defense.transform(text)
        detection = detector.detect_ai_writing_markers(transformed)
        reduction = orig_detection['ai_score'] - detection['ai_score']
        print(f"\n变换后AI概率: {detection['ai_score']:.0%} (降低: {reduction:+.0%})")
        print(f"  {transformed[:60]}...")


def test_thesaurus():
    """测试同义词库"""
    print("\n" + "=" * 70)
    print("同义词库测试")
    print("=" * 70)

    from anti_detector.transformers import ThesaurusManager

    thesaurus = ThesaurusManager()
    thesaurus.load_builtin_thesaurus()

    print(f"词库大小: {thesaurus.get_size()}")

    words = ["重要", "提高", "系统", "首先", "但是"]
    for word in words:
        synonyms = thesaurus.get_synonyms(word)
        print(f"\n{word}: {synonyms[:5]}")


def main():
    print("=" * 70)
    print("文本反检测系统 - 完整测试")
    print("=" * 70)

    test_ai_detection()
    test_translation_backends()
    test_all_presets()
    test_targeted_defense()
    test_ai_defense()
    test_thesaurus()

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
