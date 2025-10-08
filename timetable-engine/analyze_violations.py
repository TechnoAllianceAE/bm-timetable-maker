"""Analyze violation CSV files and provide detailed insights"""
import csv
import sys
from collections import defaultdict

def analyze_violations(filename):
    """Analyze a violations CSV file"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {filename}")
    print(f"{'='*80}\n")
    
    violations_by_category = defaultdict(list)
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category'] == 'NONE':
                print("✅ NO VIOLATIONS - All checks passed!\n")
                return
            violations_by_category[row['Category']].append(row)
    
    total = sum(len(v) for v in violations_by_category.values())
    print(f"Total Violations: {total}\n")
    
    for category, items in sorted(violations_by_category.items()):
        print(f"\n{category.upper().replace('_', ' ')} ({len(items)} violations):")
        print("-" * 80)
        
        if category == 'gaps':
            for item in items:
                print(f"  ❌ {item['Details']}")
        
        elif category == 'teacher_subject_uniqueness':
            for item in items:
                print(f"  ❌ {item['Details']}")
        
        elif category == 'subject_requirements':
            # Group by over/under
            over = [i for i in items if 'difference=' in i['Details'] and int(i['Details'].split('difference=')[1].split(',')[0]) > 0]
            under = [i for i in items if 'difference=' in i['Details'] and int(i['Details'].split('difference=')[1].split(',')[0]) < 0]
            
            if over:
                print(f"\n  📈 OVER-ALLOCATED ({len(over)} cases):")
                for item in over[:10]:  # Show first 10
                    print(f"     {item['Details']}")
                if len(over) > 10:
                    print(f"     ... and {len(over)-10} more")
            
            if under:
                print(f"\n  📉 UNDER-ALLOCATED ({len(under)} cases):")
                for item in under[:10]:
                    print(f"     {item['Details']}")
                if len(under) > 10:
                    print(f"     ... and {len(under)-10} more")
        
        else:
            for item in items[:5]:
                print(f"  ❌ {item['Details']}")
            if len(items) > 5:
                print(f"  ... and {len(items)-5} more")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("DETAILED VIOLATION ANALYSIS")
    print("="*80)
    
    # Find all violation CSV files
    import glob
    violation_files = sorted(glob.glob("temp_test_*_violations.csv"))
    
    if not violation_files:
        print("\n❌ No violation files found")
        sys.exit(1)
    
    for vfile in violation_files:
        analyze_violations(vfile)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")
