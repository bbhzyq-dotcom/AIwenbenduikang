#!/usr/bin/env python3
"""
小说文本反检测示例
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anti_detector import AntiDetector, create_engine
from anti_detector.transformers import (
    AiPatternDetector,
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


NOVEL_EXCERPT = """
夜幕降临，城市的霓虹灯开始闪烁。小明走在回家的路上，心里想着今天发生的事情。

"今天真是奇怪的一天。"他喃喃自语。

街道上的人群匆匆走过，没有人注意到他的存在。他像往常一样，走进那家熟悉的小餐馆。

老板娘看见他，笑着说："小明来了？今天想吃点什么？"

小明看了看菜单，犹豫了一下。"来碗牛肉面吧，"他说，"不要葱花。"

吃完面，他付了钱，走出店门。夜风吹过，带来一丝凉意。他突然想起，今天早上在公园遇到的那个神秘老人。

那个老人像是一个智者，他的眼神深邃，仿佛能看透人心。"年轻人，"老人说道，"你的命运即将发生改变。"

小明不禁加快了脚步，心中充满了疑问。
"""


def demo_novel_transformers():
    """演示所有小说文本转换器"""
    print("=" * 70)
    print("小说文本转换器演示")
    print("=" * 70)

    transformers = {
        "对话标记": lambda: DialogueTransformer(0.3).transform(NOVEL_EXCERPT),
        "叙事视角": lambda: NarrativePerspectiveTransformer(0.2).transform(NOVEL_EXCERPT),
        "比喻变换": lambda: MetaphorTransformer(0.25).transform(NOVEL_EXCERPT),
        "内心独白": lambda: InnerMonologueTransformer(0.3).transform(NOVEL_EXCERPT),
        "动作描写": lambda: ActionDescriptionTransformer(0.25).transform(NOVEL_EXCERPT),
        "场景描写": lambda: SceneDescriptionTransformer(0.2).transform(NOVEL_EXCERPT),
        "人物称呼": lambda: CharacterNameTransformer(0.2).transform(NOVEL_EXCERPT),
        "情感强度": lambda: EmotionalIntensityTransformer(0.25).transform(NOVEL_EXCERPT),
        "叙事节奏": lambda: NarrativeRhythmTransformer(0.3).transform(NOVEL_EXCERPT),
    }

    for name, func in transformers.items():
        print(f"\n[{name}]")
        result = func()
        print(result[:200] + "..." if len(result) > 200 else result)


def demo_novel_presets():
    """演示小说文本预设模式"""
    print("\n" + "=" * 70)
    print("小说文本预设模式")
    print("=" * 70)

    text = (
        "夜幕降临，她独自走在空荡荡的街道上。突然，一个黑影从巷子里窜出来。"
        "她吓得后退一步，心跳加速。那个黑影说话了："
        "「别怕，是我。」"
        "她仔细一看，原来是她一直在等待的那个人。"
        "她的眼中闪过一丝惊喜，但很快就恢复了平静。"
        "「你怎么现在才来？」她轻声问道，语气中带着一丝责备。"
    )

    presets = ["novel_balanced", "novel_aggressive"]

    for preset in presets:
        engine = create_engine(preset=preset, intensity=0.4)
        result = engine.transform(text)

        print(f"\n[{preset.upper()}]")
        print(f"  {result}")


def demo_novel_vs_general():
    """对比小说预设与通用预设"""
    print("\n" + "=" * 70)
    print("小说预设 vs 通用预设")
    print("=" * 70)

    novel_text = (
        "「你真的要走吗？」她低声问道，眼中泛着泪光。"
        "他沉默了很久，最后只是点了点头。"
        "夜风呼啸而过，吹散了两人之间的沉默。"
    )

    engine_novel = create_engine(preset="novel_aggressive", intensity=0.4)
    engine_general = create_engine(preset="aggressive", intensity=0.4)

    print(f"\n原文:\n{novel_text}")

    result_novel = engine_novel.transform(novel_text)
    result_general = engine_general.transform(novel_text)

    print(f"\n[小说预设]\n{result_novel}")
    print(f"\n[通用预设]\n{result_general}")


def demo_custom_novel_pipeline():
    """自定义小说文本处理流程"""
    print("\n" + "=" * 70)
    print("自定义小说处理流程")
    print("=" * 70)

    text = (
        "清晨的阳光透过窗帘洒进房间，他慢慢睁开眼睛。"
        "回想起昨晚的梦，他仍然心有余悸。那种恐惧感如同潮水一般涌来。"
        "他深吸一口气，试图让自己平静下来。"
        "「不过是梦而已。」他喃喃自语，声音在空荡的房间里回响。"
    )

    # 创建自定义引擎
    engine = AntiDetector(intensity=0.35)

    # 添加小说相关的转换器
    custom_pipeline = [
        "dialogue",
        "narrative_perspective",
        "metaphor",
        "action",
        "scene",
        "emotion",
        "rhythm",
        "synonym",
    ]

    print(f"\n原文:\n{text}")
    print(f"\n处理步骤: {' -> '.join(custom_pipeline)}")

    # 逐步处理
    current = text
    for step in custom_pipeline:
        current = engine.transform_with_strategy(current, [step])

    print(f"\n变换后:\n{current}")


def demo_scene_transformation():
    """场景转换演示"""
    print("\n" + "=" * 70)
    print("场景转换演示")
    print("=" * 70)

    scenes = [
        "夜幕降临，城市的霓虹灯开始闪烁。",
        "清晨的阳光洒在湖面上，波光粼粼。",
        "雨声淅沥，打在窗台上，发出清脆的声响。",
        "月光如水，洒满了整个庭院。",
    ]

    transformer = SceneDescriptionTransformer(intensity=0.4)

    for scene in scenes:
        result = transformer.transform(scene)
        print(f"原文: {scene}")
        print(f"变换: {result}\n")


def demo_emotion_variation():
    """情感变化演示"""
    print("\n" + "=" * 70)
    print("情感强度变化演示")
    print("=" * 70)

    emotions = [
        "她非常高兴，脸上洋溢着幸福的笑容。",
        "他十分生气，拳头紧握，指节发白。",
        "她极其害怕，浑身颤抖，不敢回头看。",
        "他非常悲伤，眼泪止不住地流下来。",
    ]

    transformer = EmotionalIntensityTransformer(intensity=0.4)

    for emotion in emotions:
        result = transformer.transform(emotion)
        print(f"原文: {emotion}")
        print(f"变换: {result}\n")


def demo_dialogue_format():
    """对话格式变换演示"""
    print("\n" + "=" * 70)
    print("对话格式变换演示")
    print("=" * 70)

    dialogues = [
        '小明说："今天天气真好！"',
        '「你吃饭了吗？」她问道。',
        "老师笑了笑：\"很好，你做得不错。\"",
        '「我想去旅行，」他喃喃道，「去一个遥远的地方。」',
    ]

    transformer = DialogueTransformer(intensity=0.4)

    for dialogue in dialogues:
        result = transformer.transform(dialogue)
        print(f"原文: {dialogue}")
        print(f"变换: {result}\n")


def demo_narrative_perspective():
    """叙事视角变换演示"""
    print("\n" + "=" * 70)
    print("叙事视角变换演示")
    print("=" * 70)

    perspectives = [
        "我走在回家的路上，心里想着今天发生的一切。",
        "我们一起去了那家小餐馆，老板娘对我们很热情。",
        "我看着窗外的风景，突然有了一种奇妙的感觉。",
    ]

    transformer = NarrativePerspectiveTransformer(intensity=0.3)

    for perspective in perspectives:
        result = transformer.transform(perspective)
        print(f"原文: {perspective}")
        print(f"变换: {result}\n")


def main():
    print("=" * 70)
    print("小说文本反检测系统 - 功能演示")
    print("=" * 70)

    demo_novel_transformers()
    demo_novel_presets()
    demo_novel_vs_general()
    demo_custom_novel_pipeline()
    demo_scene_transformation()
    demo_emotion_variation()
    demo_dialogue_format()
    demo_narrative_perspective()

    print("\n" + "=" * 70)
    print("演示结束")
    print("=" * 70)


if __name__ == "__main__":
    main()
