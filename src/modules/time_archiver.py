import os
import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

from src.core.config import TimeArchiverConfig
from src.logger import setup_logger

logger = setup_logger("time_archiver")

class TimeArchiver:
    def __init__(self, config: TimeArchiverConfig):
        self.config = config
        self.manifest_name = "archive_manifest.json"

    def _get_timestamp(self, file_path: Path) -> float:
        stat = file_path.stat()
        if self.config.timestamp_method == "atime":
            return stat.st_atime
        return stat.st_mtime # Default to mtime

    def archive_old_files(self, directory: Path, dry_run: bool = False):
        """Archives files untouched for a configured number of days."""
        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=self.config.days_untouched)
        cutoff_timestamp = cutoff_date.timestamp()

        files_to_archive = []
        for file_path in directory.iterdir():
            if not file_path.is_file() or file_path.name.startswith('.'):
                continue
                
            # Skip zip files that look like our archives
            if file_path.suffix == '.zip' and file_path.name.startswith(self.config.archive_prefix):
                continue
                
            # Skip manifest
            if file_path.name == self.manifest_name:
                continue

            file_ts = self._get_timestamp(file_path)
            if file_ts < cutoff_timestamp:
                files_to_archive.append(file_path)

        if not files_to_archive:
            logger.info("No old files found to archive.")
            return

        archive_name = f"{self.config.archive_prefix}{now.strftime('%Y%m%d_%H%M%S')}.zip"
        archive_path = directory / archive_name
        
        manifest_path = directory / self.manifest_name
        manifest = {}
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load manifest: {e}")

        logger.info(f"Found {len(files_to_archive)} files older than {self.config.days_untouched} days. Archiving to {archive_name}")

        if not dry_run:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in files_to_archive:
                    zf.write(file_path, arcname=file_path.name)
                    # Update manifest
                    manifest[file_path.name] = {
                        "archive": archive_name,
                        "original_path": str(file_path.absolute()),
                        "archived_at": now.isoformat()
                    }
                    # Delete original file
                    file_path.unlink()
                    logger.info(f"Archived and removed: {file_path.name}")
                    
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            logger.info("Manifest updated.")
        else:
            for file_path in files_to_archive:
                logger.info(f"[DRY RUN] Would archive and remove: {file_path.name}")
