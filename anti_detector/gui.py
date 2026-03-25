#!/usr/bin/env python3
"""
文本反检测系统 GUI 应用
左右对比显示，标记修改文字
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import random
from typing import List, Tuple, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anti_detector import AntiDetector, create_engine
from anti_detector.transformers import AiPatternDetector, TargetedDefense


class AntiDetectorGUI:
    """反检测系统GUI主类"""

    def __init__(self, root):
        self.root = root
        self.root.title("文本反检测系统 - AI Text Anti-Detector")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)

        self.original_text = ""
        self.modified_text = ""

        self.engine = create_engine(preset="balanced", intensity=0.4)
        self.detector = AiPatternDetector()

        self._create_styles()
        self._create_menu()
        self._create_widgets()

    def _create_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Microsoft YaHei", 16, "bold"))
        style.configure("Header.TLabel", font=("Microsoft YaHei", 12, "bold"))
        style.configure("Normal.TLabel", font=("Microsoft YaHei", 10))
        style.configure("Success.TLabel", foreground="#228B22")
        style.configure("Warning.TLabel", foreground="#FF8C00")

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开文本", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存原文", command=lambda: self.save_file("original"))
        file_menu.add_command(label="保存修改后", command=lambda: self.save_file("modified"))
        file_menu.add_command(label="保存对比结果", command=self.save_result)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空全部", command=self.clear_all, accelerator="Ctrl+L")
        edit_menu.add_command(label="交换文本", command=self.swap_texts, accelerator="Ctrl+X")

        preset_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="预设模式", menu=preset_menu)
        self.preset_var = tk.StringVar(value="balanced")
        presets = [
            ("gentle (轻度)", "gentle"),
            ("balanced (均衡)", "balanced"),
            ("aggressive (强力)", "aggressive"),
            ("stealth (隐蔽)", "stealth"),
            ("ultimate (极强)", "ultimate"),
            ("novel_balanced (小说均衡)", "novel_balanced"),
            ("novel_aggressive (小说强力)", "novel_aggressive"),
        ]
        for label, value in presets:
            preset_menu.add_radiobutton(label=label, variable=self.preset_var, value=value, command=self.on_preset_change)

        defense_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="针对性防御", menu=defense_menu)
        defense_menu.add_command(label="对抗 GPTZero", command=lambda: self.targeted_defense("gptzero"))
        defense_menu.add_command(label="对抗 朱雀", command=lambda: self.targeted_defense("zhuque"))
        defense_menu.add_command(label="对抗 Originality.ai", command=lambda: self.targeted_defense("originality"))
        defense_menu.add_separator()
        defense_menu.add_command(label="综合对抗", command=lambda: self.targeted_defense("all"))

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)

        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-l>", lambda e: self.clear_all())
        self.root.bind("<Control-x>", lambda e: self.swap_texts())

    def _create_widgets(self):
        """创建组件"""
        main_frame = ttk.Frame(self.root, padding="8")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="文本反检测系统", style="Title.TLabel")
        title_label.pack(pady=(0, 10))

        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        preset_frame = ttk.Frame(control_frame)
        preset_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(preset_frame, text="预设模式:").pack(side=tk.LEFT)
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, width=20,
                                    values=[p[1] for p in [("gentle", "gentle"), ("balanced", "balanced"),
                                                             ("aggressive", "aggressive"), ("stealth", "stealth"),
                                                             ("ultimate", "ultimate"), ("novel_balanced", "novel_balanced"),
                                                             ("novel_aggressive", "novel_aggressive")]],
                                    state="readonly")
        preset_combo.pack(side=tk.LEFT, padx=5)

        intensity_frame = ttk.Frame(control_frame)
        intensity_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(intensity_frame, text="扰动强度:").pack(side=tk.LEFT)
        self.intensity_var = tk.DoubleVar(value=0.4)
        intensity_scale = ttk.Scale(intensity_frame, from_=0.1, to=1.0, variable=self.intensity_var,
                                     orient=tk.HORIZONTAL, length=150, command=self.on_intensity_change)
        intensity_scale.pack(side=tk.LEFT, padx=5)
        self.intensity_label = ttk.Label(intensity_frame, text="0.4")
        self.intensity_label.pack(side=tk.LEFT)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="开始变换", command=self.start_transform,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="评估AI概率", command=self.evaluate_text).pack(side=tk.LEFT, padx=3)

        stats_frame = ttk.Frame(control_frame)
        stats_frame.pack(side=tk.RIGHT, padx=10)
        self.stats_label = ttk.Label(stats_frame, text="就绪", style="Normal.TLabel")
        self.stats_label.pack()

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        left_frame = ttk.LabelFrame(text_frame, text="源文本 (原文)", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.original_text_widget = scrolledtext.ScrolledText(
            left_frame, wrap=tk.WORD, font=("Microsoft YaHei", 11),
            background="#f0f0f0", relief=tk.SUNKEN, borderwidth=2
        )
        self.original_text_widget.pack(fill=tk.BOTH, expand=True)

        self.original_text_widget.tag_config("highlight", background="#98FB98", foreground="black")

        center_frame = ttk.Frame(text_frame, width=60)
        center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        center_frame.pack_propagate(False)

        swap_btn = ttk.Button(center_frame, text="⇄\n交换", command=self.swap_texts, width=5)
        swap_btn.pack(pady=30)

        diff_btn = ttk.Button(center_frame, text="标记\n差异", command=self.show_diff, width=5)
        diff_btn.pack(pady=10)

        clear_btn = ttk.Button(center_frame, text="清空", command=self.clear_all, width=5)
        clear_btn.pack(pady=10)

        right_frame = ttk.LabelFrame(text_frame, text="修改后文本 (处理结果)", padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.modified_text_widget = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD, font=("Microsoft YaHei", 11),
            background="#ffffff", relief=tk.SUNKEN, borderwidth=2
        )
        self.modified_text_widget.pack(fill=tk.BOTH, expand=True)

        self._create_text_tags()

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        self.status_label = ttk.Label(status_frame, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def _create_text_tags(self):
        """创建文本标签用于高亮"""
        self.modified_text_widget.tag_config("modified", background="#FFFACD", foreground="black")
        self.modified_text_widget.tag_config("removed", background="#FFB6C1", foreground="black")
        self.modified_text_widget.tag_config("added", background="#98FB98", foreground="black")

        self.original_text_widget.tag_config("highlight", background="#98FB98", foreground="black")

    def on_preset_change(self):
        """预设模式改变"""
        self.status_label.config(text=f"预设模式: {self.preset_var.get()}")

    def on_intensity_change(self, value):
        """强度改变"""
        self.intensity_label.config(text=f"{float(value):.1f}")

    def start_transform(self):
        """执行文本变换"""
        original = self.original_text_widget.get("1.0", tk.END).strip()
        if not original:
            messagebox.showwarning("警告", "请输入源文本")
            return

        self.original_text = original
        intensity = self.intensity_var.get()
        preset = self.preset_var.get()

        try:
            self.engine = create_engine(preset=preset, intensity=intensity)
            self.modified_text = self.engine.transform(original)
        except Exception as e:
            messagebox.showerror("错误", f"变换失败: {e}")
            return

        self.modified_text_widget.delete("1.0", tk.END)
        self.modified_text_widget.insert("1.0", self.modified_text)

        self._highlight_diff()

        orig_detection = self.detector.detect_ai_writing_markers(original)
        mod_detection = self.detector.detect_ai_writing_markers(self.modified_text)

        reduction = orig_detection['ai_score'] - mod_detection['ai_score']

        self.stats_label.config(
            text=f"原文AI: {orig_detection['ai_score']:.0%} → 结果: {mod_detection['ai_score']:.0%} (↓{reduction:.0%})",
            foreground="#228B22" if reduction > 0 else "#FF8C00"
        )
        self.status_label.config(text=f"变换完成 - 强度:{intensity:.1f} 模式:{preset}")

    def _highlight_diff(self):
        """高亮显示差异"""
        for tag in ["modified", "removed", "added"]:
            self.modified_text_widget.tag_remove(tag, "1.0", tk.END)
        self.original_text_widget.tag_remove("highlight", "1.0", tk.END)

        if not self.original_text or not self.modified_text:
            return

        if self.original_text == self.modified_text:
            return

        orig_chars = list(self.original_text)
        mod_chars = list(self.modified_text)

        i, j = 0, 0
        orig_pos = 0
        mod_pos = 0

        while orig_pos < len(orig_chars) or mod_pos < len(mod_chars):
            if orig_pos < len(orig_chars) and mod_pos < len(mod_chars) and orig_chars[orig_pos] == mod_chars[mod_pos]:
                orig_pos += 1
                mod_pos += 1
            elif mod_pos < len(mod_chars) and (orig_pos >= len(orig_chars) or orig_chars[orig_pos] not in mod_chars[mod_pos:]):
                self.modified_text_widget.tag_add("added", f"1.{mod_pos}", f"1.{mod_pos + 1}")
                mod_pos += 1
            elif orig_pos < len(orig_chars):
                self.modified_text_widget.tag_add("removed", f"1.{mod_pos}", f"1.{mod_pos + 1}")
                self.original_text_widget.tag_add("highlight", f"1.{orig_pos}", f"1.{orig_pos + 1}")
                orig_pos += 1
                mod_pos += 1
            else:
                self.modified_text_widget.tag_add("added", f"1.{mod_pos}", f"1.{mod_pos + 1}")
                mod_pos += 1

    def evaluate_text(self):
        """评估文本AI概率"""
        original = self.original_text_widget.get("1.0", tk.END).strip()
        if not original:
            messagebox.showwarning("警告", "请输入源文本")
            return

        detection = self.detector.detect_ai_writing_markers(original)

        info = f"""AI写作检测分析

