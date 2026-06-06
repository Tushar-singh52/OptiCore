from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ==========================================
# 1. Core Data Models (Lists/Arrays used)
# ==========================================

class Teacher(BaseModel):
    id: str
    name: str
    maxHoursPerDay: int

class Room(BaseModel):
    id: str
    name: str
    capacity: int

class Section(BaseModel):
    id: str
    name: str
    department: str
    year: int
    strength: int

class Subject(BaseModel):
    id: str
    name: str
    teacherId: str
    lecturesPerWeek: int
    isPlacement: bool = False

class Lecture(BaseModel):
    id: str
    subjectId: str
    sectionId: str
    teacherId: str
    isPlacement: bool
    strength: int

    # Assigned values
    roomId: Optional[str] = None
    day: Optional[int] = None
    timeSlot: Optional[int] = None

class InputData(BaseModel):
    teachers: List[Teacher]
    rooms: List[Room]
    sections: List[Section]
    subjects: List[Subject]
    numDays: Optional[int] = 5
    numSlotsPerDay: Optional[int] = 8

class SwapRequest(BaseModel):
    lectureId: str
    newDay: int
    newSlot: int
    newRoomId: str
    
    # Passing the whole timetable state to resolve swaps statelessly
    currentTimetable: List[Lecture]
    inputData: InputData

# 2. Tree Hierarchy Model
# Structured purely using Python Dicts representing Maps
# College -> Dept -> Year -> Section -> Subjects

class AcademicTree:
    def __init__(self):
        # A deeply nested dictionary acting as the Tree structure
        self.college = {}

    def insert_section(self, section: Section, subjects: List[Subject]):
        dept = section.department
        year = section.year
        
        if dept not in self.college:
            self.college[dept] = {}
            
        if year not in self.college[dept]:
            self.college[dept][year] = {}
            
        self.college[dept][year][section.id] = {
            "section_details": section,
            "subjects": [s for s in subjects if s.id in ["DSA", "OS", "PLAC"]] # Simplified association
        }

    def get_all_sections(self):
        """Tree traversal to get sections"""
        sections = []
        for dept_v in self.college.values():
            for year_v in dept_v.values():
                for sec_k, sec_v in year_v.items():
                    sections.append(sec_v["section_details"])
        return sections