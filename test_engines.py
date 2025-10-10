#!/usr/bin/env python3

import json
import requests
import time
import sys
import subprocess
import signal
import os
from typing import Dict, Any, Optional

class TimetableEngineTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.current_process = None
        
    def stop_current_engine(self):
        """Stop the currently running engine"""
        try:
            # Kill any Python process on port 8000
            result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(['kill', pid], check=True)
                time.sleep(2)
                print(f"Stopped engine with PID {pid}")
        except subprocess.CalledProcessError:
            pass  # No process running
    
    def start_engine(self, version: str) -> bool:
        """Start a specific engine version"""
        self.stop_current_engine()
        
        engine_files = {
            "v2.5": "main_v25.py",
            "v3.0": "main_v30.py", 
            "v3.0.1": "main_v301.py"
        }
        
        if version not in engine_files:
            print(f"Unknown engine version: {version}")
            return False
            
        engine_file = engine_files[version]
        engine_path = f"timetable-engine/{engine_file}"
        
        if not os.path.exists(engine_path):
            print(f"Engine file not found: {engine_path}")
            return False
            
        print(f"Starting {version} engine ({engine_file})...")
        
        try:
            # Start the engine in background
            self.current_process = subprocess.Popen([
                sys.executable, engine_path
            ], cwd=os.getcwd(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for engine to start
            time.sleep(5)
            
            # Test if engine is responding
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ {version} engine started successfully")
                return True
            else:
                print(f"❌ {version} engine health check failed")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start {version} engine: {e}")
            return False
    
    def get_test_data(self) -> Dict[str, Any]:
        """Get the test data from the frontend generation attempt"""
        return {
            "school_id": "default-school-id",
            "classes": [
                {"id": "cmgj2p4qb00c613dgn2ddpopx", "name": "Grade 6A", "grade": 6, "section": "A", "student_count": 35},
                {"id": "cmgj2p4qc00c813dg17lg6njz", "name": "Grade 6B", "grade": 6, "section": "B", "student_count": 26},
                {"id": "cmgj2p4qe00ca13dgxwg1vfn5", "name": "Grade 6C", "grade": 6, "section": "C", "student_count": 25},
                {"id": "cmgj2p4qg00cc13dgrjl2bd96", "name": "Grade 7A", "grade": 7, "section": "A", "student_count": 29},
                {"id": "cmgj2p4qh00ce13dgeg30xvev", "name": "Grade 7B", "grade": 7, "section": "B", "student_count": 28},
                {"id": "cmgj2p4qj00cg13dg3cce3l06", "name": "Grade 7C", "grade": 7, "section": "C", "student_count": 28},
                {"id": "cmgj2p4qk00ci13dgktgqke4z", "name": "Grade 8A", "grade": 8, "section": "A", "student_count": 27},
                {"id": "cmgj2p4qm00ck13dgcq2gspjc", "name": "Grade 8B", "grade": 8, "section": "B", "student_count": 26},
                {"id": "cmgj2p4qn00cm13dg5hdb9fek", "name": "Grade 8C", "grade": 8, "section": "C", "student_count": 35},
                {"id": "cmgj2p4qp00co13dg8jisph90", "name": "Grade 9A", "grade": 9, "section": "A", "student_count": 33},
                {"id": "cmgj2p4qq00cq13dgv41ti5se", "name": "Grade 9B", "grade": 9, "section": "B", "student_count": 26},
                {"id": "cmgj2p4qr00cs13dg34zrdir2", "name": "Grade 9C", "grade": 9, "section": "C", "student_count": 34},
                {"id": "cmgj2p4qt00cu13dgyrnsv12l", "name": "Grade 10A", "grade": 10, "section": "A", "student_count": 31},
                {"id": "cmgj2p4qu00cw13dg7ilan6im", "name": "Grade 10B", "grade": 10, "section": "B", "student_count": 25}
            ],
            "subjects": [
                {"id": "cmgj2p4ic005813dgl27wchrs", "name": "Mathematics", "code": "Mathematics", "periods_per_week": 6, "requires_lab": False},
                {"id": "cmgj2p4ik005a13dgqw29muey", "name": "English", "code": "English", "periods_per_week": 5, "requires_lab": False},
                {"id": "cmgj2p4im005c13dghtcs7gyo", "name": "Science", "code": "Science", "periods_per_week": 6, "requires_lab": True},
                {"id": "cmgj2p4ip005e13dg21myc1wl", "name": "Social Studies", "code": "Social Studies", "periods_per_week": 4, "requires_lab": False},
                {"id": "cmgj2p4ir005g13dgcm9mg5ud", "name": "Computer Science", "code": "Computer Science", "periods_per_week": 4, "requires_lab": True},
                {"id": "cmgj2p4it005i13dgv4v6v5de", "name": "Physical Education", "code": "Physical Education", "periods_per_week": 3, "requires_lab": False},
                {"id": "cmgj2p4iv005k13dg0vitayu8", "name": "Art", "code": "Art", "periods_per_week": 3, "requires_lab": False},
                {"id": "cmgj2p4ix005m13dg5f6auj0m", "name": "Music", "code": "Music", "periods_per_week": 2, "requires_lab": False},
                {"id": "cmgj2p4iz005o13dggs0zzx1c", "name": "Hindi", "code": "Hindi", "periods_per_week": 4, "requires_lab": False},
                {"id": "cmgj2p4j1005q13dgrsf2u60z", "name": "French", "code": "French", "periods_per_week": 3, "requires_lab": False}
            ],
            "time_slots": [
                {"day": "MONDAY", "start_time": "09:00", "end_time": "09:45"},
                {"day": "MONDAY", "start_time": "09:45", "end_time": "10:30"},
                {"day": "MONDAY", "start_time": "10:30", "end_time": "11:15"},
                {"day": "MONDAY", "start_time": "11:15", "end_time": "12:00"},
                {"day": "MONDAY", "start_time": "12:00", "end_time": "12:45"},
                {"day": "MONDAY", "start_time": "12:45", "end_time": "13:30"},
                {"day": "MONDAY", "start_time": "13:30", "end_time": "14:15"},
                {"day": "MONDAY", "start_time": "14:15", "end_time": "15:00"},
                {"day": "TUESDAY", "start_time": "09:00", "end_time": "09:45"},
                {"day": "TUESDAY", "start_time": "09:45", "end_time": "10:30"},
                {"day": "TUESDAY", "start_time": "10:30", "end_time": "11:15"},
                {"day": "TUESDAY", "start_time": "11:15", "end_time": "12:00"},
                {"day": "TUESDAY", "start_time": "12:00", "end_time": "12:45"},
                {"day": "TUESDAY", "start_time": "12:45", "end_time": "13:30"},
                {"day": "TUESDAY", "start_time": "13:30", "end_time": "14:15"},
                {"day": "TUESDAY", "start_time": "14:15", "end_time": "15:00"},
                {"day": "WEDNESDAY", "start_time": "09:00", "end_time": "09:45"},
                {"day": "WEDNESDAY", "start_time": "09:45", "end_time": "10:30"},
                {"day": "WEDNESDAY", "start_time": "10:30", "end_time": "11:15"},
                {"day": "WEDNESDAY", "start_time": "11:15", "end_time": "12:00"},
                {"day": "WEDNESDAY", "start_time": "12:00", "end_time": "12:45"},
                {"day": "WEDNESDAY", "start_time": "12:45", "end_time": "13:30"},
                {"day": "WEDNESDAY", "start_time": "13:30", "end_time": "14:15"},
                {"day": "WEDNESDAY", "start_time": "14:15", "end_time": "15:00"},
                {"day": "THURSDAY", "start_time": "09:00", "end_time": "09:45"},
                {"day": "THURSDAY", "start_time": "09:45", "end_time": "10:30"},
                {"day": "THURSDAY", "start_time": "10:30", "end_time": "11:15"},
                {"day": "THURSDAY", "start_time": "11:15", "end_time": "12:00"},
                {"day": "THURSDAY", "start_time": "12:00", "end_time": "12:45"},
                {"day": "THURSDAY", "start_time": "12:45", "end_time": "13:30"},
                {"day": "THURSDAY", "start_time": "13:30", "end_time": "14:15"},
                {"day": "THURSDAY", "start_time": "14:15", "end_time": "15:00"},
                {"day": "FRIDAY", "start_time": "09:00", "end_time": "09:45"},
                {"day": "FRIDAY", "start_time": "09:45", "end_time": "10:30"},
                {"day": "FRIDAY", "start_time": "10:30", "end_time": "11:15"},
                {"day": "FRIDAY", "start_time": "11:15", "end_time": "12:00"},
                {"day": "FRIDAY", "start_time": "12:00", "end_time": "12:45"},
                {"day": "FRIDAY", "start_time": "12:45", "end_time": "13:30"},
                {"day": "FRIDAY", "start_time": "13:30", "end_time": "14:15"},
                {"day": "FRIDAY", "start_time": "14:15", "end_time": "15:00"}
            ],
            "rooms": [
                {"id": "cmgj2p4jl005s13dgdpmc5w22", "name": "Classroom 1", "type": "CLASSROOM", "capacity": 30},
                {"id": "cmgj2p4jn005u13dgy0ldwl93", "name": "Classroom 2", "type": "CLASSROOM", "capacity": 33},
                {"id": "cmgj2p4jp005w13dgrkum4blp", "name": "Classroom 3", "type": "CLASSROOM", "capacity": 38},
                {"id": "cmgj2p4jr005y13dg9qouu92y", "name": "Classroom 4", "type": "CLASSROOM", "capacity": 38},
                {"id": "cmgj2p4ju006013dgivoy4xo5", "name": "Classroom 5", "type": "CLASSROOM", "capacity": 40},
                {"id": "cmgj2p4jv006213dgcpkuaury", "name": "Classroom 6", "type": "CLASSROOM", "capacity": 33},
                {"id": "cmgj2p4jx006413dgbzrxyh9w", "name": "Classroom 7", "type": "CLASSROOM", "capacity": 39},
                {"id": "cmgj2p4jz006613dgl3top5ne", "name": "Classroom 8", "type": "CLASSROOM", "capacity": 30},
                {"id": "cmgj2p4k0006813dgi2s3g83d", "name": "Classroom 9", "type": "CLASSROOM", "capacity": 36},
                {"id": "cmgj2p4k2006a13dgqng0uxcy", "name": "Classroom 10", "type": "CLASSROOM", "capacity": 34},
                {"id": "cmgj2p4k3006c13dgf0ljyj3f", "name": "Classroom 11", "type": "CLASSROOM", "capacity": 33},
                {"id": "cmgj2p4k5006e13dgqh69g7mb", "name": "Classroom 12", "type": "CLASSROOM", "capacity": 31},
                {"id": "cmgj2p4k7006g13dgj24wmxim", "name": "Classroom 13", "type": "CLASSROOM", "capacity": 36},
                {"id": "cmgj2p4k9006i13dgofgl92mh", "name": "Classroom 14", "type": "CLASSROOM", "capacity": 35},
                {"id": "cmgj2p4kb006k13dgmhv1weij", "name": "Classroom 15", "type": "CLASSROOM", "capacity": 39},
                {"id": "cmgj2p4ke006m13dggwuj6obi", "name": "Science Lab 1", "type": "LAB", "capacity": 21},
                {"id": "cmgj2p4kg006o13dg3dkfkl81", "name": "Computer Lab 2", "type": "LAB", "capacity": 34},
                {"id": "cmgj2p4ki006q13dgwjlgzeoz", "name": "Physics Lab 3", "type": "LAB", "capacity": 23},
                {"id": "cmgj2p4kk006s13dg3ec372gp", "name": "Chemistry Lab 4", "type": "LAB", "capacity": 32},
                {"id": "cmgj2p4km006u13dg6klybm90", "name": "Biology Lab 5", "type": "LAB", "capacity": 22},
                {"id": "cmgj77p8r0001jig45g18q9le", "name": "Sci Lab", "type": "LAB", "capacity": 30},
                {"id": "cmgj78je50003jig460i6j96f", "name": "SCL 2", "type": "LAB", "capacity": 30},
                {"id": "cmgj79tm40005jig41oiu3zyr", "name": "SCL1", "type": "LAB", "capacity": 30},
                {"id": "cmgj82yxj000bjig4icpqvz5x", "name": "CS L1", "type": "LAB", "capacity": 30},
                {"id": "cmgj83c2f000djig4kxz1oesj", "name": "CS l2", "type": "LAB", "capacity": 30},
                {"id": "cmgj83n1d000fjig461qbxco3", "name": "SCL 1", "type": "LAB", "capacity": 30},
                {"id": "cmgj83xmr000hjig4cj33s5r0", "name": "SCIENCE", "type": "LAB", "capacity": 30},
                {"id": "cmgj84muq000jjig4l5w23sho", "name": "SCL1", "type": "LAB", "capacity": 30},
                {"id": "cmgj85lrp000ljig4nb9es62r", "name": "sc1", "type": "LAB", "capacity": 30}
            ],
            "teachers": [
                {"id": "cmgj2p4l1006y13dgp5vcaste", "name": "dorothy.torres@school.edu", "subjects": ["Hindi", "Mathematics"], "max_periods_per_day": 6, "max_periods_per_week": 30},
                {"id": "cmgj2p4l6007213dge4w4ry76", "name": "joshua.clark@school.edu", "subjects": ["French", "Mathematics"], "max_periods_per_day": 6, "max_periods_per_week": 30}
                # Note: Truncated for brevity - include first few teachers only
            ]
        }
    
    def test_generation(self, version: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test timetable generation with specific engine version"""
        print(f"\n🧪 Testing {version} engine...")
        
        try:
            response = requests.post(f"{self.base_url}/generate", json=data, timeout=30)
            
            result = {
                "version": version,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            
            if result["success"]:
                print(f"✅ {version}: Generation successful")
                if "diagnostics" in result["response"]:
                    diag = result["response"]["diagnostics"]
                    print(f"   📊 Total entries: {diag.get('total_entries', 'N/A')}")
                    print(f"   ⚠️  Issues: {len(diag.get('issues', []))}")
                    print(f"   💡 Suggestions: {len(diag.get('suggestions', []))}")
            else:
                print(f"❌ {version}: Generation failed")
                print(f"   Status: {result['status_code']}")
                print(f"   Error: {result['response'][:200]}...")
                
        except Exception as e:
            print(f"❌ {version}: Exception during testing: {e}")
            result = {
                "version": version,
                "status_code": None,
                "success": False,
                "response": str(e)
            }
        
        return result
    
    def cleanup(self):
        """Clean up processes"""
        self.stop_current_engine()

def main():
    tester = TimetableEngineTest()
    
    try:
        # Test data
        test_data = tester.get_test_data()
        
        # Versions to test
        versions = ["v3.0.1", "v3.0", "v2.5"]
        results = []
        
        for version in versions:
            if tester.start_engine(version):
                result = tester.test_generation(version, test_data)
                results.append(result)
            else:
                print(f"❌ Failed to start {version} engine, skipping...")
                results.append({
                    "version": version,
                    "success": False,
                    "response": "Failed to start engine"
                })
                
        # Summary
        print(f"\n{'='*60}")
        print("TIMETABLE ENGINE COMPARISON RESULTS")
        print(f"{'='*60}")
        
        for result in results:
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            print(f"{result['version']:>10}: {status}")
            
        print(f"{'='*60}")
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()