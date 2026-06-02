# Import libraries
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Study:
    """
    Represents a study program with its details and progress.
    """

    # Dataclass fields
    name: str
    start_date: date
    goal_grade: float
    goal_duration: int
    total_ects: int
    semesters: list[Semester] = field(default_factory=list)

    def __post_init__(self):
        # Sort semesters by start date
        self.semesters.sort(key=lambda semester: semester.start_date)


    def get_current_semester(self) -> Optional[Semester]:
        """"
        Returns the current semester based on the current date. Or the latest started semester if no current semester is found.
        :return: Current semester
        """

        started = [s for s in self.semesters if s.start_date <= date.today()]
        if not started:
            # No semester started yet — return the next upcoming one
            upcoming = [s for s in self.semesters if s.start_date > date.today()]
            return min(upcoming, key=lambda s: s.start_date, default=None)

        latest = max(started, key=lambda s: s.start_date)

        # If the latest started semester still has incomplete modules, show it
        if any(not m.exam.completed for m in latest.modules):
            return latest

        # All modules complete — advance to the next upcoming semester if one exists
        upcoming = [s for s in self.semesters if s.start_date > date.today()]
        if upcoming:
            return min(upcoming, key=lambda s: s.start_date)

        return latest


    def get_completed_exams(self) -> Optional[list[tuple[date, int]]]:
        """
        Returns a list of completed exams and their ECTS.
        :return: List of tuples containing exam date and ECTS
        """

        # Get all completed exams and their ECTS
        completed_exams = []
        for semester in self.semesters:
            for module in semester.modules:
                # Check if the exam is completed
                if module.exam.completed:
                    # If completed, add the exam date and ECTS to the list
                    completed_exams.append((module.exam.exam_date, module.ects))

        # Check if there are any completed exams
        if len(completed_exams) == 0:
            return []

        # Sort the list by exam date
        completed_exams.sort(key=lambda exam: exam[0])

        # Return the list of completed exams
        return completed_exams


    def get_grade_graph(self) -> list[float]:
        """
        Plots the average grade of each semester of the study in a list of integers.
        :return: List of average grades per semester.
        """

        # Add semester average grades to plot list
        data = []
        for semester in self.semesters:
            # Calculate the average grade for the semester
            semester_average_grade = semester.get_average_grade()

            # Check if the average grade was calculated successfully
            if semester_average_grade is not None:
                # Append the average grade to the data list
                data.append(semester_average_grade)


        # Return the data as a list of integers
        return data


    def get_average_grade(self) -> Optional[float]:
        """
        Used to calculate the average grade of the study based on completed exams.
        :return: Average grade
        """

        # Variables
        weighted_sum = 0
        weight_sum = 0

        # Enumerate all exams
        for semester in self.semesters:
            for module in semester.modules:
                # Check if the exam is completed and has a grade
                if module.exam.completed and module.exam.grade is not None:
                    # Calculate weighted sum and weight sum
                    weighted_sum += module.exam.grade.value * module.exam.grade.weight
                    weight_sum += module.exam.grade.weight

        # Check if exams with grades were found
        if weight_sum == 0:
            # Return None if no grades were found
            return None

        # Return the average grade
        return weighted_sum / weight_sum


    def get_ects_graph(self) -> Optional[list[int]]:
        """
        Calculates the cumulative ECTS points for each month and returns the data as a list of values.
        :return: List of cumulative ECTS points for each month.
        """

        # Get all completed exams
        completed_exams = self.get_completed_exams()

        # Check if there are any completed exams
        if not completed_exams:
            return None

        # Last completed exam date
        last_date = completed_exams[-1][0]

        # Calculate months since study start until last completed exam
        total_months = ((last_date.year - self.start_date.year) * 12 + (last_date.month - self.start_date.month))

        # Generate x and y values for the ECTS graph
        data = []

        # Calculate cumulative ECTS for each month
        for month in range(0, total_months + 1):
            cumulative_ects = 0

            # Check if the exam date is within the current month
            for exam_date, ects in completed_exams:
                # Calculate the number of months since the study start
                exam_month = ((exam_date.year - self.start_date.year) * 12 + (exam_date.month - self.start_date.month))

                # Check if the exam date is within the current month
                if exam_month <= month:
                    # Add the ECTS to the cumulative ECTS
                    cumulative_ects += ects

            # Add the cumulative ECTS to the data list
            data.append(cumulative_ects)

        # Return the data
        return data


    def get_average_ects_graph(self) -> Optional[list[int]]:
        """
        Calculates the average ECTS per month and plots the curve
        :return: List of average ECTS values per month
        """

        # Get the ECTS graph data
        ects = self.get_ects_graph()

        # Check if any data is available
        if not ects:
            # Return None if no data is available
            return None

        # Calculate the ECTS gained per month
        ects_per_month = []
        for i in range(len(ects)):
            if i == 0:
                ects_per_month.append(ects[i])
            else:
                ects_per_month.append(ects[i] - ects[i - 1])

        # Calculate the average ECTS per month
        average_ects_per_month = sum(ects_per_month) / len(ects)

        # Calculate the data for the curve
        data = []
        for i in range(0, self.goal_duration):
            # Check if data has already reached 180 ECTS
            if average_ects_per_month * i <= 180:
                # Add the average ECTS per month to the data
                data.append(average_ects_per_month * i)

        # Return the data
        return data


