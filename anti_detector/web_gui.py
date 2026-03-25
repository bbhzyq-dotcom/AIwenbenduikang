#!/usr/bin/env python3
"""
文本反检测系统 Web GUI 应用
用户只需输入文本和选择选项，一键自动处理
"""

import sys
import os
import json
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, render_template_string, jsonify, session
from anti_detector import AntiDetector, create_engine
from anti_detector.transformers import (
    AiPatternDetector,
    TargetedDefense,
    TranslationChainV2,
    SmartParaphraser,
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

DEFAULT_CONFIG = {
    "llm_enabled": False,
    "llm_mode": "",
    "llm_url": "",
    "llm_api_key": "",
    "llm_model": "gpt-3.5-turbo",
    "translate_chains": ["zh-CN,en,zh-CN", "zh-CN,ja,zh-CN", "zh-CN,de,zh-CN"],
    "translate_iterations": 2,
    "preset": "balanced",
    "intensity": 0.4,
    "use_long_text_optimization": True,
}

detector = AiPatternDetector()
engine_cache = {}


def get_engine(preset="balanced", intensity=0.4):
    """获取或创建引擎"""
    key = f"{preset}_{intensity}"
    if key not in engine_cache:
        engine_cache[key] = create_engine(preset=preset, intensity=intensity)
    return engine_cache[key]


def get_llm_client(config):
    """根据配置获取LLM客户端"""
    if not config.get("llm_enabled"):
        return None

    mode = config.get("llm_mode", "")
    url = config.get("llm_url", "")
    api_key = config.get("llm_api_key", "")
    model = config.get("llm_model", "gpt-3.5-turbo")

    if not url:
        return None

    try:
        if mode == "ollama":
            from anti_detector.transformers.llm_client import create_ollama_client
            return create_ollama_client(base_url=url, model=model)
        elif mode == "openai":
            from anti_detector.transformers.llm_client import create_openai_client
            return create_openai_client(api_base=url, api_key=api_key, model=model)
        elif mode == "vllm":
            from anti_detector.transformers.llm_client import create_vllm_client
            return create_vllm_client(api_base=url, model=model)
    except Exception as e:
        print(f"LLM初始化失败: {e}")
    return None


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文本反检测系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 24px; }
        .header-right { display: flex; gap: 10px; }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-secondary { background: #48bb78; color: white; }
        .btn-secondary:hover { background: #38a169; }
        .btn-outline { background: transparent; border: 2px solid white; color: white; }
        .btn-outline:hover { background: rgba(255,255,255,0.1); }
        .btn-config { background: #f56565; }
        .btn-config:hover { background: #e53e3e; }

        .control-bar {
            background: #f8f9fa;
            padding: 15px 30px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
            border-bottom: 1px solid #e0e0e0;
        }
        .control-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .control-group label {
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }
        select, input[type="text"], input[type="number"] {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
        }
        select:focus, input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        input[type="range"] {
            width: 100px;
        }

        .main-content {
            display: flex;
            padding: 20px 30px;
            gap: 20px;
        }
        .text-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .panel-title {
            font-weight: 700;
            font-size: 15px;
            color: #333;
            padding: 5px 15px;
            border-radius: 20px;
        }
        .panel-title.original { background: #fed7d7; color: #c53030; }
        .panel-title.modified { background: #c6f6d5; color: #276749; }
        textarea {
            flex: 1;
            min-height: 400px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 15px;
            line-height: 1.8;
            resize: none;
            outline: none;
            font-family: inherit;
        }
        textarea:focus { border-color: #667eea; }
        textarea.original { background: #fffaf0; }
        textarea.modified { background: #f0fff4; }

        .center-panel {
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 15px;
            min-width: 120px;
        }

        .stats-bar {
            background: #f8f9fa;
            padding: 15px 30px;
            display: flex;
            justify-content: center;
            gap: 50px;
            border-top: 1px solid #e0e0e0;
        }
        .stat-item { text-align: center; }
        .stat-value { font-size: 28px; font-weight: 700; color: #667eea; }
        .stat-value.good { color: #48bb78; }
        .stat-value.bad { color: #f56565; }
        .stat-label { font-size: 12px; color: #666; margin-top: 4px; }

        .config-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .config-modal.active { display: flex; }
        .config-content {
            background: white;
            border-radius: 16px;
            padding: 30px;
            width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .config-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }
        .config-header h2 { color: #333; }
        .close-btn {
            width: 36px;
            height: 36px;
            border: none;
            background: #fed7d7;
            color: #c53030;
            border-radius: 50%;
            font-size: 20px;
            cursor: pointer;
            font-weight: bold;
        }
        .config-section {
            margin-bottom: 25px;
        }
        .config-section h3 {
            font-size: 16px;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 1px dashed #ddd;
        }
        .config-row {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            gap: 10px;
        }
        .config-row label {
            min-width: 80px;
            font-weight: 600;
            color: #555;
        }
        .config-row input[type="text"], .config-row input[type="password"] {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
        }
        .config-row select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; }
        .config-row input[type="checkbox"] { width: 18px; height: 18px; }
        .chain-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .chain-tag {
            padding: 6px 12px;
            background: #e9e9e9;
            border-radius: 15px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .chain-tag.selected { background: #667eea; color: white; }
        .chain-tag:hover { background: #ddd; }
        .config-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }

        .loading {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        .loading.active { display: flex; }
        .loading-content {
            background: white;
            padding: 30px 50px;
            border-radius: 16px;
            text-align: center;
        }
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e0e0e0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading-text { color: #333; font-size: 16px; }

        @media (max-width: 900px) {
            .main-content { flex-direction: column; }
            textarea { min-height: 250px; }
            .center-panel { flex-direction: row; justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>文本反检测系统</h1>
            <div class="header-right">
                <button class="btn btn-config" onclick="openConfig()">⚙️ 配置</button>
            </div>
        </div>

        <div class="control-bar">
            <div class="control-group">
                <label>预设模式:</label>
                <select id="preset">
                    <option value="gentle">🌱 轻度</option>
                    <option value="balanced" selected>⚖️ 均衡</option>
                    <option value="aggressive">🔥 强力</option>
                    <option value="stealth">🌫️ 隐蔽</option>
                    <option value="ultimate">🚀 极强</option>
                    <option value="translate_heavy">🔄 回译优先</option>
                </select>
            </div>

            <div class="control-group">
                <label>强度:</label>
                <input type="range" id="intensity" min="0.1" max="1.0" step="0.1" value="0.4">
                <span id="intensityValue">0.4</span>
            </div>

            <div class="control-group">
                <label>回译次数:</label>
                <input type="number" id="translateIterations" min="1" max="5" value="2" style="width:60px;">
            </div>

            <button class="btn btn-primary" onclick="startTransform()" style="padding: 12px 30px; font-size: 16px;">
                ▶️ 开始变换
            </button>
            <button class="btn btn-secondary" onclick="evaluateOnly()">
                📊 评估AI概率
            </button>
        </div>

        <div class="main-content">
            <div class="text-panel">
                <div class="panel-header">
                    <span class="panel-title original">📝 原文</span>
                    <span id="originalInfo" style="color:#666;font-size:12px;"></span>
                </div>
                <textarea id="originalText" class="original" placeholder="在这里粘贴要处理的文本..."></textarea>
            </div>

            <div class="center-panel">
                <button class="btn btn-outline" onclick="loadSample()">📄 示例</button>
                <button class="btn btn-outline" onclick="clearAll()">🗑️ 清空</button>
            </div>

            <div class="text-panel">
                <div class="panel-header">
                    <span class="panel-title modified">✨ 结果</span>
                    <span id="modifiedInfo" style="color:#666;font-size:12px;"></span>
                </div>
                <textarea id="modifiedText" class="modified" placeholder="处理结果将显示在这里..."></textarea>
            </div>
        </div>

        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value" id="origScore">--</div>
                <div class="stat-label">原文AI概率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="modScore">--</div>
                <div class="stat-label">结果AI概率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="reduction">--</div>
                <div class="stat-label">降低幅度</div>
            </div>
        </div>
    </div>

    <div class="loading" id="loading">
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-text" id="loadingText">正在处理...</div>
        </div>
    </div>

    <div class="config-modal" id="configModal">
        <div class="config-content">
            <div class="config-header">
                <h2>⚙️ 系统配置</h2>
                <button class="close-btn" onclick="closeConfig()">×</button>
            </div>

            <div class="config-section">
                <h3>🤖 LLM配置 (可选)</h3>
                <div class="config-row">
                    <input type="checkbox" id="llmEnabled">
                    <label>启用LLM辅助</label>
                </div>
                <div class="config-row">
                    <label>LLM模式:</label>
                    <select id="llmMode" onchange="updateLLMFields()">
                        <option value="">不使用</option>
                        <option value="ollama">Ollama (本地)</option>
                        <option value="openai">OpenAI</option>
                        <option value="vllm">vLLM</option>
                    </select>
                </div>
                <div class="config-row" id="llmUrlRow" style="display:none;">
                    <label>API地址:</label>
                    <input type="text" id="llmUrl" placeholder="http://localhost:11434">
                </div>
                <div class="config-row" id="llmKeyRow" style="display:none;">
                    <label>API Key:</label>
                    <input type="password" id="llmApiKey" placeholder="sk-...">
                </div>
                <div class="config-row" id="llmModelRow" style="display:none;">
                    <label>模型:</label>
                    <input type="text" id="llmModel" placeholder="llama3.2">
                </div>
                <div class="config-row">
                    <button class="btn btn-outline" onclick="testLLM()" style="margin-left:88px;">🔗 测试连接</button>
                    <span id="llmTestResult" style="margin-left:10px;"></span>
                </div>
            </div>

            <div class="config-section">
                <h3>🔄 翻译回译路径</h3>
                <p style="color:#666;font-size:12px;margin-bottom:10px;">选择翻译回译使用的语言路径，可以多选</p>
                <div class="chain-list" id="chainList">
                    <span class="chain-tag selected" data-chain="zh-CN,en,zh-CN">中→英→中</span>
                    <span class="chain-tag selected" data-chain="zh-CN,ja,zh-CN">中→日→中</span>
                    <span class="chain-tag selected" data-chain="zh-CN,de,zh-CN">中→德→中</span>
                    <span class="chain-tag selected" data-chain="zh-CN,fr,zh-CN">中→法→中</span>
                    <span class="chain-tag" data-chain="zh-CN,ko,zh-CN">中→韩→中</span>
                    <span class="chain-tag" data-chain="zh-CN,ru,zh-CN">中→俄→中</span>
                    <span class="chain-tag" data-chain="zh-CN,es,zh-CN">中→西→中</span>
                    <span class="chain-tag" data-chain="zh-CN,en,de,zh-CN">中→英→德→中</span>
                    <span class="chain-tag" data-chain="zh-CN,en,fr,zh-CN">中→英→法→中</span>
                    <span class="chain-tag" data-chain="zh-CN,en,ja,zh-CN">中→英→日→中</span>
                    <span class="chain-tag" data-chain="zh-CN,de,en,zh-CN">中→德→英→中</span>
                    <span class="chain-tag" data-chain="zh-CN,ja,en,zh-CN">中→日→英→中</span>
                </div>
            </div>

            <div class="config-section">
                <h3>📝 其他选项</h3>
                <div class="config-row">
                    <input type="checkbox" id="useLongTextOpt" checked>
                    <label>长文本优化处理</label>
                </div>
            </div>

            <div class="config-actions">
                <button class="btn btn-outline" onclick="resetConfig()">🔄 重置</button>
                <button class="btn btn-primary" onclick="saveConfig()">💾 保存</button>
            </div>
        </div>
    </div>

    <script>
        let config = {};

        document.getElementById('intensity').addEventListener('input', function() {
            document.getElementById('intensityValue').textContent = this.value;
        });

        document.querySelectorAll('.chain-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                this.classList.toggle('selected');
            });
        });

        function openConfig() {
            document.getElementById('configModal').classList.add('active');
            loadConfig();
        }

        function closeConfig() {
            document.getElementById('configModal').classList.remove('active');
        }

        function updateLLMFields() {
            const mode = document.getElementById('llmMode').value;
            document.getElementById('llmUrlRow').style.display = mode ? 'flex' : 'none';
            document.getElementById('llmKeyRow').style.display = (mode === 'openai') ? 'flex' : 'none';
            document.getElementById('llmModelRow').style.display = mode ? 'flex' : 'none';
        }

        function loadConfig() {
            fetch('/get_config')
                .then(r => r.json())
                .then(data => {
                    config = data;
                    document.getElementById('llmEnabled').checked = data.llm_enabled || false;
                    document.getElementById('llmMode').value = data.llm_mode || '';
                    document.getElementById('llmUrl').value = data.llm_url || '';
                    document.getElementById('llmApiKey').value = data.llm_api_key || '';
                    document.getElementById('llmModel').value = data.llm_model || 'llama3.2';
                    document.getElementById('translateIterations').value = data.translate_iterations || 2;
                    document.getElementById('useLongTextOpt').checked = data.use_long_text_optimization !== false;
                    updateLLMFields();

                    document.querySelectorAll('.chain-tag').forEach(tag => {
                        const chain = tag.dataset.chain;
                        tag.classList.toggle('selected', (data.translate_chains || []).includes(chain));
                    });
                });
        }

        function saveConfig() {
            const selectedChains = Array.from(document.querySelectorAll('.chain-tag.selected'))
                .map(tag => tag.dataset.chain);

            config = {
                llm_enabled: document.getElementById('llmEnabled').checked,
                llm_mode: document.getElementById('llmMode').value,
                llm_url: document.getElementById('llmUrl').value,
                llm_api_key: document.getElementById('llmApiKey').value,
                llm_model: document.getElementById('llmModel').value || 'llama3.2',
                translate_chains: selectedChains,
                translate_iterations: parseInt(document.getElementById('translateIterations').value) || 2,
                use_long_text_optimization: document.getElementById('useLongTextOpt').checked,
            };

            fetch('/save_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            }).then(() => {
                closeConfig();
                showLoading('配置已保存');
            });
        }

        function resetConfig() {
            fetch('/reset_config', { method: 'POST' })
                .then(() => {
                    loadConfig();
                    showLoading('配置已重置');
                });
        }

        function testLLM() {
            const result = document.getElementById('llmTestResult');
            result.textContent = '测试中...';
            result.style.color = 'orange';

            fetch('/test_llm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: document.getElementById('llmMode').value,
                    url: document.getElementById('llmUrl').value,
                    api_key: document.getElementById('llmApiKey').value,
                    model: document.getElementById('llmModel').value || 'llama3.2'
                })
            }).then(r => r.json())
              .then(data => {
                  if (data.success) {
                      result.textContent = '✓ 连接成功';
                      result.style.color = 'green';
                  } else {
                      result.textContent = '✗ ' + (data.message || '连接失败');
                      result.style.color = 'red';
                  }
              });
        }

        function showLoading(text) {
            document.getElementById('loadingText').textContent = text;
            document.getElementById('loading').classList.add('active');
            setTimeout(() => {
                document.getElementById('loading').classList.remove('active');
            }, 500);
        }

        function startTransform() {
            const original = document.getElementById('originalText').value.trim();
            if (!original) {
                alert('请输入要处理的文本');
                return;
            }

            document.getElementById('loadingText').textContent = '正在变换...';
            document.getElementById('loading').classList.add('active');

            fetch('/transform', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: original,
                    preset: document.getElementById('preset').value,
                    intensity: parseFloat(document.getElementById('intensity').value),
                    translate_iterations: parseInt(document.getElementById('translateIterations').value) || 2,
                })
            }).then(r => r.json())
              .then(data => {
                  document.getElementById('loading').classList.remove('active');
                  document.getElementById('modifiedText').value = data.modified;
                  document.getElementById('originalInfo').textContent = `${original.length} 字`;
                  document.getElementById('modifiedInfo').textContent = `${data.modified.length} 字`;
                  updateStats(data.orig_score, data.mod_score);
              });
        }

        function evaluateOnly() {
            const original = document.getElementById('originalText').value.trim();
            if (!original) {
                alert('请输入要处理的文本');
                return;
            }

            document.getElementById('loadingText').textContent = '正在评估...';
            document.getElementById('loading').classList.add('active');

            fetch('/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: original })
            }).then(r => r.json())
              .then(data => {
                  document.getElementById('loading').classList.remove('active');
                  document.getElementById('origScore').textContent = (data.ai_score * 100).toFixed(1) + '%';
                  document.getElementById('origScore').className = 'stat-value ' + (data.ai_score > 0.5 ? 'bad' : 'good');
                  document.getElementById('modScore').textContent = '--';
                  document.getElementById('reduction').textContent = '--';
              });
        }

        function updateStats(orig, mod) {
            const origEl = document.getElementById('origScore');
            const modEl = document.getElementById('modScore');
            const reductionEl = document.getElementById('reduction');

            origEl.textContent = (orig * 100).toFixed(1) + '%';
            origEl.className = 'stat-value ' + (orig > 0.5 ? 'bad' : 'good');
            modEl.textContent = (mod * 100).toFixed(1) + '%';
            modEl.className = 'stat-value ' + (mod > 0.5 ? 'bad' : 'good');

            const reduction = (orig - mod) * 100;
            reductionEl.textContent = (reduction > 0 ? '↓' : '↑') + Math.abs(reduction).toFixed(1) + '%';
            reductionEl.className = 'stat-value ' + (reduction > 0 ? 'good' : 'bad');
        }

        function loadSample() {
            const samples = [
                "首先，人工智能技术的发展为各行各业带来了深刻的变革。其次，通过机器学习和深度学习算法，计算机能够处理更加复杂的任务。最后，我们需要关注AI技术带来的伦理和安全问题。",
                "随着时代的快速发展，人工智能已经成为了当今社会最热门的话题之一。本文旨在探讨人工智能技术在各个领域中的应用及其未来发展趋势。大量研究表明，人工智能具有巨大的潜力，可以为人类带来诸多便利。",
            ];
            document.getElementById('originalText').value = random.choice(samples);
        }

        function clearAll() {
            document.getElementById('originalText').value = '';
            document.getElementById('modifiedText').value = '';
            document.getElementById('origScore').textContent = '--';
            document.getElementById('modScore').textContent = '--';
            document.getElementById('reduction').textContent = '--';
            document.getElementById('originalInfo').textContent = '';
            document.getElementById('modifiedInfo').textContent = '';
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/get_config')
def get_config():
    return jsonify(session.get('config', DEFAULT_CONFIG))


@app.route('/save_config', methods=['POST'])
def save_config():
    session['config'] = request.json
    return jsonify({'success': True})


@app.route('/reset_config', methods=['POST'])
def reset_config():
    session['config'] = DEFAULT_CONFIG
    return jsonify({'success': True})


@app.route('/test_llm', methods=['POST'])
def test_llm():
    data = request.json
    mode = data.get('mode', '')
    url = data.get('url', '')
    api_key = data.get('api_key', '')
    model = data.get('model', 'llama3.2')

    if not url:
        return jsonify({'success': False, 'message': '请输入API地址'})

    try:
        if mode == 'ollama':
            import requests
            resp = requests.get(f"{url.rstrip('/')}/api/tags", timeout=10)
            if resp.status_code == 200:
                return jsonify({'success': True, 'message': 'Ollama连接成功'})
        elif mode == 'openai':
            import requests
            headers = {'Authorization': f'Bearer {api_key}'}
            resp = requests.get(f"{url.rstrip('/')}/models", headers=headers, timeout=10)
            if resp.status_code == 200:
                return jsonify({'success': True, 'message': 'OpenAI连接成功'})
        elif mode == 'vllm':
            import requests
            resp = requests.get(f"{url.rstrip('/')}/models", timeout=10)
            if resp.status_code == 200:
                return jsonify({'success': True, 'message': 'vLLM连接成功'})
        return jsonify({'success': False, 'message': '连接失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/transform', methods=['POST'])
def transform():
    data = request.json
    text = data.get('text', '')
    preset = data.get('preset', 'balanced')
    intensity = data.get('intensity', 0.4)
    iterations = data.get('translate_iterations', 2)

    config = session.get('config', DEFAULT_CONFIG)

    engine = get_engine(preset, intensity)
    paraphraser = SmartParaphraser()

    chains = config.get('translate_chains', ['zh-CN,en,zh-CN'])

    result = text

    for _ in range(iterations):
        chain_str = random.choice(chains)
        chain = tuple(chain_str.split(','))

        if len(chain) >= 2:
            translator = TranslationChainV2()
            result = translator.back_translate(result, chain)

    if intensity > 0.2:
        result = engine.transform(result)

    orig_detection = detector.detect_ai_writing_markers(text)
    mod_detection = detector.detect_ai_writing_markers(result)

    return jsonify({
        'modified': result,
        'orig_score': orig_detection['ai_score'],
        'mod_score': mod_detection['ai_score'],
    })


@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    text = data.get('text', '')
    result = detector.detect_ai_writing_markers(text)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
