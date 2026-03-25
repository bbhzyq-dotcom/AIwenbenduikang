"""
Anti Detector - 文本反检测系统
通过多种文本扰动策略对抗AI文本检测器
"""

from .core import AntiDetector, Pipeline, create_engine, HybridEngine

__version__ = "0.2.0"
__all__ = ["AntiDetector", "Pipeline", "create_engine", "HybridEngine"]
