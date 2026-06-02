# Import libraries
import os
from pathlib import Path
from typing import Iterable
from dotenv import load_dotenv
from textual.app import SystemCommand, Screen, App
from textual_plotext import PlotextPlot

from .database import Database
from .importer import Importer
from .ui import *

load_dotenv(Path.home() / ".env")


class StudyDashboard(App):
    CSS_PATH = "ui.tcss"

    def __init__(self):
        super().__init__()

        self.grade_ticks = [1.0, 1.7, 2.3, 3.0, 3.7, 5.0]
        self.gradient = Gradient.from_colors(
            "#1aff00",
            "#4dff00",
            "#80ff00",
            "#b3ff00",
            "#e6ff00",
            "#ffd900",
            "#ffb300",
            "#ff8000",
            "#e65c00",
            "#cc3300",
            "#b30000",
        )

        self.database = Database()
        self.importer = Importer(self.database)
        self.importer.import_data(os.environ.get("STUDY_JSON", "study.json"))
        self.study = self.database.load_study()

        if not self.study:
            raise Exception("No study data available")

        self.semester = self.study.get_current_semester()

        if self.semester is None:
            raise Exception("No semester data available")

        if len(self.semester.modules) < 1:
            raise Exception("Semester has no modules")


    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield PlotextPlot(id="ects-overview", disabled=True)

        for i, module in enumerate(self.semester.modules[:4]):
            yield ModuleWidget(module, self.gradient)

        yield PlotextPlot(id="study-grade-overview", disabled=True)
        yield PlotextPlot(id="semester-grade-overview", disabled=True)

        if len(self.semester.modules) > 4:
            yield ModuleWidget(self.semester.modules[4], self.gradient, classes="bottom-module")


    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Import JSON", "Import study from file", self.import_data)


    def on_mount(self) -> None:
        self.theme = "dracula"
        self.ects_digramm()
        self.study_grade_overview()
        self.semester_grade_overview()


    async def import_data(self):
        self.importer.import_data(os.environ.get("STUDY_JSON", "study.json"))
        self.study = self.database.load_study()

        if not self.study:
            raise Exception("No study data available")

        # Update the current semester reference
        self.semester = self.study.get_current_semester()

        if self.semester is None:
            raise Exception("No semester data available")

        # Remove all existing module widgets
        await self.query(ModuleWidget).remove()

        # Mount the first 4 modules before the grade overview plots
        modules = self.semester.modules
        await self.mount(
            *[ModuleWidget(m, self.gradient) for m in modules[:4]],
            before=self.query_one("#study-grade-overview"),
        )

        # Mount the 5th module after the semester grade overview (if present)
        if len(modules) > 4:
            await self.mount(
                ModuleWidget(modules[4], self.gradient, classes="bottom-module"),
                after=self.query_one("#semester-grade-overview"),
            )

        self.ects_digramm()
        self.study_grade_overview()
        self.semester_grade_overview()
        self.notify("Data imported!")


    @staticmethod
    def invert_grade(grade: float) -> float:
        return 6.0 - grade


    def ects_digramm(self):
        ects_overview = self.query_one("#ects-overview", PlotextPlot).plt
        ects_overview.plot([self.study.total_ects] * self.study.goal_duration, marker="-", color="green")
        ects_plot = self.study.get_ects_graph()

        if ects_plot:
            ects_overview.plot(self.study.get_average_ects_graph(), marker="braille", color="red")
            ects_overview.plot(ects_plot, marker="braille")

        ects_overview.xticks(list(range(1, self.study.goal_duration + 1)))
        ects_overview.xlim(1, self.study.goal_duration)
        ects_overview.yticks(list(range(0, 185, 20)))
        ects_overview.ylim(0, self.study.total_ects)
        ects_overview.title("ECTS Übersicht")
        ects_overview.xlabel("Monat")
        ects_overview.ylabel("ECTS")


    def study_grade_overview(self):
        y_ticks = [self.invert_grade(grade) for grade in self.grade_ticks]
        y_labels = [str(grade) for grade in self.grade_ticks]
        study_grade_overview = self.query_one("#study-grade-overview", PlotextPlot).plt
        study_grade_overview.plot([self.invert_grade(self.study.goal_grade)] * 9, marker="-", color="green")
        study_grade_plot = [self.invert_grade(grade) for grade in self.study.get_grade_graph()]

        if study_grade_plot:
            study_grade_overview.plot([self.invert_grade(self.study.get_average_grade())] * 9, marker="-", color="blue")
            study_grade_overview.plot(study_grade_plot, marker="braille")

        study_grade_overview.xticks(list(range(1, int((self.study.goal_duration / 6) + 1))))
        study_grade_overview.xlim(1, int(self.study.goal_duration / 6))
        study_grade_overview.yticks(y_ticks, y_labels)
        study_grade_overview.ylim(1.0, 5.0)
        study_grade_overview.title("Notenübersicht Studium")
        study_grade_overview.xlabel("Semester")
        study_grade_overview.ylabel("Note")


    def semester_grade_overview(self):
        y_ticks = [self.invert_grade(grade) for grade in self.grade_ticks]
        y_labels = [str(grade) for grade in self.grade_ticks]
        semester_grade_overview = self.query_one("#semester-grade-overview", PlotextPlot).plt
        semester_grade_overview.plot([self.invert_grade(self.study.goal_grade)] * 5, marker="-", color="green")
        average_grade = self.semester.get_average_grade()
        if average_grade is not None:
            semester_grade_overview.plot([self.invert_grade(average_grade)] * 5, marker="-", color="blue")

        grade_graph = self.semester.get_grade_graph()
        if grade_graph:
            semester_grade_overview.plot([self.invert_grade(grade) for grade in grade_graph], marker="braille")
        semester_grade_overview.xticks(list(range(1, 6)))
        semester_grade_overview.xlim(1, 5)
        semester_grade_overview.yticks(y_ticks, y_labels)
        semester_grade_overview.ylim(1.0, 5.0)
        semester_grade_overview.title("Notenübersicht Semester")
        semester_grade_overview.xlabel("Modul")
        semester_grade_overview.ylabel("Note")


def main():
    app = StudyDashboard()
    app.run()


if __name__ == "__main__":
    main()
