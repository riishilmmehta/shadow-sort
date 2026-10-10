import imagehash
from pathlib import Path
from src.core.config import ImageClusterConfig
from src.modules.image_cluster import ImageClusterer

class MockImageHash:
    def __init__(self, value):
        self.value = value

    def __sub__(self, other):
        # Mock hamming distance
        return abs(self.value - other.value)

def test_hash_clustering_logic(mocker, tmp_path):
    config = ImageClusterConfig(
        hash_size=8,
        hash_method="phash",
        similarity_threshold=5,
        review_folder_name="Dups"
    )
    
    clusterer = ImageClusterer(config)
    
    # Mock the _compute_hash method directly to return predictable hashes
    def mock_compute_hash(file_path: Path):
        # Use filename as a basis for the hash value
        if "sim1" in file_path.name:
            return MockImageHash(10)
        elif "sim2" in file_path.name:
            return MockImageHash(12)  # Distance 2 from sim1
        elif "diff" in file_path.name:
            return MockImageHash(100) # Distance 90 from sim1
        return MockImageHash(0)

    mocker.patch.object(clusterer, '_compute_hash', side_effect=mock_compute_hash)
    
    # Create dummy files
    (tmp_path / "sim1.jpg").touch()
    (tmp_path / "sim2.jpg").touch()
    (tmp_path / "diff.jpg").touch()
    
    clusterer.cluster_and_move(tmp_path, dry_run=False)
    
    # sim1 and sim2 should be clustered because diff is 2 <= 5
    assert (tmp_path / "Dups" / "cluster_1" / "sim1.jpg").exists()
    assert (tmp_path / "Dups" / "cluster_1" / "sim2.jpg").exists()
    
    # diff should NOT be moved because it doesn't form a cluster with anything
    assert (tmp_path / "diff.jpg").exists()
