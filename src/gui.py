import streamlit as st
import os
from pathlib import Path
import json

from src.core.config import AppConfig
from src.core.move_log import MoveLogger
from src.modules.semantic_sort import SemanticSorter
from src.modules.image_cluster import ImageClusterer
from src.modules.time_archiver import TimeArchiver
from src.modules.dep_detector import DependencyDetector
from src.restore import undo_moves

st.set_page_config(page_title="Shadow Sort UI", page_icon="🗄️", layout="wide")

st.title("🗄️ Shadow Sort")
st.markdown("### Smart Local File Organizer")
st.caption("100% Local • Privacy-First • Non-destructive")

config = AppConfig()
logger = MoveLogger(config.target_dir)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Directories")
    source_dir = st.text_input("Source Directory", str(config.source_dir))
    target_dir = st.text_input("Target Directory", str(config.target_dir))
    
    st.subheader("Thresholds")
    semantic_threshold = st.slider("Semantic Confidence Threshold", 0.0, 1.0, config.semantic_sort.confidence_threshold, 0.05)
    image_hash_threshold = st.slider("Image Hash Difference", 0, 20, config.image_cluster.hash_diff_threshold, 1)
    
    st.divider()
    st.info("Files are moved safely. You can always undo operations in the Undo tab.")

# Update config from UI
config.source_dir = Path(source_dir)
config.target_dir = Path(target_dir)
config.semantic_sort.confidence_threshold = semantic_threshold
config.image_cluster.hash_diff_threshold = image_hash_threshold

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧠 Semantic Sort", 
    "🖼️ Image Cluster", 
    "⏳ Time Archiver", 
    "💻 Project Cleanup",
    "↩️ Undo Manager"
])

with tab1:
    st.header("Semantic Text Classification")
    st.write("Automatically categorize your documents (.txt, .md, .docx, .pdf) using a local zero-shot AI model based on their actual content.")
    
    if st.button("Run Semantic Sort", type="primary", key="sem_btn"):
        with st.spinner("Loading AI model and analyzing documents... This may take a minute."):
            sorter = SemanticSorter(config, logger)
            moved = sorter.run()
            if moved > 0:
                st.success(f"Successfully categorized {moved} documents!")
            else:
                st.info("No documents found to categorize.")

with tab2:
    st.header("Visual Duplicate Detection")
    st.write("Find and group visually similar images using perceptual hashing, even if they have different resolutions or formats.")
    
    if st.button("Run Image Clusterer", type="primary", key="img_btn"):
        with st.spinner("Analyzing and clustering images..."):
            clusterer = ImageClusterer(config, logger)
            moved = clusterer.run()
            if moved > 0:
                st.success(f"Successfully clustered {moved} visually similar images!")
            else:
                st.info("No similar images found to cluster.")

with tab3:
    st.header("Time-Based Archiving")
    st.write("Archive old files that haven't been modified in a long time into compressed ZIP archives.")
    
    if st.button("Run Time Archiver", type="primary", key="time_btn"):
        with st.spinner("Scanning for old files and compressing..."):
            archiver = TimeArchiver(config, logger)
            moved = archiver.run()
            if moved > 0:
                st.success(f"Successfully archived {moved} files into time-based folders!")
            else:
                st.info("No old files found to archive.")

with tab4:
    st.header("Developer Project Cleanup")
    st.write("Detect orphaned code files and group them into logical project directories based on their dependencies (e.g., package.json, requirements.txt).")
    
    if st.button("Run Project Cleanup", type="primary", key="proj_btn"):
        with st.spinner("Detecting code projects and organizing..."):
            detector = DependencyDetector(config, logger)
            moved = detector.run()
            if moved > 0:
                st.success(f"Successfully grouped {moved} project files!")
            else:
                st.info("No orphaned project files found.")

with tab5:
    st.header("Undo Operations")
    st.write("Review recent moves and safely restore files back to their original locations.")
    
    log_file = config.target_dir / "move_log.json"
    if log_file.exists():
        with open(log_file, "r") as f:
            logs = json.load(f)
            
        if logs:
            st.write(f"**{len(logs)}** operations currently logged.")
            with st.expander("View recent move logs"):
                st.json(logs[-10:]) # Show last 10
                
            if st.button("Undo All Recent Moves", type="primary", key="undo_btn"):
                with st.spinner("Restoring files..."):
                    undo_moves(config.target_dir)
                    st.success("Successfully restored all files to their original locations!")
                    st.rerun()
        else:
            st.info("Move log is empty. No operations to undo.")
    else:
        st.info("No move log found. Run some operations first!")

st.divider()
st.caption("Built locally. No cloud servers harmed.")
