# Import libraries
from typing import Iterable
from textual_plotext import PlotextPlot
from textual.color import Gradient
from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import *

from database import Database
from importer import Importer
from ui import *


class StudyDashboard(App):
    # CSS file path
    CSS_PATH = "ui.tcss"

    def __init__(self):
        # Superclass constructor
        super().__init__()

        # Config
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

        # Initialize database and importer
        self.database = Database()
        self.importer = Importer(self.database)

        # Import data from the JSON file
        self.importer.import_data("study.json")

        # Load study data from the database
        self.study = self.database.load_study()

        # Check if study data is available
        if not self.study:
            # Display an error message if study data is not available
            raise Exception("No study data available")

        self.semester = self.study.get_current_semester()

        # Check if semester data is available
        if self.semester is None:
            # Display an error message if semester data is not available
            raise Exception("No semester data available")


    def compose(self) -> ComposeResult:
        # Display the header
        yield Header(show_clock=True)

        # Display the ECTS overview
        yield PlotextPlot(id="ects-overview", disabled=True)

        # Display 4/5 modules
        yield ModuleWidget(self.semester.modules[0], self.gradient)
        yield ModuleWidget(self.semester.modules[1], self.gradient)
        yield ModuleWidget(self.semester.modules[2], self.gradient)
        yield ModuleWidget(self.semester.modules[3], self.gradient)

        # Display the grade overview
        yield PlotextPlot(id="study-grade-overview", disabled=True)
        yield PlotextPlot(id="semester-grade-overview", disabled=True)

        # Display the bottom module
        yield ModuleWidget(self.semester.modules[4], self.gradient, classes="bottom-module")


    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Import JSON", "Import study from file", self.import_data)


    def on_mount(self) -> None:
        # Set the theme
        self.theme = "dracula"

        # Display the plots
        self.ects_digramm()
        self.study_grade_overview()
        self.semester_grade_overview()


    def import_data(self):
        """
        Imports data from a JSON file
        :return: None
        """

        # Import data from the JSON file
        self.importer.import_data("study.json")

        # Reload study data from the database
        self.study = self.database.load_study()

        # Check if study data is available
        if not self.study:
            # Display an error message if study data is not available
            raise Exception("No study data available")

        # Update plots
        self.ects_digramm()
        self.study_grade_overview()
        self.semester_grade_overview()

        # Display a notification
        self.notify("Data imported!")


    @staticmethod
    def invert_grade(grade: float) -> float:
        """
        Inverts a grade value from 1.0 to 6.0 scale to 6.0 to 1.0 scale.
        :param grade: Grade value to invert
        :return: Inverted grade value
        """

        return 6.0 - grade


    def ects_digramm(self):
        """
        Displays a plot showing the ECTS curve.
        :return: None
        """

        # Get ects overview plot
        ects_overview = self.query_one("#ects-overview", PlotextPlot).plt

        # Plot goal ECTS
        ects_overview.plot([self.study.total_ects] * self.study.goal_duration, marker="-", color="green")

        # Plot the average ECTS curve
        ects_plot = self.study.get_ects_graph()

        # Check if data is available
        if ects_plot:
            # Plot the average ECTS curve and the ECTS curve
            ects_overview.plot(self.study.get_average_ects_graph(), marker="braille", color="red")
            ects_overview.plot(ects_plot, marker="braille")

        # Adjust the plot settings
        ects_overview.xticks(list(range(1, self.study.goal_duration + 1)))
        ects_overview.xlim(1, self.study.goal_duration)
        ects_overview.yticks(list(range(0, 185, 20)))
        ects_overview.ylim(0, self.study.total_ects)

        # Add labels and title to the plot
        ects_overview.title("ECTS Übersicht")
        ects_overview.xlabel("Monat")
        ects_overview.ylabel("ECTS")


    def study_grade_overview(self):
        """
        Displays a plot showing the grade overview for the whole current study.
        :return: None
        """

        # Define the y-axis ticks and labels
        y_ticks = [self.invert_grade(grade) for grade in self.grade_ticks]
        y_labels = [str(grade) for grade in self.grade_ticks]

        # Get study grade overview plot
        study_grade_overview = self.query_one("#study-grade-overview", PlotextPlot).plt

        # Plot the goal grade
        study_grade_overview.plot([self.invert_grade(self.study.goal_grade)] * 9, marker="-", color="green")

        # Plot the average grade
        study_grade_plot = [self.invert_grade(grade) for grade in self.study.get_grade_graph()]

        # Check if data is available
        if study_grade_plot:
            # Plot the average grade and the grades
            study_grade_overview.plot([self.invert_grade(self.study.get_average_grade())] * 9, marker="-", color="blue")
            study_grade_overview.plot(study_grade_plot, marker="braille")

        # Adjust the plot settings
        study_grade_overview.xticks(list(range(1, int((self.study.goal_duration / 6) + 1))))
        study_grade_overview.xlim(1, int(self.study.goal_duration / 6))
        study_grade_overview.yticks(y_ticks, y_labels)
        study_grade_overview.ylim(1.0, 5.0)

        # Add labels and title to the plot
        study_grade_overview.title("Notenübersicht Studium")
        study_grade_overview.xlabel("Semester")
        study_grade_overview.ylabel("Note")


    def semester_grade_overview(self):
        """
        Displays a plot showing the grade overview for the current semester.
        :return: None
        """

        # Define the y-axis ticks and labels
        y_ticks = [self.invert_grade(grade) for grade in self.grade_ticks]
        y_labels = [str(grade) for grade in self.grade_ticks]

        # Get semester grade overview plot
        semester_grade_overview = self.query_one("#semester-grade-overview", PlotextPlot).plt

        # Display reference lines
        semester_grade_overview.plot([self.invert_grade(self.study.goal_grade)] * 5, marker="-", color="green")

        # Plot the average grade for the current semester
        semester_grade_overview.plot([self.invert_grade(self.semester.get_average_grade())] * 5, marker="-", color="blue")

        # Plot the grades for the current semester
        semester_grade_overview.plot([self.invert_grade(grade) for grade in self.semester.get_grade_graph()], marker="braille")

        # Adjust the plot settings
        semester_grade_overview.xticks(list(range(1, 6)))
        semester_grade_overview.xlim(1, 5)
        semester_grade_overview.yticks(y_ticks, y_labels)
        semester_grade_overview.ylim(1.0, 5.0)

        # Add labels and title to the plot
        semester_grade_overview.title("Notenübersicht Semester")
        semester_grade_overview.xlabel("Modul")
        semester_grade_overview.ylabel("Note")


if __name__ == "__main__":
    app = StudyDashboard()
    app.run()