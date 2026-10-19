
from assihnment import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Student Management API",
    description="A beginner-friendly CRUD API",
    version="1.0.0"
)

# Temporary in-memory storage
students = {}
next_id = 1


# Request body model
class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    age: int = Field(gt=0, le=120)


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = None
    age: int | None = Field(default=None, gt=0, le=120)


# ROUTE 1: Home
@app.get("/")
def home():
    return {"message": "Welcome to the Student API"}


# ROUTE 2: Get all students
@app.get("/students")
def get_students():
    return list(students.values())


# ROUTE 3: Get one student by ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    return students[student_id]


# ROUTE 4: Create a student
@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    global next_id

    student_data = {
        "id": next_id,
        **student.model_dump()
    }

    students[next_id] = student_data
    next_id += 1

    return student_data


# ROUTE 5: Replace/update all supplied student fields
@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentCreate):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    students[student_id] = {
        "id": student_id,
        **student.model_dump()
    }

    return students[student_id]


# ROUTE 6: Partially update a student
@app.patch("/students/{student_id}")
def partial_update_student(
    student_id: int,
    student: StudentUpdate
):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = student.model_dump(exclude_unset=True)
    students[student_id].update(update_data)

    return students[student_id]


# ROUTE 7: Delete a student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    deleted_student = students.pop(student_id)

    return {
        "message": "Student deleted successfully",
        "student": deleted_student
    }