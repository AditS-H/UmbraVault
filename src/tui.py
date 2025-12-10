import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from src.selector import ToolSelector
from src.executor import ToolExecutor
from src.reporter import Reporter
from src.sanitizer import InputSanitizer


def main_tui(config_path: str = None):
    console = Console()
    project_root = Path(__file__).resolve().parents[1]
    cfg_path = Path(config_path) if config_path else project_root / 'config.json'
    config = json.loads(cfg_path.read_text(encoding='utf-8'))
    InputSanitizer.validate_json_config(str(cfg_path))
    selector = ToolSelector(config.get('tools_path', './tools/'), config)
    executor = ToolExecutor(config)
    reporter = Reporter(config.get('logs_path', './logs/'))

    console.print(Panel("HexStrike-Local TUI: Enter 'quit' to exit.", title="🚀 Ready"))

    while True:
        task_type = Prompt.ask("Task type", choices=['network', 'web', 'quit'])
        if task_type == 'quit':
            break
        target = Prompt.ask("Target (IP/domain)")
        try:
            InputSanitizer.sanitize_task({'target': target})
        except Exception as e:
            console.print(f"[red]Invalid target:[/red] {e}")
            continue
        if not Confirm.ask("Run?"):
            continue
        tools = selector.select_tools(task_type, target)
        results = []
        for tool in tools:
            console.print(f"Running [bold]{tool['name']}[/bold]...")
            res = executor.execute(tool['cmd'], target)
            results.append({**tool, **res})
        reporter.generate_report(task_type, results)


if __name__ == '__main__':
    main_tui()
