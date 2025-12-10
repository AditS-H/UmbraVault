import json
from typing import List, Dict, Any
from pathlib import Path

try:
    import ollama
except Exception:
    ollama = None


class ToolSelector:
    def __init__(self, tools_path: str, config: Dict[str, Any]):
        self.tools_path = Path(tools_path)
        self.tools = self.load_tools(self.tools_path)
        self.ai_enabled = bool(config.get('ai_model')) and ollama is not None

    def load_tools(self, path: Path) -> Dict[str, Dict]:
        tools = {}
        if not path.exists():
            return tools
        for p in path.glob('*.json'):
            try:
                with p.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    tools.update(data)
            except Exception:
                continue
        return tools

    def select_tools(self, task_type: str, target: str) -> List[Dict[str, str]]:
        mappings = {
            'network': ['nmap', 'rustscan'],
            'web': ['gobuster', 'nikto', 'sqlmap'],
        }
        base = mappings.get(task_type, ['nmap'])
        selected = []
        for tool in base:
            if tool in self.tools:
                cmd = self.tools[tool]['cmd'].format(target=target)
                selected.append({'name': tool, 'cmd': cmd})

        # optional AI: simple suggestion via ollama if configured
        if self.ai_enabled:
            try:
                # simplistic prompt
                prompt = f"Suggest up to 1 extra tool name for {task_type} on {target} from: {list(self.tools.keys())}"
                resp = ollama.generate(model='llama3.2', prompt=prompt)
                text = resp.get('response', '') if isinstance(resp, dict) else str(resp)
                # pick first token-like candidate
                for token in text.replace('\n', ' ').split():
                    t = token.strip().strip('.,')
                    if t in self.tools and t not in [s['name'] for s in selected]:
                        selected.append({'name': t, 'cmd': self.tools[t]['cmd'].format(target=target)})
                        break
            except Exception:
                pass

        return selected[:4]
