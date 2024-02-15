"""
views for voyage app
"""
from django.views.generic import DetailView, ListView, TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Count, Avg
from django.shortcuts import render

from apps.voyage.models import Faculty, Student, Assignment
from apps.voyage.forms import CreateCourseForm, CreateAssignmentForm
from qux.seo.mixin import SEOMixin


class VoyageDefaultView(SEOMixin, TemplateView):
    """
    Default view for the Voyage app. Inherits from SEOMixin for SEO-related functionality.
    """

    template_name = "voyage/index.html"


class FacultyListView(ListView):
    """
    View for listing all faculty members.
    """

    template_name = "voyage/faculty_list.html"
    model = Faculty
    context_object_name = "faculties"


class FacultyDashboardView(DetailView):
    """
    View for displaying the dashboard of a specific faculty member.
    """

    template_name = "voyage/faculty_dashboard.html"
    model = Faculty
    context_object_name = "faculty"

    def get_context_data(self, **kwargs):
        """
        Override to add additional context data, such as the courses taught by the faculty.
        """
        context = super().get_context_data(**kwargs)
        faculty = self.get_object()
        courses_taught = faculty.courses()

        context["courses_taught"] = courses_taught

        return context


class StudentListView(ListView):
    """
    View for listing all students.
    """

    model = Student
    template_name = "student_list.html"
    context_object_name = "students"


class StudentDashboardView(DetailView):
    """
    View for displaying the dashboard of a specific student.
    """

    model = Student
    template_name = "voyage/student_dashboard.html"
    context_object_name = "student"

    def get_context_data(self, **kwargs):
        """
        Override to add additional context data, such as the courses,
        assignments, grades, and submissions of the student.
        """
        context = super().get_context_data(**kwargs)
        student = self.object

        courses = student.courses()

        assignments_counts = (
            Assignment.objects.filter(course__in=courses)
            .values("course__name")
            .annotate(num_assignments=Count("id"))
        )

        assignments = Assignment.objects.filter(
            program=student.program,
            course__in=courses,
        )

        avg_grades = assignments.values("id", "content__name").annotate(
            avg_grade=Avg("studentassignment__grade")
        )

        submissions = student.assignments_submitted()

        submissions_counts = assignments.values("content__name").annotate(
            num_submissions=Count("studentassignment")
        )

        context["courses"] = courses
        context["assignments_counts"] = assignments_counts
        context["avg_grades"] = avg_grades
        context["submissions"] = submissions
        context["submissions_counts"] = submissions_counts

        return context


class CreateNewCourse(TemplateView):
    """
    View for creating a new course. Inherits from TemplateView for simplicity.
    """

    template_name = "voyage/common_create_data.html"

    def get_context_data(self, **kwargs):
        """
        Override to add the CreateCourseForm to the context.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = CreateCourseForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request when creating a new course.
        """
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("faculty_list"))
        return render(request, self.template_name, {"form": form})


class CreateNewAssignment(TemplateView):
    """
    View for creating a new assignment. Inherits from TemplateView for simplicity.
    """

    template_name = "voyage/common_create_data.html"

    def get_context_data(self, **kwargs):
        """
        Override to add the CreateAssignmentForm to the context.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = CreateAssignmentForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request when creating a new assignment.
        """
        form = CreateAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("faculty_list"))
        return render(request, self.template_name, {"form": form})
