from typing import TYPE_CHECKING, List
from .school_artifact import SchoolArtifact

if TYPE_CHECKING:
    from .course import Course

class Teacher(SchoolArtifact):
    def __init__(self, name, courses: List['Course'] = []):
        super().__init__(name)
        self.courses = courses

    def assign_to_course(self, course: 'Course'):
        course.assign_teacher(self)
        self.courses.append(course)

    def create_course(self, course_code: str) -> 'Course':
        from .course import Course  # Local import for runtime use
        new_course = Course(course_code)
        new_course.assign_teacher(self)
        self.courses.append(new_course)
        return new_course