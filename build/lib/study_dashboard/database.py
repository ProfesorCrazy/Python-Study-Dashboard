# Import libraries
import sqlite3

from .models import *


class Database:
    def __init__(self, db_path: str = "database.db"):
        # Connect to the database
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

        # Check if database is set up
        if self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='study'").fetchone() is None:
            # Set up the database
            self.setup()


    def setup(self) -> None:
        """
        Used to set up the database and create the tables
        :return: None
        """

        # Create the Study table
        self.cursor.execute("""
           CREATE TABLE IF NOT EXISTS study
           (
               study_id      INTEGER PRIMARY KEY,
               name          TEXT    NOT NULL UNIQUE,
               start_date    DATE    NOT NULL,
               goal_grade    REAL    NOT NULL,
               goal_duration INTEGER NOT NULL,
               total_ects    INTEGER NOT NULL
           )
        """)

        # Create the Semester table
        self.cursor.execute("""
           CREATE TABLE IF NOT EXISTS semester
           (
               semester_id INTEGER PRIMARY KEY,
               name        TEXT NOT NULL UNIQUE,
               start_date  DATE NOT NULL,
               end_date    DATE NOT NULL,
               study_id    INTEGER,
               FOREIGN KEY (study_id) REFERENCES study (study_id)
           )
        """)

        # Create the Modul table
        self.cursor.execute("""
           CREATE TABLE IF NOT EXISTS module
           (
               module_id   INTEGER PRIMARY KEY,
               status      TEXT    NOT NULL,
               name        TEXT    NOT NULL UNIQUE,
               ects        INTEGER NOT NULL,
               start_date  DATE    NOT NULL,
               semester_id INTEGER,
               FOREIGN KEY (semester_id) REFERENCES semester (semester_id)
           )
        """)

        # Create the Progress table
        self.cursor.execute("""
           CREATE TABLE IF NOT EXISTS progress
           (
               progress_id     INTEGER PRIMARY KEY,
               total_units     INTEGER NOT NULL,
               completed_units INTEGER NOT NULL,
               learned_units   INTEGER NOT NULL,
               module_id       INTEGER NOT NULL,
               FOREIGN KEY (module_id) REFERENCES module (module_id)
           )
       """)

        # Create the Exam table with fields for all exam types
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exam
            (
                exam_id                INTEGER PRIMARY KEY,
                exam_type              TEXT    NOT NULL,
                exam_date              DATE    NOT NULL,
                completed              BOOLEAN NOT NULL,
                module_id              INTEGER NOT NULL,

                pages_written          INTEGER,
                pages_target           INTEGER,
                literature_progress    INTEGER,
                outline_done           BOOLEAN,

                analysis_progress      INTEGER,
                solution_defined       BOOLEAN,
                reflection_done        BOOLEAN,

                milestones_done        INTEGER,
                milestones_total       INTEGER,
                product_finished       BOOLEAN,

                slides_done            INTEGER,
                slides_total           INTEGER,
                rehearsals_done        INTEGER,
                ready_for_presentation BOOLEAN,

                phase_1_done           BOOLEAN,
                phase_2_done           BOOLEAN,
                phase_3_done           BOOLEAN,
                final_submission_ready BOOLEAN,

                tasks_done             INTEGER,
                tasks_total            INTEGER,

                submitted              BOOLEAN,
                presentation_ready     BOOLEAN,
                questions_prepared     BOOLEAN,

                FOREIGN KEY (module_id) REFERENCES module (module_id)
            )
        """)

        # Create the Grade table
        self.cursor.execute("""
           CREATE TABLE IF NOT EXISTS grade
           (
               grade_id INTEGER PRIMARY KEY,
               value    REAL    NOT NULL,
               weight   REAL    NOT NULL,
               exam_id  INTEGER NOT NULL,
               FOREIGN KEY (exam_id) REFERENCES exam (exam_id)
           )
        """)


    def get_study_id(self, name: str) -> int | None:
        """
        Retrieves the study_id for a given study name from the database.
        :param name: The name of the study to retrieve the ID for.
        :return: The study_id if found, otherwise None.
        """

        # Get the id of the study
        self.cursor.execute("SELECT study_id FROM study WHERE name = ?", (name,))
        row = self.cursor.fetchone()

        # Return the id if found, otherwise return None
        return row[0] if row else None


    def get_semester_id(self, study_id: int, name: str) -> int | None:
        """
        Retrieves the semester_id for a given study_id and semester name from the database.
        :param study_id: The id of the study the semester belongs to.
        :param name: The name of the semester to retrieve the ID for.
        :return: The semester_id if found, otherwise None.
        """

        # Get the id of the semester
        self.cursor.execute(
            "SELECT semester_id FROM semester WHERE study_id = ? AND name = ?",
            (study_id, name,),
        )
        row = self.cursor.fetchone()

        # Return the id if found, otherwise return None
        return row[0] if row else None


    def get_module_id(self, semester_id: int, name: str) -> int | None:
        """
        Retrieves the module_id for a given semester_id and module name from the database.
        :param semester_id: The id of the semester the module belongs to.
        :param name: The name of the module to retrieve the ID for.
        :return: The module_id if found, otherwise None.
        """

        # Get the id of the module
        self.cursor.execute(
            "SELECT module_id FROM module WHERE semester_id = ? AND name = ?",
            (semester_id, name,),
        )
        row = self.cursor.fetchone()

        # Return the id if found, otherwise return None
        return row[0] if row else None


    def get_progress_id(self, module_id: int) -> int | None:
        """
        Retrieves the progress_id for a given module_id from the database.
        :param module_id: The id of the module the progress belongs to.
        :return: The progress_id if found, otherwise None.
        """

        # Get the id of the progress
        self.cursor.execute("SELECT progress_id FROM progress WHERE module_id = ?", (module_id,))
        row = self.cursor.fetchone()

        # Return the id if found, otherwise return None
        return row[0] if row else None


    def get_exam_id(self, module_id: int, exam_type: str) -> int | None:
        """
        Retrieves the exam_id for a given module_id and exam_type from the database.
        :param module_id: The id of the module the exam belongs to.
        :param exam_type: The type of the exam to retrieve the ID for.
        :return: The exam_id if found, otherwise None.
        """

        # Get the id of the exam
        self.cursor.execute(
            "SELECT exam_id FROM exam WHERE module_id = ? AND exam_type = ?",
            (module_id, exam_type,),
        )
        row = self.cursor.fetchone()

        # Return the id if found, otherwise return None
        return row[0] if row else None


    def get_grade_id(self, exam_id: int) -> int | None:
        """
        Retrieves the grade_id for a given exam_id from the database.
        :param exam_id: The id of the exam the grade belongs to.
        :return: The grade_id if found, otherwise None.
        """

        # Get the id of the grade
        self.cursor.execute("SELECT grade_id FROM grade WHERE exam_id = ?", (exam_id,))
        row = self.cursor.fetchone()

        # Return the id if found, otherwise return None
        return row[0] if row else None


    @staticmethod
    def create_exam(exam_row, grade: Grade | None) -> Exam:
        """
        Create an Exam object from a database row and optional grade.
        :param exam_row: Database row containing exam data
        :param grade: Grade object associated with the exam, if available
        :return: Exam object
        """

        # Extract exam type from the database row
        exam_type = exam_row["exam_type"]

        # Initialize Exam object based on exam type
        base_data = {
            "exam_date": date.fromisoformat(exam_row["exam_date"]),
            "completed": bool(exam_row["completed"]),
            "grade": grade,
        }

        # Check if exam type is one of the specific exam types and initialize accordingly
        if exam_type == "HomeworkExam":
            # Extract specific exam fields from the database row and initialize HomeworkExam object
            return HomeworkExam(
                **base_data,
                pages_written=exam_row["pages_written"] or 0,
                pages_target=exam_row["pages_target"] or 10,
                literature_progress=exam_row["literature_progress"] or 0,
                outline_done=bool(exam_row["outline_done"]),
            )

        if exam_type == "SeminarPaperExam":
            # Extract specific exam fields from the database row and initialize SeminarPaperExam object
            return SeminarPaperExam(
                **base_data,
                pages_written=exam_row["pages_written"] or 0,
                pages_target=exam_row["pages_target"] or 10,
                literature_progress=exam_row["literature_progress"] or 0,
                outline_done=bool(exam_row["outline_done"]),
            )

        if exam_type == "CaseStudyExam":
            # Extract specific exam fields from the database row and initialize CaseStudyExam object
            return CaseStudyExam(
                **base_data,
                analysis_progress=exam_row["analysis_progress"] or 0,
                solution_defined=bool(exam_row["solution_defined"]),
                reflection_done=bool(exam_row["reflection_done"]),
            )

        if exam_type == "ProjectReportExam":
            # Extract specific exam fields from the database row and initialize ProjectReportExam object
            return ProjectReportExam(
                **base_data,
                milestones_done=exam_row["milestones_done"] or 0,
                milestones_total=exam_row["milestones_total"] or 1,
                product_finished=bool(exam_row["product_finished"]),
                reflection_done=bool(exam_row["reflection_done"]),
            )

        if exam_type == "ProjectPresentationExam":
            # Extract specific exam fields from the database row and initialize ProjectPresentationExam object
            return ProjectPresentationExam(
                **base_data,
                slides_done=exam_row["slides_done"] or 0,
                slides_total=exam_row["slides_total"] or 1,
                rehearsals_done=exam_row["rehearsals_done"] or 0,
                ready_for_presentation=bool(exam_row["ready_for_presentation"]),
            )

        if exam_type == "PortfolioExam":
            # Extract specific exam fields from the database row and initialize PortfolioExam object
            return PortfolioExam(
                **base_data,
                phase_1_done=bool(exam_row["phase_1_done"]),
                phase_2_done=bool(exam_row["phase_2_done"]),
                phase_3_done=bool(exam_row["phase_3_done"]),
                final_submission_ready=bool(exam_row["final_submission_ready"]),
            )

        if exam_type == "AdvancedWorkbookExam":
            # Extract specific exam fields from the database row and initialize AdvancedWorkbookExam object
            return AdvancedWorkbookExam(
                **base_data,
                tasks_done=exam_row["tasks_done"] or 0,
                tasks_total=exam_row["tasks_total"] or 6,
            )

        if exam_type == "BachelorThesisExam":
            # Extract specific exam fields from the database row and initialize BachelorThesisExam object
            return BachelorThesisExam(
                **base_data,
                pages_written=exam_row["pages_written"] or 0,
                pages_target=exam_row["pages_target"] or 40,
                milestones_done=exam_row["milestones_done"] or 0,
                milestones_total=exam_row["milestones_total"] or 4,
                submitted=bool(exam_row["submitted"]),
            )

        if exam_type == "ColloquiumExam":
            # Extract specific exam fields from the database row and initialize ColloquiumExam object
            return ColloquiumExam(
                **base_data,
                presentation_ready=bool(exam_row["presentation_ready"]),
                rehearsals_done=exam_row["rehearsals_done"] or 0,
                questions_prepared=bool(exam_row["questions_prepared"]),
            )

        # Return base Exam object if exam has no special type
        return Exam(**base_data)


    def load_study(self) -> Study | None:
        """
        Used to load the study data from the database
        :return: Study | None
        """

        # Read Study data from the database
        self.cursor.execute("SELECT * FROM study")
        study_row = self.cursor.fetchone()

        # Check if there is any data in the database
        if study_row is None:
            return None

        # Create the Study object
        study = Study(
            name=study_row[1],
            start_date=date.fromisoformat(study_row[2]),
            goal_grade=study_row[3],
            goal_duration=study_row[4],
            total_ects=study_row[5]
        )

        # Read Semester data from the database
        self.cursor.execute(
            "SELECT semester_id, name, start_date, end_date FROM semester WHERE study_id = ?",
            (study_row[0],)
        )
        semester_rows = self.cursor.fetchall()

        # Create the Semester objects
        for semester_row in semester_rows:
            # Create a Semester object
            semester = Semester(
                name=semester_row[1],
                start_date=date.fromisoformat(semester_row[2]),
                end_date=date.fromisoformat(semester_row[3])
            )

            # Read Module data from the database
            self.cursor.execute(
                "SELECT module_id, status, name, ects, start_date FROM module WHERE semester_id = ?",
                (semester_row[0],)
            )
            module_rows = self.cursor.fetchall()

            # Create the Module objects
            for module_row in module_rows:
                # Read Progress data from the database
                self.cursor.execute(
                    "SELECT total_units, completed_units, learned_units FROM progress WHERE module_id = ?",
                    (module_row[0],)
                )
                progress_row = self.cursor.fetchone()

                # Create a Progress object
                progress = Progress(
                    total_units=progress_row[0],
                    completed_units=progress_row[1],
                    learned_units=progress_row[2]
                )

                # Read Exam data from the database
                self.cursor.execute(
                    "SELECT * FROM exam WHERE module_id = ?",
                    (module_row[0],)
                )
                exam_row = self.cursor.fetchone()

                grade = None
                # Check if exam data exists in the database
                if exam_row is not None:
                    # Read Grade data from the database
                    self.cursor.execute(
                        "SELECT value, weight FROM grade WHERE exam_id = ?",
                        (exam_row[0],)
                    )
                    grade_row = self.cursor.fetchone()

                    # Check if grade data exists in the database
                    if grade_row is not None:
                        # Create a Grade object
                        grade = Grade(
                            value=grade_row[0],
                            weight=grade_row[1]
                        )

                    # Create an Exam object
                    exam = self.create_exam(exam_row, grade)
                else:
                    # Create an Exam object
                    exam = Exam(
                        exam_date=date.today(),
                        completed=False,
                        grade=None,
                    )

                # Create a Module object
                module = Module(
                    status=module_row[1],
                    name=module_row[2],
                    ects=module_row[3],
                    start_date=date.fromisoformat(module_row[4]),
                    progress=progress,
                    exam=exam,
                )

                # Add the Module object to the Semester object
                semester.modules.append(module)

            # Add the Semester object to the Study object
            study.semesters.append(semester)

        # Return the Study object
        return study
