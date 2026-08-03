from datetime import datetime
from pathlib import Path
import shutil


def create_database_backup(source_path: str | Path, backup_dir: str | Path | None = None) -> Path:
    source = Path(source_path)
    backup_directory = Path(backup_dir or "backups")
    backup_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_directory / f"{source.stem}_{timestamp}{source.suffix}"
    shutil.copy2(source, backup_path)
    return backup_path