@dataclass
class Semester:
    """
    Represents a semester with modules and exams.
    """

    # Dataclass fields
    name: str
    start_date: date
    end_date: date
    modules: list[Module] = field(default_factory=list)

    def __post_init__(self):
        # Sort modules by exam date
        self.modules.sort(key=lambda module: module.exam.exam_date)


    def get_average_grade(self) -> Optional[float]:
        """
        Used to calculate the average grade of the semester based on completed exams.
        :return: Average grade
        """

        # Variables
        weighted_sum = 0
        weight_sum = 0

        # Enumerate all exams
        for module in self.modules:
            # Check if the exam is completed and has a grade
            if module.exam.completed and module.exam.grade is not None:
                # Calculate weighted sum and weight sum
                weighted_sum += module.exam.grade.value * module.exam.grade.weight
                weight_sum += module.exam.grade.weight

        # Check if exams with grades were found
        if weight_sum == 0:
            # Return None if no grades were found
            return None

        # Return the average grade
        return weighted_sum / weight_sum


    def get_grade_graph(self) -> list[float]:
        """
        Plots the grades of each module of the semester in a list of integers.
        :return: List of grades per module.
        """

        modules = self.modules
        modules.sort(key=lambda module: module.exam.exam_date)

        # Enumerate all modules
        data = []
        for module in self.modules:
            # Check if the exam is completed and has a grade
            if module.exam.completed and module.exam.grade is not None:
                # Append the grade to the data list
                data.append(module.exam.grade.value)

        # Return the data as a list of integers
        return data


@dataclass
class Module:
    """
    Represents a module with its details and progress.
    """

    # Dataclass fields
    status: str
    name: str
    ects: int
    start_date: date
    progress: Progress
    exam: Exam


