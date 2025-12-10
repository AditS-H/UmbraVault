import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table


class Reporter:
    def __init__(self, logs_path: str):
        self.logs_path = Path(logs_path)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.console = Console()

    def generate_report(self, task_type: str, results: List[Dict[str, Any]]) -> str:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        report = {
            'timestamp': now.isoformat(),
            'task_type': task_type,
            'results': results,
            'summary': {'success_count': sum(1 for r in results if r.get('success'))}
        }
        fname = f"{task_type}_{now.strftime('%Y%m%d_%H%M%S')}.json"
        path = self.logs_path / fname
        with path.open('w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        # print a short preview to console
        table = Table(title=f"{task_type.upper()} report")
        table.add_column("Tool")
        table.add_column("Status")
        table.add_column("Elapsed")
        for res in results:
            name = res.get('name', 'unknown')
            status = '✅' if res.get('success') else '❌'
            elapsed = f"{res.get('elapsed', 0):.1f}s"
            table.add_row(name, status, elapsed)
        self.console.print(table)

        return str(path)
