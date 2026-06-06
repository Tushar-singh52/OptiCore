import heapq
from typing import List, Dict, Set, Optional
from backend.models import InputData, Lecture, Room, Section
from backend.graph_builder import ConflictGraph

class TimetableScheduler:
    def __init__(self, data: InputData):
        self.data = data
        self.lectures: List[Lecture] = []
        self.conflict_graph = None
        
        # 4. HASHMAP / DICTIONARY applications
        self.teacher_hours: Dict[str, Dict[int, int]] = {t.id: {d: 0 for d in range(data.numDays)} for t in data.teachers}
        self.teacher_max_hours: Dict[str, int] = {t.id: t.maxHoursPerDay for t in data.teachers}
        self.rooms: Dict[str, Room] = {r.id: r for r in data.rooms}
        self.sections: Dict[str, Section] = {s.id: s for s in data.sections}
        
        # 5. SET application 
        # For O(1) check of occupied slots: "day_slot_EntityID"
        self.occupied_slots: Set[str] = set()

    def generate_lectures(self):
        lecture_idx = 1
        for sec in self.data.sections:
            for sub in self.data.subjects:
                for _ in range(sub.lecturesPerWeek):
                    lec = Lecture(
                        id=f"L{lecture_idx}",
                        subjectId=sub.id,
                        sectionId=sec.id,
                        teacherId=sub.teacherId,
                        isPlacement=sub.isPlacement,
                        strength=sec.strength
                    )
                    self.lectures.append(lec)
                    lecture_idx += 1
                    
        self.conflict_graph = ConflictGraph(self.lectures)

    def _make_key(self, day: int, slot: int, entity_id: str) -> str:
        return f"{day}_{slot}_{entity_id}"

    def is_slot_free(self, day: int, slot: int, entity_id: str) -> bool:
        return self._make_key(day, slot, entity_id) not in self.occupied_slots

    def mark_slot(self, day: int, slot: int, entity_id: str, occupied: bool):
        key = self._make_key(day, slot, entity_id)
        if occupied:
            self.occupied_slots.add(key)
        else:
            self.occupied_slots.discard(key)

    def find_available_room(self, strength: int, day: int, slot: int) -> Optional[str]:
        for room_id, room in self.rooms.items():
            if room.capacity >= strength and self.is_slot_free(day, slot, room_id):
                return room_id
        return None

    def schedule(self) -> List[Lecture]:
        self.generate_lectures()
        
        # 2. HEAP / PRIORITY QUEUE Application
        # Priority rules for min-heap (lower value = higher priority):
        #   - Placement classes (-2)
        #   - Class strength (higher strength = lower negative value)
        priority_queue = []
        for index, lec in enumerate(self.lectures):
            priority_placement = -2 if lec.isPlacement else 0
            priority_strength = -lec.strength
            heapq.heappush(priority_queue, (priority_placement, priority_strength, index, lec))
            
        # 6. LIST / ARRAY
        assigned_lectures = []
        
        # Backtracking/Greedy assignment
        while priority_queue:
            _, _, _, lec = heapq.heappop(priority_queue)
            
            assigned = False
            for d in range(self.data.numDays):
                if assigned: 
                    break
                    
                # Constraint: Teacher daily limit
                if self.teacher_hours.get(lec.teacherId, {}).get(d, 0) >= self.teacher_max_hours.get(lec.teacherId, 99):
                    continue
                    
                for s in range(self.data.numSlotsPerDay):
                    # Constraint: Free slot for teacher and section
                    if self.is_slot_free(d, s, lec.teacherId) and self.is_slot_free(d, s, lec.sectionId):
                        
                        # Graph Constraint Resolution checking
                        conflicts = self.conflict_graph.get_conflicts(lec.id)
                        graph_conflict = False
                        for a_lec in assigned_lectures:
                            if a_lec.id in conflicts and a_lec.day == d and a_lec.timeSlot == s:
                                graph_conflict = True
                                break
                                
                        if not graph_conflict:
                            room_id = self.find_available_room(lec.strength, d, s)
                            if room_id:
                                # Safe Allocation
                                lec.day = d
                                lec.timeSlot = s
                                lec.roomId = room_id
                                
                                self.mark_slot(d, s, lec.teacherId, True)
                                self.mark_slot(d, s, lec.sectionId, True)
                                self.mark_slot(d, s, room_id, True)
                                self.teacher_hours[lec.teacherId][d] += 1
                                
                                assigned_lectures.append(lec)
                                assigned = True
                                break
                                
        return assigned_lectures