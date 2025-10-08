# Utopia Central School - Foundation Stage Database

## Overview
Complete school data has been successfully seeded for **Utopia Central School - Foundation Stage**.

---

## 📊 Database Summary

### School Information
- **Name**: Utopia Central School
- **Address**: 123 Education Avenue, Delhi, India
- **Email**: info@utopiacentral.edu.in
- **Phone**: +91-11-12345678
- **Principal**: Dr. Rajesh Kumar
- **Total Students**: 875 (35 classes × 25 students)
- **Academic Year**: 2025-2026
- **Subscription Tier**: Premium

---

## 🎓 Foundation Stage Structure

### Grades & Classes
| Grade Level | Code | Full Name | Divisions | Total Classes |
|------------|------|-----------|-----------|---------------|
| LKG | 0 | Lower Kindergarten | A, B, C, D, E, F, G | 7 |
| UKG | 1 | Upper Kindergarten | A, B, C, D, E, F, G | 7 |
| G1 | 2 | Grade 1 | A, B, C, D, E, F, G | 7 |
| G2 | 3 | Grade 2 | A, B, C, D, E, F, G | 7 |
| G3 | 4 | Grade 3 | A, B, C, D, E, F, G | 7 |

**Total Classes**: 35
**Students per Class**: 25

---

## 📚 Subjects

### Core Subjects (6)
| Subject | Code | Periods/Week | Requires Lab |
|---------|------|--------------|--------------|
| English | ENG | 6 | No |
| Mathematics | MATH | 6 | No |
| Environmental Studies | EVS | 5 | No |
| Hindi | HIN | 4 | No |
| General Knowledge | GK | 3 | No |
| Computer Basics | COMP | 2 | Yes |

### Co-curricular Subjects (2)
| Subject | Code | Periods/Week | Requires Lab |
|---------|------|--------------|--------------|
| Art & Craft | ART | 2 | No |
| Physical Education | PE | 2 | No |

**Total Subjects**: 8
**Total Periods per Week per Class**: 30

---

## 👥 Users & Teachers

### Administrative Users
| Role | Name | Email | Password |
|------|------|-------|----------|
| Principal | Dr. Rajesh Kumar | principal@utopiacentral.edu.in | principal123 |
| Vice Principal | Mrs. Sunita Sharma | vp@utopiacentral.edu.in | vp123 |

### Teachers
**Total Teachers**: 40 (All names from indianNames.csv)

#### Teacher Distribution by Subject
| Subject | Teachers | Total Periods/Week | Avg Load per Teacher |
|---------|----------|-------------------|---------------------|
| English | 8 | 210 (35 classes × 6) | 26.25 periods |
| Mathematics | 8 | 210 (35 classes × 6) | 26.25 periods |
| Environmental Studies | 6 | 175 (35 classes × 5) | 29.17 periods |
| Hindi | 5 | 140 (35 classes × 4) | 28.00 periods |
| General Knowledge | 4 | 105 (35 classes × 3) | 26.25 periods |
| Computer Basics | 3 | 70 (35 classes × 2) | 23.33 periods |
| Art & Craft | 3 | 70 (35 classes × 2) | 23.33 periods |
| Physical Education | 3 | 70 (35 classes × 2) | 23.33 periods |

**All teachers use password**: `teacher123`

**Sample Teacher Emails**:
- amira.mirza@utopiacentral.edu.in
- ira.mukherjee@utopiacentral.edu.in
- myra.bose@utopiacentral.edu.in
- rahul.pandey@utopiacentral.edu.in
- anjali.bhattacharya@utopiacentral.edu.in
- simran.kulkarni@utopiacentral.edu.in
- (and 34 more...)

---

## ⏰ Time Slots

### Schedule Structure
- **Days**: Monday to Friday (5 days)
- **Periods per Day**: 6 teaching periods + 2 breaks
- **Total Active Time Slots**: 35 (5 days × 7 periods, excluding breaks)

