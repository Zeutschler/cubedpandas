from typing import TYPE_CHECKING, List
from .school_artifact import SchoolArtifact

if TYPE_CHECKING:
    from student import Student
    from teacher import Teacher

class Course(SchoolArtifact):
    def __init__(self, name):
        super().__init__(name)
        self.students: List['Student'] = []
        self.teacher: 'Teacher' = None

    def enroll_student(self, student: 'Student'):
        self.students.append(student)

    def assign_teacher(self, teacher: 'Teacher'):
        self.teacher = teacher