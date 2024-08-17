from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .student import Student
    from .teacher import Teacher
    from .course import Course

class SchoolArtifact:
    artifact_count = 0

    def __init__(self, name: str):
        self.name = name
        SchoolArtifact.artifact_count += 1
        self.id = SchoolArtifact.artifact_count

    def display_info(self) -> str:
        return f"Artifact ID: {self.id}, Name: {self.name}"

    @staticmethod
    def factory(artifact_type: str, name: str, *args: Any) -> 'SchoolArtifact':
        if artifact_type == "student":
            from .student import Student
            return Student(name, *args)
        elif artifact_type == "teacher":
            from .teacher import Teacher
            return Teacher(name, *args)
        elif artifact_type == "course":
            from .course import Course
            return Course(name)
        else:
            raise ValueError("Unknown artifact type")