# 📊 Test Data Generator Guide

A comprehensive guide to generating test data and creating timetables using the tt_tester toolkit.

## 🎯 Overview

The tt_tester provides a complete suite of tools for generating realistic school timetable data, creating interactive viewers, and testing timetable algorithms with various constraints and scenarios.

## 🚀 Quick Start

### 1. Generate Basic Test Data
```bash
cd tt_tester
python3 generate_30class_test.py
```

This creates:
- `test_data_classes.csv` - 30 classes across grades 6-12
- `test_data_teachers.csv` - 121 teachers (max 2 subjects each)
- `test_data_rooms.csv` - 35 rooms (25 classrooms + 10 labs)
- `test_data_assignments.csv` - 210 teacher-subject-class assignments
- `test_data_subjects.csv` - Subject definitions

### 2. Create Interactive Viewer
```bash
python3 enhanced_interactive_viewer.py
```

Opens an HTML viewer with teacher details and class information.

## 📋 Available Generators

### 🏫 School Size Generators

#### Small School (14 Classes)
```bash
python3 generate_14_classes.py
```
- **Classes**: 14
- **Teachers**: ~35
- **Use Case**: Small private schools, testing basic algorithms

#### Medium School (30 Classes) - **Recommended**
```bash
python3 generate_30class_test.py
```
- **Classes**: 30
- **Teachers**: 121 (optimized with 2-subject constraint)
- **Use Case**: Standard public schools, comprehensive testing

#### Large School (50+ Classes)
```bash
python3 generate_large_school_timetable.py
```
- **Classes**: 50+
- **Teachers**: 200+
- **Use Case**: Large institutions, performance testing

### 🎛️ Specialized Generators

#### Realistic Timetable Generator
```bash
python3 generate_real_timetable.py
```
- Uses actual teacher assignments
- Respects subject constraints
- Creates realistic scheduling patterns

#### Demo Data Generator
```bash
python3 demo_30class_output.py
```
- Quick mock data for presentations
- Simplified constraints
- Fast generation

## 🔧 Configuration Options

### Teacher Constraints

#### 2-Subject Maximum (Default)
```python
# In generate_30class_test.py
BASE_TEACHERS = 105  # Each handles 2 assignments
SUBSTITUTE_TEACHERS = 16  # 15% buffer
```

#### Custom Subject Distribution
```python
# Modify in generator files
teacher["subjects_qualified"] = random.sample(available_subjects, 2)
```

### Class Configuration

#### Grade Distribution
```python
GRADES = ["6", "7", "8", "9", "10", "11", "12"]
classes_per_grade = NUM_CLASSES // len(GRADES)
```

#### Subject Selection
```python
SUBJECTS_PER_CLASS = 7  # Random selection from 10 available
selected_subjects = random.sample(SUBJECTS, SUBJECTS_PER_CLASS)
```

### Room Types

#### Classroom vs Lab Ratio
```python
# 25 regular classrooms
for i in range(1, 26):
    rooms.append({"type": "classroom"})

# 10 specialized labs
lab_types = ["Science Lab", "Computer Lab", "Physics Lab", ...]
```

## 📊 Data Analysis Tools

### Teacher Subject Analysis
```bash
python3 analyze_teacher_subjects.py
```

**Output:**
```
=== TEACHER SUBJECT ANALYSIS ===
Total teachers: 121
Max subjects per teacher: 2
Constraint satisfied: ✓ YES

=== SUBJECT COUNT DISTRIBUTION ===
1 subjects: 13 teachers (10.7%)
2 subjects: 108 teachers (89.3%)
```

### Timetable Statistics
```bash
python3 generate_real_timetable.py
```

**Output:**
```
📊 Statistics:
   Total entries: 1200
   Teaching periods: 831
   Free periods: 369
   Utilization: 69.2%
```

## 🌐 Interactive Viewers

### Enhanced Viewer (Recommended)
```bash
python3 enhanced_interactive_viewer.py
```

**Features:**
- Teacher details panel with contact info
- Class-teacher mapping table
- Dual view modes (Class/Teacher)
- Mobile responsive design

