"""
database tables  for voyage app
"""
import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db import models
from qux.models import QuxModel
# import git


class Faculty(QuxModel):
    """
    Represents a faculty member.
    """

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    github = models.CharField(max_length=39, unique=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def create_random_faculty(cls):
        """
        Creates and saves random faculty members.
        """
        for i in range(1, 6):
            user = get_user_model().objects.create_user(
                username=f"faculty_{i}",
                email=f"e9{i}@gmail.com",
                password="password{i}",
            )
            faculty = cls(
                user=user,
                github=f"github_{random.randint(1000, 9999)}",
                is_active=random.choice([True, False]),
            )
            faculty.save()

        return faculty

    def programs(self):
        """
        this returns the  programs
        """
        return Program.objects.filter(assignment__content__faculty=self).distinct()

    def courses(self):
        """
        returns courses
        """

        return Course.objects.filter(assignment__content__faculty=self).distinct()

    def content(self, program=None, course=None):
        """
        returns content
        """
        if program and course:
            return self.content_set.filter(
                assignment__program=program, assignment__course=course
            )
        if program:
            return self.content_set.filter(assignment__program=program)
        if course:
            return self.content_set.filter(assignment__course=course)

        return self.content_set.all()

    def assignments_graded(self, assignment=None):
        """
        this returns assignments graded if thre is
        assignments else all the assignments
        """
        queryset = self.studentassignment_set.filter(grade__isnull=False)
        if assignment:
            queryset = queryset.filter(assignment=assignment)
        return list(queryset)

    def num_assignments(self):
        """
        returns number of assignments
        """

        return Assignment.objects.filter(content__faculty=self)
    

class Program(QuxModel):
    """
    Represents an educational program.
    """

    name = models.CharField(max_length=128)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.name

    def students(self):
        """
        Returns students.
        """
        return self.student_set.all()

    @classmethod
    def create_random_program(cls):
        """
        Creates and saves random programs.
        """
        for i in range(1, 4):
            program = cls(
                name=f"Program_{i}",
                start=datetime.now() - timedelta(days=random.randint(30, 365)),
                end=datetime.now() + timedelta(days=random.randint(30, 365)),
            )
            program.save()

        return program


class Course(QuxModel):
    """
    Represents a course.
    """

    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    def programs(self):
        """
        Returns a set of programs associated with the course.
        """
        return Program.objects.filter(assignment__course=self).distinct()
    @property
    def students(self):
        """
        Returns a set of students associated with the course.
        """
        return Student.objects.filter(program__assignment__course=self)


    def content(self):
        """
        Returns a set of content associated with the course.
        """
        return Content.objects.filter(assignment__course=self).distinct()

    @property
    def assignments(self):
        """
        Returns a set of assignments associated with the course.
        """
        return set(self.assignment_set.all())

    @classmethod
    def create_random_course(cls):
        """
        Creates and saves random courses.
        """
        for i in range(1, 4):
            course = cls(name=f"Course_{i}")
            course.save()

        return course


class Content(QuxModel):
    """
    Represents educational content.
    """

    name = models.CharField(max_length=128)
    faculty = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING)
    repo = models.URLField(max_length=240, unique=True)

    class Meta:
        verbose_name = "Content"
        verbose_name_plural = "Content"

    @classmethod
    def create_random_content(cls):
        """
        created random data for Content model
        """
        faculties = Faculty.objects.all()
        for i in range(1, 29):
            faculty = random.choice(faculties)

            content = cls(
                name=f"Content_{i}",
                faculty=faculty,
                repo=f"https://github.com/{faculty.github}/repo_{i}",
            )
            content.save()

        return content


