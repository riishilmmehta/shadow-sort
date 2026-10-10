import typer
from pathlib import Path
from src.core.config import load_config
from src.core.path_utils import get_downloads_path, get_documents_path
from src.modules.semantic_sort import SemanticSorter
from src.modules.image_cluster import ImageClusterer
from src.modules.time_archiver import TimeArchiver
from src.modules.dep_detector import DependencyDetector
from src.core.move_log import MoveLogger
from src.restore import undo_moves
from src.logger import setup_logger

app = typer.Typer(help="Smart Local File Organizer ('Shadow Sort')")

@app.command()
def run(
    path: str = typer.Option(None, "--path", "-p", help="Specific directory to organize. Defaults to Downloads."),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Run without moving or deleting any files."),
    undo: bool = typer.Option(False, "--undo", "-u", help="Undo the last successful run in the specified directory."),
    config_path: str = typer.Option("config.yaml", "--config", "-c", help="Path to configuration file."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging.")
):
    """Run the Smart Local File Organizer."""
    logger = setup_logger("cli", verbose)
    
    config = load_config(config_path)
    logger.info("Loaded configuration.")
    
    target_dir = Path(path) if path else get_downloads_path()
    
    if not target_dir.exists() or not target_dir.is_dir():
        logger.error(f"Target directory does not exist or is not a directory: {target_dir}")
        raise typer.Exit(1)
        
    move_log_path = target_dir / "move_log.json"
    
    if undo:
        undo_moves(move_log_path)
        return
        
    logger.info(f"Starting organization for directory: {target_dir}")
    if dry_run:
        logger.info("--- DRY RUN MODE ENABLED ---")
        
    move_logger = MoveLogger(move_log_path)

    # 1. Semantic Sorting
    logger.info("--- Phase 1: Semantic Sorting ---")
    sorter = SemanticSorter(config.semantic_sort, move_logger=move_logger)
    sorter.classify_and_move(target_dir, dry_run=dry_run)
    
    # 2. Image Clustering
    logger.info("--- Phase 2: Image Clustering ---")
    clusterer = ImageClusterer(config.image_cluster, move_logger=move_logger)
    clusterer.cluster_and_move(target_dir, dry_run=dry_run)
    
    # 3. Project Detection
    logger.info("--- Phase 3: Developer Project Detection ---")
    detector = DependencyDetector(config.dependency_detector, move_logger=move_logger)
    detector.detect_and_move(target_dir, dry_run=dry_run)
    
    # 4. Time-Decay Archiving
    logger.info("--- Phase 4: Time-Decay Archiving ---")
    archiver = TimeArchiver(config.time_archiver)
    archiver.archive_old_files(target_dir, dry_run=dry_run)
    
    if not dry_run:
        move_logger.save()
    
    logger.info("Organization complete.")

if __name__ == "__main__":
    app()
