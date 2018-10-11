# -*- coding: utf-8 -*-
from datetime import datetime
import json


class Question:
    def __init__(self):
        self._editable = True

        self._question_id = ""
        self._questionID_modified = False

        self._language = ""
        self._language_modified = False

        self._points = 0
        self._points_modified = False

        self._question = ""
        self._question_modified = False

        self._answer = ""
        self._answer_modified = False

        self._usable = 0
        self._usable_modified = False

        self._not_in_same_exam = set()
        self._not_in_same_exam_modified = False

        self._tags = []
        self._tags_modified = False

        self._package_requirement = []
        self._package_requirement_modified = False

        self._graphics_requirement = set()
        self._graphics_requirement_modified = False

        self._bibliography_requirement = []
        self._bibliography_requirement_modified = False

        self._declarationRequirement = set()
        self._declaration_requirement_modified = False

        self._course = {"course_code": "",
                        "course_version": "",
                        }
        self._course_modified = False

        self._ilo = []
        self._ilo_modified = False

        self.inDatabase = False
        self._modified = False
        self.lastUsed = datetime.strptime('1970-01-01', '%Y-%m-%d')
        self.cnx = None
        self.ExamDB = None
        self.examDate = None

    def set_connector(self, cnx):
        self.cnx = cnx
        return

    def set_exam_database(self, exam_db):
        self.ExamDB = exam_db

    def load_from_database(self, question_id, lang, points, question, answer, usable, goals,
                           course_code, course_version, tags, not_in_same_exam, last_used, declaration_requirement,
                           bibliography_requirement, package_requirement):

        self._question_id = question_id
        self._language = lang

        if isinstance(points, str):
            self._points = float(points)
        else:
            self._points = points

        self._question = question
        self._answer = answer
        self._usable = int(usable)
        self._course["course_code"] = course_code
        self._course["course_version"] = course_version

        if goals:
            if isinstance(goals, str):
                self.append_to_ilo(goals)
            else:
                for _ilo in goals:
                    self.append_to_ilo(_ilo)

        if tags:
            self.set_tags(json.loads(tags))

        for similar in not_in_same_exam:
            self._not_in_same_exam.add(similar)

        self.lastUsed = last_used

        self.set_declaration_requirement(declaration_requirement)
        self.set_bibliography_requirement(bibliography_requirement)
        self.set_package_requirement(package_requirement)

        self._modified = False  # Nothing has been modified.
        return

    def import_question(self, question_id, lang, points, question, answer, usable, goals,
                        course_code, course_version, tags, not_in_same_exam, last_used, declaration_requirement,
                        bibliography_requirement, graphics_requirement, package_requirement):
        """
        Method used for copying a question, should be used with export_questions as indata.
        :param question_id:
        :param lang:
        :param points:
        :param question:
        :param answer:
        :param usable:
        :param goals: List of goals
        :param course_code:
        :param course_version:
        :param tags: List of tags
        :param not_in_same_exam:
        :param last_used:
        :param declaration_requirement:
        :param bibliography_requirement:
        :param graphics_requirement:
        :param package_requirement:

        :return:
        """

        self.set_question_id(question_id)
        self.set_language(lang)

        if isinstance(points, str):
            self.set_points(float(points))
        else:
            self.set_points(points)

        self.set_question(question)
        self.set_answer(answer)
        self.set_usable(int(usable))
        self.set_course_information(course_code, course_version)
        self.set_belong_to_ilo(course_code, course_version, goals)
        self.set_tags(tags)

        for similar in not_in_same_exam:
            self.append_not_in_same_exam_as(similar)

        self.set_last_used(last_used.strftime("%Y-%m-%d"))

        self.set_declaration_requirement(declaration_requirement)
        self.set_bibliography_requirement(bibliography_requirement)
        self.set_graphics_requirement(graphics_requirement)
        self.set_package_requirement(package_requirement)

        self._modified = True  # Nothing has been modified.
        return

    def export_question(self):
        """
        Method used to export question, should be used together with import question.
        :return:
        """
        return [
            self._question_id,
            self._language,
            self._points,
            self._question,
            self._answer,
            self._usable,
            self._ilo,
            self._course["course_code"],
            self._course["course_version"],
            self._tags,
            self._not_in_same_exam,
            self.lastUsed,
            self._declarationRequirement,
            self._bibliography_requirement,
            self._graphics_requirement,
            self._package_requirement,
        ]

    def get_in_database(self):
        return self.inDatabase

    def set_in_database(self, in_database):
        if self._editable:
            self.inDatabase = in_database
        return

    def set_modified(self, status):
        if self._editable:
            self._modified = status
        return

    def get_modified(self):
        return self._modified

    def get_question_id(self):
        return self._question_id

    def set_question_id(self, question_id):
        if self._editable:
            assert len(question_id) <= 15, "question ID too long"
            self._question_id = question_id
            self._questionID_modified = True
            self._modified = True

    def get_language(self):
        return self._language

    def set_language(self, language):
        if self._editable:
            language.upper()
            self._language = language
            self._language_modified = True
            self._modified = True

    def get_points(self):
        return self._points

    def set_points(self, points):
        if self._editable:
            self._points = points
            self._points_modified = True
            self._modified = True

    def append_points(self, points):
        if self._editable:
            self._points += points
            self._points_modified = True
            self._modified = True

    def get_question(self):
        return self._question

    def get_question_for_print(self):
        """
        Method to retrieve the question for print in exam. Adds the goal to the question.
        :return: String with question.
        """
        if not self._ilo:
            return self._question

        question = self._question.splitlines()
        if len(question) > 1:
            question[1] += ('\\emph{(ILO: %s)}' % (self._ilo[0][11:],))
            
            # Check if question finishes with new line. If not, add it, so that
            # question and solution is separate.
            last_line = question[len(question)-1]
            if not last_line[-1] == "\n":
                last_line = last_line + "\n"
        
        return '\n'.join(question)

    def get_question_code(self):
        _question_code = ('%s'
                          '\\begin{solution} \n'
                          '\\textbf{for question %s: }\\\\\n'
                          '%s'
                          '\\end{solution}\n'
                          % (self.get_question_for_print(),
                             self._question_id,
                             self._answer)
                          )
        return _question_code

    def set_question(self, question):
        if self._editable:
            self._question = question
            self._question_modified = True
            self._modified = True

    def append_question(self, question):
        if self._editable:
            self._question += question
            self._question_modified = True
            self._modified = True

    def get_answer(self):
        return self._answer

    def set_answer(self, answer):
        if self._editable:
            self._answer = answer
            self._answer_modified = True
            self._modified = True

        return

    def append_answer(self, answer):
        if self._editable:
            self._answer += answer
            self._answer_modified = True
            self._modified = True
        return

    def get_usable(self):
        return self._usable

    def set_usable(self, usable):
        if self._editable:
            self._usable = int(usable)
            self._usable_modified = True

    def get_last_used(self):
        return self.lastUsed

    def get_last_used_str(self):
        if self.lastUsed != datetime.strptime('1970-01-01', '%Y-%m-%d'):
            return self.lastUsed.strftime('%Y-%m-%d')

        return ''

    def set_last_used(self, last_used):
        if self._editable:
            if isinstance(last_used, str):
                self.examDate = datetime.strptime(last_used, '%Y-%m-%d')
            elif isinstance(last_used, datetime):
                self.examDate = last_used

            else:
                print('examdate is of type %s, only expect string or datetime.'
                      % type(last_used))
        return

    def get_not_in_same_exam_as(self):
        return self._not_in_same_exam

    def set_not_in_same_exam_as(self, question_id):
        if not self._editable:
            return

        self._not_in_same_exam = question_id
        self._not_in_same_exam_modified = True
        self._modified = True

    def append_not_in_same_exam_as(self, question_id):
        if not self._editable:
            return

        self._not_in_same_exam.add(question_id)
        self._not_in_same_exam_modified = True
        self._modified = True

    def remove_not_in_same_exam_as(self, question_id):
        if not self._editable:
            return

        self._not_in_same_exam.remove(question_id)
        self._modified = True

    def get_course_code(self):
        return self._course["course_code"]

    def get_course_version(self):
        return self._course["course_version"]

    def set_course_information(self, course_code, course_version):
        self._course["course_code"] = course_code
        self._course["course_version"] = course_version
        self._course_modified = True

    def set_ilo(self):
        if not self._ilo:
            return False
        else:
            return True

    def get_ilo_modified(self):
        return self._ilo_modified

    def get_ilo(self):
        # course code, coursever, [goals]

        return self._course["course_code"], self._course["course_version"], self._ilo

    def set_belong_to_ilo(self, course_code, course_version, goal):
        """
        Sets the ILO for a course.
        :param course_code:
        :param course_version:
        :param goal: List of goals
        :return:
        """
        if self._editable:
            self._course["course_code"] = course_code
            self._course["course_version"] = course_version
            self._ilo = goal
            self._ilo_modified = True
            self._course_modified = True

            self._modified = True

    def append_to_ilo(self, goals):
        if self._editable:
            self._ilo.append(goals)

            self._ilo_modified = True
            self._course_modified = True
            self._modified = True

    def set_tags(self, tags):
        if self._editable:
            self._tags_modified = True
            self._tags = tags
            self._modified = True

    def get_tags(self):
        return self._tags

    def append_tags(self, tag):
        if self._editable:
            self._tags.append(tag)
            self._modified = True
            self._tags_modified = True

    def get_package_requirement(self):
        return self._package_requirement

    def set_package_requirement(self, package_req):
        if self._editable:
            self._package_requirement = package_req
            self._package_requirement_modified = True
            self._modified = True

    def _package_requirement_exist(self, package_id):
        for _orig_pack_req in self._package_requirement:
            # If package already exist in Exam, add options
            if _orig_pack_req[0] == package_id:
                return _orig_pack_req

        return None

    def append_package_requirement(self, package_id, options=None):
        if not self._editable:
            return

        if package_id is None:
            return

        _modified = False

        _orig_pack_req = self._package_requirement_exist(package_id)
        if _orig_pack_req:
            updated_package = list(_orig_pack_req)
            if options:
                if _orig_pack_req[1]:
                    # Split options to be able to compare each option
                    _original_package_options = _orig_pack_req[1].split(',')
                    _new_package_options = options.split(',')
                    # Search if option candidate already in list
                    for _new_opt in _new_package_options:
                        _option_exist = False
                        for _opt in _original_package_options:
                            if _opt == _new_opt:
                                _option_exist = True

                        # If the candidate option is not already in list, add it.
                        if not _option_exist:
                            if not updated_package[1]:
                                updated_package[1] = _new_opt
                                _modified = True

                            else:
                                updated_package[1] = updated_package[1] + ',' + _new_opt
                                _modified = True

                # If no previous option exist
                else:
                    updated_package[1] = options
                    _modified = True

            if _modified:
                self._package_requirement.remove(_orig_pack_req)
                self._package_requirement.append(updated_package)
                self._modified = True

        else:
            self._package_requirement.append([package_id, options])
            self._package_requirement_modified = True
            self._modified = True

    def reset_package_requirement(self):  # Unused?
        if self._editable:
            self._package_requirement = set()
            self._package_requirement_modified = True
            self._modified = True

    def get_bibliography_requirement(self):
        return self._bibliography_requirement

    def set_bibliography_requirement(self, id_bibliography):
        if self._editable:
            self._bibliography_requirement = id_bibliography
            self._bibliography_requirement_modified = True
            self._modified = True

    def append_bibliography_requirement(self, bibliography_dict):
        """
        :param bibliography_dict: dictionary in form {'optional': [], 'bibliography': ''}
        :return:
        """
        if self._editable:
            if not self._bibliography_requirement:
                self._bibliography_requirement.append(bibliography_dict)
                return

            bibliography_match = False
            for bibliography in self._bibliography_requirement:  # Loop existing bibliography requirements
                if bibliography['bibliography'] == bibliography_dict['bibliography']:
                    bibliography_match = True
                    for new_optional in bibliography_dict['optional']:  # Loop new optionals for bibliography
                        optional_match = False

                        for optional in bibliography['optional']:  # Loop existing optionals
                            if new_optional == optional:
                                optional_match = True

                        if not optional_match:
                            bibliography['optional'].append(new_optional)

            if not bibliography_match:
                self._bibliography_requirement.append(bibliography_dict)

            self._bibliography_requirement_modified = True
            self._modified = True

    def remove_bibliography_requirement(self, bibliography_dict):
        if self._editable:
            if not self._bibliography_requirement:
                return

            bibliography_to_be_removed = []

            for bibliography in self._bibliography_requirement:  # Loop existing bibliography requirements
                if bibliography['bibliography'] == bibliography_dict['bibliography']:
                    for new_optional in bibliography_dict['optional']:  # Loop new optionals for bibliography
                        for optional in bibliography['optional']:  # Loop existing optionals
                            if new_optional == optional:
                                bibliography['optional'].remove(new_optional)

                if len(bibliography['optional']) == 0:
                    bibliography_dict['optional'] = []  # So that bibliography_dict math dictionary in bibreq
                    bibliography_to_be_removed.append(bibliography_dict)

            for bib in bibliography_to_be_removed:
                self._bibliography_requirement.remove(bib)

    def get_graphics_requirement(self):
        return self._graphics_requirement

    def set_graphics_requirement(self, graphics_id):
        if self._editable:
            self._graphics_requirement = graphics_id
            self._graphics_requirement_modified = True
            self._modified = True

    def append_graphics_requirement(self, graphics_id):
        if self._editable:
            self._graphics_requirement.add(graphics_id)
            self._graphics_requirement_modified = True
            self._modified = True

    def remove_graphics_requirement(self, graphics_id):
        if self._editable:
            self._graphics_requirement.remove(graphics_id)
            self._graphics_requirement_modified = True
            self._modified = True

    def get_declaration_requirement(self):
        return self._declarationRequirement

    def set_declaration_requirement(self, declaration_id):
        if self._editable:
            self._declarationRequirement = declaration_id
            self._declaration_requirement_modified = True
            self._modified = True

    def append_declaration_requirement(self, declaration_id):
        if self._editable:
            self._declarationRequirement.add(declaration_id)
            self._declaration_requirement_modified = True
            self._modified = True

    def remove_declaration_requirement(self, declaration_id):
        if self._editable:
            self._declarationRequirement.remove(declaration_id)
            self._declaration_requirement_modified = True
            self._modified = True

    def set_editable(self, value):
        self._editable = value

    def get_editable(self):
        return self._editable

    def insert_into_database(self):
        if not self.cnx:
            return None
        cursor = self.cnx.cursor()
        cursor.execute("INSERT INTO Questions \
                    (`question_id`, `language`, `points`, `question`,\
                     `answer`, `usable`, `tags`)\
                    VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (self._question_id, self._language, self._points,
                        self._question, self._answer, self._usable,
                        json.dumps(self._tags)))

        if self._not_in_same_exam_modified:
            for _nise in self._not_in_same_exam:
                cursor.execute("INSERT INTO Questions_Not_In_Same_Exam \
                        (`question_id`, `question_id_similar`) VALUES\
                         (?, ?)", (self._question_id, _nise))
                self._not_in_same_exam_modified = False

        if self.ExamDB:
            if self._declaration_requirement_modified:
                for declreq in self._declarationRequirement:
                    if self.ExamDB.declaration_exists(declreq):
                        cursor.execute("INSERT INTO Question_has_Declaration_Requirement \
                                (`question_id`, `declaration_id`) VALUES\
                                 (?, ?)", (self._question_id, declreq))
                        self._declaration_requirement_modified = False
                    else:
                        print('No such declaration: %s' % declreq)

            if self._bibliography_requirement_modified:
                for bibreq in self._bibliography_requirement:
                    if self.ExamDB.bibliography_exist(bibreq['bibliography']):
                        cursor.execute("INSERT INTO Question_has_Bibliography_Requirement \
                                (`question_id`, `bibliography_id`, `optional`) VALUES\
                                 (?, ?, ?)",
                                       (self._question_id, bibreq['bibliography'], json.dumps(bibreq['optional'])))
                        self._bibliography_requirement_modified = False
                    else:
                        print('No such bibliography: %s' % bibreq)

            if self._package_requirement_modified:
                for packagereq in self._package_requirement:
                    cursor.execute("INSERT INTO Question_has_Package_Requirement \
                            (`question_id`, `package_id`, `options`) VALUES\
                             (?, ?, ?)",
                                   (self._question_id, packagereq[0], packagereq[1]))
                    self._package_requirement_modified = False

            if self._graphics_requirement_modified:
                for _graphic_req in self._graphics_requirement:
                    cursor.execute("INSERT INTO Questions_has_Graphics "
                                   "(`question_id`, `graphics_id`) VALUES"
                                   "(?, ?)", (self._question_id, _graphic_req))
                    self._graphics_requirement_modified = False

        if self._ilo_modified:
            for _ilo in self._ilo:
                cursor.execute("INSERT INTO Questions_has_ILO \
                          (`question_id`, `goal`, `course_code`,`course_version`)\
                          VALUES (?, ?, ?, ?)",
                               (self._question_id, _ilo,
                                self._course["course_code"],
                                self._course["course_version"]))
            self._ilo_modified = False
            self._course_modified = False

        if self._not_in_same_exam_modified:
            for _nise in self._not_in_same_exam:
                cursor.execute("INSERT INTO Questions\
                                (question_id,question_id_similar)=?\
                                VALUES (?, ?)",
                               (_nise, self._question_id, _nise)
                               )

        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if self._language_modified:
            cursor.execute("UPDATE Questions\
                            SET language = ?\
                            WHERE question_id = ?",
                           (self._language, self._question_id)
                           )
            self._language_modified = False

        if self._points_modified:
            cursor.execute("UPDATE Questions\
                            SET points = ?\
                            WHERE question_id = ?",
                           (self._points, self._question_id)
                           )
            self._points_modified = False

        if self._question_modified:
            cursor.execute("UPDATE Questions\
                            SET question = ?\
                            WHERE question_id = ?",
                           (self._question, self._question_id)
                           )
            self._question_modified = False

        if self._answer_modified:
            cursor.execute("UPDATE Questions\
                            SET answer= ? \
                            WHERE question_id = ?",
                           (self._answer, self._question_id)
                           )
            self._answer_modified = False

        if self._usable_modified:
            cursor.execute("UPDATE Questions\
                            SET usable = ?\
                            WHERE question_id = ?",
                           (self._usable, self._question_id)
                           )
            self._usable_modified = False

        if self._tags_modified:
            cursor.execute("UPDATE Questions\
                           SET tags = ?\
                           WHERE question_id = ? ",
                           (json.dumps(self._tags), self._question_id))

        # Start by removing all the old entries.
        if self._not_in_same_exam_modified:
            cursor.execute("DELETE FROM Questions_Not_In_Same_Exam\
                            WHERE `question_id`= ? OR \
                            `question_id_similar`= ?",
                           (self._question_id, self._question_id))

            # Insert new entries.
            for nise in self._not_in_same_exam:
                cursor.execute("INSERT INTO Questions_Not_In_Same_Exam\
                            (question_id,question_id_similar)\
                            VALUES (?, ?)",
                               (self._question_id, nise)
                               )
            self._not_in_same_exam_modified = False

        if self._package_requirement_modified:
            cursor.execute("DELETE FROM Question_has_Package_Requirement\
                      WHERE `question_id`=?", (self._question_id,))

            for packagereq in self._package_requirement:
                cursor.execute("INSERT INTO Question_has_Package_Requirement \
                        (`question_id`, `package_id`, `options`) VALUES\
                         (?, ?, ?)",
                               (self._question_id,
                                packagereq[0],
                                packagereq[1]))
            self._package_requirement_modified = False

        if self._bibliography_requirement_modified:
            cursor.execute("DELETE FROM Question_has_Bibliography_Requirement\
                      WHERE `question_id`= ? ",
                           (self._question_id,))

            if self._bibliography_requirement:
                for bibreq in self._bibliography_requirement:
                    if self.ExamDB.bibliography_exist(bibreq['bibliography']):
                        cursor.execute("INSERT INTO \
                                        Question_has_Bibliography_Requirement "
                                       "(`question_id`, `bibliography_id`, `optional`) "
                                       "VALUES (?, ?, ?)",
                                       (self._question_id, bibreq['bibliography'], json.dumps(bibreq['optional'])))

                        self._bibliography_requirement_modified = False
                    else:
                        print('No such bibliography: %s' % bibreq)

            self._bibliography_requirement_modified = False

        if self._graphics_requirement_modified:
            cursor.execute("DELETE FROM Questions_has_Graphics\
                      WHERE `question_id`=?", (self._question_id,))

            for _graphics_req in self._graphics_requirement:
                cursor.execute("INSERT INTO Questions_has_Graphics \
                        (`question_id`, `graphics_id`) VALUES\
                         (?, ?)",
                               (self._question_id,
                                _graphics_req))
            self._graphics_requirement_modified = False

        if self._declaration_requirement_modified:
            cursor.execute("DELETE FROM Question_has_Declaration_Requirement\
                      WHERE `question_id`= ?", (self._question_id,))

            if self._declarationRequirement:
                for declreq in self._declarationRequirement:
                    if self.ExamDB.declaration_exists(declreq[0]):
                        cursor.execute("INSERT INTO \
                                Question_has_Declaration_Requirement \
                                (`question_id`, `declaration_id`) VALUES\
                                 (?, ?)", (self._question_id, declreq[0]))
                        self._declaration_requirement_modified = False
                    else:
                        print('No such declaration: %s' % declreq[0])

        if self._ilo_modified:
            cursor.execute("DELETE FROM Questions_has_ILO \
                            WHERE question_id = ? ",
                           (self._question_id,))

            for goal in self._ilo:
                cursor.execute("INSERT INTO Questions_has_ILO \
                                  (question_id, goal, course_code, course_version) VALUES\
                                  (?, ?, ?, ?)",
                               (self._question_id, goal, self.get_course_code(), self.get_course_version())
                               )
            self._ilo_modified = False

        self.cnx.commit()
        cursor.close()
        return

    def remove_similar(self, similar_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        for s in self._not_in_same_exam.copy():
            if s == similar_id:
                self._not_in_same_exam.remove(s)

        cursor.execute("DELETE FROM Questions_Not_In_Same_Exam\
                        WHERE question_id = ? and question_id_similar = ?",
                       (self._question_id, similar_id))

        cursor.execute("DELETE FROM Questions_Not_In_Same_Exam\
                        WHERE question_id = ? AND \
                             question_id_similar = ?",
                       (similar_id, self._question_id))

        self.cnx.commit()
        cursor.close()
        return

    def remove_package_requirement(self, package_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        for _p in self._package_requirement:
            if _p == package_id:
                self._package_requirement.remove(_p)

        cursor.execute("DELETE FROM Question_has_Package_Requirement\
                        WHERE question_id = ? and package_id = ?",
                       (self._question_id, package_id))

        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("DELETE FROM Questions_Not_In_Same_Exam \
                            WHERE question_id = ?",
                       (self._question_id,))

        cursor.execute("DELETE FROM Question_has_Package_Requirement \
                      WHERE `question_id`=?", (self._question_id,))

        cursor.execute("DELETE FROM Question_has_Bibliography_Requirement \
                      WHERE `question_id`= ? ",
                       (self._question_id,))

        cursor.execute("DELETE FROM Questions_has_ILO \
                        WHERE question_id = ? ",
                       (self._question_id,))

        cursor.execute("DELETE FROM Questions \
                        WHERE question_id = ? ",
                       (self._question_id,))

        self.cnx.commit()
        cursor.close()
        return

    def __repr__(self):
        """
        Allows for sorting questions based on question id or ilo
        :return:
        """
        return repr((self._question_id, self._ilo[0]))
