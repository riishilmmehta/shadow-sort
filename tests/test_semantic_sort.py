from src.core.config import SemanticSortConfig
from src.modules.semantic_sort import SemanticSorter


class MockClassifier:
    def __init__(self, confidence):
        self.confidence = confidence

    def __call__(self, text, labels, multi_label=False):
        return {
            'labels': labels, # Mocking that the first label is best
            'scores': [self.confidence] + [0.1] * (len(labels) - 1)
        }

def test_classification_thresholding_high_confidence(mocker, tmp_path):
    config = SemanticSortConfig(
        model_name="test-model",
        labels=["Finance", "Work"],
        confidence_threshold=0.8,
        needs_review_folder_name="Review"
    )
    
    # Mock pipeline
    mocker.patch('src.modules.semantic_sort.pipeline', return_value=MockClassifier(0.9))
    sorter = SemanticSorter(config)
    
    # Create dummy file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Invoice and billing.")
    
    sorter.classify_and_move(tmp_path, dry_run=False)
    
    # Should be moved to Finance
    assert (tmp_path / "Finance" / "test.txt").exists()
    assert not test_file.exists()

def test_classification_thresholding_low_confidence(mocker, tmp_path):
    config = SemanticSortConfig(
        model_name="test-model",
        labels=["Finance", "Work"],
        confidence_threshold=0.8,
        needs_review_folder_name="Review"
    )
    
    # Mock pipeline
    mocker.patch('src.modules.semantic_sort.pipeline', return_value=MockClassifier(0.5))
    sorter = SemanticSorter(config)
    
    # Create dummy file
    test_file = tmp_path / "test2.txt"
    test_file.write_text("Some random text.")
    
    sorter.classify_and_move(tmp_path, dry_run=False)
    
    # Should be moved to Review
    assert (tmp_path / "Review" / "test2.txt").exists()
    assert not test_file.exists()
