#!/usr/bin/env python
# coding:utf-8

from dateutil.parser import parse
from datetime import datetime, timedelta
from Database.ExamQuery import ExamQuery
import json

__author__ = "Lennart Franked"
__email__ = "lennart.franked@miun.se"
__version__ = "0.5"

"""
"""


class ExamDB:
    def __init__(self):

        self.packages = []
        self.cnx = None
        self.dbQuery = None

    def connect_to_db(self, database_path=None):
        """
        Establish connection to database
        """
        # noinspection PyBroadException
        try:
            self.dbQuery = ExamQuery(database_path)
            self.cnx = self.dbQuery.get_connector()
            if self.cnx:
                return self.dbQuery
            else:
                return False
        except:
            return False

    def gen_id(self, _typ, course=None, course_version=None):
        """
        Generating ID's for inserting data into the database.
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        # Method for generating unique ID for insertion into database.
        if course is None:
            course = ''

        if course_version is None:
            course_version = course_version

        if _typ == 'exam':
            _ident = ('%s' + 'v%s' + 'e') % (course, course_version)

        elif _typ == 'question':
            _ident = ('%s' + 'q') % course

        elif _typ == 'coursegoal':
            _ident = ('%s' + 'v%s' + 'g') % (course, course_version)

        else:
            _ident = _typ

        cursor.execute("SELECT counter_value \
                        FROM Counters\
                        WHERE type = ? AND \
                        ident = ?", (_typ, _ident))

        counter = cursor.fetchall()
        cursor.close()
        if not counter:  # No counter for specified type exists, so counter
            # is created and method is called again.
            self._insert_counter(_ident, _typ, '0')
            return self.gen_id(_typ, course, course_version)
        else:  # Generate ID if counter exist.
            cnt = int(counter[0][0])
            cnt += 1
            self._update_counter(_ident, _typ, cnt)
            generated_id = ('%s' % _ident + str(cnt))
            return generated_id

    def _insert_counter(self, ident, typ, value):
        """
        Support method for genID. Inserts a new counter value to the Counters
        table if necessary.
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("INSERT INTO `Counters` \
        (`type`, `ident`, `counter_value`) VALUES (?, ?, ?)"
                       , (typ, ident, value))

        self.cnx.commit()
        cursor.close()
        return

    def _update_counter(self, ident, typ, value):
        """
        Support method for genID. Updates the counter values after its been
        used to generate a new ID.
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("UPDATE `Counters` \
                        SET `counter_value`=? \
                        WHERE `type`=? and`ident`=?",
                       (value, typ, ident))

        self.cnx.commit()
        cursor.close()
        return

    def similar_question_used(self, question_id, allow_same_tags=False):
        """
        Retrieve question ID's for questions that are not allowed to appear in the same
        exam as question_id
        :param question_id: question to get similar questions for.
        :param allow_same_tags: Sets whether or not same tags should be considered same topic.
        :return: list of question ids that should not appear in the same exam as question id
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT `question_id`, `question_id_similar`\
                  FROM Questions_Not_In_Same_Exam \
                  WHERE question_id = ? OR \
                    question_id_similar = ?"
                       , (question_id, question_id))
        self.cnx.commit()

        _similar = cursor.fetchall()

        _similar_questions = set()

        if not allow_same_tags:
            # Do not include questions that has the same tag.
            cursor.execute("SELECT `tags`\
                                  FROM Questions\
                                  WHERE question_id = ?"
                           , (question_id,))
            _tag = cursor.fetchall()

            cursor.execute("SELECT `question_id` \
                            FROM Questions \
                            WHERE tags = ?",
                           (_tag[0][0],)
                           )
            _similar_tag = cursor.fetchall()

            cursor.close()

            for _s in _similar_tag:
                _similar_questions.add(_s[0])

        # Remove original question id from list.
        for _s in _similar:
            if _s[0] == question_id:
                _similar_questions.add(_s[1])
            elif _s[1] == question_id:
                _similar_questions.add(_s[0])

        return _similar_questions

    def get_declarations(self, declaration_id=None):
        """
        Retrieve all defined declarations.
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        if declaration_id is None:
            cursor.execute("SELECT declaration_id, data, tags\
                            FROM Declarations")
            declaration_data = cursor.fetchall()
        else:
            cursor.execute("SELECT declaration_id, data, tags\
                            FROM Declarations\
                            WHERE declaration_id = ?"
                           , (declaration_id,))
            declaration_data = cursor.fetchall()
        cursor.close()

        return declaration_data

    def declaration_used(self, declaration_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("SELECT question_id\
                  FROM Question_has_Declaration_Requirement\
                  WHERE declaration_id = ?"
                       , (declaration_id,))
        reply = cursor.fetchall()
        cursor.close()

        return reply

    def get_declaration_for_question(self, question_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT `declaration_id`\
                  FROM `Question_has_Declaration_Requirement`\
                  WHERE `question_id`=?"
                       , (question_id,))
        reply = cursor.fetchall()
        cursor.close()
        return reply

    def get_package_req_for_question(self, question_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT package_id, options\
                       FROM Question_has_Package_Requirement\
                       WHERE question_id = ?",
                       (question_id,))

        reply = cursor.fetchall()
        cursor.close()

        return reply

    def graphics_exist(self, graphics_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT graphics_id "
                       "FROM Graphics "
                       "WHERE graphics_id = ? ",
                       (graphics_id,))

        reply = cursor.fetchall()
        cursor.close()
        if reply:
            return reply[0][0]
        else:
            return

    def get_graphics(self, graphics_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("SELECT graphics_id, uri \
                        FROM Graphics \
                        WHERE Graphics.graphics_id = ?"
                       , (graphics_id,))

        reply = cursor.fetchall()
        cursor.close()

        return reply

    def get_preamble_packages(self, default_packages=None):
        """
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if default_packages is None:
            cursor.execute("SELECT DISTINCT default_package_id "
                           "FROM Default_Packages")
            reply = cursor.fetchall()
            cursor.close()
            return reply

        else:
            cursor.execute("SELECT Packages.package_id,Packages.package,"
                           "Packages.options "
                           "FROM Packages JOIN Default_Packages "
                           "ON Packages.package_id = Default_Packages.package_id "
                           "WHERE default_package_id=?"
                           , (default_packages,))
            reply = cursor.fetchall()
            cursor.close()
            return reply

    def get_package_list(self, package_id=None):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if not package_id:
            cursor.execute("SELECT package_id, package, options "
                           "FROM Packages")
            reply = cursor.fetchall()

        else:
            cursor.execute("SELECT package_id, package, options "
                           "FROM Packages "
                           "WHERE package_id = ?", (package_id,))

            reply = cursor.fetchall()

        cursor.close()
        return reply

    def package_exist(self, package_name):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT package_id "
                       "FROM Packages "
                       "WHERE package = ? ",
                       (package_name,))

        reply = cursor.fetchall()
        cursor.close()
        if reply:
            return reply[0][0]
        else:
            return

    def package_used(self, package_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT package_id "
                       "FROM Default_Packages "
                       "WHERE package_id = ? ",
                       (package_id,))

        reply = cursor.fetchall()
        cursor.close()

        if len(reply) < 1:
            return False
        else:
            return True

    def preamble_package_already_used(self, preamble_package_id=None):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if preamble_package_id is None:
            cursor.execute("SELECT DISTINCT default_package_id "
                           "FROM Preamble")
        else:
            cursor.execute("SELECT DISTINCT default_package_id "
                           "FROM Preamble "
                           "WHERE default_package_id = ?",
                           (preamble_package_id,))

        reply = cursor.fetchall()
        cursor.close()

        if len(reply) < 1:
            return False
        else:
            return True

    def load_preamble_package(self, preamble_package_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT package_id "
                       "FROM Default_Packages "
                       "WHERE default_package_id = ?",
                       (preamble_package_id,))

        reply = cursor.fetchall()
        cursor.close()

        return list(reply)

    def get_questions_by_ilo(self, ilo, course_code, course_version):
        """
        Retrieves questions from database, based on set course goal.
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("\
        SELECT Questions.question_id\
        FROM Questions join Questions_has_ILO\
             on Questions.question_id = Questions_has_ILO.question_id\
         WHERE Questions_has_ILO.course_code = ? and \
             Questions_has_ILO.course_version=? and\
             Questions_has_ILO.goal = ? and\
             Questions.usable = 1"
                       , (course_code, course_version, ilo)
                       )
        reply = cursor.fetchall()
        cursor.close()
        return reply

    def get_questions_by_id(self, question_ids):
        """
        Retrieves questions from database, based on set question ID.
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        assert (isinstance(question_ids, str))

        cursor.execute("\
         SELECT Questions.question_id,Questions.language, Questions.points,\
                Questions.question, Questions.answer,\
                Questions.usable, Questions_has_ILO.goal,\
                Questions_has_ILO.course_code,\
                Questions_has_ILO.course_version,\
                Questions.tags\
            FROM Questions join Questions_has_ILO\
             ON Questions.question_id = Questions_has_ILO.question_id\
         WHERE Questions.question_id =?", (question_ids,))
        question_information = cursor.fetchall()
        cursor.close()

        if not question_information:
            return None

        not_in_same_exam = self.similar_question_used(question_ids)

        if not_in_same_exam is None:
            not_in_same_exam = []

        last_used = self.get_question_last_used(question_ids)
        declaration_requirement = self.get_declaration_for_question(question_ids)
        bibliography_requirement = self.get_bibliography_for_question(question_ids)
        package_requirement = self.get_package_req_for_question(question_ids)

        answer = question_information[0] + (not_in_same_exam,) + (last_used,) + (declaration_requirement,) + \
                 (bibliography_requirement,) + (package_requirement,)

        if answer is None:
            return None
        else:
            return answer

    def get_questions_without_ilo_by_id(self, question_ids, course_code, course_version):
        """
        Retrieves questions from database, based on set question ID.
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        assert (isinstance(question_ids, str))

        cursor.execute("\
         SELECT Questions.question_id,\
                Questions.language,\
                Questions.points,\
                Questions.question,\
                Questions.answer,\
                Questions.usable, \
                Questions.tags\
         FROM Questions \
         WHERE Questions.question_id =?", (question_ids,))

        question_information = cursor.fetchall()
        cursor.close()

        if not question_information:
            return None

        question = list(question_information[0])
        question.insert(6, None)
        question.insert(7, course_code)
        question.insert(8, course_version)

        not_in_same_exam = self.similar_question_used(question_ids)

        if not_in_same_exam is None:
            not_in_same_exam = []

        last_used = self.get_question_last_used(question_ids)
        declaration_requirement = self.get_declaration_for_question(question_ids)
        bibliography_requirement = self.get_bibliography_for_question(question_ids)
        package_requirement = self.get_package_req_for_question(question_ids)

        answer = [*question, not_in_same_exam, last_used, declaration_requirement,
                  bibliography_requirement, package_requirement]

        return answer

    def get_question_ilo(self, question_id):
        if not self.cnx:
            return None

        assert (isinstance(question_id, str))

        cursor = self.cnx.cursor()
        cursor.execute("SELECT Questions_has_ILO.goal, ILO.description  \
                       FROM Questions_has_ILO JOIN ILO \
                            ON Questions_has_ILO.goal = ILO.goal\
                        WHERE question_id = ?",
                       (question_id,)
                       )
        reply = cursor.fetchall()
        cursor.close()

        return reply[0]

    def get_question_tags(self, question_id):
        if not self.cnx:
            return None

        assert (isinstance(question_id, str))

        cursor = self.cnx.cursor()
        cursor.execute("SELECT tags \
                       FROM Questions \
                        WHERE question_id = ?",
                       (question_id,)
                       )
        reply = cursor.fetchall()
        cursor.close()

        return json.loads(reply[0][0])

    def get_question_max_point(self, question_id):
        if not self.cnx:
            return None

        assert (isinstance(question_id, str))

        cursor = self.cnx.cursor()
        cursor.execute("SELECT points \
                       FROM Questions \
                        WHERE question_id = ?",
                       (question_id,)
                       )
        reply = cursor.fetchall()
        cursor.close()

        return reply[0][0]

    def recently_used(self, question_id):
        assert (isinstance(question_id, str))
        _last_used = self.get_question_last_used(question_id)
        if _last_used < datetime.today() \
                - timedelta(days=365):
            return False

        return True

    def question_already_used(self, question_id):
        assert (isinstance(question_id, str))

        _last_used = self.get_question_last_used(question_id)
        _epochTime = datetime.strptime('1970-01-01', '%Y-%m-%d')
        if _last_used == _epochTime:
            return False

        return True

    def get_question_last_used(self, question_ids):
        """
        Support function for _getNotRecentlyUsedQuestion. Retrieves when the question was
        used last time. If not used then return 1970-01-01 as _lastUsed
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        assert (isinstance(question_ids, str))

        cursor.execute("SELECT Exams.exam_date\
                    FROM Exams JOIN Questions_in_Exam \
                    on Exams.exam_id = Questions_in_Exam.exam_id\
                    WHERE Questions_in_Exam.question_id = ?"
                       , (question_ids,))
        _used_questions = cursor.fetchall()
        cursor.close()
        _last_used = datetime.strptime('1970-01-01', '%Y-%m-%d')

        if not _used_questions:
            return _last_used

        for d in _used_questions:
            _question_last_used = datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S')
            if _question_last_used > _last_used:
                _last_used = _question_last_used

        return _last_used

    def question_usable(self, question_id):
        """
        Get a questions usable status.
        :param question_id: Question ID to check
        :return: True or False
        """
        if not self.cnx:
            return None

        assert (isinstance(question_id, str))

        cursor = self.cnx.cursor()
        cursor.execute("SELECT usable \
                       FROM Questions \
                        WHERE question_id = ?",
                       (question_id,)
                       )
        reply = cursor.fetchall()
        cursor.close()

        return reply[0][0]

    def bibliography_already_used(self, bib_id):
        assert (isinstance(bib_id, str))

        _last_used = self.get_bibliography_last_used(bib_id)
        _epoch_time = datetime.strptime('1970-01-01', '%Y-%m-%d')
        if _last_used == _epoch_time:
            return False

        return True

    def get_bibliography_last_used(self, bib_id):
        """
        Support function for _getNotRecentlyUsedQuestion. Retrieves when the question was
        used last time. If not used then return 1970-01-01 as _lastUsed
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        assert (isinstance(bib_id, str))

        cursor.execute("SELECT Exams.exam_date "
                       "FROM Exams JOIN Questions_in_Exam "
                       "ON Exams.exam_id = Questions_in_Exam.exam_id "
                       "JOIN Question_has_Bibliography_Requirement "
                       "ON Questions_in_Exam.question_id = "
                       "Question_has_Bibliography_Requirement.question_id "
                       "WHERE Question_has_Bibliography_Requirement.bibliography_id = "
                       "?", (bib_id,))

        _lastUsed = datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        _used_bibliography = cursor.fetchall()
        cursor.close()

        if _used_bibliography is None:
            return _lastUsed

        for d in _used_bibliography:
            _bibliography_last_used = datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S')
            if _bibliography_last_used > _lastUsed:
                _lastUsed = _bibliography_last_used

        return _lastUsed

    def author_exist(self, author_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT author_id\
                  FROM Authors\
                  WHERE author_id = ?"
                       , (author_id,))
        reply = cursor.fetchall()
        cursor.close()
        return reply

    def course_exist(self, course_code, course_version):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT course_code, course_version\
                  FROM Course\
                  WHERE course_code = ? AND\
                  course_version = ?"
                       , (course_code, course_version))
        reply = cursor.fetchall()
        cursor.close()
        return reply

    def course_goal_exists(self, goal_id):
        if not self.cnx:
            return None
        cursor = self.cnx.cursor()
        cursor.execute("SELECT goal \
                  FROM ILO \
                  WHERE goal = ?", (goal_id,))
        reply = cursor.fetchall()
        cursor.close()
        return reply

    def question_exists(self, question_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT question_id\
                  FROM Questions\
                  WHERE question_id = ?"
                       , (question_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def declaration_exists(self, declaration_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT declaration_id\
                  FROM Declarations\
                  WHERE declaration_id = ?"
                       , (declaration_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def document_class_exists(self, document_class):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT document_class_id\
                  FROM Document_Classes\
                  WHERE document_class_id = ?"
                       , (document_class,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def instruction_exist(self, instruction_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT instruction_id\
                  FROM Instructions\
                  WHERE instruction_id = ?"
                       , (instruction_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def bibliography_exist(self, bib_id):
        if not self.cnx:
            return None

        if isinstance(bib_id, tuple):
            bib_id = bib_id[0]

        assert (isinstance(bib_id, str))

        cursor = self.cnx.cursor()
        cursor.execute("SELECT bibliography_id\
                  FROM Bibliography\
                  WHERE bibliography_id = ?"
                       , (bib_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def bibliography_used(self, bib_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT bibliography_id, question_id\
                  FROM Question_has_Bibliography_Requirement\
                  WHERE bibliography_id = ?"
                       , (bib_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def get_bibliography_for_question(self, question_id):
        if not self.cnx:
            return None

        assert (isinstance(question_id, str))

        cursor = self.cnx.cursor()
        cursor.execute("SELECT bibliography_id, optional \
                        FROM Question_has_Bibliography_Requirement \
                        WHERE question_id = ?",
                       (question_id,)
                       )
        reply = cursor.fetchall()
        cursor.close()
        reading_list = []
        if reply:
            for reading in reply:
                reading_list.append({'optional': json.loads(reading[1]), 'bibliography': reading[0]})

            return reading_list

        return None

    def get_bibliography(self, bib_id=None):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        if bib_id is None:
            cursor.execute("SELECT * FROM Bibliography")
        else:
            cursor.execute("SELECT * "
                           "FROM Bibliography "
                           "WHERE bibliography_id = ?"
                           , (bib_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def get_question_ids(self, course_code, course_version):
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()

        _cursor.execute("SELECT Questions.question_id, Questions.tags,Questions_has_ILO.goal \
            FROM Questions JOIN Questions_has_ILO\
            ON Questions.question_id = Questions_has_ILO.question_id\
            WHERE Questions_has_ILO.course_code = ?\
                AND Questions_has_ILO.course_version = ?"
                        , (course_code, course_version)
                        )
        _reply = _cursor.fetchall()
        _cursor.close()
        reply_list = []
        for _entry in _reply:
            if not reply_list:
                reply_list.append([_entry[0], _entry[1], [_entry[2]]])
            else:
                match = False
                for _question_id in reply_list:
                    if _entry[0] == _question_id[0]:
                        match = True
                        _question_id[2].append(_entry[2])

                if not match:
                    reply_list.append([_entry[0], _entry[1], [_entry[2]]])

        return reply_list

    def get_questions_without_ilo(self, course_code, course_version):
        if not self.cnx:
            return None
        _course = course_code + '%'

        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT `question_id`, `tags`\
                        FROM Questions\
                        WHERE question_id LIKE ?\
                        EXCEPT\
                        SELECT Questions.question_id, Questions.tags \
                            FROM Questions JOIN Questions_has_ILO\
                            ON Questions.question_id = Questions_has_ILO.question_id\
                            WHERE Questions_has_ILO.course_code = ?\
                                AND Questions_has_ILO.course_version = ?"
                        , (_course, course_code, course_version)
                        )
        reply = _cursor.fetchall()
        _cursor.close()
        return reply

    def get_course_codes(self):
        """
        Method used for entry completion in GUI
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT distinct course_code \
                        FROM Course")

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def get_course_information_by_exam(self, exam_id):
        """
        Grabs what course an exam was used in.

        :param exam_id:
        :return: course_code, course_version
        """

        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("SELECT `course_code`, `course_version` \
                        FROM Exams\
                        WHERE exam_id = ?", (exam_id,))

        reply = cursor.fetchall()[0]
        cursor.close()
        return reply

    def retrieve_authors(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT `author_id`, `name`, `email`, `phone` \
                        FROM Authors")

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def get_author(self, author_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT `author_id`, `name`, `email`, `phone`\
                  FROM Authors\
                  WHERE `author_id` = ?", (author_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def author_used(self, author_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT author_id \
                        FROM Exam_Authors\
                        WHERE author_id = ?",
                       (author_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def retrieve_courses(self, course_code=None, course_ver=None):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        if (course_code is None) or (course_ver is None):
            cursor.execute("SELECT course_code, course_version, course_name_swe, \
                        course_name_eng, course_credits, course_progression\
                      FROM Course")
        else:
            cursor.execute("SELECT course_code, course_version, course_name_swe, \
                         course_name_eng, course_credits, course_progression\
                      FROM Course\
                      WHERE `course_code` = ? AND `course_version` = ?"
                           , (course_code, course_ver))

        _reply = cursor.fetchall()
        cursor.close()
        return _reply

    def course_used(self, course_code, course_version):
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT course_code \
                  FROM Exams\
                  WHERE `course_code` = ? AND `course_version` = ?"
                        , (course_code, course_version))

        _reply = _cursor.fetchall()
        _cursor.close()
        return _reply

    def get_ilo_by_id(self, goal):
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT goal,course_code,course_version,description, tags\
                  FROM ILO\
                  WHERE `goal` = ?", (goal,))
        _reply = _cursor.fetchall()
        _cursor.close()
        return _reply

    def get_ilos_for_course(self, course_code, course_version):
        """
        Method used by GUI for generating selectable list of course goals
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("SELECT goal, description, tags \
                  FROM ILO \
                  WHERE course_code = ? and course_version=?"
                       , (course_code, course_version))
        _reply = cursor.fetchall()
        cursor.close()
        return _reply

    def have_ilo_been_used(self, goal_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT ILO.goal\
            FROM\
                ILO, Questions_has_ILO,\
                Questions, Questions_in_Exam\
            WHERE\
                ILO.goal = Questions_has_ILO.goal\
                 AND\
                Questions_has_ILO.question_id = Questions.question_id\
                 AND\
                Questions.question_id = Questions_in_Exam.question_id\
                 AND\
                ILO.goal = ?", (goal_id,))

        reply = cursor.fetchall()
        cursor.close()
        return reply

    def get_document_class(self, document_class=None):
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()
        if document_class is None:
            _cursor.execute("SELECT document_class_id, class, options\
                      FROM Document_Classes")
        else:
            _cursor.execute("SELECT document_class_id, class, options\
                      FROM Document_Classes\
                      WHERE `document_class_id` = ?", (document_class,))

        _reply = _cursor.fetchall()
        _cursor.close()
        return _reply

    def docclass_used(self, document_class):
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT Document_Classes.document_class_id\
                  FROM Document_Classes JOIN Preamble\
                     ON Document_Classes.document_class_id = \
                         Preamble.document_class_id\
                    JOIN Exams\
                     ON Preamble.exam_id = Exams.exam_id\
                  WHERE Document_Classes.document_class_id = ?", (document_class,))
        _reply = _cursor.fetchall()
        _cursor.close()
        return _reply

    def instruction_used(self, instruction_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT Instructions.instruction_id\
                  FROM Instructions JOIN Preamble\
                     ON Instructions.instruction_id = \
                         Preamble.instruction_id\
                    JOIN Exams\
                     ON Preamble.exam_id = Exams.exam_id\
                  WHERE Instructions.instruction_id = ?", (instruction_id,))
        _reply = cursor.fetchall()
        cursor.close()
        return _reply

    def get_instructions(self, instr_id=None):
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()
        if instr_id is None:
            _cursor.execute("SELECT instruction_id,language, data\
                      FROM Instructions")

        else:
            _cursor.execute("SELECT instruction_id,language, data\
                      FROM Instructions\
                      WHERE `instruction_id` = ?"
                            , (instr_id,))

        _reply = _cursor.fetchall()
        _cursor.close()
        return _reply

    def get_old_exams(self, course=None):
        """
        Generator method to retrieve all old exams
        :param course: Exams for a specific course.
        :return: List in form [course, [[examid (str), examdate (datetime)]]]
        """
        '''
        '''
        if not self.cnx:
            return None

        _reply = []

        _cursor = self.cnx.cursor()

        if not course:
            # Get unique courses, which have saved old exams.
            _cursor.execute("SELECT DISTINCT course_code\
                             FROM Exams")
            _course_codes = _cursor.fetchall()
        else:
            _course_codes = [(course,)]  # Put in in same format as return type from SQL

        # For each unique course, add a list of exams
        for _course in _course_codes:
            _entry = [_course[0], []]  # list in form [course, [examid,course,examdate]]
            _cursor.execute("SELECT exam_id, exam_date, exam_type\
                             FROM Exams\
                             WHERE `course_code` = ?"
                            , (_course[0],)
                            )
            _answer = _cursor.fetchall()

            for _exam in _answer:
                _exam_list = []
                for _e in _exam:
                    _exam_list.append(_e)
                _exam_list[1] = parse(_exam_list[1])
                _entry[1].append(_exam_list)
            _reply.append(_entry)
            yield _entry

        _cursor.close()

    def exam_exist(self, exam_id):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("SELECT `exam_id`\
                       FROM Exams\
                       WHERE exam_id = ?"
                       , (exam_id,))

        if cursor.fetchall():
            return True

        return False

    def get_exam_info_by_id(self, exam_id):
        """
        Grabs Exam ID, Course Code, Course Version, Exam Date, Language, Timelimit, Exam Aids, Grade Limit, Exam Type
        and Grade Comments from Database.

        :param exam_id:
        :return: Exam ID, Exam Date, Language, Time limit, Exam Aids, Grade Limit,
                 Exam Type and Grade Comments
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("SELECT `exam_id`, `exam_date`, `language`, `time_limit`,\
                        `exam_aids`, `grade_limits`, `exam_type`, `grade_comment`\
                        FROM Exams\
                        WHERE exam_id = ?"
                       , (exam_id,))

        exam_data = list(cursor.fetchall()[0])
        exam_data[5] = json.loads(exam_data[5])  # Decode json back to dictionary

        cursor.close()

        return exam_data

    def get_exam_preamble_info(self, exam_id):
        """
        Grabs Preamble information based on Exam ID.
        :param exam_id
        :return: instruction_id, document_class_id, default_packages_id
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        preamble_list = []

        cursor.execute("SELECT `instruction_id`,`document_class_id`,\
                         `default_package_id`\
                  FROM Preamble\
                  WHERE `exam_id` = ?"
                       , (exam_id,))

        preambles = cursor.fetchall()[0]
        for p in preambles:
            preamble_list.append(p)

        cursor.close()

        return preamble_list

    def get_exam_question_ids(self, exam_id):
        """
        Grabs all questions that was used in the exam.
        :param exam_id:
        :return: [question_id]
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        question_list = []

        cursor.execute("SELECT `question_id`\
                  FROM Questions_in_Exam \
                  WHERE `exam_id` = ? \
                  ORDER BY `order` "
                       , (exam_id,))

        questions = cursor.fetchall()
        for q in questions:
            question_list.append(q[0])

        cursor.close()

        return question_list

    def get_exam_authors(self, exam_id):
        """
        Grabs Author ID for all authors connected to an exam.
        :param exam_id:
        :return: [author_id]
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        author_list = []

        cursor.execute("SELECT `author_id`\
                  FROM Exam_Authors\
                  WHERE `exam_id` = ?"
                       , (exam_id,))

        author = cursor.fetchall()
        for a in author:
            author_list.append(a[0])

        cursor.close()

        return author_list

    def get_available_profiles(self):
        if not self.cnx:
            return None
        _profile = []
        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT course_code, course_version \
                        FROM Profile")
        _result = _cursor.fetchall()

        for _entry in _result:
            _profileName = ('%s%s' % (_entry[0], _entry[1]))
            _profile.append([_entry[0], _entry[1], _profileName])

        return _profile

    def get_profile(self, course_code=None, course_version=None):
        if not self.cnx:
            return None
        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT instruction_id, document_class_id, \
                    default_package_id, author_id, goal, exam_aids, \
                    exam_type, time_limit, language, number_of_questions, exam_date, grade_limits,\
                    grade_comment, allow_same_tags \
                    FROM Profile \
                    WHERE `course_code` = ? AND \
                   `course_version` = ?", (course_code, course_version))

        _data = _cursor.fetchall()
        if _data is None:
            return None

        _profile = list(_data[0])
        _cursor.close()

        if _profile[11]:
            if len(_profile[11]) > 0:
                _profile[11] = json.loads(_profile[11])  # Decode json back to dictionary

        return _profile

    def get_students_for_exam(self, exam_id):
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT DISTINCT student_id \
                        FROM Exam_Results \
                        WHERE exam_id = ? \
                        ORDER BY `order`",
                        (exam_id,))
        _student_list = _cursor.fetchall()

        return _student_list

    def student_exist(self, student_id, exam_id):
        """
        Return student id if it exists in the Exam_Results table
        :param student_id: The student ID that is sought after.
        :param exam_id: The exam the student took.
        :return student_id or None:
        """
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("SELECT student_id "
                       "FROM Exam_Results "
                       "WHERE student_id = ? \
                        AND\
                        exam_id = ?",
                       (student_id, exam_id)
                       )

        reply = cursor.fetchall()
        cursor.close()
        if reply:
            return reply[0][0]
        else:
            return

    def get_student_result_from_exam(self, exam_id, student_id):
        """
        Retrieves exam result for a specific student
        :param exam_id: Exam to return results for
        :param student_id: Which student result is wanted
        :return: question_id, points, feedback, max_point, ilo
        """
        if not self.cnx:
            return None

        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT `Exam_Results`.`question_id`, `Exam_Results`.`points`, `Exam_Results`.`custom_feedback`,\
                                `Questions_in_Exam`.`order`\
                         FROM `Exam_Results` JOIN `Questions_in_Exam`\
                            ON `Exam_Results`.`question_id` = `Questions_in_Exam`.`question_id`\
                            AND `Exam_Results`.`exam_id` = `Questions_in_Exam`.`exam_id`\
                        WHERE `Exam_Results`.`exam_id` = ? AND\
                            `Exam_Results`.`student_id` = ?\
                        ORDER BY `Exam_Results`.`order`, `Questions_in_Exam`.`order`",
                        (exam_id, student_id)
                        )
        _student_result = []
        for _r in _cursor.fetchall():
            _temp = list(_r)
            _question = self.get_questions_by_id(_temp[0])
            _temp.append(self.get_bibliography_for_question(_temp[0]))
            _temp.append(self.get_question_ilo(_temp[0]))
            _temp.append(self.get_question_max_point(_temp[0]))
            _temp.append(self.get_question_tags(_temp[0]))
            _temp.append(_question[4])
            _student_result.append(_temp)

        return _student_result

    def update_student_id_from_exam_result(self, exam_id, order, student_id, new_student_id):
        if not self.cnx:
            return None

        if self.student_exist(student_id,exam_id):
            return

        _cursor = self.cnx.cursor()
        _cursor.execute("UPDATE `Exam_Results`\
                        SET `student_id` = ?,\
                            `order` = ?\
                        WHERE `student_id` = ?\
                        AND\
                        `exam_id` = ?",
                        (new_student_id, order, student_id, exam_id)
                        )
        self.cnx.commit()
        _cursor.close()
        return

    def get_question_scores(self, question_id):
        """
        Get average question score for a question.
        :param question_id: Question ID to collect data about.
        :return: dictionary in form {"max_point": 0,
                                     "question_data": ['student points']
                                    }
        """
        if not self.cnx:
            return None

        _result = {"max_point": 0,
                   "question_data": []
                   }

        _cursor = self.cnx.cursor()
        _cursor.execute("SELECT points \
                         FROM Questions \
                         WHERE question_id = ?",
                        (question_id,)
                        )

        _data = _cursor.fetchall()

        if not _data:
            return _result

        _result["max_point"] = _data[0][0]

        _cursor.execute("SELECT points \
                         FROM Exam_Results \
                         WHERE question_id = ?",
                        (question_id,)
                        )

        _question_result = _cursor.fetchall()

        if _question_result:
            for _score in _question_result:
                _result["question_data"].append(float(_score[0]))

        return _result
