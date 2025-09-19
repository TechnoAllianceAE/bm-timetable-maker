# 🧪 Timetable Tester & Mock Data

**Consolidated testing framework with reusable tools for timetable generation and visualization.**

## 🎯 Core Tools (Reusable)

### 🔧 **Data Generator** - `data_generator.py`
**Universal data generator supporting multiple school configurations**
```bash
python3 data_generator.py --config medium    # 30 classes (default)
python3 data_generator.py --config small     # 14 classes  
python3 data_generator.py --config large     # 50 classes
```

**Features:**
- **Complete schedule generation** - All classes get exactly 40 periods
- **Teacher constraint optimization** - Maximum 2 subjects per teacher
- **Unique TT Generation IDs** - Full traceability
- **Multiple school sizes** - Small, medium, large configurations
- **Realistic data** - Proper grade distribution, room allocation

### 🌐 **Universal Viewer** - `timetable_viewer.py`
**Single viewer for all timetable data sources**
```bash
python3 timetable_viewer.py <TT_ID>         # View specific generation
python3 timetable_viewer.py latest          # View latest generation
python3 timetable_viewer.py legacy          # View legacy test data
```

**Features:**
- **Auto-detection** of data files by TT ID
- **Schedule validation** with visual highlighting
- **Teacher information panels** with contact details and subjects
- **Class-teacher mapping** tables
- **Mobile responsive** professional design
- **Real-time schedule validation**

### 📊 **Generation Tracker** - `tt_generation_tracker.py`
**Management system for all TT generations**
```bash
python3 tt_generation_tracker.py list       # List all generations
python3 tt_generation_tracker.py latest     # Show latest valid generation
python3 tt_generation_tracker.py cleanup 3  # Keep only 3 recent
python3 tt_generation_tracker.py report     # Create HTML report
```

### 🔍 **Analysis Tool** - `analyze_teacher_subjects.py`
**Validate teacher constraint compliance**
```bash
python3 analyze_teacher_subjects.py
```

## 📊 Legacy Test Data (Stable)
- `test_data_classes.csv` - 30 classes across grades 6-12
- `test_data_teachers.csv` - 121 teachers (max 2 subjects each)
- `test_data_rooms.csv` - 35 rooms (25 classrooms + 10 labs)
- `test_data_assignments.csv` - 210 teacher-subject-class assignments
- `test_data_subjects.csv` - Subject definitions and requirements

## 🆔 TT Generation System

### Generation ID Format
```
TT_YYYYMMDD_HHMMSS_<8-char-uuid>
Example: TT_20250919_120829_4c651766
```

### Generated Files per TT ID
```
data_classes_TT_20250919_120829_4c651766.csv      # Class data
data_teachers_TT_20250919_120829_4c651766.csv     # Teacher data  
data_rooms_TT_20250919_120829_4c651766.csv        # Room data
data_assignments_TT_20250919_120829_4c651766.csv  # Assignment data
data_subjects_TT_20250919_120829_4c651766.csv     # Subject data
metadata_TT_20250919_120829_4c651766.json         # Generation metadata
timetable_viewer_TT_20250919_120829_4c651766_*.html  # Interactive viewer
```

## 🚀 Quick Start

### Generate New Test Data
```bash
cd tt_tester
python3 generate_30class_test.py
```

### View Interactive Timetable
```bash
python3 advanced_timetable_viewer.py
# Open the generated HTML file in browser
```

### Analyze Teacher Distribution
```bash
python3 analyze_teacher_subjects.py
```

### Run Tests
```bash
cd tests
python3 -m pytest
```

## 📊 Key Features Tested

### ✅ Teacher Optimization
- Maximum 2 subjects per teacher constraint
- 121 teachers handling 210 assignments
- 15% substitution buffer

### ✅ Complete School Coverage
- 30 classes across all grades
- 1,200 total period assignments
- 69.2% optimal utilization

### ✅ Interactive Presentations
- Professional HTML viewers
- Real-time statistics
- Mobile responsive design
- Multiple viewing modes

## 🎯 Use Cases

1. **Development Testing** - Test new features with realistic data
2. **Performance Testing** - Benchmark with large datasets
3. **UI Testing** - Validate viewers and interfaces
4. **Constraint Validation** - Verify optimization rules
5. **Demo Presentations** - Show system capabilities

---

All files in this folder are for testing and demonstration purposes. The main timetable engine remains in the `timetable-engine/` directory.