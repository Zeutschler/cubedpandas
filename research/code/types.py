from typing import Union
from .student import Student
from .teacher import Teacher
from .course import Course

# Define a type alias for any type of school artifact
SchoolArtifactType = Union[Student, Teacher, Course]