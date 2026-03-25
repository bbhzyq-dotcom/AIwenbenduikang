"""
Thesaurus module - 同义词词库管理
"""

SYNONYM_DATA = {}

def load_extended_thesaurus():
    """加载扩展词库（可扩展至外部文件或API）"""
    pass

def get_synonyms(word: str) -> list:
    """获取同义词列表"""
    return SYNONYM_DATA.get(word, [])
