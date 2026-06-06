from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import InputData, SwapRequest
from backend.scheduler import TimetableScheduler
from backend.conflict_resolver import ConflictResolver
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_generated_timetable = []

@app.post("/generate-timetable")
async def generate_timetable(data: InputData):
    global latest_generated_timetable
    try:
        scheduler = TimetableScheduler(data)
        timetable = scheduler.schedule()
        
        assigned_lectures = [lec.model_dump() for lec in timetable if lec.day is not None]
        errors = [f"Could not schedule lecture {l.id} ({l.subjectId})" for l in timetable if l.day is None]
        
        latest_generated_timetable = assigned_lectures
        return {
            "assignedLectures": assigned_lectures,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/edit-slot")
async def edit_slot(req: SwapRequest):
    try:
        resolver = ConflictResolver(req.inputData, req.currentTimetable)
        res = resolver.attempt_swap(req)
        
        if res["success"]:
            return {
                "message": res["message"], 
                "assignedLectures": [lec.model_dump() for lec in res["timetable"]]
            }
        else:
            raise HTTPException(status_code=400, detail=res["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-timetable")
async def get_timetable():
    day_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday"}
    time_map = {0: "8 AM", 1: "9 AM", 2: "10 AM", 3: "11 AM", 4: "1 PM", 5: "2 PM", 6: "3 PM", 7: "4 PM"}
    
    formatted = []
    for lec in latest_generated_timetable:
        formatted.append({
            "day": day_map.get(lec["day"], "Unknown"),
            "time": time_map.get(lec["timeSlot"], "Unknown"),
            "subject": lec["subjectId"],
            "teacher": lec["teacherId"],
            "room": lec["roomId"]
        })
    return {"timetable": formatted}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)