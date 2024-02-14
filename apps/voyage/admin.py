"""
Admin panel configuration for the Voyage app.
"""
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from django.db.models import Avg, Count
from .models import (
    Faculty,
    Content,
    Program,
    Course,
    Student,
    Assignment,
    StudentAssignment,
)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Faculty model.
    """

    list_display = (
        "user",
        "github",
        "is_active",
        "num_courses_taught",
        "num_assignments_graded",
    )

    list_display_links = (
        "user",
        "github",
        "num_courses_taught",
        "num_assignments_graded",
    )

    def num_courses_taught(self, obj):
        """
        Returns the number of courses taught by the faculty.
        """
        return len(obj.programs())

    def num_assignments_graded(self, obj):
        """
        Returns the number of assignments graded by the faculty.
        """
        return StudentAssignment.objects.filter(
            reviewer=obj, grade__isnull=False
        ).count()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Student model.
    """

    list_display = (
        "user",
        "github",
        "is_active",
        "program_name",
        "num_courses_enrolled",
        "num_assignments",
        "average_grade",
    )

    list_display_links = (
        "user",
        "program_name",
        "num_courses_enrolled",
        "num_assignments",
        "average_grade",
    )

    def program_name(self, obj):
        """
        Returns the name of the program in which the student is enrolled.
        """
        return obj.program.name

    def num_courses_enrolled(self, obj):
        """
        Returns the number of courses enrolled by the student.
        """
        return len(obj.courses())

    def num_assignments(self, obj):
        """
        num of assignments
        """
        return obj.assignments().count()

    def average_grade(self, obj):
        """
        Returns the average grade of assignments submitted by the student.
        """
        submitted_assignments = obj.studentassignment_set.filter(grade__isnull=False)
        if submitted_assignments.exists():
            average = submitted_assignments.aggregate(Avg("grade"))["grade__avg"]
            return round(average, 2)
        return None


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Content model.
    """

    list_display = ("name", "faculty", "repo", "num_courses", "num_assignments")

    list_display_links = ("name", "faculty", "repo", "num_courses", "num_assignments")

    def num_courses(self, obj):
        """
        Returns the related course(s) associated with the content.
        """
        return Course.objects.filter(assignment__content=obj).distinct().count()

    def num_assignments(self, obj):
        """
        Returns the number of assignments associated with the content.
        """
        return obj.assignment_set.all().count()


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Program model.
    """

    list_display = ("name", "num_courses", "num_students")

    list_display_links = ("name", "num_courses", "num_students")

    def num_courses(self, obj):
        """
        Returns the number of courses associated with the program.
        """
        return (
            obj.assignment_set.values("course")
            .annotate(course_count=Count("course"))
            .count()
        )

    def num_students(self, obj):
        """
        Returns the number of students enrolled in the program.
        """
        return obj.student_set.count()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Course model.
    """

    list_display = ("name", "num_assignments", "num_completed_assignments")

    list_display_links = ("name", "num_assignments", "num_completed_assignments")

    def num_assignments(self, obj):
        """
        Returns the number of assignments associated with the course.
        """
        return obj.assignment_set.count()

    def num_completed_assignments(self, obj):
        """
        Returns the number of completed assignments (graded 100%) associated with the course.
        """
        assignments = obj.assignment_set.all()
        c = 0
        for assignment in assignments:
            # c += len(assignment.studentassignment_set.filter(grade=100.0))
            c += len(assignment.studentassignment_set.filter(grade__gte=40))
        return c


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Assignment model.
    """

    list_display = ("__str__", "average_grade", "due")

    list_display_links = ("__str__", "average_grade", "due")

    def average_grade(self, obj):
        """
        Returns the average grade of assignments associated with this assignment.
        """
        result = obj.studentassignment_set.aggregate(Avg("grade"))["grade__avg"]
        return round(result, 2) if result is not None else None


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    """
    Default admin interface for StudentAssignment model.
    """

    list_display = (
        "student_name",
        "assignment",
        "grade",
        "submitted",
        "reviewed",
        "reviewer",
        "feedback",
    )

    list_display_links = (
        "student_name",
        "assignment",
        "grade",
        "submitted",
        "reviewed",
        "reviewer",
        "feedback",
    )

    def student_name(self, obj):
        """
        returns student name
        """
        return obj.student.user