### Advanced Viewer
```bash
python3 advanced_timetable_viewer.py
```

**Features:**
- Professional sidebar navigation
- Statistics dashboard
- Gradient design
- Export capabilities

### CSV Viewer
```bash
python3 csv_timetable_viewer.py
```

**Features:**
- Basic dropdown selection
- Simple table display
- Fast loading

## 🧪 Testing Scenarios

### Constraint Testing

#### Teacher Subject Limits
```bash
# Generate data with 2-subject constraint
python3 generate_30class_test.py

# Verify constraint compliance
python3 analyze_teacher_subjects.py
```

#### Room Utilization
```bash
# Check lab vs classroom usage
grep "needs_lab.*true" test_data_assignments.csv | wc -l
```

#### Period Distribution
```bash
# Analyze periods per subject
cut -d',' -f7 test_data_assignments.csv | sort | uniq -c
```

### Performance Testing

#### Large Dataset Generation
```bash
# Modify NUM_CLASSES in generator
NUM_CLASSES = 100
python3 generate_30class_test.py
```

#### Memory Usage Testing
```bash
# Monitor during generation
python3 -m memory_profiler generate_30class_test.py
```

## 📁 File Structure

### Generated Data Files
```
tt_tester/
├── test_data_classes.csv      # Class definitions
├── test_data_teachers.csv     # Teacher profiles
├── test_data_rooms.csv        # Room inventory
├── test_data_assignments.csv  # Teacher-subject mappings
├── test_data_subjects.csv     # Subject definitions
└── realistic_timetable_*.csv  # Complete timetables
```

### Generated Viewers
```
tt_tester/
├── enhanced_timetable_viewer_*.html    # Enhanced interactive
├── advanced_timetable_viewer_*.html    # Professional design
├── demo_timetable_*.html               # Basic viewers
└── *_viewer_*.html                     # Various formats
```

## 🎨 Customization Guide

### Adding New Subjects
```python
# In generate_30class_test.py
SUBJECTS = [
    {"name": "Your Subject", "code": "YS", "needs_lab": False, "periods_per_week": 4},
    # ... existing subjects
]
```

### Custom Teacher Names
```python
# Modify name lists in generators
first_names = ["Custom", "Names", "Here"]
last_names = ["Custom", "Surnames", "Here"]
```

### Room Specializations
```python
# Add new lab types
lab_types = ["Your Lab", "Custom Room", "Special Space"]
```

## 🔍 Troubleshooting

### Common Issues

#### Missing CSV Files
```bash
# Regenerate base data
python3 generate_30class_test.py
```

#### Constraint Violations
```bash
# Check teacher subject distribution
python3 analyze_teacher_subjects.py
```

#### Viewer Not Loading
```bash
# Check file paths in HTML
# Ensure CSV files exist in same directory
```

### Debug Mode
```python
# Add to any generator
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Best Practices

### 1. **Start Small**
- Use 14-class generator for initial testing
- Scale up to 30-class for full testing
- Use large generators only for performance testing

### 2. **Validate Constraints**
- Always run `analyze_teacher_subjects.py` after generation
- Check utilization rates in output
- Verify room assignments match subject requirements

### 3. **Version Control**
- Keep generated data files in git
- Tag successful configurations
- Document custom modifications

### 4. **Performance Monitoring**
- Time generation processes
- Monitor memory usage with large datasets
- Profile viewer loading times

## 🎯 Use Cases

### Development Testing
```bash
# Quick iteration cycle
python3 generate_30class_test.py
python3 enhanced_interactive_viewer.py
# Test changes, repeat
```

### Demo Preparation
```bash
# Create presentation-ready data
python3 demo_30class_output.py
python3 advanced_timetable_viewer.py
```

### Algorithm Validation
```bash
# Generate test cases
python3 generate_real_timetable.py
# Run your algorithm
# Compare results
```

### Stress Testing
```bash
# Large dataset
python3 generate_large_school_timetable.py
# Monitor performance
```

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review generator source code
3. Run analysis tools for debugging
4. Check file permissions and paths

---

**Happy Testing!** 🎉

The tt_tester toolkit provides everything needed for comprehensive timetable testing and development.