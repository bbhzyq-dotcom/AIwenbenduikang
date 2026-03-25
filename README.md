# 文本反检测系统 (Anti-Detector)

基于 Python 的文本扰动引擎，通过多种策略对抗 AI 文本检测器。

## 功能特性

### 1. 文本变换策略

| 策略 | 说明 | 有效性 |
|------|------|--------|
| 同义词替换 | 打破固有的概率链条 | 中低 |
| 结构变换 | 改变句式、长短句分布 | 中 |
| 语气转换 | 书面语转口语，添加犹豫语气 | 中 |
| 设问插入 | 添加人类写作的思维跳跃特征 | 中高 |
| 字符混淆 | Unicode同形字、全角半角转换 | 低 |
| 标点操纵 | 随机化标点符号 | 低 |
| 风格混合 | 正式与非正式表达混合 | 中 |
| 句子碎片化 | 将完整句子拆分 | 中 |
| 回译变换 | 多语言翻译打乱语序 | 高 |
| AI检测器对抗 | 针对特定检测器的专项对抗 | 高 |

### 2. 翻译后端支持

| 后端 | 状态 | 说明 |
|------|------|------|
| MyMemory | ✅ 可用 | 免费API，无需密钥 |
| Google Translate | ✅ 可用 | 非官方免费接口 |
| LibreTranslate | ✅ 可用 | 开源免费API |

### 3. AI检测器专项对抗

| 检测器 | 主要检测维度 | 对抗策略 |
|--------|-------------|---------|
| **GPTZero** | 困惑度、突发性 | 增加词汇变化、制造长短句 |
| **朱雀** | 词汇分布、句子结构 | 打破N-gram、变化句式 |
| **Originality.ai** | N-gram分布、词汇丰富度 | 同义词替换、添加口语化 |

### 4. 预设模式

- **gentle**: 轻度扰动，保留原文结构
- **balanced**: 均衡模式，同义词+结构变换
- **aggressive**: 强力模式，全策略启用
- **stealth**: 隐蔽模式，低强度多策略
- **ultimate**: 极强模式，最大扰动
- **novel_balanced**: 小说均衡模式
- **novel_aggressive**: 小说强力模式
- **academic**: 学术文本模式
- **colloquial**: 口语化模式

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### Web GUI 应用（推荐）

```bash
cd /workspace
python3 -m anti_detector.web_gui
```

然后在浏览器中打开 http://localhost:5000

功能特性：
- 左右对比显示
- 修改文字高亮标记
- 强度滑块调节
- 预设模式选择
- 针对性防御
- AI概率评估
- 差异对比视图

### 命令行工具

```bash
# 文本变换
python -m anti_detector.cli -t "要变换的文本"

# 评估AI概率
python -m anti_detector.cli -e "待评估的文本"

# 对比策略
python -m anti_detector.cli -c "待对比的文本"
```

### Python API

```python
from anti_detector import AntiDetector, create_engine

# 基础用法
engine = AntiDetector(intensity=0.5)
text = "提高系统的安全性是非常重要的一环。"
result = engine.transform(text)

# 使用预设
engine = create_engine(preset="aggressive")
result = engine.transform(text)

# 批量处理
texts = ["文本1", "文本2", "文本3"]
results = engine.batch_transform(texts)
```

## AI检测评估

```python
from anti_detector.transformers import AiPatternDetector

detector = AiPatternDetector()
result = detector.detect_ai_writing_markers(text)

print(f"AI概率: {result['ai_score']:.0%}")
print(f"正式度: {result['formality_score']:.0%}")
print(f"突发性: {result['burstiness']:.0%}")
print(f"词汇丰富度: {result['vocabulary_richness']:.0%}")
```

## 针对性防御

```python
from anti_detector.transformers import TargetedDefense

defense = TargetedDefense(intensity=0.5)

# 针对GPTZero
result = defense.transform(text, target="gptzero")

# 针对朱雀
result = defense.transform(text, target="zhuque")

# 针对Originality.ai
result = defense.transform(text, target="originality")

# 综合对抗
result = defense.transform(text, target="all")
```

## 多翻译器回译

```python
from anti_detector.transformers import MultiTranslator

translator = MultiTranslator()  # 自动使用可用后端
result = translator.translate_with_fallback(text, "zh-CN", "en")
```

## 项目结构

```
anti_detector/
├── __init__.py
├── core.py              # 核心引擎
├── gui.py               # Tkinter GUI (需要 tkinter)
├── web_gui.py           # Flask Web GUI
├── cli.py               # 命令行工具
├── transformers/
│   ├── synonym_transformer.py      # 同义词替换
│   ├── structure_transformer.py    # 结构变换
│   ├── tense_transformer.py        # 语气转换
│   ├── interrogative_transformer.py # 设问插入
│   ├── backtranslation_transformer.py  # 回译
│   ├── char_obfuscator.py         # 字符混淆
│   ├── format_transformer.py       # 格式变换
│   ├── semantic_transformer.py      # 语义变换
│   ├── novel_transformer.py        # 小说文本变换
│   ├── translation_engine.py        # 多翻译器引擎
│   ├── thesaurus_manager.py        # 同义词库管理
│   └── ai_defense.py               # AI检测器对抗策略
└── thesaurus/
```

## AI检测维度说明

| 维度 | 含义 | 人类写作特征 | AI写作特征 |
|------|------|-------------|-----------|
| **困惑度** | 文本的预测难度 | 变化大 | 稳定低 |
| **突发性** | 句子长度的变化 | 长短不一 | 均匀一致 |
| **正式度** | 文本的正式程度 | 有口语化 | 过于正式 |
| **词汇丰富度** | 词汇的多样性 | 变化大 | 高频词重复 |

## 示例文件

- `example.py` - 通用文本反检测示例
- `example_novel.py` - 小说文本反检测示例
- `test_all.py` - 完整功能测试

## 注意事项

- 本工具仅供技术研究和学习使用
- 实际效果因检测器不同而有差异
- 建议根据文本特点选择合适的预设模式
