from typing import TYPE_CHECKING, List
from .school_artifact import SchoolArtifact

if TYPE_CHECKING:
    from .course import Course


class Student(SchoolArtifact):
    def __init__(self, name, courses: List['Course'] = []):
        super().__init__(name)
        self.courses = courses

    def enroll_in_course(self, course: 'Course'):
        course.enroll_student(self)
        self.courses.append(course)

