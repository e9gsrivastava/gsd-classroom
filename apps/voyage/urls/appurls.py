from django.urls import path
from ..views.appviews import (
    VoyageDefaultView,
    FacultyListView,
    FacultyDashboardView,
    StudentListView,
    CreateNewCourse,
    CreateNewAssignment,
    StudentDashboardView,
)

urlpatterns = [
    path("", VoyageDefaultView.as_view(), name="home"),
    path("faculties/", FacultyListView.as_view(), name="faculty_list"),
    path("faculty/<int:pk>/", FacultyDashboardView.as_view(), name="faculty_dashboard"),
    path("students/", StudentListView.as_view(), name="student_list"),
    path("course/new/", CreateNewCourse.as_view(), name="create_new_course"),
    path(
        "assignment/new/", CreateNewAssignment.as_view(), name="create_new_assignment"
    ),
    # path('dashboard/student/<int:student_id>/', StudentDashboardView.as_view(), name='student_dashboard'),
    path(
        "dashboard/student/<int:pk>/",
        StudentDashboardView.as_view(),
        name="student_dashboard",
    ),
]
