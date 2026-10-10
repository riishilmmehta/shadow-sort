import shutil
from pathlib import Path

from src.core.config import DependencyDetectorConfig
from src.core.move_log import MoveLogger
from src.core.path_utils import get_home_path
from src.logger import setup_logger

logger = setup_logger("dep_detector")

class DependencyDetector:
    def __init__(self, config: DependencyDetectorConfig, move_logger: MoveLogger = None):
        self.config = config
        self.move_logger = move_logger

    def _get_dir_size(self, directory: Path) -> int:
        """Returns the size of the directory in bytes."""
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(directory):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except Exception as e:
            logger.debug(f"Error getting size for {directory}: {e}")
        return total_size

    def detect_and_move(self, directory: Path, dry_run: bool = False):
        """Detects developer projects and moves them to a central location."""
        
        home = get_home_path()
        target_projects_dir = home / self.config.project_folder_name
        
        # Avoid recursive moving if already in the target dir
        if target_projects_dir in directory.parents or directory == target_projects_dir:
            return

        projects_found = []

        # Iterate over subdirectories in the given directory
        for item in directory.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                is_project = False
                heavy_deps = []
                
                # Check for markers
                try:
                    for subitem in item.iterdir():
                        if subitem.name in self.config.markers:
                            is_project = True
                            if subitem.is_dir() and subitem.name in ['node_modules', '.venv', 'venv', 'target']:
                                heavy_deps.append(subitem)
                except PermissionError:
                    continue
                    
                if is_project:
                    projects_found.append((item, heavy_deps))

        if not projects_found:
            logger.info("No developer projects detected.")
            return

        for project_dir, deps in projects_found:
            logger.info(f"Detected project: {project_dir.name}")
            for dep in deps:
                size_mb = self._get_dir_size(dep) / (1024 * 1024)
                logger.info(f"  -> Found heavy dependency: {dep.name} ({size_mb:.2f} MB)")
            
            target_path = target_projects_dir / project_dir.name
            
            if not dry_run:
                target_projects_dir.mkdir(parents=True, exist_ok=True)
                if target_path.exists():
                    target_path = target_projects_dir / f"{project_dir.name}_1"
                    
                shutil.move(str(project_dir), str(target_path))
                if self.move_logger:
                    self.move_logger.log_move(project_dir, target_path)
                logger.info(f"Moved project to {target_path}")
            else:
                logger.info(f"[DRY RUN] Would move {project_dir.name} to {target_projects_dir}/")
                
import os  # Ensure os is imported for walk
