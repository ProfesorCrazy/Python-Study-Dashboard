# Import libraries
from models import *
from textual.containers import *
from textual.widgets import *
from textual.screen import Screen
from textual.color import Gradient
from textual.app import App, ComposeResult, SystemCommand


class ModuleProgressWidget(Static):
    """
    Static widget for displaying module progress
    :param total_units: Total units of the module
    :param completed_units: Completed units of the module
    :param learned_units: Learned units of the module
    :param gradient: Gradient for the progress bar
    :yield:
    """

    def __init__(self, total_units: int, completed_units: int, learned_units: int, gradient: Gradient):
        # Superclass constructor
        super().__init__()

        # Initialize module progress attributes
        self.total_units = total_units
        self.completed_units = completed_units
        self.learned_units = learned_units

        # Set the widget classes and gradient
        self.classes = "module-progress-widget"
        self.gradient = gradient


    def compose(self) -> ComposeResult:
        # Display the completed and learned units progress bars
        with Vertical(classes="module-progress-container"):
            # Display the title
            yield Static("Fortschritt", classes="content-title")

            # Display completed units progress bar
            yield Static("Completed Units", classes="title")
            yield ProgressBar(total=self.total_units, show_eta=False, gradient=self.gradient, id="completed_units", classes="module-progress")

            # Display learned units progress bar
            yield Static("Learned Units", classes="title")
            yield ProgressBar(total=self.total_units, show_eta=False, gradient=self.gradient, id="learned_units", classes="module-progress")


    def on_mount(self) -> None:
        # Query the completed and learned units progress bars
        completed_units_progress_bar = self.query_one("#completed_units", ProgressBar)
        learned_units_progress_bar = self.query_one("#learned_units", ProgressBar)

        # Update the progress bars with the current module progress
        completed_units_progress_bar.advance(self.completed_units)
        learned_units_progress_bar.advance(self.learned_units)


class GradeWidget(Static):
    """
    Box widget for displaying grade data
    :param value: Grade value
    :param weight: Grade weight
    :yield:
    """

    def __init__(self, value: float, weight: float):
        # Superclass constructor
        super().__init__()

        # Initialize grade attributes
        self.value = value
        self.weight = weight

        # Set the widget classes
        self.classes = "grade-widget"


    def compose(self) -> ComposeResult:
        # Display the exam date and completion status
        with Vertical(classes="grade-container"):
            # Display the title
            yield Static("Note", classes="content-title")

            # Display the grade value and weight
            yield Static(f"[b]Note[/b]: {self.value}", classes="grade")
            yield Static(f"[b]Gewicht[/b]: {self.weight}", classes="grade")


class ExamWidget(Static):
    """
    Box widget for displaying exam data
    :param exam_type: Type of exam
    :param progress: Exam progress
    :param date: Exam date
    :param gradient: Gradient for the progress bar
    :yield:
    """

    def __init__(self, exam_type: str, progress: int, date: date, gradient: Gradient):
        # Superclass constructor
        super().__init__()

        # Initialize exam attributes
        self.exam_type = exam_type
        self.progress = progress
        self.date = date

        # Set the widget classes
        self.classes = "exam-widget"
        self.gradient = gradient


    def compose(self) -> ComposeResult:
        # Display the exam date and completion status
        with Vertical(classes="exam-container"):
            # Display the exam type
            yield Static(self.exam_type, classes="content-title")

            # Display the exam date and completion status
            yield Static(f"[b]Prüfungs Datum[/b]: {self.date}", classes="exam")
            yield Static("Fortschritt", classes="title")
            yield ProgressBar(total=self.progress, show_eta=False, gradient=self.gradient, id="exam_progress", classes="exam-progress")

    def on_mount(self) -> None:
        # Query the exam progress bar
        exma_progress_bar = self.query_one("#exam_progress", ProgressBar)

        # Update the exam progress bar
        exma_progress_bar.advance(self.progress)


class ModuleWidget(Static):
    """
    Box widget for displaying module data
    :param module: Module object
    :yield:
    """

    def __init__(self, module: Module, gradient: Gradient, classes: str = "module"):
        # Superclass constructor
        super().__init__()

        # Initialize module attributes
        self.module = module

        # Set the widget classes
        self.classes = classes
        self.gradient = gradient

    def compose(self) -> ComposeResult:
        # Display the module name
        yield Static(self.module.name, classes="panel-title")

        # Create the panel container
        with Grid(classes="panel"):
            # Display the module progress, exam and grade
            yield ModuleProgressWidget(self.module.progress.total_units, self.module.progress.completed_units, self.module.progress.learned_units, self.gradient)
            yield ExamWidget(self.module.exam.get_exam_type(), self.module.exam.get_progress_percent(), self.module.exam.exam_date, self.gradient)

            # Check if a grade is present
            if self.module.exam.grade is not None:
                # Display grade widget
                yield GradeWidget(self.module.exam.grade.value, self.module.exam.grade.weight)
            else:
                # Display placeholder
                yield GradeWidget(0.0, 0,)