class Student(QuxModel):
    """
    Represents a student enrolled in a specific program.
    """

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    github = models.CharField(max_length=39, unique=True)
    is_active = models.BooleanField(default=True)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING)

    def courses(self):
        """
        Returns a set of courses associated with the student's program.
        """
        return Course.objects.filter(assignment__program__student=self).distinct()

    def assignments(self):
        """
        Returns all assignments associated with the student's program.
        """
        return self.program.assignment_set.all()

    def assignments_submitted(self, assignment=None):
        """
        Returns a set of submitted assignments, optionally filtered by assignment.
        """

        if assignment:
            return self.studentassignment_set.filter(
                assignment=assignment, submitted__isnull=False
            )
        return self.studentassignment_set.filter(submitted__isnull=False)

    def assignments_not_submited(self, assignment=None):
        """
        Returns assignments that have not been submitted, optionally filtered by assignment.
        """

        if assignment:
            return self.studentassignment_set.filter(
                assignment=assignment, submitted__isnull=True
            )
        return self.studentassignment_set.filter(submitted__isnull=True)

    def assignments_graded(self, assignment=None):
        """
        Returns graded assignments, optionally filtered by assignment.
        """

        if assignment:
            return self.studentassignment_set.filter(
                assignment=assignment, submitted__isnull=False, grade__isnull=False
            )
        return self.studentassignment_set.filter(
            submitted__isnull=False, grade__isnull=False
        )

    @classmethod
    def create_random_student(cls):
        """
        Creates and saves random students with associated programs.
        """

        programs = Program.objects.all()
        for i in range(1, 11):
            user = get_user_model().objects.create_user(
                username=f"student_{random.randint(1000, 9999)}",
                email=f"e9student{i}@gmail.com",
                password="password{i}",
            )
            program = random.choice(programs)
            student = cls(
                user=user,
                github=f"github_{random.randint(1000, 9999)}",
                is_active=random.choice([True, False]),
                program=program,
            )
            student.save()
        return student


class Assignment(QuxModel):
    """
    Represents an assignment given to students in a specific program and course.
    """

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    due = models.DateTimeField()
    instructions = models.TextField()
    rubric = models.TextField()

    class Meta:
        unique_together = ["program", "course", "content"]

    def __str__(self):
        """
        Returns a string representation of the assignment.
        """
        return self.content.name

    def students(self):
        """
        Returns a set of students who have been assigned this assignment.
        """

        return Student.objects.filter(program__assignment=self).distinct()

    def submissions(self, graded=None):
        """
        Return a queryset of submissions that are either all, graded, or not graded.
        """
        submissions_query = self.studentassignment_set.all()

        if graded is not None:
            if graded:
                submissions_query = submissions_query.filter(grade__isnull=False)
            else:
                submissions_query = submissions_query.filter(grade__isnull=True)

        return submissions_query
    
    # def clone_repo_for_student(self, course_repo_url, student_username):
    #     """
    #     when assignment is created this will help 
    #     """
    #     repo = git.Repo.clone_from(course_repo_url, f'https://github.com/{student_username}/{self.content}')
    #     return repo

    # def save(self, **kwargs):
    #     """
    #     to save data 
    #     """
    #     students = Student.objects.all()

    #     for student in students:
    #         self.clone_repo_for_student(self.content.repo, student.user.username)

    #     return super().save(**kwargs)

    @classmethod
    def create_random_assignment(cls):
        """
        Creates and saves random assignments with associated programs, courses, and content.
        """

        programs = Program.objects.all()
        courses = Course.objects.all()
        contents = Content.objects.all()

        for _ in range(1, 6):
            program = random.choice(programs)
            course = random.choice(courses)
            content = random.choice(contents)
            due_date = datetime.now() + timedelta(days=random.randint(7, 30))

            assignment = cls(
                program=program,
                course=course,
                content=content,
                due=due_date,
                instructions=f"Instructions for Assignment_{random.randint(100, 999)}",
                rubric=f"Rubric for Assignment_{random.randint(100, 999)}",
            )
            assignment.save()

        return assignment


class StudentAssignment(QuxModel):
    """
    Represents an assignment submitted by a student, along with grading details.
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=None,
        null=True,
        blank=True,
    )
    submitted = models.DateTimeField(default=None, null=True, blank=True)
    reviewed = models.DateTimeField(default=None, null=True, blank=True)
    reviewer = models.ForeignKey(
        Faculty, on_delete=models.DO_NOTHING, default=None, null=True, blank=True
    )
    feedback = models.TextField(default=None, null=True, blank=True)

    @classmethod
    def create_random_student_assignment(cls):
        """
        Creates and saves random student assignments with
        associated students, assignments, and faculties.
        """

        students = Student.objects.all()
        assignments = Assignment.objects.all()
        faculties = Faculty.objects.all()
        for _ in range(1, 11):
            student = random.choice(students)
            assignment = random.choice(assignments)
            faculty = random.choice(faculties)

            submitted_date = datetime.now() - timedelta(days=random.randint(0, 7))
            reviewed_date = submitted_date + timedelta(days=random.randint(0, 7))

            student_assignment = cls(
                student=student,
                assignment=assignment,
                grade=random.choice([None, random.uniform(60, 100)]),
                submitted=submitted_date,
                reviewed=reviewed_date,
                reviewer=faculty,
                feedback=f"Feedback for Assignment_{assignment.id}",
            )
            student_assignment.save()

        return student_assignment
