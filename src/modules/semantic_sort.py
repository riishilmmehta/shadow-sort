import shutil
from pathlib import Path

import docx
from transformers import pipeline

from src.core.config import SemanticSortConfig
from src.core.move_log import MoveLogger
from src.logger import setup_logger

logger = setup_logger("semantic_sort")

class SemanticSorter:
    def __init__(self, config: SemanticSortConfig, move_logger: MoveLogger = None):
        self.config = config
        self.move_logger = move_logger
        logger.info(f"Loading zero-shot classification model: {self.config.model_name}...")
        self.classifier = pipeline("zero-shot-classification", model=self.config.model_name)
        logger.info("Model loaded successfully.")

    def extract_text(self, file_path: Path) -> str | None:
        """Extracts text from .txt, .md, or .docx files."""
        try:
            if file_path.suffix.lower() in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read(2000)  # Read up to 2000 chars for context
            elif file_path.suffix.lower() == '.docx':
                doc = docx.Document(file_path)
                full_text = [para.text for para in doc.paragraphs]
                return '\n'.join(full_text)[:2000]
        except Exception as e:
            logger.warning(f"Failed to extract text from {file_path}: {e}")
        return None

    def classify_and_move(self, directory: Path, dry_run: bool = False):
        """Classifies text files in the given directory and moves them to labeled folders."""
        for file_path in directory.iterdir():
            if not file_path.is_file() or file_path.name.startswith('.'):
                continue
                
            if file_path.suffix.lower() not in ['.txt', '.md', '.docx']:
                continue

            text = self.extract_text(file_path)
            if not text or not text.strip():
                continue

            # Classify
            result = self.classifier(text, self.config.labels, multi_label=False)
            best_label = result['labels'][0]
            confidence = result['scores'][0]

            if confidence >= self.config.confidence_threshold:
                target_folder_name = best_label
                log_msg = f"Classified {file_path.name} as '{best_label}' (conf: {confidence:.2f})"
            else:
                target_folder_name = self.config.needs_review_folder_name
                log_msg = f"Low confidence ({confidence:.2f}) for {file_path.name}, flagging for review."

            logger.info(log_msg)
            
            target_dir = directory / target_folder_name
            
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / file_path.name
                # Avoid overwriting
                if target_path.exists():
                    target_path = target_dir / f"{file_path.stem}_1{file_path.suffix}"
                shutil.move(str(file_path), str(target_path))
                if self.move_logger:
                    self.move_logger.log_move(file_path, target_path)
                logger.info(f"Moved to {target_path}")
            else:
                logger.info(f"[DRY RUN] Would move {file_path.name} to {target_folder_name}/")
