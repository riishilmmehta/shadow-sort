import json
from datetime import UTC, datetime
from pathlib import Path


class MoveLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.moves = []

    def log_move(self, source: Path, destination: Path):
        self.moves.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "source": str(source.absolute()),
            "destination": str(destination.absolute())
        })

    def save(self):
        if not self.moves:
            return
            
        data = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                pass
                
        data.extend(self.moves)
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