基本指标:
  • AI概率得分: {detection['ai_score']:.0%}
  • 正式程度: {detection['formality_score']:.0%}
  • 句子突发性: {detection['burstiness']:.0%}
  • 词汇丰富度: {detection['vocabulary_richness']:.0%}

检测到的AI模式:
  词汇模式: {len(detection['lexical_patterns'])} 处
  结构模式: {len(detection['structural_patterns'])} 处

优化建议:
"""
        for s in detection['suggestions']:
            info += f"  • {s}\n"

        info += f"\n{'='*30}\n结论: {'可能是AI生成' if detection['is_likely_ai'] else '可能是人类写作'}"

        messagebox.showinfo("AI概率评估", info)

    def targeted_defense(self, target: str):
        """针对性防御变换"""
        original = self.original_text_widget.get("1.0", tk.END).strip()
        if not original:
            messagebox.showwarning("警告", "请输入源文本")
            return

        defense = TargetedDefense(intensity=self.intensity_var.get())
        self.modified_text = defense.transform(original, target)

        self.modified_text_widget.delete("1.0", tk.END)
        self.modified_text_widget.insert("1.0", self.modified_text)

        self._highlight_diff()

        orig_detection = self.detector.detect_ai_writing_markers(original)
        mod_detection = self.detector.detect_ai_writing_markers(self.modified_text)

        reduction = orig_detection['ai_score'] - mod_detection['ai_score']

        target_names = {"gptzero": "GPTZero", "zhuque": "朱雀", "originality": "Originality.ai", "all": "综合"}
        self.stats_label.config(
            text=f"针对性[{target_names.get(target, target)}] AI: {orig_detection['ai_score']:.0%} → {mod_detection['ai_score']:.0%} (↓{reduction:.0%})",
            foreground="#228B22" if reduction > 0 else "#FF8C00"
        )
        self.status_label.config(text=f"针对性防御完成 - 目标:{target_names.get(target, target)}")

    def show_diff(self):
        """显示差异对比"""
        if not self.original_text or not self.modified_text:
            messagebox.showwarning("警告", "请先执行变换")
            return

        diff_window = tk.Toplevel(self.root)
        diff_window.title("文本差异对比")
        diff_window.geometry("800x600")

        diff_frame = ttk.Frame(diff_window, padding="10")
        diff_frame.pack(fill=tk.BOTH, expand=True)

        info_label = ttk.Label(diff_frame, text="高亮说明: 绿色=原文, 黄色=修改/新增, 粉色=删除",
                               font=("Microsoft YaHei", 9))
        info_label.pack(pady=5)

        diff_text = scrolledtext.ScrolledText(
            diff_frame, wrap=tk.WORD, font=("Microsoft YaHei", 10)
        )
        diff_text.pack(fill=tk.BOTH, expand=True)

        diff_text.tag_config("unchanged", background="white")
        diff_text.tag_config("modified", background="#FFFACD")
        diff_text.tag_config("removed", background="#FFB6C1")
        diff_text.tag_config("added", background="#98FB98")

        orig_chars = list(self.original_text)
        mod_chars = list(self.modified_text)

        i, j = 0, 0

        while i < len(orig_chars) or j < len(mod_chars):
            if i < len(orig_chars) and j < len(mod_chars) and orig_chars[i] == mod_chars[j]:
                diff_text.insert(tk.END, orig_chars[i], "unchanged")
                i += 1
                j += 1
            elif j < len(mod_chars) and (i >= len(orig_chars) or orig_chars[i] not in mod_chars[j:]):
                diff_text.insert(tk.END, mod_chars[j], "added")
                j += 1
            elif i < len(orig_chars):
                diff_text.insert(tk.END, orig_chars[i], "removed")
                i += 1
            else:
                diff_text.insert(tk.END, mod_chars[j], "added")
                j += 1

        diff_text.config(state=tk.DISABLED)

    def swap_texts(self):
        """交换左右文本"""
        original = self.original_text_widget.get("1.0", tk.END).strip()
        modified = self.modified_text_widget.get("1.0", tk.END).strip()

        self.original_text_widget.delete("1.0", tk.END)
        self.original_text_widget.insert("1.0", modified)

        self.modified_text_widget.delete("1.0", tk.END)
        self.modified_text_widget.insert("1.0", original)

        self.original_text, self.modified_text = modified, original
        self._highlight_diff()
        self.status_label.config(text="已交换原文和处理结果")

    def clear_all(self):
        """清空所有文本"""
        self.original_text_widget.delete("1.0", tk.END)
        self.modified_text_widget.delete("1.0", tk.END)
        self.original_text = ""
        self.modified_text = ""
        self.stats_label.config(text="就绪", foreground="black")
        self.status_label.config(text="已清空")
        for tag in ["modified", "removed", "added", "highlight"]:
            self.modified_text_widget.tag_remove(tag, "1.0", tk.END)
            self.original_text_widget.tag_remove(tag, "1.0", tk.END)

    def open_file(self):
        """打开文本文件"""
        filepath = filedialog.askopenfilename(
            title="打开文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.original_text_widget.delete("1.0", tk.END)
                self.original_text_widget.insert("1.0", content)
                self.original_text = content
                self.status_label.config(text=f"已打开: {filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {e}")

    def save_file(self, which: str):
        """保存文本"""
        if which == "original":
            content = self.original_text_widget.get("1.0", tk.END).strip()
            default_name = "original_text.txt"
        else:
            content = self.modified_text_widget.get("1.0", tk.END).strip()
            default_name = "modified_text.txt"

        if not content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return

        filepath = filedialog.asksaveasfilename(
            title="保存文本",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("成功", f"已保存到:\n{filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {e}")

    def save_result(self):
        """保存对比结果"""
        if not self.original_text and not self.modified_text:
            messagebox.showwarning("警告", "没有可保存的结果")
            return

        filepath = filedialog.asksaveasfilename(
            title="保存对比结果",
            defaultextension=".txt",
            initialfile="anti_detection_result.txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("=" * 60 + "\n")
                    f.write("文本反检测系统 - 处理结果\n")
                    f.write("=" * 60 + "\n\n")

                    f.write("【源文本】\n")
                    f.write(self.original_text_widget.get("1.0", tk.END).strip())
                    f.write("\n\n")

                    f.write("【修改后文本】\n")
                    f.write(self.modified_text_widget.get("1.0", tk.END).strip())
                    f.write("\n\n")

                    orig_detection = self.detector.detect_ai_writing_markers(self.original_text_widget.get("1.0", tk.END).strip())
                    mod_detection = self.detector.detect_ai_writing_markers(self.modified_text_widget.get("1.0", tk.END).strip())

                    f.write("【AI概率分析】\n")
                    f.write(f"原文 AI概率: {orig_detection['ai_score']:.0%}\n")
                    f.write(f"结果 AI概率: {mod_detection['ai_score']:.0%}\n")
                    f.write(f"降低: {orig_detection['ai_score'] - mod_detection['ai_score']:.0%}\n")

                messagebox.showinfo("成功", f"结果已保存到:\n{filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {e}")

    def show_help(self):
        """显示帮助"""
        help_text = """文本反检测系统 - 使用说明

