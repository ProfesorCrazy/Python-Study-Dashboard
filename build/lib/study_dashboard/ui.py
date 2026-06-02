# Import libraries
from .models import *
from textual.containers import *
from textual.widgets import *
from textual.color import Gradient
from textual.app import ComposeResult


class ModuleProgressWidget(Static):
    def __init__(self, total_units: int, completed_units: int, learned_units: int, gradient: Gradient):
        super().__init__()
        self.total_units = total_units
        self.completed_units = completed_units
        self.learned_units = learned_units
        self.classes = "module-progress-widget"
        self.gradient = gradient

    def compose(self) -> ComposeResult:
        with Vertical(classes="module-progress-container"):
            yield Static("Fortschritt", classes="content-title")
            yield Static("Completed Units", classes="title")
            yield ProgressBar(total=self.total_units, show_eta=False, gradient=self.gradient, id="completed_units", classes="module-progress")
            yield Static("Learned Units", classes="title")
            yield ProgressBar(total=self.total_units, show_eta=False, gradient=self.gradient, id="learned_units", classes="module-progress")

    def on_mount(self) -> None:
        completed_units_progress_bar = self.query_one("#completed_units", ProgressBar)
        learned_units_progress_bar = self.query_one("#learned_units", ProgressBar)
        completed_units_progress_bar.advance(self.completed_units)
        learned_units_progress_bar.advance(self.learned_units)


class GradeWidget(Static):
    def __init__(self, value: float, weight: float):
        super().__init__()
        self.value = value
        self.weight = weight
        self.classes = "grade-widget"

    def compose(self) -> ComposeResult:
        with Vertical(classes="grade-container"):
            yield Static("Note", classes="content-title")
            yield Static(f"[b]Note[/b]: {self.value}", classes="grade")
            yield Static(f"[b]Gewicht[/b]: {self.weight}", classes="grade")


class ExamWidget(Static):
    def __init__(self, exam_type: str, progress: int, date: date, gradient: Gradient):
        super().__init__()
        self.exam_type = exam_type
        self.progress = progress
        self.date = date
        self.classes = "exam-widget"
        self.gradient = gradient

    def compose(self) -> ComposeResult:
        with Vertical(classes="exam-container"):
            yield Static(self.exam_type, classes="content-title")
            yield Static(f"[b]Prüfungs Datum[/b]: {self.date}", classes="exam")
            yield Static("Fortschritt", classes="title")
            yield ProgressBar(total=100, show_eta=False, gradient=self.gradient, id="exam_progress", classes="exam-progress")

    def on_mount(self) -> None:
        exma_progress_bar = self.query_one("#exam_progress", ProgressBar)
        exma_progress_bar.advance(self.progress)


class ModuleWidget(Static):
    def __init__(self, module: Module, gradient: Gradient, classes: str = "module"):
        super().__init__()
        self.module = module
        self.classes = classes
        self.gradient = gradient

    def compose(self) -> ComposeResult:
        yield Static(self.module.name, classes="panel-title")
        with Grid(classes="panel"):
            yield ModuleProgressWidget(self.module.progress.total_units, self.module.progress.completed_units, self.module.progress.learned_units, self.gradient)
            yield ExamWidget(self.module.exam.get_exam_type(), self.module.exam.get_progress_percent(), self.module.exam.exam_date, self.gradient)
            if self.module.exam.grade is not None:
                yield GradeWidget(self.module.exam.grade.value, self.module.exam.grade.weight)
            else:
                yield GradeWidget(0.0, 0)
