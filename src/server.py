from flask import Flask, request, jsonify
import jwt
import json
from pathlib import Path
from src.sanitizer import InputSanitizer
from src.selector import ToolSelector
from src.executor import ToolExecutor
from src.reporter import Reporter


def load_config():
    project_root = Path(__file__).resolve().parents[1]
    cfg_path = project_root / 'config.json'
    with cfg_path.open('r', encoding='utf-8') as f:
        return json.load(f), str(cfg_path)


config, config_path = load_config()
try:
    InputSanitizer.validate_json_config(config_path)
except Exception as e:
    print(f"Config validation error: {e}")

SECRET = config['api']['secret_token']
app = Flask(__name__)
selector = ToolSelector(config.get('tools_path', './tools/'), config)
executor = ToolExecutor(config)
reporter = Reporter(config.get('logs_path', './logs/'))


def verify_token(token: str) -> bool:
    try:
        jwt.decode(token, SECRET, algorithms=['HS256'])
        return True
    except Exception:
        return False


@app.route('/health')
def health():
    return jsonify({'status': 'active', 'local_only': True})


@app.route('/run/<task_type>', methods=['POST'])
def run_task(task_type):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not verify_token(auth_header.replace('Bearer ', '')):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        data = request.get_json() or {}
        data = InputSanitizer.sanitize_task(data)
        target = data['target']
        tools = selector.select_tools(task_type, target)
        results = []
        for tool in tools:
            result = executor.execute(tool['cmd'], target)
            results.append({**tool, **result})
        report_path = reporter.generate_report(task_type, results)
        return jsonify({'results': results, 'report': report_path})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host=config['api']['host'], port=int(config['api']['port']), debug=False)
