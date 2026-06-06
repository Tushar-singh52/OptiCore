from typing import Dict, Any
from backend.models import InputData, Lecture, SwapRequest
from backend.scheduler import TimetableScheduler
from backend.graph_builder import ConflictGraph

class ConflictResolver:
    def __init__(self, data: InputData, current_timetable: list[Lecture]):
        self.data = data
        self.timetable = current_timetable
        
        self.validator = TimetableScheduler(self.data)
        self.validator.lectures = current_timetable
        self.validator.conflict_graph = ConflictGraph(self.validator.lectures)
        
        # Populate occupied sets based on the existing timetable state
        for lec in self.timetable:
            if lec.day is not None and lec.timeSlot is not None and lec.roomId is not None:
                self.validator.mark_slot(lec.day, lec.timeSlot, lec.roomId, True)
                self.validator.mark_slot(lec.day, lec.timeSlot, lec.teacherId, True)
                self.validator.mark_slot(lec.day, lec.timeSlot, lec.sectionId, True)

    def attempt_swap(self, req: SwapRequest) -> Dict[str, Any]:
        lec_to_move = next((l for l in self.timetable if l.id == req.lectureId), None)
        if not lec_to_move:
            return {"success": False, "message": "Lecture not found"}

        if lec_to_move.isPlacement:
            return {"success": False, "message": "Placement classes cannot be moved manually."}

        dest_lec = next((l for l in self.timetable if l.day == req.newDay and l.timeSlot == req.newSlot and l.roomId == req.newRoomId), None)

        if not dest_lec:
            # Move to Free Slot
            self._unmark(lec_to_move)

            if (self.validator.is_slot_free(req.newDay, req.newSlot, lec_to_move.roomId) and
                self.validator.is_slot_free(req.newDay, req.newSlot, lec_to_move.teacherId) and
                self.validator.is_slot_free(req.newDay, req.newSlot, lec_to_move.sectionId)):

                lec_to_move.day = req.newDay
                lec_to_move.timeSlot = req.newSlot
                lec_to_move.roomId = req.newRoomId
                
                return {"success": True, "timetable": self.timetable, "message": "Slot was free. Class moved successfully."}
            else:
                self._mark(lec_to_move) 
                return {"success": False, "message": "Constraint violation: Teacher or Section already occupied at new time."}

        else:
            # Smart Swap Logic
            if dest_lec.isPlacement:
                return {"success": False, "message": "Target slot contains a Placement class. Cannot be swapped."}
            
            old_day_src, old_slot_src, old_room_src = lec_to_move.day, lec_to_move.timeSlot, lec_to_move.roomId
            old_day_dst, old_slot_dst, old_room_dst = dest_lec.day, dest_lec.timeSlot, dest_lec.roomId
            
            self._unmark(lec_to_move)
            self._unmark(dest_lec)
            
            # Cross-check constraints for swapping
            valid_src_to_dst = (self.validator.is_slot_free(old_day_dst, old_slot_dst, lec_to_move.teacherId) and
                                self.validator.is_slot_free(old_day_dst, old_slot_dst, lec_to_move.sectionId))
            
            valid_dst_to_src = (self.validator.is_slot_free(old_day_src, old_slot_src, dest_lec.teacherId) and
                                self.validator.is_slot_free(old_day_src, old_slot_src, dest_lec.sectionId))
            
            if valid_src_to_dst and valid_dst_to_src:
                lec_to_move.day, lec_to_move.timeSlot, lec_to_move.roomId = old_day_dst, old_slot_dst, old_room_dst
                dest_lec.day, dest_lec.timeSlot, dest_lec.roomId = old_day_src, old_slot_src, old_room_src
                return {"success": True, "timetable": self.timetable, "message": "Smart Swap successful! Constraints validated."}
            else:
                self._mark(lec_to_move)
                self._mark(dest_lec)
                return {"success": False, "message": "Smart Swap failed: Cascade constraint violation."}
                
    def _unmark(self, lec: Lecture):
        if lec.day is not None and lec.timeSlot is not None and lec.roomId is not None:
            self.validator.mark_slot(lec.day, lec.timeSlot, lec.roomId, False)
            self.validator.mark_slot(lec.day, lec.timeSlot, lec.teacherId, False)
            self.validator.mark_slot(lec.day, lec.timeSlot, lec.sectionId, False)
            
    def _mark(self, lec: Lecture):
        if lec.day is not None and lec.timeSlot is not None and lec.roomId is not None:
            self.validator.mark_slot(lec.day, lec.timeSlot, lec.roomId, True)
            self.validator.mark_slot(lec.day, lec.timeSlot, lec.teacherId, True)
            self.validator.mark_slot(lec.day, lec.timeSlot, lec.sectionId, True)