@dataclass
class Progress:
    """
    Represents the progress of a module, including total units, completed units, and learned units.
    """

    # Dataclass fields
    total_units: int
    completed_units: int
    learned_units: int = 0

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the module.
        :return: progress
        """

        # Prevent division by 0
        if self.total_units == 0:
            return 100

        # Return the progress which is calculated based on the completed units
        return min(int(self.completed_units / self.total_units * 100), 100)


@dataclass
class Exam:
    """
    Represents an exam with its details and result.
    """

    # Dataclass fields
    exam_date: date
    completed: bool
    grade: Grade | None = None

    def is_passed(self) -> bool:
        """
        Checks if the exam is passed based on the grade.
        :return: passed
        """

        # Check if the exam is completed and has a grade
        return self.grade is not None and self.grade.value < 5.0


    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        if self.completed:
            return 100
        else:
            return 0


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Exam"


@dataclass
class HomeworkExam(Exam):
    """
    Represents a homework exam with pages written, target pages, literature progress, and outline done.
    """

    # Dataclass fields
    pages_written: int = 0
    pages_target: int = 10
    literature_progress: int = 0
    outline_done: bool = False

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Prevent division by 0
        if self.pages_target == 0:
            # Return progress
            return 100

        # Calculate the page progress
        page_progress = min(self.pages_written / self.pages_target * 100, 100)

        # Check if the outline is done and add bonus points if it is
        outline_bonus = 10 if self.outline_done else 0

        # Calculate the total progress
        return min(int((page_progress * 0.7) + (self.literature_progress * 0.2) + outline_bonus), 100)

    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Homework Exam"


@dataclass
class SeminarPaperExam(HomeworkExam):
    """
    Represents a seminar paper exam with pages written, target pages, literature progress, and outline done.
    """

    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Seminar Paper"


@dataclass
class CaseStudyExam(Exam):
    """
    Represents a case study exam with analysis progress and reflection done.
    """

    # Dataclass fields
    analysis_progress: int = 0
    solution_defined: bool = False
    reflection_done: bool = False

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Progress is based on the analysis progress and the reflection done
        progress = self.analysis_progress

        # Add bonus points for solution defined and reflection done
        if self.solution_defined:
            progress += 20
        if self.reflection_done:
            progress += 20

        # Return the progress
        return min(progress, 100)


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Case Study"


@dataclass
class ProjectReportExam(Exam):
    """
    Represents a project report exam with milestones completed and total milestones.
    """

    # Dataclass fields
    milestones_done: int = 0
    milestones_total: int = 1
    product_finished: bool = False
    reflection_done: bool = False

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Prevent division by 0
        if self.milestones_total == 0:
            # Return progress
            return 100

        # Calculate the milestone progress
        milestone_progress = self.milestones_done / self.milestones_total * 100

        # Add bonus points for product finished and reflection done
        bonus = 0
        if self.product_finished:
            bonus += 15
        if self.reflection_done:
            bonus += 15

        # Return the total progress
        return min(int(milestone_progress * 0.7 + bonus), 100)


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Project Report"


@dataclass
class ProjectPresentationExam(Exam):
    """
    Represents a project presentation exam with slides, rehearsals, and readiness for presentation.
    """

    # Dataclass fields
    slides_done: int = 0
    slides_total: int = 1
    rehearsals_done: int = 0
    ready_for_presentation: bool = False

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Prevent division by 0
        if self.slides_total == 0:
            # Return progress
            return 100

        # Calculate slide and rehearsal progress
        slide_progress = self.slides_done / self.slides_total * 100
        rehearsal_progress = min(self.rehearsals_done / 3 * 100, 100)

        # Add bonus points for readiness for presentation
        ready_bonus = 10 if self.ready_for_presentation else 0

        # Return the total progress
        return min(int(slide_progress * 0.6 + rehearsal_progress * 0.3 + ready_bonus), 100)


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Project presentation"


@dataclass
class PortfolioExam(Exam):
    """
    Represents a portfolio exam with portfolio items and readiness for submission.
    """

    # Dataclass fields
    phase_1_done: bool = False
    phase_2_done: bool = False
    phase_3_done: bool = False
    final_submission_ready: bool = False

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Calculate the progress based on the phases completed
        progress = 0
        if self.phase_1_done:
            progress += 30
        if self.phase_2_done:
            progress += 30
        if self.phase_3_done:
            progress += 30
        if self.final_submission_ready:
            progress += 10

        # Return the total progress
        return progress


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Portfolio"


@dataclass
class AdvancedWorkbookExam(Exam):
    """
    Represents an advanced workbook exam with tasks completed and total tasks.
    """

    # Dataclass fields
    tasks_done: int = 0
    tasks_total: int = 6

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Prevent division by 0
        if self.tasks_total == 0:
            # Return progress
            return 100

        # Return the progress which is calculated based on the tasks completed
        return min(int(self.tasks_done / self.tasks_total * 100), 100)


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Advanced Workbook"


@dataclass
class BachelorThesisExam(Exam):
    """
    Represents a bachelor thesis exam with pages written, milestones completed, and submission status.
    """

    # Dataclass fields
    pages_written: int = 0
    pages_target: int = 40
    milestones_done: int = 0
    milestones_total: int = 4
    submitted: bool = False

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Prevent division by 0
        if self.pages_target == 0 or self.milestones_total == 0:
            # Return progress
            return 100

        # Calculate page and milestone progress
        page_progress = min(self.pages_written / self.pages_target * 100, 100)
        milestone_progress = self.milestones_done / self.milestones_total * 100

        # Add bonus points for submission
        submission_bonus = 10 if self.submitted else 0

        # Return the total progress
        return min(int(page_progress * 0.6 + milestone_progress * 0.3 + submission_bonus), 100)


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Bachelor Thesis Exam"


@dataclass
class ColloquiumExam(Exam):
    """
    Represents a colloquium exam with slides, rehearsals, and readiness for presentation.
    """

    # Dataclass fields
    presentation_ready: bool = False
    rehearsals_done: int = 0
    questions_prepared: bool = False

    def get_progress_percent(self) -> int:
        """
        Calculates the progress percentage of the exam.
        :return: The progress of the exam.
        """

        # Add bonus points for presentation readiness and questions preparation
        progress = 0
        if self.presentation_ready:
            progress += 40
        if self.questions_prepared:
            progress += 20

        # Add bonus points for rehearsals done
        progress += min(self.rehearsals_done * 20, 40)

        # Return the total progress
        return min(progress, 100)


    @staticmethod
    def get_exam_type() -> str:
        """
        Returns the type of the exam.
        :return: The type of the exam.
        """

        return "Colloquium"


@dataclass
class Grade:
    """
    Represents a grade with a value and weight.
    """

    # Dataclass fields
    value: float
    weight: float














