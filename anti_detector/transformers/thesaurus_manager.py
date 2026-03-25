"""
同义词库模块
支持多种免费同义词数据源
"""

import os
import json
import random
import re
import jieba
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path


class ThesaurusManager:
    """同义词库管理器"""

    def __init__(self):
        self.synonym_dict: Dict[str, List[str]] = {}
        self.category_dict: Dict[str, List[str]] = {}  # 按类别组织
        self.ai_patterns: Set[str] = set()
        self._loaded = False

    def load_builtin_thesaurus(self) -> None:
        """加载内置同义词库"""
        self.synonym_dict = {
            # 程度副词/形容词
            "重要": ["关键", "要紧", "核心", "重中之重", "举足轻重", "意义重大"],
            "特别": ["格外", "尤为", "尤其", "特别地", "与众不同"],
            "非常": ["极其", "相当", "十分", "格外", "颇为", "甚是"],
            "很": ["颇为", "相当", "甚为", "极为", "特别"],
            "明显": ["显著", "明晰", "显然", "尤为突出", "不言而喻"],
            "巨大": ["庞大", "巨大", "可观", "惊人", "了不起"],
            "严重": ["严峻", "沉重", "惨重", "厉害", "深重"],
            "复杂": ["繁杂", "庞杂", "复杂", "盘根错节"],
            "简单": ["简洁", "单纯", "单纯", "简明", "直白"],
            "困难": ["艰难", "困难", "艰巨", "不易"],
            "容易": ["轻松", "轻易", "易如反掌", "不难"],
            "快速": ["迅速", "飞快", "高速", "神速"],
            "缓慢": ["迟缓", "慢慢", "舒缓", "迟延"],
            "美好": ["美妙", "美好", "优美", "绮丽"],
            "糟糕": ["差劲", "不妙", "恶劣", "恶劣"],
            "完美": ["圆满", "完善", "完备", "天衣无缝"],
            "精彩": ["精妙", "出众", "卓越", "杰出"],
            "平凡": ["普通", "寻常", "平常", "平淡"],
            "安静": ["宁静", "寂静", "静谧", "鸦雀无声"],
            "热闹": ["繁华", "喧闹", "繁忙", "红火"],
            "认真": ["仔细", "细致", "用心", "一丝不苟"],
            "马虎": ["草率", "敷衍", "潦草", "粗心"],
            "高兴": ["开心", "快乐", "愉快", "喜悦", "欢快"],
            "悲伤": ["难过", "伤心", "悲痛", "哀伤", "伤感"],
            "生气": ["发怒", "愤怒", "恼火", "气愤", "恼怒"],
            "害怕": ["恐惧", "畏惧", "害怕", "惶恐", "胆怯"],
            "惊讶": ["吃惊", "惊讶", "意外", "诧异", "震惊"],
            "满意": ["满足", "称心", "如意", "欣慰"],
            "失望": ["绝望", "悲观", "沮丧", "失落"],
            "担心": ["担忧", "忧虑", "顾虑", "忧虑", "操心"],
            "相信": ["信任", "信赖", "确信", "笃信"],
            "怀疑": ["疑惑", "置疑", "质疑", "猜疑"],
            "知道": ["清楚", "明白", "了解", "懂得", "知晓"],
            "理解": ["领会", "领悟", "理解", "懂得"],
            "思考": ["思索", "考虑", "思量", "寻思"],
            "记得": ["记住", "忆起", "想起", "回想起"],
            "忘记": ["遗忘", "忘却", "淡忘", "忘怀"],

            # 动词
            "提高": ["提升", "增强", "优化", "改善", "增进", "拔高"],
            "加强": ["强化", "巩固", "加大", "增强", "夯实"],
            "解决": ["处理", "化解", "应对", "攻克", "处理掉"],
            "发展": ["推进", "进步", "成长", "演进", "崛起"],
            "进行": ["开展", "实施", "推进", "执行", "推行"],
            "认为": ["主张", "觉得", "指出", "强调", "坚信", "认定"],
            "说明": ["表明", "显示", "印证", "证明", "显示"],
            "分析": ["剖析", "研判", "考察", "探究", "解读"],
            "研究": ["探讨", "探究", "分析", "钻研", "审视"],
            "了解": ["认知", "熟悉", "理解", "把握", "洞悉"],
            "使用": ["运用", "应用", "利用", "采用", "采纳"],
            "实现": ["达成", "完成", "达到", "得以实现", "变成现实"],
            "发挥": ["展现", "发挥", "释放", "彰显", "流露"],
            "造成": ["导致", "致使", "引发", "引起", "招致"],
            "提供": ["给予", "供应", "供给", "带来", "奉献"],
            "包括": ["涵盖", "包含", "覆盖", "涉及", "囊括"],
            "相关": ["关联", "涉及", "牵连", "有关", "牵扯"],
            "需要": ["须要", "需求", "必需", "亟待", "少不了"],
            "应该": ["应当", "理应", "宜", "当", "该当"],
            "可以": ["能够", "可", "得以", "会", "能"],
            "必须": ["务必", "须得", "不得不", "一定要"],
            "可能": ["或许", "也许", "大概", "恐怕", "兴许"],
            "开始": ["启动", "开启", "着手", "起步", "展开"],
            "结束": ["完成", "终结", "完毕", "终了", "收尾"],
            "改变": ["转变", "改变", "变化", "变革", "改动"],
            "保持": ["维持", "保留", "维持", "存留"],
            "增加": ["增长", "增多", "添加", "添加", "扩大"],
            "减少": ["降低", "减少", "缩减", "削减", "减小"],
            "出现": ["浮现", "显现", "呈现", "露出", "产生"],
            "消失": ["消散", "隐去", "不见", "消散", "消亡"],
            "成功": ["胜利", "达成", "成就", "功成", "得逞"],
            "失败": ["挫折", "失利", "败北", "落空", "泡汤"],
            "学习": ["掌握", "学会", "习得", "研习"],
            "工作": ["干活", "劳动", "任职", "执业"],
            "生活": ["生存", "度日", "过活", "营生"],
            "等待": ["等候", "期待", "盼望", "守候"],
            "寻找": ["找寻", "寻求", "查找", "搜索"],
            "发现": ["发觉", "察觉", "注意到", "找到"],
            "创造": ["发明", "创作", "首创", "缔造"],
            "建立": ["创立", "创建", "设立", "构筑"],
            "删除": ["去除", "移除", "删掉", "抹去"],
            "发送": ["寄送", "传达", "传递", "发出"],
            "接收": ["收到", "接纳", "收受", "接获"],
            "打开": ["开启", "敞开", "翻开", "启动"],
            "关闭": ["关上", "合上", "封闭", "停闭"],
            "开始": ["启动", "开启", "着手", "起步"],
            "停止": ["停下", "中止", "终止", "暂停"],
            "继续": ["延续", "接续", "持续", "维持"],
            "计划": ["打算", "谋划", "规划", "筹谋"],
            "希望": ["期望", "渴望", "盼望", "指望"],
            "需要": ["需求", "须要", "必要", "少不了"],
            "愿意": ["乐意", "甘愿", "情愿", "肯"],
            "喜欢": ["喜爱", "爱", "宠爱", "钟爱", "青睐"],
            "讨厌": ["厌恶", "厌烦", "反感", "嫌弃"],
            "害怕": ["惧怕", "畏怯", "恐惧", "发憷"],
            "帮助": ["帮忙", "协助", "援手", "扶持"],
            "告诉": ["告知", "通知", "通报", "说与"],
            "询问": ["打听", "咨询", "追问", "探问"],
            "回答": ["答复", "回复", "回应", "作答"],
            "讨论": ["商量", "商议", "探讨", "辩论"],
            "同意": ["赞同", "认可", "答应", "允诺"],
            "拒绝": ["回绝", "否决", "推辞", "不接受"],
            "表扬": ["称赞", "赞扬", "赞誉", "夸奖"],
            "批评": ["批判", "指责", "责备", "数落"],
            "庆祝": ["庆贺", "祝贺", "欢庆", "喜迎"],
            "抱怨": ["埋怨", "诉苦", "发牢骚", "吐槽"],

            # 名词
            "系统": ["体系", "架构", "平台", "机制", "框架", "系统"],
            "问题": ["议题", "难题", "挑战", "困境", "麻烦", "症结"],
            "情况": ["状况", "状态", "情形", "局面", "态势", "景况"],
            "原因": ["缘由", "起因", "根由", "因素", "来由", "根苗"],
            "结果": ["成果", "成效", "结局", "后果", "结局", "着落"],
            "作用": ["功效", "功能", "效能", "影响", "效用", "功用"],
            "方法": ["手段", "途径", "方式", "做法", "法子", "门道"],
            "因素": ["要素", "因子", "缘由", "原因", "缘由", "成分"],
            "过程": ["历程", "进程", "步骤", "阶段", "经过", "轨迹"],
            "条件": ["前提", "要素", "状况", "基础", "资格"],
            "原则": ["准则", "主旨", "核心", "要义", "圭臬", "信条"],
            "目标": ["目的", "宗旨", "方向", "指向", "靶心", "愿景"],
            "特点": ["特性", "特征", "特色", "亮点", "卖点", "长处"],
            "方面": ["维度", "角度", "层面", "领域", "方向", "口子"],
            "水平": ["程度", "水准", "境界", "素养", "涵养", "功力"],
            "意义": ["价值", "意义", "重要性", "分量", "意味"],
            "基础": ["根基", "底子", "根本", "基石", "奠基石"],
            "机会": ["时机", "契机", "良机", "机遇"],
            "危险": ["风险", "隐患", "危机", "险情"],
            "方法": ["办法", "法子", "措施", "对策"],
            "理由": ["原因", "缘由", "根据", "缘故"],
            "关系": ["联系", "关联", "纽带", "牵连"],
            "影响": ["作用", "效果", "后果", "波及"],
            "作用": ["功用", "价值", "功效", "意义", "裨益"],
            "任务": ["使命", "职责", "天职", "担当"],
            "阶段": ["时期", "年代", "时刻", "关头"],
            "水平": ["层次", "等级", "段位", "级别"],
            "能力": ["本事", "才干", "才能", "本领"],
            "经验": ["阅历", "经历", "体验", "心得"],
            "知识": ["学识", "认知", "见识", "资讯"],
            "想法": ["念头", "主意", "看法", "观点"],
            "意见": ["看法", "见解", "主张", "建议"],
            "决定": ["决策", "决断", "结论", "裁决"],
            "原因": ["起因", "根源", "来由", "根由"],
            "结果": ["后果", "结局", "下场", "归宿"],
            "目的": ["意图", "初衷", "动机", "主旨"],
            "方式": ["方法", "形式", "形态", "路子"],
            "态度": ["立场", "姿态", "看法", "心态"],
            "关系": ["联系", "往来", "交情", "友谊"],
            "差距": ["差异", "区别", "出入", "悬殊"],
            "可能性": ["几率", "概率", "机会", "希望"],
            "必要性": ["必然性", "需要性", "迫切性"],
            "重要性": ["意义", "价值", "分量", "关键"],
            "普遍性": ["广泛性", "通用性", "共性"],
            "特殊性": ["独特性", "个性", "特点"],
            "规律性": ["法则", "原理", "逻辑", "道道"],
            "直接性": ["直截性", "直观性", "明确性"],
            "间接性": ["迂回性", "曲折性", "隐晦性"],

            # 连接词
            "但是": ["不过", "然而", "可是", "只是", "但", "偏偏", "倒是"],
            "因此": ["所以", "因而", "故而", "于是", "就这么着", "于是乎"],
            "虽然": ["尽管", "固然", "虽", "虽说", "固然", "即或"],
            "如果": ["假如", "倘若", "若", "要是", "一旦", "万一"],
            "而且": ["并且", "同时", "此外", "再者", "加之", "且"],
            "或者": ["亦或", "要么", "要不", "还是", "亦或是"],
            "因为": ["由于", "鉴于", "基于", "缘于", "因了", "由是"],
            "所以": ["故而", "因此", "于是", "因而", "故", "是故"],
            "然而": ["可是", "但是", "不过", "只是", "却", "偏"],
            "不过": ["然而", "但是", "只是", "然而", "却", "倒"],
            "于是": ["于是乎", "就这么着", "于是", "故而", "因而"],
            "并且": ["而且", "同时", "此外", "再者", "加之", "且"],
            "即使": ["即便", "纵然", "哪怕", "就是"],
            "除非": ["除却", "除了", "只消", "只要"],
            "自从": ["自打", "打从", "从", "自"],
            "只要": ["只需", "不过要", "总要", "必须"],
            "除非": ["要不", "不然", "否则", "要不"],

            # AI高频词 - 需要替换为非AI风格
            "综上所述": ["总之", "归根结底", "说到底", "总而言之", "要而言之", "归根到底"],
            "总而言之": ["总之", "归根结底", "说到底", "要之", "概言之", "总的来说"],
            "首先": ["第一", "首要", "先行", "开端", "起先", "一开头"],
            "其次": ["第二", "而后", "接着", "随后", "而后", "再者"],
            "最后": ["最终", "末了", "归结", "收尾", "临了", "到头来"],
            "值得注意的是": ["要我说", "关键在于", "重点是", "说真的", "说实在的"],
            "毋庸置疑": ["不用说", "明摆着", "毫无疑问", "自不待言", "不言而喻"],
            "从某种意义上": ["在一定层面上", "某种程度上", "可以说", "往好了说"],
            "在当今社会": ["眼下", "当今", "时下", "如今", "当今年头"],
            "随着时代的发展": ["时代变了", "这些年", "眼下", "当今", "时下"],
            "本文旨在": ["这篇", "本文", "这里要", "这篇文章"],
            "本文将": ["这篇", "这里要", "本文", "将要"],
            "本文通过": ["本文", "这里通过", "借着"],
            "本文认为": ["我觉得", "笔者的看法是", "依我看", "笔者的观点"],
            "笔者认为": ["我觉得", "个人看法是", "依我看", "我的观点是"],
            "研究表明": ["有道是", "常言道", "有句话说的好", "常言说的"],
            "实验数据表明": ["看得出来", "显然", "一目了然", "明摆着"],
            "大量研究表明": ["有道是", "常言道", "有句话", "民间流传"],
            "由此可见": ["可见", "这么看", "看来", "不用说"],
            "事实上": ["说真的", "其实", "实际说起来", "说实在的"],
            "客观来说": ["说真的", "实话实说", "说实在的", "凭良心说"],
            "一般来说": ["通常而言", "通常来说", "一般情况下", "大面上"],
            "显而易见": ["明摆着", "不用说", "一看便知", "昭然若揭"],
            "毫无疑问": ["不用说", "明摆着", "毫无疑问", "自不待言"],
            "不得不承认": ["得承认", "说真的", "实话说", "得说"],
            "更重要的是": ["更要紧的是", "关键的是", "要紧的是", "核心是"],
            "总的来说": ["总之", "要之", "归拢起来", "总起来说", "大面上"],
            "简而言之": ["总之", "简言之", "长话短说", "概括起来"],
            "举例来说": ["拿个例子", "比方说", "打个比方", "就像"],
            "正如所述": ["如前所述", "上面说的", "前文提到", "如上所述"],
        }

        self._loaded = True

    def load_from_file(self, filepath: str) -> bool:
        """从文件加载同义词库"""
        path = Path(filepath)

        if not path.exists():
            return False

        try:
            if path.suffix == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.synonym_dict.update(data)
            elif path.suffix == ".txt":
                self._load_txt_format(path)

            self._loaded = True
            return True
        except Exception:
            return False

    def _load_txt_format(self, path: Path) -> None:
        """加载TXT格式同义词库（每行: 词=同义词1,同义词2,...）"""
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, values = line.split("=", 1)
                    synonyms = [v.strip() for v in values.split(",") if v.strip()]
                    if key.strip() and synonyms:
                        self.synonym_dict[key.strip()] = synonyms

    def load_cilin_format(self, filepath: str) -> bool:
        """
        加载Cilin格式（同义词词林格式）

        哈尔滨工业大学同义词词林格式：
        每行: 代码\t词语\t词性
        或: 代码\t词语1,词语2,...\t词性
        """
        path = Path(filepath)
        if not path.exists():
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                current_group = ""
                current_words: List[str] = []

                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split("\t")
                    if len(parts) >= 2:
                        code = parts[0].strip()
                        words_part = parts[1].strip()

                        if code == current_group:
                            words = [w.strip() for w in words_part.replace(",", " ").split() if w.strip()]
                            current_words.extend(words)
                        else:
                            if current_words and len(current_words) > 1:
                                self._add_synonym_group(current_words)
                            current_group = code
                            words = [w.strip() for w in words_part.replace(",", " ").split() if w.strip()]
                            current_words = words

                if current_words and len(current_words) > 1:
                    self._add_synonym_group(current_words)

            self._loaded = True
            return True
        except Exception:
            return False

    def _add_synonym_group(self, words: List[str]) -> None:
        """添加一组同义词"""
        if len(words) < 2:
            return

        for word in words:
            others = [w for w in words if w != word]
            if word not in self.synonym_dict:
                self.synonym_dict[word] = others
            else:
                existing = set(self.synonym_dict[word])
                existing.update(others)
                self.synonym_dict[word] = list(existing)

    def get_synonyms(self, word: str) -> List[str]:
        """获取同义词列表"""
        return self.synonym_dict.get(word, [])

    def get_random_synonym(self, word: str) -> str:
        """获取随机同义词"""
        synonyms = self.get_synonyms(word)
        return random.choice(synonyms) if synonyms else word

    def add_synonym(self, word: str, synonym: str) -> None:
        """添加同义词对"""
        if word not in self.synonym_dict:
            self.synonym_dict[word] = []
        if synonym not in self.synonym_dict[word]:
            self.synonym_dict[word].append(synonym)

    def get_size(self) -> int:
        """获取词库大小"""
        return len(self.synonym_dict)

    def get_words(self) -> List[str]:
        """获取所有词条"""
        return list(self.synonym_dict.keys())


