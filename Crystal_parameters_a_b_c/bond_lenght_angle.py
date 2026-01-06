import os
import re
import pandas as pd
from pathlib import Path
from datetime import datetime

def parse_statistics_file(file_path):
    """Parse a bond_angle_statistics.txt file and extract the statistics."""
    stats = {
        'file_path': str(file_path),
        'bond_lengths': {},
        'bond_angles': {}
    }
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse bond length statistics
        bond_length_pattern = r'(\w+-\w+):\s*Mean\s*=\s*([\d.]+)\s*Angstrom,\s*Std\s*=\s*([\d.]+)\s*Angstrom,\s*Count\s*=\s*(\d+)'
        bond_length_matches = re.findall(bond_length_pattern, content)
        
        for match in bond_length_matches:
            bond_type, mean, std, count = match
            stats['bond_lengths'][bond_type] = {
                'mean': float(mean),
                'std': float(std),
                'count': int(count)
            }
        
        # Parse bond angle statistics
        bond_angle_pattern = r'(\w+-\w+-\w+):\s*Mean\s*=\s*([\d.]+)\s*degrees,\s*Std\s*=\s*([\d.]+)\s*degrees,\s*Count\s*=\s*(\d+)'
        bond_angle_matches = re.findall(bond_angle_pattern, content)
        
        for match in bond_angle_matches:
            angle_type, mean, std, count = match
            stats['bond_angles'][angle_type] = {
                'mean': float(mean),
                'std': float(std),
                'count': int(count)
            }
        
        return stats
    
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

def find_all_statistics_files(base_dir):
    """Find all bond_angle_statistics.txt files in the directory tree."""
    base_path = Path(base_dir)
    statistics_files = []
    
    for file_path in base_path.rglob('bond_angle_statistics.txt'):
        statistics_files.append(file_path)
    
    return statistics_files

def aggregate_statistics(base_dir):
    """Aggregate all statistics from bond_angle_statistics.txt files."""
    # Find all statistics files
    statistics_files = find_all_statistics_files(base_dir)
    print(f"Found {len(statistics_files)} bond_angle_statistics.txt files")
    
    # Parse all files
    all_stats = []
    for file_path in statistics_files:
        stats = parse_statistics_file(file_path)
        if stats:
            all_stats.append(stats)
    
    # Create summary text file
    summary_txt_path = os.path.join(base_dir, 'bond_statistics_summary.txt')
    with open(summary_txt_path, 'w') as f:
        f.write(f"Bond Statistics Summary\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total files processed: {len(all_stats)}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, stats in enumerate(all_stats):
            f.write(f"File {i+1}: {stats['file_path']}\n")
            f.write("-" * 40 + "\n")
            
            if stats['bond_lengths']:
                f.write("Bond Length Statistics:\n")
                for bond_type, values in stats['bond_lengths'].items():
                    f.write(f"{bond_type}: Mean = {values['mean']} Angstrom, ")
                    f.write(f"Std = {values['std']} Angstrom, Count = {values['count']}\n")
            
            if stats['bond_angles']:
                f.write("\nBond Angle Statistics:\n")
                for angle_type, values in stats['bond_angles'].items():
                    f.write(f"{angle_type}: Mean = {values['mean']} degrees, ")
                    f.write(f"Std = {values['std']} degrees, Count = {values['count']}\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
    
    print(f"Summary text file saved to: {summary_txt_path}")
    
    # Create CSV file
    csv_data = []
    for stats in all_stats:
        # Extract relative path for better readability
        rel_path = os.path.relpath(stats['file_path'], base_dir)
        
        # Add bond length data
        for bond_type, values in stats['bond_lengths'].items():
            csv_data.append({
                'File_Path': rel_path,
                'Type': 'Bond Length',
                'Bond/Angle': bond_type,
                'Mean': values['mean'],
                'Std': values['std'],
                'Count': values['count'],
                'Unit': 'Angstrom'
            })
        
        # Add bond angle data
        for angle_type, values in stats['bond_angles'].items():
            csv_data.append({
                'File_Path': rel_path,
                'Type': 'Bond Angle',
                'Bond/Angle': angle_type,
                'Mean': values['mean'],
                'Std': values['std'],
                'Count': values['count'],
                'Unit': 'degrees'
            })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(csv_data)
    csv_path = os.path.join(base_dir, 'bond_statistics_summary.csv')
    df.to_csv(csv_path, index=False)
    print(f"CSV file saved to: {csv_path}")
    
    # Create a pivot table for easier analysis
    if len(df) > 0:
        pivot_csv_path = os.path.join(base_dir, 'bond_statistics_pivot.csv')
        
        # Create separate pivot tables for bond lengths and angles
        bond_length_df = df[df['Type'] == 'Bond Length'][['File_Path', 'Bond/Angle', 'Mean']]
        bond_angle_df = df[df['Type'] == 'Bond Angle'][['File_Path', 'Bond/Angle', 'Mean']]
        
        if not bond_length_df.empty:
            bond_length_pivot = bond_length_df.pivot(index='File_Path', columns='Bond/Angle', values='Mean')
            bond_length_pivot.columns = [f"BondLength_{col}_Mean" for col in bond_length_pivot.columns]
        
        if not bond_angle_df.empty:
            bond_angle_pivot = bond_angle_df.pivot(index='File_Path', columns='Bond/Angle', values='Mean')
            bond_angle_pivot.columns = [f"BondAngle_{col}_Mean" for col in bond_angle_pivot.columns]
        
        # Combine the pivot tables
        if not bond_length_df.empty and not bond_angle_df.empty:
            combined_pivot = pd.concat([bond_length_pivot, bond_angle_pivot], axis=1)
        elif not bond_length_df.empty:
            combined_pivot = bond_length_pivot
        elif not bond_angle_df.empty:
            combined_pivot = bond_angle_pivot
        else:
            combined_pivot = pd.DataFrame()
        
        if not combined_pivot.empty:
            combined_pivot.to_csv(pivot_csv_path)
            print(f"Pivot table CSV saved to: {pivot_csv_path}")
    
    return all_stats, df

# Main execution
if __name__ == "__main__":
    base_directory = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/crystal_parameters_a_b_c"
    
    # Run the aggregation
    all_stats, df = aggregate_statistics(base_directory)
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total files processed: {len(all_stats)}")
    
    if len(df) > 0:
        print("\nBond types found:")
        bond_types = df[df['Type'] == 'Bond Length']['Bond/Angle'].unique()
        print(f"  Bond lengths: {', '.join(bond_types)}")
        
        angle_types = df[df['Type'] == 'Bond Angle']['Bond/Angle'].unique()
        print(f"  Bond angles: {', '.join(angle_types)}")
        
        print("\nOverall statistics:")
        for bond_type in bond_types:
            bond_data = df[(df['Type'] == 'Bond Length') & (df['Bond/Angle'] == bond_type)]
            if not bond_data.empty:
                print(f"  {bond_type}: Mean = {bond_data['Mean'].mean():.3f} ± {bond_data['Mean'].std():.3f} Angstrom")
        
        for angle_type in angle_types:
            angle_data = df[(df['Type'] == 'Bond Angle') & (df['Bond/Angle'] == angle_type)]
            if not angle_data.empty:
                print(f"  {angle_type}: Mean = {angle_data['Mean'].mean():.1f} ± {angle_data['Mean'].std():.1f} degrees")
