# -*- coding: utf-8 -*-
import json


class Profile:
    def __init__(self, course_code, course_version):
        self.course_code = course_code
        self.course_code_modified = False

        self.course_version = course_version
        self.course_version_modified = False

        self.instructions = ''
        self.instructions_modified = False

        self.document_class = ''
        self.document_class_modified = False

        self.default_packages = ''
        self.default_packages_modified = False

        self.exam_aids = ''
        self.exam_aids_modified = False

        self.type_of_exam = ''
        self.type_of_exam_modified = False

        self.time_limit = ''
        self.time_limit_modified = False

        self.authors = ''
        self.authors_modified = False

        self.language = ''
        self.language_modified = False

        self.number_of_questions = ''
        self.number_of_questions_modified = False

        self.exam_date = ''
        self.exam_date_modified = False

        self.ilo = ''
        self.ilo_modified = False

        self._grade_limits = {"PF": False,
                              "Percent": False,
                              "ILO_based_grading": False,
                              "F": None,
                              "Fx": None,
                              "Pass": "0",
                              "D": "0",
                              "C": "0",
                              "B": "0",
                              "A": "0",
                              }

        self._grade_limits_modified = False

        self._grade_comment = ''
        self._grade_comment_modified = False

        self.allow_same_tags = False
        self.allow_same_tags_modified = False

        self.inDatabase = False
        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx
        return

    def load_from_database(self, instruction, document_class, default_packages, authors,
                           ilo, exam_aids, type_of_exam, time_limit, language,
                           number_of_questions, exam_date, grade_limit, grade_comment, allow_same_tags):

        self.instructions = instruction
        self.instructions_modified = True

        self.document_class = document_class
        self.document_class_modified = True

        self.default_packages = default_packages
        self.default_packages_modified = True

        self.exam_aids = exam_aids
        self.exam_aids_modified = True

        self.type_of_exam = type_of_exam
        self.type_of_exam_modified = True

        self.time_limit = time_limit
        self.time_limit_modified = True

        self.authors = authors
        self.authors_modified = True

        self.language = language
        self.language_modified = True

        self.number_of_questions = number_of_questions
        self.number_of_questions_modified = True

        self.exam_date = exam_date
        self.exam_date_modified = True

        self.ilo = ilo
        self.ilo_modified = True

        if grade_limit is not None:
            self._grade_limits = grade_limit
            self._grade_limits_modified = True

        self._grade_comment = grade_comment
        self._grade_comment_modified = True

        self.allow_same_tags = allow_same_tags
        self.allow_same_tags_modified = True

        self.inDatabase = True

    def set_course_code(self, course_code):
        self.course_code = course_code
        self.course_code_modified = True

    def get_course_code(self):
        return self.course_code

    def set_course_version(self, course_version):
        self.course_version = course_version
        self.course_version_modified = False

    def get_course_version(self):
        return self.course_version

    def set_instructions(self, instruction):
        self.instructions = instruction
        self.instructions_modified = True

    def get_instructions(self):
        return self.instructions

    def set_document_class(self, document_class):
        self.document_class = document_class
        self.document_class_modified = True

    def get_document_class(self):
        return self.document_class

    def set_default_packages(self, default_packages):
        self.default_packages = default_packages
        self.default_packages_modified = True

    def get_default_packages(self):
        return self.default_packages

    def set_exam_aids(self, exam_aids):
        self.exam_aids = exam_aids
        self.exam_aids_modified = True

    def get_exam_aids(self):
        return self.exam_aids

    def set_type_of_exam(self, type_of_exam):
        self.type_of_exam = type_of_exam
        self.type_of_exam_modified = True

    def get_type_of_exam(self):
        return self.type_of_exam

    def set_time_limit(self, time_limit):
        self.time_limit = time_limit
        self.time_limit_modified = True

    def get_time_limit(self):
        return self.time_limit

    def set_authors(self, authors):
        self.authors = authors
        self.authors_modified = True

    def get_authors(self):
        return self.authors

    def set_language(self, language):
        self.language = language
        self.language_modified = True

    def get_language(self):
        return self.language

    def set_number_of_questions(self, number_of_questions):
        self.number_of_questions = number_of_questions
        self.number_of_questions_modified = True

    def get_number_of_questions(self):
        return self.number_of_questions

    def set_exam_date(self, exam_date):
        self.exam_date = exam_date
        self.exam_date_modified = True

    def get_exam_date(self):
        return self.exam_date

    def set_ilo(self, ilo):
        if not (ilo == '' or ilo == ' ' or ilo is None):
            self.ilo = ilo
            self.ilo_modified = True

    def get_ilo(self):
        return self.ilo

    def get_grade_comment(self):
        return self._grade_comment

    def set_grade_comment(self, comment):
        self._grade_comment_modified = True
        self._grade_comment = comment
        return True

    def get_grade_limits(self, grade=None):
        if grade is None:
            return self._grade_limits
        else:
            return self._grade_limits.get(grade, None)

    def set_grade_limits(self, grade, value):
        if value is None:
            return

        self._grade_limits_modified = True
        try:
            if isinstance(value, str):
                self._grade_limits[grade] = float(value)
            else:
                self._grade_limits[grade] = value

            if self._grade_limits["PF"]:
                for k in self._grade_limits.keys():
                    if k != ('Pass' or 'PF' or 'Percent'):
                        self._grade_limits[k] = None

        except TypeError as err:
            print(err)
            return False

    def get_allow_same_tags(self):
        return self.allow_same_tags

    def set_allow_same_tags(self, allow_tag):
        self.allow_same_tags = allow_tag
        self.allow_same_tags_modified = True

    def insert_into_database(self):
        # This will be run when a profile is created for the first time, which
        # is when a new course will be created.
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("INSERT INTO Profile "
                       "(`course_code`, `course_version`) "
                       "VALUES (?, ?)"
                       , (self.course_code, self.course_version))
        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None
        cursor = self.cnx.cursor()
        if self.instructions_modified:
            cursor.execute("UPDATE Profile "
                           "SET instruction_id = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.instructions, self.course_code, self.course_version)
                           )
        if self.document_class_modified:
            cursor.execute("UPDATE Profile "
                           "SET document_class_id = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.document_class, self.course_code, self.course_version)
                           )
        if self.default_packages_modified:
            cursor.execute("UPDATE Profile "
                           "SET default_package_id = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.default_packages, self.course_code,
                            self.course_version)
                           )
        if self.authors_modified:
            cursor.execute("UPDATE Profile "
                           "SET author_id = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.authors, self.course_code, self.course_version)
                           )
        if self.ilo_modified:
            cursor.execute("UPDATE Profile "
                           "SET goal = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.ilo, self.course_code, self.course_version)
                           )
        if self.exam_aids_modified:
            cursor.execute("UPDATE Profile "
                           "SET exam_aids = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.exam_aids, self.course_code, self.course_version)
                           )
        if self.type_of_exam_modified:
            cursor.execute("UPDATE Profile "
                           "SET exam_type = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.type_of_exam, self.course_code, self.course_version)
                           )
        if self.time_limit_modified:
            cursor.execute("UPDATE Profile "
                           "SET time_limit = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.time_limit, self.course_code, self.course_version)
                           )
        if self.language_modified:
            cursor.execute("UPDATE Profile "
                           "SET language = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.language, self.course_code, self.course_version)
                           )
        if self.number_of_questions_modified:
            cursor.execute("UPDATE Profile "
                           "SET number_of_questions = ? "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.number_of_questions, self.course_code, self.course_version)
                           )
        if self._grade_limits_modified:
            cursor.execute("UPDATE Profile \
                            SET grade_limits = ?\
                            WHERE course_code = ? AND\
                             course_version = ?",
                           (json.dumps(self._grade_limits),
                            self.course_code,
                            self.course_version)
                           )

        if self._grade_comment_modified:
            cursor.execute("UPDATE Profile \
                            SET grade_comment = ?\
                            WHERE course_code = ? AND\
                             course_version = ?",
                           (self._grade_comment,
                            self.course_code,
                            self.course_version)
                           )

        if self.allow_same_tags_modified:
            cursor.execute("UPDATE Profile \
                           SET allow_same_tags = ?\
                           WHERE course_code = ? AND\
                           course_version = ?",
                           (self.allow_same_tags,
                            self.course_code,
                            self.course_version)
                           )

        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("DELETE FROM Profile "
                       "WHERE course_code = ? AND "
                       "course_version = ?",
                       (self.course_code, self.course_version)
                       )

        self.cnx.commit()
        cursor.close()
        return
