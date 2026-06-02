# Import libraries
import json
from .database import Database


class Importer:
    """
    Class for importing data into the database.
    """

    def __init__(self, database: Database):
        self.database = database
        self.connection = database.connection
        self.cursor = database.cursor

    @staticmethod
    def create_exam_data(exam: dict, module_id: int) -> dict:
        """
        Used to create exam data that can be inserted into the database.
        :param exam:
        :param module_id:
        :return:
        """

        # Extract exam type from the exam data
        exam_type = exam["exam_type"]

        # Create exam data dictionary
        exam_data = {
            "exam_type": exam_type,
            "exam_date": exam["exam_date"],
            "completed": int(exam.get("completed", False)),
            "module_id": module_id,
        }

        # Check if exam is HomeworkExam or SeminarPaperExam
        if exam_type in ["HomeworkExam", "SeminarPaperExam"]:
            # Extract specific exam fields for HomeworkExam and SeminarPaperExam objects
            exam_data.update({
                "pages_written": exam.get("pages_written", 0),
                "pages_target": exam.get("pages_target", 10),
                "literature_progress": exam.get("literature_progress", 0),
                "outline_done": int(exam.get("outline_done", False)),
            })

        # Check if exam is CaseStudyExam
        elif exam_type == "CaseStudyExam":
            # Extract specific exam fields for CaseStudyExam object
            exam_data.update({
                "analysis_progress": exam.get("analysis_progress", 0),
                "solution_defined": int(exam.get("solution_defined", False)),
                "reflection_done": int(exam.get("reflection_done", False)),
            })

        # Check if exam is ProjectReportExam
        elif exam_type == "ProjectReportExam":
            # Extract specific exam fields for ProjectReportExam object
            exam_data.update({
                "milestones_done": exam.get("milestones_done", 0),
                "milestones_total": exam.get("milestones_total", 1),
                "product_finished": int(exam.get("product_finished", False)),
                "reflection_done": int(exam.get("reflection_done", False)),
            })

        # Check if exam is ProjectPresentationExam
        elif exam_type == "ProjectPresentationExam":
            # Extract specific exam fields for ProjectPresentationExam object
            exam_data.update({
                "slides_done": exam.get("slides_done", 0),
                "slides_total": exam.get("slides_total", 1),
                "rehearsals_done": exam.get("rehearsals_done", 0),
                "ready_for_presentation": int(exam.get("ready_for_presentation", False)),
            })

        # Check if exam is PortfolioExam
        elif exam_type == "PortfolioExam":
            # Extract specific exam fields for PortfolioExam object
            exam_data.update({
                "phase_1_done": int(exam.get("phase_1_done", False)),
                "phase_2_done": int(exam.get("phase_2_done", False)),
                "phase_3_done": int(exam.get("phase_3_done", False)),
                "final_submission_ready": int(exam.get("final_submission_ready", False)),
            })

        # Check if exam is AdvancedWorkbookExam
        elif exam_type == "AdvancedWorkbookExam":
            # Extract specific exam fields for AdvancedWorkbookExam object
            exam_data.update({
                "tasks_done": exam.get("tasks_done", 0),
                "tasks_total": exam.get("tasks_total", 6),
            })

        # Check if exam is BachelorThesisExam
        elif exam_type == "BachelorThesisExam":
            # Extract specific exam fields for BachelorThesisExam object
            exam_data.update({
                "pages_written": exam.get("pages_written", 0),
                "pages_target": exam.get("pages_target", 40),
                "milestones_done": exam.get("milestones_done", 0),
                "milestones_total": exam.get("milestones_total", 4),
                "submitted": int(exam.get("submitted", False)),
            })

        # Check if exam is ColloquiumExam
        elif exam_type == "ColloquiumExam":
            # Extract specific exam fields for ColloquiumExam object
            exam_data.update({
                "presentation_ready": int(exam.get("presentation_ready", False)),
                "rehearsals_done": exam.get("rehearsals_done", 0),
                "questions_prepared": int(exam.get("questions_prepared", False)),
            })

        # Return exam data
        return exam_data


    def import_data(self, file_path: str) -> None:
        """
        Used to import data from a JSON file into the database
        :param file_path: Path to the JSON file
        :return: None
        """

        with open(file_path) as f:
            data = json.load(f)

        # Check if the study already exists in the database
        study_id = self.database.get_study_id(data["name"])

        # If the study does not exist, insert it into the database if it does exist, update it
        if study_id is None:
            # Create the study in the database
            self.cursor.execute("""
                                INSERT INTO study (name, start_date, goal_grade, goal_duration, total_ects)
                                VALUES (?, ?, ?, ?, ?)
                                """, (
                                    data["name"],
                                    data["start_date"],
                                    data["goal_grade"],
                                    data["goal_duration"],
                                    data["total_ects"],
            ))

            # Parse study id
            study_id = self.cursor.lastrowid
        else:
            # Update the study in the database
            self.cursor.execute("""
                                UPDATE study
                                SET start_date    = ?,
                                    goal_grade    = ?,
                                    goal_duration = ?,
                                    total_ects    = ?
                                WHERE study_id = ?
                                """, (
                                    data["start_date"],
                                    data["goal_grade"],
                                    data["goal_duration"],
                                    data["total_ects"],
                                    study_id,
            ))

        # Enumerate semesters
        for semester in data.get("semesters", []):
            # Check if the semester already exists in the database
            semester_id = self.database.get_semester_id(study_id, semester["name"])

            # If the semester does not exist, insert it into the database if it does exist, update it
            if semester_id is None:
                # Insert semester into the database
                self.cursor.execute("""
                                    INSERT INTO semester (name, start_date, end_date, study_id)
                                    VALUES (?, ?, ?, ?)
                                    """, (
                                        semester["name"],
                                        semester["start_date"],
                                        semester["end_date"],
                                        study_id,
                ))

                # Parse semester id
                semester_id = self.cursor.lastrowid
            else:
                # Update the semester in the database
                self.cursor.execute("""
                                    UPDATE semester
                                    SET start_date = ?,
                                        end_date   = ?
                                    WHERE semester_id = ?
                                    """, (
                                        semester["start_date"],
                                        semester["end_date"],
                                        semester_id,
                ))

            # Enumerate modules
            for module in semester.get("modules", []):
                # Check if the module already exists in the database
                module_id = self.database.get_module_id(semester_id, module["name"])

                # Check if the module already exists in the database
                if module_id is None:
                    # Insert module into the database
                    self.cursor.execute("""
                                        INSERT INTO module (status, name, ects, start_date, semester_id)
                                        VALUES (?, ?, ?, ?, ?)
                                        """, (
                                            module["status"],
                                            module["name"],
                                            module["ects"],
                                            module["start_date"],
                                            semester_id,
                    ))

                    # Parse module id
                    module_id = self.cursor.lastrowid
                else:
                    # Update the module in the database
                    self.cursor.execute("""UPDATE module SET status     = ?,
                                            ects       = ?,
                                            start_date = ?
                                        WHERE module_id = ?
                                        """, (
                                            module["status"],
                                            module["ects"],
                                            module["start_date"],
                                            module_id,
                    ))

                # Check if the progress already exists in the database
                progress_id = self.database.get_progress_id(module_id)

                # Get the progress data from the json file
                progress = module["progress"]

                # If the progress already exists in the database, it will not be created, so it will not be created
                if progress_id is None:
                    # Insert progress into the database
                    self.cursor.execute("""INSERT INTO progress (total_units, completed_units, learned_units, module_id)
                                           VALUES (?, ?, ?, ?)
                                        """, (
                                            progress["total_units"],
                                            progress["completed_units"],
                                            progress["learned_units"],
                                            module_id,
                    ))
                else:
                    # Update the progress in the database
                    self.cursor.execute("""
                                        UPDATE progress
                                        SET total_units     = ?,
                                            completed_units = ?,
                                            learned_units   = ?
                                        WHERE module_id = ?
                                        """, (
                                            progress["total_units"],
                                            progress["completed_units"],
                                            progress["learned_units"],
                                            module_id,
                    ))

                # Get exam data from the json file
                exam = module["exam"]

                # Check if the exam already exists in the database
                exam_id = self.database.get_exam_id(module_id, exam["exam_type"])

                # Generate exam data
                exam_data = self.create_exam_data(exam, module_id)

                # If the exam already exists in the database, it will not be created, so it will not be created
                if exam_id is None:
                    # Construct column names and placeholders from the exam data
                    columns = ", ".join(exam_data.keys())
                    placeholders = ", ".join(["?"] * len(exam_data))

                    # Insert exam into the database
                    self.cursor.execute(
                        f"INSERT INTO exam ({columns}) VALUES ({placeholders})",
                        tuple(exam_data.values())
                    )

                    # Parse exam id
                    exam_id = self.cursor.lastrowid
                else:
                    # Construct set clause from the exam data
                    set_clause = ", ".join([f"{key} = ?" for key in exam_data.keys()])

                    # Update exam in the database
                    self.cursor.execute(
                        f"UPDATE exam SET {set_clause} WHERE exam_id = ?",
                        tuple(exam_data.values()) + (exam_id,)
                    )

                # Check if the grade already exists in the database
                grade_id = self.database.get_grade_id(exam_id)

                # Get the grade data from the json file
                grade = exam.get("grade")

                # Check if grade exists in the JSON file
                if grade is None:
                    # Check if grade exists in the database
                    if grade_id is not None:
                        # Delete grade from the database
                        self.cursor.execute("DELETE FROM grade WHERE exam_id = ?", (exam_id,))
                else:
                    # Check if grade exists in the database and update it if it does, insert it if it does not exist
                    if grade_id is None:
                        # Insert grade into the database
                        self.cursor.execute("""
                                            INSERT INTO grade (value, weight, exam_id)
                                            VALUES (?, ?, ?)
                                            """, (
                                                grade["value"],
                                                grade["weight"],
                                                exam_id,
                        ))
                    else:
                        # Update grade in the database
                        self.cursor.execute("""
                                            UPDATE grade
                                            SET value  = ?,
                                                weight = ?
                                            WHERE exam_id = ?
                                            """, (
                                                grade["value"],
                                                grade["weight"],
                                                exam_id,
                        ))

        # Commit changes to the database
        self.connection.commit()
