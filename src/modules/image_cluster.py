import shutil
from pathlib import Path

import imagehash
from PIL import Image

from src.core.config import ImageClusterConfig
from src.core.move_log import MoveLogger
from src.logger import setup_logger

logger = setup_logger("image_cluster")

class ImageClusterer:
    def __init__(self, config: ImageClusterConfig, move_logger: MoveLogger = None):
        self.config = config
        self.move_logger = move_logger

    def _compute_hash(self, image_path: Path) -> imagehash.ImageHash:
        with Image.open(image_path) as img:
            if self.config.hash_method == "phash":
                return imagehash.phash(img, hash_size=self.config.hash_size)
            elif self.config.hash_method == "ahash":
                return imagehash.average_hash(img, hash_size=self.config.hash_size)
            else:
                # Default to phash
                return imagehash.phash(img, hash_size=self.config.hash_size)

    def cluster_and_move(self, directory: Path, dry_run: bool = False):
        """Finds visually similar images and groups them into cluster folders."""
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp'} # HEIC omitted to simplify without pillow-heif for now
        
        # Store hash and corresponding file path
        hashes: dict[Path, imagehash.ImageHash] = {}
        
        for file_path in directory.iterdir():
            if not file_path.is_file() or file_path.name.startswith('.'):
                continue
            if file_path.suffix.lower() in image_extensions:
                try:
                    img_hash = self._compute_hash(file_path)
                    hashes[file_path] = img_hash
                except Exception as e:
                    logger.warning(f"Failed to process image {file_path.name}: {e}")

        # Find clusters
        clusters = []
        visited = set()
        
        file_paths = list(hashes.keys())
        for i, path1 in enumerate(file_paths):
            if path1 in visited:
                continue
                
            cluster = [path1]
            visited.add(path1)
            hash1 = hashes[path1]
            
            for j in range(i + 1, len(file_paths)):
                path2 = file_paths[j]
                if path2 in visited:
                    continue
                    
                hash2 = hashes[path2]
                if hash1 - hash2 <= self.config.similarity_threshold:
                    cluster.append(path2)
                    visited.add(path2)
                    
            if len(cluster) > 1:
                clusters.append(cluster)

        # Move to review folders
        if not clusters:
            logger.info("No similar image clusters found.")
            return

        review_dir = directory / self.config.review_folder_name
        
        for i, cluster in enumerate(clusters):
            cluster_dir_name = f"cluster_{i+1}"
            logger.info(f"Found cluster {cluster_dir_name} with {len(cluster)} images.")
            
            cluster_dir = review_dir / cluster_dir_name
            
            for file_path in cluster:
                if not dry_run:
                    cluster_dir.mkdir(parents=True, exist_ok=True)
                    target_path = cluster_dir / file_path.name
                    if target_path.exists():
                        target_path = cluster_dir / f"{file_path.stem}_1{file_path.suffix}"
                    shutil.move(str(file_path), str(target_path))
                    if self.move_logger:
                        self.move_logger.log_move(file_path, target_path)
                    logger.info(f"Moved {file_path.name} to {target_path}")
                else:
                    logger.info(f"[DRY RUN] Would move {file_path.name} to {review_dir.name}/{cluster_dir_name}/")
