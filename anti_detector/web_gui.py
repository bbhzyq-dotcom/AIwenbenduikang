#!/usr/bin/env python3
"""
文本反检测系统 Web GUI 应用
基于Flask的左右对比界面
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, render_template_string, jsonify, send_file
from anti_detector import AntiDetector, create_engine
from anti_detector.transformers import (
    AiPatternDetector, TargetedDefense, HybridAntiAI,
    create_ollama_client, create_openai_client, create_vllm_client
)
import io

app = Flask(__name__)

engine = create_engine(preset="balanced", intensity=0.4)
detector = AiPatternDetector()
hybrid_engine = None  # LLM混合引擎

def get_hybrid_engine():
    """获取混合引擎（带LLM）"""
    global hybrid_engine
    if hybrid_engine is None:
        try:
            # 尝试创建Ollama客户端（本地模型）
            llm_client = create_ollama_client(model="llama3.2")
            hybrid_engine = HybridAntiAI(
                traditional_engine=engine,
                llm_client=llm_client,
                use_llm=True,
                llm_strategy="repair"
            )
        except Exception as e:
            print(f"LLM初始化失败: {e}")
            hybrid_engine = None
    return hybrid_engine

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文本反检测系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .control-panel {
            background: #f8f9fa;
            padding: 20px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
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
        select, input[type="range"] {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
        }
        select:focus, input:focus {
            border-color: #667eea;
        }
        input[type="range"] {
            width: 120px;
            cursor: pointer;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
        .btn-outline {
            background: transparent;
            border: 2px solid #667eea;
            color: #667eea;
        }
        .btn-outline:hover {
            background: #667eea;
            color: white;
        }
        .main-content {
            display: flex;
            padding: 20px;
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
            padding: 0 5px;
        }
        .panel-title {
            font-weight: 700;
            font-size: 16px;
            color: #333;
        }
        .panel-title.original { color: #e74c3c; }
        .panel-title.modified { color: #27ae60; }
        .stats {
            font-size: 12px;
            color: #666;
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 12px;
        }
        textarea {
            flex: 1;
            width: 100%;
            min-height: 450px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 15px;
            font-family: inherit;
            resize: none;
            line-height: 1.8;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea.original {
            background: #fff5f5;
        }
        textarea.modified {
            background: #f0fff4;
        }
        .center-controls {
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 10px;
            padding: 0 10px;
        }
        .stats-panel {
            background: #f8f9fa;
            padding: 15px 30px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
        }
        .stat-item {
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
        }
        .stat-value.down { color: #27ae60; }
        .stat-value.up { color: #e74c3c; }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }
        .diff-view {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .diff-content {
            background: white;
            border-radius: 16px;
            padding: 30px;
            max-width: 900px;
            max-height: 80vh;
            overflow: auto;
        }
        .diff-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .diff-legend {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 13px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }
        .legend-unchanged { background: white; border: 1px solid #ddd; }
        .legend-added { background: #98FB98; }
        .legend-removed { background: #FFB6C1; }
        .legend-modified { background: #FFFACD; }
        .diff-text {
            font-size: 15px;
            line-height: 2;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            min-height: 300px;
        }
        .diff-added { background: #98FB98; }
        .diff-removed { background: #FFB6C1; text-decoration: line-through; }
        .diff-modified { background: #FFFACD; }
        .highlight-added { background: #98FB98; }
        .highlight-removed { background: #FFB6C1; }
        .highlight-modified { background: #FFFACD; }
        @media (max-width: 900px) {
            .main-content {
                flex-direction: column;
            }
            textarea {
                min-height: 300px;
            }
            .center-controls {
                flex-direction: row;
                justify-content: center;
                padding: 10px 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>文本反检测系统</h1>
            <p>AI Text Anti-Detector - 左右对比，智能变换</p>
        </div>

        <div class="control-panel">
            <div class="control-group">
                <label>预设模式:</label>
                <select id="preset">
                    <option value="gentle">gentle (轻度)</option>
                    <option value="balanced" selected>balanced (均衡)</option>
                    <option value="aggressive">aggressive (强力)</option>
                    <option value="stealth">stealth (隐蔽)</option>
                    <option value="ultimate">ultimate (极强)</option>
                    <option value="novel_balanced">novel_balanced (小说均衡)</option>
                    <option value="novel_aggressive">novel_aggressive (小说强力)</option>
                </select>
            </div>

            <div class="control-group">
                <label>扰动强度:</label>
                <input type="range" id="intensity" min="0.1" max="1.0" step="0.1" value="0.4">
                <span id="intensityValue">0.4</span>
            </div>

            <div class="control-group">
                <input type="checkbox" id="useLongText" checked>
                <label for="useLongText">长文本优化</label>
                <span id="textLength" style="color:#666;font-size:12px;margin-left:5px;"></span>
            </div>

            <button class="btn btn-primary" onclick="startTransform()">开始变换</button>
            <button class="btn btn-secondary" onclick="evaluateText()">评估AI概率</button>
            <button class="btn btn-outline" onclick="showDiff()">标记差异</button>
            <button class="btn btn-secondary" onclick="clearAll()">清空</button>

            <div class="control-group">
                <label>针对性:</label>
                <select id="targetSelect">
                    <option value="">综合</option>
                    <option value="gptzero">GPTZero</option>
                    <option value="zhuque">朱雀</option>
                    <option value="originality">Originality.ai</option>
                </select>
                <button class="btn btn-outline" onclick="targetedDefense()">执行</button>
            </div>

            <div class="control-group">
                <label>LLM模式:</label>
                <select id="llmMode">
                    <option value="">不使用</option>
                    <option value="ollama">Ollama (本地)</option>
                    <option value="openai">OpenAI</option>
                    <option value="vllm">vLLM</option>
                </select>
                <input type="text" id="llmUrl" placeholder="API地址" style="width:150px;">
                <button class="btn btn-outline" onclick="testLLM()">测试</button>
            </div>

            <div class="control-group" id="llmStatus" style="display:none;">
                <span id="llmStatusText" style="color:green;">LLM已连接</span>
            </div>

            <div class="control-group">
                <input type="checkbox" id="useLLM">
                <label for="useLLM">使用LLM辅助</label>
            </div>
        </div>

        <div class="main-content">
            <div class="text-panel">
                <div class="panel-header">
                    <span class="panel-title original">源文本 (原文)</span>
                    <span class="stats" id="originalStats"></span>
                </div>
                <textarea id="originalText" class="original" placeholder="请输入要处理的文本..."></textarea>
            </div>

            <div class="center-controls">
                <button class="btn btn-secondary" onclick="swapTexts()">⇄ 交换</button>
                <button class="btn btn-outline" onclick="loadSample()">示例</button>
            </div>

            <div class="text-panel">
                <div class="panel-header">
                    <span class="panel-title modified">修改后文本</span>
                    <span class="stats" id="modifiedStats"></span>
                </div>
                <textarea id="modifiedText" class="modified" placeholder="处理结果将显示在这里..."></textarea>
            </div>
        </div>

        <div class="stats-panel">
            <div class="stat-item">
                <div class="stat-value" id="origAIScore">--</div>
                <div class="stat-label">原文AI概率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="modAIScore">--</div>
                <div class="stat-label">结果AI概率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value down" id="reduction">--</div>
                <div class="stat-label">降低幅度</div>
            </div>
        </div>
    </div>

    <div class="diff-view" id="diffView">
        <div class="diff-content">
            <div class="diff-header">
                <h3>文本差异对比</h3>
                <button class="btn btn-secondary" onclick="closeDiff()">关闭</button>
            </div>
            <div class="diff-legend">
                <div class="legend-item">
                    <div class="legend-color legend-unchanged"></div>
                    <span>未变化</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color legend-added"></div>
                    <span>新增/修改</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color legend-removed"></div>
                    <span>删除</span>
                </div>
            </div>
            <div class="diff-text" id="diffText"></div>
        </div>
    </div>

    <script>
        let currentData = { original: '', modified: '', origScore: 0, modScore: 0 };

        document.getElementById('intensity').addEventListener('input', function() {
            document.getElementById('intensityValue').textContent = this.value;
        });

        function startTransform() {
            const original = document.getElementById('originalText').value;
            if (!original.trim()) {
                alert('请输入源文本');
                return;
            }
            const preset = document.getElementById('preset').value;
            const intensity = document.getElementById('intensity').value;
            const useLongText = document.getElementById('useLongText').checked;
            const useLLM = document.getElementById('useLLM').checked;

            const textLen = original.length;
            let processingNote = '';
            if (textLen >= 500 && useLongText) {
                processingNote = '(长文本优化处理中...)';
            }
            if (useLLM) {
                processingNote += ' [LLM辅助]';
            }

            fetch('/transform', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: original, preset, intensity: parseFloat(intensity), use_long_text: useLongText, use_llm: useLLM })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('modifiedText').value = data.modified;
                currentData.original = original;
                currentData.modified = data.modified;
                currentData.origScore = data.orig_score;
                currentData.modScore = data.mod_score;
                updateStats(data.orig_score, data.mod_score);
                document.getElementById('textLength').textContent = (textLen >= 500 ? `${textLen}字(长文本优化)` : `${textLen}字`) + (data.used_llm ? ' [LLM已启用]' : '');
            });
            });
        }

        function evaluateText() {
            const original = document.getElementById('originalText').value;
            if (!original.trim()) {
                alert('请输入源文本');
                return;
            }
            fetch('/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: original })
            })
            .then(r => r.json())
            .then(data => {
                alert(`AI写作检测分析\\n\\nAI概率: ${(data.ai_score * 100).toFixed(0)}%\\n正式度: ${(data.formality_score * 100).toFixed(0)}%\\n突发性: ${(data.burstiness * 100).toFixed(0)}%\\n词汇丰富度: ${(data.vocabulary_richness * 100).toFixed(0)}%\\n\\n${data.suggestions.join('\\n')}`);
            });
        }

        function targetedDefense() {
            const original = document.getElementById('originalText').value;
            if (!original.trim()) {
                alert('请输入源文本');
                return;
            }
            const target = document.getElementById('targetSelect').value;
            const intensity = document.getElementById('intensity').value;

            fetch('/targeted_defense', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: original, target, intensity: parseFloat(intensity) })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('modifiedText').value = data.modified;
                currentData.original = original;
                currentData.modified = data.modified;
                currentData.origScore = data.orig_score;
                currentData.modScore = data.mod_score;
                updateStats(data.orig_score, data.mod_score);
            });
        }

        function updateStats(origScore, modScore) {
            document.getElementById('origAIScore').textContent = (origScore * 100).toFixed(0) + '%';
            document.getElementById('modAIScore').textContent = (modScore * 100).toFixed(0) + '%';
            const reduction = ((origScore - modScore) * 100).toFixed(0);
            const reductionEl = document.getElementById('reduction');
            reductionEl.textContent = (reduction >= 0 ? '↓' : '↑') + Math.abs(reduction) + '%';
            reductionEl.className = 'stat-value ' + (reduction >= 0 ? 'down' : 'up');

            const origReduction = document.getElementById('originalStats');
            const modReduction = document.getElementById('modifiedStats');
            if (origReduction) origReduction.textContent = `AI ${(origScore * 100).toFixed(0)}%`;
            if (modReduction) modReduction.textContent = `AI ${(modScore * 100).toFixed(0)}%`;
        }

        function showDiff() {
            if (!currentData.original || !currentData.modified) {
                alert('请先执行变换');
                return;
            }
            fetch('/compute_diff', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ original: currentData.original, modified: currentData.modified })
            })
            .then(r => r.json())
            .then(data => {
                const diffText = document.getElementById('diffText');
                diffText.innerHTML = data.html;
                document.getElementById('diffView').style.display = 'flex';
            });
        }

        function closeDiff() {
            document.getElementById('diffView').style.display = 'none';
        }

        function swapTexts() {
            const original = document.getElementById('originalText');
            const modified = document.getElementById('modifiedText');
            const temp = original.value;
            original.value = modified.value;
            modified.value = temp;
        }

        function clearAll() {
            document.getElementById('originalText').value = '';
            document.getElementById('modifiedText').value = '';
            document.getElementById('origAIScore').textContent = '--';
            document.getElementById('modAIScore').textContent = '--';
            document.getElementById('reduction').textContent = '--';
            document.getElementById('originalStats').textContent = '';
            document.getElementById('modifiedStats').textContent = '';
            currentData = { original: '', modified: '', origScore: 0, modScore: 0 };
        }

        function loadSample() {
            document.getElementById('originalText').value = `综上所述，本文通过深入分析表明，提高系统的安全性对于保障数据安全具有重要意义。随着信息技术的快速发展，网络安全问题日益凸显，成为制约信息化建设的主要瓶颈之一。

首先，我们需要明确研究的目标。本研究旨在通过深入分析当前网络安全形势，提出切实可行的安全防护方案。

其次，通过实验数据验证假设。我们收集了大量的一手资料，包括最新的安全事件报告、漏洞统计数据以及行业专家的访谈记录。

最后，总结结论并提出建议。基于以上分析，我们认为应该从技术、管理和制度三个层面构建全方位的安全保障体系。

综上所述，本文的研究具有重要的理论价值和实践意义。毫无疑问，在当今社会，科学技术的发展对于提高生产效率具有重要作用。随着时代的发展，人工智能、大数据、云计算等新兴技术正在深刻改变我们的生活方式。

从某种意义上说，信息化程度已经成为衡量一个国家综合实力的重要标志。因此，我们必须高度重视网络安全问题，采取有效措施加以防范。`;
            document.getElementById('textLength').textContent = '示例长文本';
        }

        document.getElementById('diffView').addEventListener('click', function(e) {
            if (e.target === this) closeDiff();
        });

        function testLLM() {
            const mode = document.getElementById('llmMode').value;
            const url = document.getElementById('llmUrl').value;
            const statusDiv = document.getElementById('llmStatus');
            const statusText = document.getElementById('llmStatusText');

            if (!mode) {
                statusText.textContent = '未启用LLM';
                statusText.style.color = 'gray';
                statusDiv.style.display = 'block';
                return;
            }

            statusText.textContent = '正在测试连接...';
            statusText.style.color = 'orange';
            statusDiv.style.display = 'block';

            fetch('/test_llm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode, url })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    statusText.textContent = data.message;
                    statusText.style.color = 'green';
                } else {
                    statusText.textContent = '连接失败: ' + data.message;
                    statusText.style.color = 'red';
                }
            });
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/transform', methods=['POST'])
def transform():
    data = request.json
    text = data.get('text', '')
    preset = data.get('preset', 'balanced')
    intensity = data.get('intensity', 0.4)
    use_long_text = data.get('use_long_text', True)
    use_llm = data.get('use_llm', False)

    global engine
    engine = create_engine(preset=preset, intensity=intensity)

    hybrid = None
    if use_llm:
        hybrid = get_hybrid_engine()
        if hybrid:
            if use_long_text and len(text) >= 500:
                modified = hybrid.transform_long_text(text)
            else:
                modified = hybrid.transform(text)
        else:
            modified = engine.transform(text)
    elif use_long_text and len(text) >= 500:
        modified = engine.transform_long_text(text)
    else:
        modified = engine.transform(text)

    global detector
    orig_detection = detector.detect_ai_writing_markers(text)
    mod_detection = detector.detect_ai_writing_markers(modified)

    return jsonify({
        'modified': modified,
        'orig_score': orig_detection['ai_score'],
        'mod_score': mod_detection['ai_score'],
        'used_long_text_processor': use_long_text and len(text) >= 500,
        'used_llm': hybrid is not None,
        'text_length': len(text)
    })


@app.route('/transform_long', methods=['POST'])
def transform_long():
    """专门处理长文本的接口"""
    data = request.json
    text = data.get('text', '')
    preset = data.get('preset', 'balanced')
    intensity = data.get('intensity', 0.4)

    global engine
    engine = create_engine(preset=preset, intensity=intensity)

    processed, report = engine.transform_with_report(text)

    return jsonify({
        'modified': processed,
        'report': report
    })


@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    text = data.get('text', '')

    global detector
    result = detector.detect_ai_writing_markers(text)

    return jsonify(result)


@app.route('/targeted_defense', methods=['POST'])
def targeted_defense():
    data = request.json
    text = data.get('text', '')
    target = data.get('target', 'all')
    intensity = data.get('intensity', 0.4)

    defense = TargetedDefense(intensity=intensity)
    modified = defense.transform(text, target)

    global detector
    orig_detection = detector.detect_ai_writing_markers(text)
    mod_detection = detector.detect_ai_writing_markers(modified)

    return jsonify({
        'modified': modified,
        'orig_score': orig_detection['ai_score'],
        'mod_score': mod_detection['ai_score']
    })


@app.route('/test_llm', methods=['POST'])
def test_llm():
    """测试LLM连接"""
    data = request.json
    mode = data.get('mode', '')
    url = data.get('url', '')

    try:
        if mode == 'ollama':
            client = create_ollama_client(base_url=url or "http://localhost:11434")
            result = client.generate("Hello, respond with 'OK'")
            if 'ok' in result.lower():
                return jsonify({'success': True, 'message': 'Ollama连接成功'})
            return jsonify({'success': False, 'message': '响应异常'})

        elif mode == 'openai':
            client = create_openai_client(api_base=url or "https://api.openai.com/v1")
            result = client.generate("Hello, respond with 'OK'")
            if 'ok' in result.lower():
                return jsonify({'success': True, 'message': 'OpenAI连接成功'})
            return jsonify({'success': False, 'message': '响应异常'})

        elif mode == 'vllm':
            client = create_vllm_client(api_base=url or "http://localhost:8000")
            result = client.generate("Hello, respond with 'OK'")
            if 'ok' in result.lower():
                return jsonify({'success': True, 'message': 'vLLM连接成功'})
            return jsonify({'success': False, 'message': '响应异常'})

        return jsonify({'success': False, 'message': '未知模式'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/compute_diff', methods=['POST'])
def compute_diff():
    data = request.json
    original = data.get('original', '')
    modified = data.get('modified', '')

    orig_chars = list(original)
    mod_chars = list(modified)

    i, j = 0, 0
    html_parts = []

    while i < len(orig_chars) or j < len(mod_chars):
        if i < len(orig_chars) and j < len(mod_chars) and orig_chars[i] == mod_chars[j]:
            html_parts.append(f'<span>{orig_chars[i]}</span>')
            i += 1
            j += 1
        elif j < len(mod_chars) and (i >= len(orig_chars) or orig_chars[i] not in mod_chars[j:]):
            html_parts.append(f'<span class="highlight-added">{mod_chars[j]}</span>')
            j += 1
        elif i < len(orig_chars):
            html_parts.append(f'<span class="highlight-removed">{orig_chars[i]}</span>')
            i += 1
            j += 1
        else:
            html_parts.append(f'<span class="highlight-added">{mod_chars[j]}</span>')
            j += 1

    return jsonify({'html': ''.join(html_parts)})


if __name__ == '__main__':
    print("启动文本反检测系统 Web GUI...")
    print("请在浏览器中打开: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