class AiPatternDetector:
    """AI写作模式检测器

    基于现有AI检测器研究，AI文本通常具有以下特征：
    1. Perplexity（困惑度）：AI文本 perplexity 通常较低
    2. Burstiness（突发性）：AI句子长度变化小
    3. Formality（正式程度）：AI文本倾向于过于正式
    4. N-gram分布：特定n-gram频率异常
    5. 词汇丰富度：AI文本词汇变化较少
    6. 句子结构一致性：AI句子结构过于规整
    """

    # AI高频词汇模式
    AI_LEXICAL_PATTERNS = [
        r"首先.*?其次.*?最后",
        r"一方面.*?另一方面",
        r"综上所述",
        r"总而言之",
        r"简而言之",
        r"毫无疑问",
        r"不言而喻",
        r"显而易见",
        r"值得注意的是",
        r"更重要的是",
        r"从某种意义上",
        r"在当今社会",
        r"随着时代的发展",
        r"大量研究表明",
        r"实验数据表明",
        r"本文旨在",
        r"本文将",
        r"本文通过",
        r"本文认为",
        r"笔者认为",
    ]

    # AI写作结构标记
    AI_STRUCTURAL_PATTERNS = [
        r"第一[，、]",
        r"第二[，、]",
        r"第三[，、]",
        r"其一[，、]",
        r"其二[，、]",
        r"其三[，、]",
        r"首先[，、]",
        r"其次[，、]",
        r"最后[，、]",
        r"最后",
        r"总之",
        r"总的来说",
        r"综上所述",
    ]

    # 过于正式/书面的词汇
    FORMAL_WORDS = [
        "从而", "故而", "因而", "由此", "可见", "由于", "鉴于",
        "然而", "但是", "因此", "所以", "而言", "表明", "显示",
        "表明", "印证", "佐证", "体现", "彰显", "确保", "得以",
    ]

    # 缺乏口语化标记
    COLLOQUIAL_MARKERS = [
        "我觉得", "我认为", "说实话", "实话说", "说真的",
        "要我说", "按理说", "这么一看", "说起来", "你知道",
        "说实话", "说实在的", "个人感觉", "我个人", "嗯",
        "啊", "嘛", "呢", "吧", "呀", "哦", "呃", "喔",
    ]

    def __init__(self):
        self.lexical_patterns = [re.compile(p, re.DOTALL) for p in self.AI_LEXICAL_PATTERNS]
        self.structural_patterns = [re.compile(p) for p in self.AI_STRUCTURAL_PATTERNS]

    def detect_lexical_ai_patterns(self, text: str) -> List[str]:
        """检测词汇层面的AI模式"""
        detected = []
        for pattern in self.lexical_patterns:
            match = pattern.search(text)
            if match:
                detected.append(match.group())

        return detected

    def detect_structural_ai_patterns(self, text: str) -> List[str]:
        """检测结构层面的AI模式"""
        detected = []
        for pattern in self.structural_patterns:
            matches = pattern.findall(text)
            detected.extend(matches)

        return detected

    def calculate_formality_score(self, text: str) -> float:
        """
        计算文本正式程度得分 (0-1)

        得分越高表示越正式，越可能是AI生成
        """
        formal_count = sum(1 for word in self.FORMAL_WORDS if word in text)
        colloquial_count = sum(1 for marker in self.COLLOQUIAL_MARKERS if marker in text)

        total_markers = formal_count + colloquial_count
        if total_markers == 0:
            return 0.5

        return formal_count / total_markers

    def calculate_burstiness(self, text: str) -> float:
        """
        计算句子长度突发性 (0-1)

        人类写作：句子长短变化大，burstiness高
        AI写作：句子长度均匀，burstiness低
        """
        import jieba
        sentences = re.split(r'[。！？；\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5

        lengths = [len(s) for s in sentences]
        if not lengths:
            return 0.5

        mean = sum(lengths) / len(lengths)
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)

        std_dev = variance ** 0.5
        coefficient_of_variation = std_dev / mean if mean > 0 else 0

        normalized_burstiness = min(1.0, coefficient_of_variation / 2.0)
        return normalized_burstiness

    def calculate_vocabulary_richness(self, text: str) -> float:
        """
        计算词汇丰富度 (0-1)

        人类写作：词汇变化较大
        AI写作：高频词重复多，词汇变化小
        """
        words = list(jieba.cut(text))
        words = [w for w in words if len(w) > 1]

        if not words:
            return 0.5

        unique_words = set(words)
        richness = len(unique_words) / len(words)

        return min(1.0, richness)

    def detect_ai_writing_markers(self, text: str) -> Dict[str, any]:
        """
        综合检测AI写作特征

        Returns:
            包含各项检测指标的字典
        """
        lexical_patterns = self.detect_lexical_ai_patterns(text)
        structural_patterns = self.detect_structural_ai_patterns(text)
        formality_score = self.calculate_formality_score(text)
        burstiness = self.calculate_burstiness(text)
        vocabulary_richness = self.calculate_vocabulary_richness(text)

        ai_score = 0.0
        ai_score += 0.2 if len(lexical_patterns) > 0 else 0
        ai_score += 0.1 if len(structural_patterns) > 2 else 0
        ai_score += formality_score * 0.3
        ai_score += (1 - burstiness) * 0.2
        ai_score += (1 - vocabulary_richness) * 0.2

        return {
            "ai_score": min(1.0, ai_score),
            "lexical_patterns": lexical_patterns,
            "structural_patterns": structural_patterns,
            "formality_score": formality_score,
            "burstiness": burstiness,
            "vocabulary_richness": vocabulary_richness,
            "is_likely_ai": ai_score > 0.5,
            "suggestions": self._generate_suggestions(ai_score, formality_score, burstiness, vocabulary_richness),
        }

    def _generate_suggestions(
        self,
        ai_score: float,
        formality: float,
        burstiness: float,
        vocabulary: float
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if ai_score > 0.5:
            suggestions.append("文本AI特征明显，建议使用强力变换")

        if formality > 0.7:
            suggestions.append("文本过于正式，建议添加口语化表达")

        if burstiness < 0.3:
            suggestions.append("句子长度过于均匀，建议变化句式长短")

        if vocabulary < 0.4:
            suggestions.append("词汇变化较少，建议增加同义词替换")

        if not suggestions:
            suggestions.append("文本AI特征不明显")

        return suggestions


def create_thesaurus_manager() -> ThesaurusManager:
    """创建同义词库管理器"""
    manager = ThesaurusManager()
    manager.load_builtin_thesaurus()
    return manager


def create_ai_detector() -> AiPatternDetector:
    """创建AI写作检测器"""
    return AiPatternDetector()
