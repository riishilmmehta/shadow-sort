# Smart Local File Organizer ("Shadow Sort")

A cross-platform (Windows/macOS/Linux) desktop automation script that performs local, privacy-preserving intelligent organization of a user's file system.

## Core Features
1. **100% Local Processing**: No data leaves the machine. Privacy-first.
2. **Zero-Config OS Paths**: Auto-discovery of common OS paths like Downloads.
3. **Non-destructive Default**: Files are flagged or moved to review folders rather than deleted.
4. **Idempotent**: Safe to re-run without duplicating work or corrupting state.

## Modules
- **Semantic Sorting**: Parses text/docs and uses local zero-shot classification to sort files into topics. Low confidence moves to review.
- **Image Clustering**: Uses perceptual hashing to find near-duplicates and group them for manual review.
- **Time-Decay Archiver**: Zips and archives untouched files older than a configured threshold.
- **Dependency Detector**: Identifies development projects and heavy dependency folders (e.g., node_modules) for easy cleanup and consolidation.

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the CLI:
   ```bash
   python src/cli.py --help
   ```

## Configuration
Edit `config.yaml` to customize labels, thresholds, and folder names.

## Safety Note
The default mode will **never** permanently delete files. It only moves, archives, or flags them for your review. Semantic classification confidence isn't perfect — low-confidence items go to the review folder.
