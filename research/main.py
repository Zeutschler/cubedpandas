from code.school_artifact import SchoolArtifact

# Create a student
john = SchoolArtifact.factory("student", "John Doe")

# Create a teacher
jane = SchoolArtifact.factory("teacher", "Jane Smith")

# Create a course
math101 = SchoolArtifact.factory("course", "Math 101")

print(john.display_info())
print(jane.display_info())
print(math101.display_info())