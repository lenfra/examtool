# -*- coding: utf-8 -*-
class ILO:
    def __init__(self):
        self.goal = None
        self.goal_modified = False

        self.course_code = None
        self.course_code_modified = False

        self.course_version = None
        self.course_version_modified = False

        self.description = None
        self.description_modified = False

        self.tags = None
        self.tags_modified = False

        self.in_database = False
        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx

    def load_from_database(self, goal, course_code, course_version, description, tags):
        self.goal = goal
        self.goal_modified = True

        self.course_code = course_code

        self.course_version = course_version

        self.description = description
        self.description_modified = True

        self.tags = tags
        self.tags_modified = True

        self.in_database = True
        return

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def get_goal(self):
        return self.goal

    def set_goal(self, goal):
        self.goal = goal
        self.goal_modified = True

    def get_course_code(self):
        return self.course_code

    def set_course_code(self, course_code):
        self.course_code = course_code
        self.course_code_modified = True

    def get_course_version(self):
        return self.course_version

    def set_course_version(self, course_version):
        self.course_version = course_version
        self.course_version_modified = True

    def get_description(self):
        return self.description

    def set_description(self, desc):
        self.description = desc
        self.description_modified = True

    def get_tags(self):
        return self.tags

    def set_tags(self, tags):
        self.tags = tags
        self.tags_modified = True

    def insert_into_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("INSERT INTO ILO \
                        (goal, course_code, course_version, description, tags)\
                        VALUES (?, ?, ?, ?, ?)",
                       (self.goal, self.course_code, self.course_version,
                        self.description, self.tags))
        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if self.description_modified:
            cursor.execute("UPDATE ILO\
                            SET description = ?\
                            WHERE goal = ?",
                           (self.description, self.goal)
                           )

        if self.tags_modified:
            cursor.execute("UPDATE ILO\
                            SET tags = ?\
                            WHERE goal = ?",
                           (self.tags, self.goal)
                           )
        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("DELETE FROM Questions_has_ILO\
                        WHERE goal = ?",
                       (self.goal,))

        cursor.execute("DELETE FROM ILO \
                        WHERE goal = ?",
                       self.goal)
        self.cnx.commit()
        cursor.close()
        return
