#!/usr/bin/env python3
"""
Anti Detector CLI - 命令行工具
"""

import argparse
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from anti_detector import create_engine, AntiDetector
from anti_detector.transformers import AiPatternDetector


def evaluate_text(text: str, args) -> None:
    """评估文本AI概率"""
    evaluator = AiPatternDetector()
    result = evaluator.detect_ai_writing_markers(text)
    score = result["ai_score"]
    suggestions = result["suggestions"]

    print(f"\n[评估结果]")
    print(f"AI概率得分: {score:.2%}")
    print(f"建议: {', '.join(suggestions)}")

    if score > 0.5:
        print("提示: 文本AI特征明显，建议使用强力模式")
    elif score > 0.3:
        print("提示: 文本有一定AI特征，建议使用均衡模式")
    else:
        print("提示: 文本AI特征不明显")


def transform_text(text: str, args) -> None:
    """变换文本"""
    engine = create_engine(intensity=args.intensity, preset=args.preset)

    print(f"\n[配置]")
    print(f"强度: {args.intensity}")
    print(f"预设: {args.preset}")
    print(f"原文:\n{text}")
    print(f"\n{'='*60}")

    result = engine.transform(text)

    print(f"\n变换后:\n{result}")

    # 评估变换效果
    evaluator = AiPatternDetector()
    orig_detection = evaluator.detect_ai_writing_markers(text)
    new_detection = evaluator.detect_ai_writing_markers(result)
    orig_score = orig_detection["ai_score"]
    new_score = new_detection["ai_score"]

    print(f"\n[效果评估]")
    print(f"原文AI概率: {orig_score:.2%}")
    print(f"变换后AI概率: {new_score:.2%}")
    print(f"AI概率下降: {(orig_score - new_score):.2%}")


def batch_transform_file(filepath: str, args) -> None:
    """批量变换文件"""
    path = Path(filepath)
    if not path.exists():
        print(f"错误: 文件不存在 - {filepath}")
        return

    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')

    engine = create_engine(intensity=args.intensity, preset=args.preset)

    print(f"正在处理 {len(lines)} 行文本...")

    results = []
    for i, line in enumerate(lines, 1):
        if line.strip():
            transformed = engine.transform(line)
            results.append(transformed)
            print(f"[{i}/{len(lines)}] 完成")

    # 输出结果
    output_path = path.with_suffix('.transformed.md')
    output_path.write_text('\n'.join(results), encoding='utf-8')
    print(f"\n结果已保存到: {output_path}")


def compare_strategies(text: str, args) -> None:
    """对比不同策略的效果"""
    presets = ["gentle", "balanced", "aggressive", "stealth"]

    print(f"\n原文:\n{text}")
    print(f"\n{'='*60}")

    evaluator = AiPatternDetector()
    orig_detection = evaluator.detect_ai_writing_markers(text)
    orig_score = orig_detection["ai_score"]

    print(f"\n原文AI概率: {orig_score:.2%}")
    print(f"\n{'='*60}")

    for preset in presets:
        engine = create_engine(intensity=args.intensity, preset=preset)
        result = engine.transform(text)
        new_detection = evaluator.detect_ai_writing_markers(result)
        new_score = new_detection["ai_score"]

        print(f"\n[{preset.upper()}] AI概率: {new_score:.2%} (降低: {orig_score - new_score:.2%})")
        print(f"变换后: {result[:100]}{'...' if len(result) > 100 else ''}")


def main():
    parser = argparse.ArgumentParser(
        description="Anti Detector - 文本反检测系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -t "要检测的文本"
  %(prog)s -t "文本" --preset aggressive
  %(prog)s -e "文本"
  %(prog)s -c "文本"
  %(prog)s -f input.txt
        """
    )

    parser.add_argument("-t", "--text", type=str, help="要变换的文本")
    parser.add_argument("-e", "--evaluate", type=str, help="评估文本AI概率")
    parser.add_argument("-c", "--compare", type=str, help="对比不同策略效果")
    parser.add_argument("-f", "--file", type=str, help="批量处理文件")
    parser.add_argument("-i", "--intensity", type=float, default=0.3,
                        help="扰动强度 0-1 (默认: 0.3)")
    parser.add_argument("-p", "--preset", type=str, default="balanced",
                        choices=["gentle", "balanced", "aggressive", "stealth"],
                        help="预设模式 (默认: balanced)")
    parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    args = parser.parse_args()

    if args.evaluate:
        evaluate_text(args.evaluate, args)
    elif args.compare:
        compare_strategies(args.compare, args)
    elif args.text:
        transform_text(args.text, args)
    elif args.file:
        batch_transform_file(args.file, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
