#!/usr/bin/env python3
import sys
import os
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import and run
from data_generator import TimetableDataGenerator

if __name__ == "__main__":
    generator = TimetableDataGenerator("large")
    data = generator.generate_all_data()

    # Save to CSV files
    generator.save_data(data)

    print(f"\nGenerated large school data: {generator.tt_id}")
    print(f"  Classes: {len(data['classes'])}")
    print(f"  Teachers: {len(data['teachers'])}")
    print(f"  Assignments: {len(data['assignments'])}")
    print(f"  Total periods: {len(data['classes']) * 40}")