### Daily Schedule
| Period | Time | Type |
|--------|------|------|
| 1 | 08:30 - 09:15 | Teaching |
| 2 | 09:15 - 10:00 | Teaching |
| 3 | 10:00 - 10:45 | Teaching |
| - | 10:45 - 11:00 | Short Break |
| 4 | 11:00 - 11:45 | Teaching |
| 5 | 11:45 - 12:30 | Teaching |
| - | 12:30 - 13:00 | Lunch Break |
| 6 | 13:00 - 13:45 | Teaching |
| 7 | 13:45 - 14:30 | Teaching |

---

## 🏛️ Rooms & Facilities

**Total Rooms**: 46

### Breakdown
- **Regular Classrooms**: 40 (Room 001 - Room 040)
- **Computer Labs**: 2 (Computer Lab 1, Computer Lab 2)
- **Special Rooms**: 4
  - Art Room
  - Music Room
  - Library (capacity: 50)
  - Activity Hall (capacity: 100)

**Classroom Capacity**: 30 students
**Lab Capacity**: 30 students

---

## 🔐 Login Instructions

### Frontend Access
1. Start all services:
   ```bash
   ./START_ALL_SERVICES.sh   # macOS/Linux
   START_ALL_SERVICES.bat    # Windows
   ```

2. Open browser: http://localhost:3000

3. Login with Principal credentials:
   - **Email**: principal@utopiacentral.edu.in
   - **Password**: principal123

4. Navigate to Admin Dashboard → Timetable Generation

---

## 🎯 Next Steps

### Immediate Actions
1. ✅ **Foundation Stage Complete** - All data seeded
2. 🔄 **Generate Timetables** - Use frontend to create timetables for classes
3. 📊 **View Analytics** - Check teacher workload and class schedules

### Future Expansion
Add more stages to Utopia Central School via frontend:

#### Primary Stage (Grade 4-5)
- 2 grades × 7 divisions = 14 classes
- Expanded subjects (add Social Studies, Science separate from EVS)
- Additional teachers

#### Middle Stage (Grade 6-8)
- 3 grades × 7 divisions = 21 classes
- Subject specialization begins
- Department-wise teachers

#### Senior Stage (Grade 9-12)
- 4 grades × 7 divisions = 28 classes
- Stream-based (Science, Commerce, Arts for 11-12)
- Advanced subjects and electives

**Total School Capacity**: 98 classes (LKG to Grade 12)

---

## 🛠️ Regeneration Script

To regenerate or modify the data, use:

```bash
python3 utopia_school_generator.py
```

**Before regenerating**:
1. Backup database if needed
2. Clear existing Utopia Central School data
3. Run generator script

---

## 📋 Database Statistics

```sql
Schools:        1
Users:          43 (1 Principal + 1 VP + 40 Teachers + 1 Admin)
Teachers:       40
Classes:        35
Subjects:       8
Time Slots:     45 (35 active + 10 breaks)
Rooms:          46
Academic Years: 1
```

---

## 🎓 Educational Philosophy

Utopia Central School follows a comprehensive curriculum for Foundation Stage:

- **Balanced Learning**: Equal emphasis on academics and co-curricular activities
- **Language Development**: Strong focus on English and Hindi
- **Holistic Growth**: Art, Craft, Physical Education integrated into daily schedule
- **Technology Integration**: Early introduction to Computer Basics
- **Environmental Awareness**: EVS and GK for real-world understanding

---

## 📞 Support

For questions or issues:
1. Check backend logs: `logs/backend.log`
2. Check frontend logs: `logs/frontend.log`
3. Verify database integrity: `sqlite3 backend/prisma/dev.db`
4. Consult CLAUDE.md for project documentation

---

**Generated**: October 8, 2025
**Generator Script**: utopia_school_generator.py
**Database**: backend/prisma/dev.db
