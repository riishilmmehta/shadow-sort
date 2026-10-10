import json
import shutil
import zipfile
from pathlib import Path

from src.logger import setup_logger

logger = setup_logger("restorer")

def undo_moves(log_path: Path):
    """Reverses the file moves documented in the move log."""
    if not log_path.exists():
        logger.info("No move log found to undo.")
        return
        
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            moves = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read move log: {e}")
        return
        
    logger.info(f"Undoing {len(moves)} file moves...")
    
    # Reverse the order so we undo the most recent first
    for move in reversed(moves):
        src = Path(move['source'])
        dest = Path(move['destination'])
        
        if dest.exists() and not src.exists():
            try:
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dest), str(src))
                logger.info(f"Restored {dest.name} to {src.parent}")
            except Exception as e:
                logger.error(f"Failed to restore {dest}: {e}")
        else:
            logger.warning(f"Could not restore {dest} - either it's missing or source already exists.")
            
    # Clear the log after undo
    log_path.unlink()
    logger.info("Undo complete. Log cleared.")

def restore_archive(directory: Path, archive_name: str | None = None):
    """Restores files from a specific archive, or all archives if None."""
    manifest_path = directory / "archive_manifest.json"
    if not manifest_path.exists():
        logger.info("No archive manifest found.")
        return
        
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read archive manifest: {e}")
        return
        
    archives_to_restore = set()
    files_restored = []
    
    for filename, data in manifest.items():
        arch_name = data.get('archive')
        if archive_name is None or arch_name == archive_name:
            archives_to_restore.add((arch_name, data.get('original_path')))

    if not archives_to_restore:
        logger.info("No files matching the criteria found to restore.")
        return

    # Extracting
    for arch_name, orig_path_str in archives_to_restore:
        arch_path = directory / arch_name
        orig_path = Path(orig_path_str)
        
        if not arch_path.exists():
            logger.warning(f"Archive {arch_name} missing, skipping...")
            continue
            
        with zipfile.ZipFile(arch_path, 'r') as zf:
            filename = orig_path.name
            if filename in zf.namelist():
                # Extract file to its original location
                orig_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(filename) as source, open(orig_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                logger.info(f"Restored {filename} to {orig_path.parent}")
                files_restored.append(filename)

    # Clean up manifest
    for f in files_restored:
        if f in manifest:
            del manifest[f]
            
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    logger.info("Manifest updated.")
