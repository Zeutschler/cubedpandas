from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from student import Student
    from teacher import Teacher
    from course import Course

class UserInterface(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

class CourseInterface(ABC):
    @abstractmethod
    def enroll_student(self, student: 'Student') -> None:
        pass

    @abstractmethod
    def assign_teacher(self, teacher: 'Teacher') -> None:
        pass

    def update_course(self, course: 'Course') -> None:
        pass