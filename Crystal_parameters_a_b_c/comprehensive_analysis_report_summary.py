import os
from pathlib import Path
from datetime import datetime

def find_all_comprehensive_reports(base_dir):
    """Find all comprehensive_analysis_report.txt files in the directory tree."""
    base_path = Path(base_dir)
    report_files = []
    
    for file_path in base_path.rglob('comprehensive_analysis_report.txt'):
        report_files.append(file_path)
    
    return sorted(report_files)  # Sort for consistent ordering

def aggregate_comprehensive_reports(base_dir):
    """Aggregate all comprehensive_analysis_report.txt files into a single text file."""
    # Find all report files
    report_files = find_all_comprehensive_reports(base_dir)
    print(f"Found {len(report_files)} comprehensive_analysis_report.txt files")
    
    # Create summary text file
    summary_txt_path = os.path.join(base_dir, 'all_comprehensive_reports_summary.txt')
    
    with open(summary_txt_path, 'w', encoding='utf-8') as summary_file:
        # Write header
        summary_file.write("=" * 80 + "\n")
        summary_file.write("COMPREHENSIVE ANALYSIS REPORTS SUMMARY\n")
        summary_file.write("=" * 80 + "\n")
        summary_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        summary_file.write(f"Total files found: {len(report_files)}\n")
        summary_file.write(f"Base directory: {base_dir}\n")
        summary_file.write("=" * 80 + "\n\n")
        
        # Process each file
        for i, file_path in enumerate(report_files, 1):
            # Get relative path for better readability
            rel_path = os.path.relpath(file_path, base_dir)
            
            print(f"Processing file {i}/{len(report_files)}: {rel_path}")
            
            # Write file separator
            summary_file.write("\n" + "#" * 80 + "\n")
            summary_file.write(f"# FILE {i}: {rel_path}\n")
            summary_file.write("#" * 80 + "\n\n")
            
            try:
                # Read and write the content of each report
                with open(file_path, 'r', encoding='utf-8') as report_file:
                    content = report_file.read()
                    summary_file.write(content)
                    
                    # Add extra newlines between files for clarity
                    summary_file.write("\n\n")
                    
            except Exception as e:
                error_msg = f"ERROR: Could not read file {rel_path}: {str(e)}\n"
                print(error_msg)
                summary_file.write(error_msg)
                summary_file.write("\n\n")
        
        # Write footer
        summary_file.write("\n" + "=" * 80 + "\n")
        summary_file.write("END OF SUMMARY\n")
        summary_file.write("=" * 80 + "\n")
    
    print(f"\nSummary file saved to: {summary_txt_path}")
    print(f"Total size: {os.path.getsize(summary_txt_path) / 1024 / 1024:.2f} MB")
    
    return report_files

def extract_key_values(base_dir):
    """Extract key values from all reports and create a compact summary."""
    report_files = find_all_comprehensive_reports(base_dir)
    
    if not report_files:
        print("No comprehensive_analysis_report.txt files found!")
        return
    
    # Create a compact summary with key values
    compact_summary_path = os.path.join(base_dir, 'comprehensive_reports_key_values.txt')
    
    with open(compact_summary_path, 'w', encoding='utf-8') as summary_file:
        summary_file.write("COMPREHENSIVE REPORTS - KEY VALUES SUMMARY\n")
        summary_file.write("=" * 80 + "\n")
        summary_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        summary_file.write(f"Total files: {len(report_files)}\n")
        summary_file.write("=" * 80 + "\n\n")
        
        for i, file_path in enumerate(report_files, 1):
            rel_path = os.path.relpath(file_path, base_dir)
            summary_file.write(f"[{i}] {rel_path}\n")
            summary_file.write("-" * 40 + "\n")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract key information using simple line parsing
                    for line in content.split('\n'):
                        line = line.strip()
                        # Look for lines with key statistics
                        if any(keyword in line for keyword in ['Mean:', 'Total atoms:', 'Chemical formula', 
                                                               'First Peak', 'coordination number']):
                            summary_file.write(f"  {line}\n")
                            
            except Exception as e:
                summary_file.write(f"  ERROR: {str(e)}\n")
            
            summary_file.write("\n")
    
    print(f"Compact summary saved to: {compact_summary_path}")

# Main execution
if __name__ == "__main__":
    # Set your base directory path here
    base_directory = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/crystal_parameters_a_b_c"
    
    # Run the aggregation
    print("Starting comprehensive report aggregation...")
    report_files = aggregate_comprehensive_reports(base_directory)
    
    # Also create a compact summary with key values
    print("\nCreating compact summary with key values...")
    extract_key_values(base_directory)
    
    print("\nDone!")
