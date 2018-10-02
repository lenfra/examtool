# -*- coding: utf-8 -*-
class Course:
    def __init__(self):
        self.course_code = None
        self.course_code_modified = False

        self.course_name_swe = None
        self.course_name_swe_modified = False

        self.course_name_eng = None
        self.course_name_eng_modified = False

        self.course_credits = None
        self.course_credits_modified = False

        self.course_progression = None
        self.course_progression_modified = False

        self.course_version = None
        self.course_version_modified = False

        self.in_database = False

        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx

    def load_from_database(self, course_code, course_version, course_name_sve, course_name_eng, course_credit,
                           course_progression):

        self.course_code = course_code
        self.course_code_modified = True

        self.course_version = course_version
        self.course_version_modified = True

        self.course_name_swe = course_name_sve
        self.course_name_swe_modified = True

        self.course_name_eng = course_name_eng
        self.course_name_eng_modified = True

        self.course_credits = course_credit
        self.course_credits_modified = True

        self.course_progression = course_progression
        self.course_progression_modified = True

        self.in_database = True

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def get_course_code(self):
        return self.course_code

    def set_course_code(self, course_code):
        self.course_code = course_code
        self.course_code_modified = True

    def get_course_name_sve(self):
        return self.course_name_swe

    def set_course_name_sve(self, course_name_sve):
        self.course_name_swe = course_name_sve
        self.course_name_swe_modified = True

    def get_course_name_eng(self):
        return self.course_name_eng

    def set_course_name_eng(self, course_name_eng):
        self.course_name_eng = course_name_eng
        self.course_name_eng_modified = True

    def get_course_credit(self):
        return self.course_credits

    def set_course_credit(self, course_credit):
        self.course_credits = float(course_credit)
        self.course_credits_modified = True

    def get_course_progression(self):
        return self.course_progression

    def set_course_progression(self, course_progression):
        self.course_progression = course_progression
        self.course_progression_modified = True

    def get_course_version(self):
        return self.course_version

    def set_course_version(self, course_ver):
        self.course_version = float(course_ver)
        self.course_version_modified = True

    def insert_into_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("INSERT INTO Course \
                        (course_code, course_name_swe, course_name_eng,\
                         course_credits, course_progression, course_version)\
                         VALUES (?, ?, ?, ?, ?, ?)",
                       (self.course_code, self.course_name_swe,
                        self.course_name_eng, self.course_credits,
                        self.course_progression, self.course_version)
                       )

        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if self.course_name_swe_modified:
            cursor.execute("UPDATE Course\
                            SET course_name_swe = ?\
                            WHERE course_code = ? AND\
                            course_version = ?",
                           (self.course_name_swe, self.course_code,
                            self.course_version)
                           )

        if self.course_name_eng_modified:
            cursor.execute("UPDATE Course\
                            SET course_name_eng = ?\
                            WHERE course_code = ? AND\
                            course_version = ?",
                           (self.course_name_eng, self.course_code,
                            self.course_version)
                           )

        if self.course_credits_modified:
            cursor.execute("UPDATE Course \
                            SET course_credits = ?\
                      WHERE course_code = ? AND\
                      course_version = ?",
                           (self.course_credits, self.course_code, self.course_version)
                           )

        if self.course_progression_modified:
            cursor.execute("UPDATE Course \
                            SET course_progression = ? \
                            WHERE course_code = ? AND\
                            course_version = ?",
                           (self.course_progression, self.course_code,
                            self.course_version)
                           )

        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        # noinspection PyBroadException
        try:
            cursor.execute("DELETE FROM ILO "
                           "WHERE course_code = ? AND course_version = ?",
                           (self.course_code, self.course_version))

            cursor.execute("DELETE FROM Profile "
                           "WHERE course_code = ? AND "
                           "course_version = ?",
                           (self.course_code, self.course_version)
                           )

            cursor.execute("DELETE FROM Course "
                           "WHERE course_code = ? AND course_version = ?",
                           (self.course_code, self.course_version))
        except:
            print('error')

        self.cnx.commit()
        cursor.close()
        return
