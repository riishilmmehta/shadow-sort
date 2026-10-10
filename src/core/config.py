
import yaml
from pydantic_settings import BaseSettings


class SemanticSortConfig(BaseSettings):
    model_name: str
    labels: list[str]
    confidence_threshold: float
    needs_review_folder_name: str

class ImageClusterConfig(BaseSettings):
    hash_size: int
    hash_method: str
    similarity_threshold: int
    review_folder_name: str

class TimeArchiverConfig(BaseSettings):
    days_untouched: int
    timestamp_method: str
    archive_prefix: str

class DependencyDetectorConfig(BaseSettings):
    markers: list[str]
    project_folder_name: str

class AppConfig(BaseSettings):
    semantic_sort: SemanticSortConfig
    image_cluster: ImageClusterConfig
    time_archiver: TimeArchiverConfig
    dependency_detector: DependencyDetectorConfig

def load_config(config_path: str = "config.yaml") -> AppConfig:
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    return AppConfig(**config_dict)