【基本操作】
1. 在左侧"源文本"框中输入或粘贴要处理的文本
2. 选择预设模式和调整强度滑块
3. 点击"开始变换"进行文本处理
4. 右侧将显示修改后的文本

【按钮说明】
• 开始变换: 执行文本反检测处理
• 评估AI概率: 分析原文的AI写作特征
• 交换: 将左右两侧文本互换位置
• 标记差异: 在新窗口中显示详细的差异对比
• 清空: 清空所有文本框

【针对性防御】
• 对抗 GPTZero: 针对GPTZero的检测特点优化
• 对抗朱雀: 针对朱雀检测器优化
• 对抗 Originality.ai: 针对Originality.ai优化
• 综合对抗: 使用综合策略

【高亮说明】
• 绿色: 原文内容
• 黄色: 修改/新增的内容
• 粉色: 删除的内容

【快捷键】
• Ctrl+O: 打开文件
• Ctrl+L: 清空全部
• Ctrl+X: 交换文本

【预设模式】
• gentle: 轻度扰动，保留原文结构
• balanced: 均衡模式，同义词+结构变换
• aggressive: 强力模式，全策略启用
• stealth: 隐蔽模式，低强度多策略
• novel_*: 专门针对小说文本优化
"""
        messagebox.showinfo("使用说明", help_text)

    def show_about(self):
        """显示关于"""
        about_text = """文本反检测系统 v2.0

基于Python的文本扰动引擎
用于对抗AI文本检测器

【功能特性】
• 多翻译后端回译
• 同义词替换
• 句子结构变换
• 针对性防御策略
• AI概率评估

【支持检测器】
• GPTZero
• 朱雀
• Originality.ai

仅供技术研究使用

© 2024
"""
        messagebox.showinfo("关于", about_text)


def main():
    root = tk.Tk()
    app = AntiDetectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
