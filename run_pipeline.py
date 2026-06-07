# run_pipeline.py
from scripts.phase_1_parser import parse_ipl_csv_files
# from src.feature_engineering import build_modeling_features # Uncomment when you create this

def main():
    print("--- Starting Pipeline ---")
    
    # Phase 1: Parsing
    parse_ipl_csv_files(raw_dir="data/raw", processed_dir="data/processed")
    
    # Phase 2: Feature Engineering (Coming soon)
    # build_modeling_features()
    
    print("--- Pipeline Complete ---")

if __name__ == "__main__":
    main()