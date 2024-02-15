"""
Admin panel configuration for the Voyage app.
"""
from django.db.models import Avg
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
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
        "num_assignments_by_faculty",
    )

    def num_courses_taught(self, obj):
        """
        Returns the number of courses taught by the faculty.
        """
        courses = obj.courses()
        ids = [i.id for i in courses]
        if courses:
            html = '<a href="/admin/voyage/course/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(courses)}</a>')
        return 0

    num_courses_taught.short_description = "Courses Taught"

    def num_assignments_graded(self, obj):
        """
        Returns number of assignments that have been graded
        """
        assignments = obj.assignments_graded()
        ids = [i.id for i in assignments]
        if assignments:
            html = '<a href="/admin/voyage/studentassignment/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(assignments)}</a>')

        return 0

    num_assignments_graded.short_description = "Assignments Graded"

    def num_assignments_by_faculty(self, obj):
        """
        Returns the total number of assignments associated with the faculty.
        """
        assignments = obj.num_assignments()
        ids = [a.id for a in assignments]
        if assignments:
            html = '<a href="/admin/voyage/assignment/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(assignments)}</a>')

        return 0


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

    def program_name(self, obj):
        """
        Returns the name of the program in which the student is enrolled.
        """
        return obj.program.name

    def num_courses_enrolled(self, obj):
        """
        number of courses each student is enrolled in
        """
        courses = obj.courses()
        ids = [i.id for i in courses]
        if courses:
            html = '<a href="/admin/voyage/course/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(courses)}</a>')

        return 0

    def num_assignments(self, obj):
        """
        number of assignments assigned to the student
        """
        assignments = obj.assignments()
        ids = [i.id for i in assignments]
        if assignments:
            html = '<a href="/admin/voyage/assignment/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(assignments)}</a>')

        return 0

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
    class content methods
    """
    list_display = ("name", "faculty", "repo", "num_courses", "num_assignments")

    def num_courses(self, obj):
        """
        number of courses that use each content
        """
        assignments = obj.assignment_set.all()
        courses = set(i.course for i in assignments)
        ids = [i.id for i in courses]
        if courses:
            html = '<a href="/admin/voyage/course/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(courses)}</a>')

        return 0

    def num_assignments(self, obj):
        """
        number of assignments that use each content
        """
        assignments = obj.assignment_set.all()
        ids = [i.id for i in assignments]
        if assignments:
            html = '<a href="/admin/voyage/assignment/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(assignments)}</a>')

        return 0


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Program model.
    """

    list_display = ("name", "num_courses", "num_students")

    def num_courses(self, obj):
        """
        number of courses in each program
        """
        assignments = obj.assignment_set.all()
        courses = set(i.course for i in assignments)
        ids = [i.id for i in courses]
        if courses:
            html = '<a href="/admin/voyage/course/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(courses)}</a>')

        return 0

    def num_students(self, obj):
        """
        number of students in each program
        """
        students = obj.students()
        ids = [i.id for i in students]
        if students:
            html = '<a href="/admin/voyage/student/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(students)}</a>')

        return 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Course model.
    """

    list_display = ("name", "num_assignments", "num_completed_assignments")

    def num_assignments(self, obj):
        """
        number of assignments in each course
        """
        assignments = obj.assignments
        ids = [i.id for i in assignments]
        if assignments:
            html = '<a href="/admin/voyage/assignment/?id__in='
            for i in ids:
                html = "".join((html, f"{i},"))
            return format_html(html[:-1] + f'">{len(assignments)}</a>')

        return 0

    def num_completed_assignments(self, obj):
        """
        Number of assignments that are completed and graded 100%.
        """
        assignments = obj.assignment_set.all()
        max_grade = 100.0
        graded_assignments = set()

        for assignment in assignments:
            graded_assignments.update(
                assignment.studentassignment_set.filter(grade__gte=max_grade)
            )

        count = len(graded_assignments)

        if count:
            url = (
                reverse("admin:voyage_studentassignment_changelist")
                + f'?id__in={",".join(map(str, graded_assignments.values_list("id", flat=True)))}'
            )
            return format_html('<a href="{}">{}</a>', url, count)

        return 0


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
