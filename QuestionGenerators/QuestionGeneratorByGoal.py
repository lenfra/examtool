# -*- coding: utf-8 -*-
import random
from datetime import timedelta, date
from math import floor

from ExamClasses.QuestionClass import Question


class GenerateQuestionsByGoal:
    """
    This module is used for generating questions based on Intended learning outcomes. It also takes into account
    whether or not a question has been used within the last year. By default questions with the same tags are considered
     to similar and therefore same tagged questions can not be in the same exam. This can be allowed by setting
     allow_same_tags to True.
    """

    def __init__(self, examdb, number_of_questions, intended_learning_outcome_used, course_code,
                 course_version, exam_date, allow_same_tags=False, existing_questions=None):
        """
        Init function, sets all the variables necessary to be able to get questions for an exam.
        :param examdb: An object ot the ExamDB class, used to retreive questions from the database.
        :param number_of_questions: Number of questions that the exam should hold.
        :param intended_learning_outcome_used: What Intended Learning Outcomes should be examined.
        :param course_code: The course code of the course the exam is given for.
        :param course_version: The course version of this course.
        :param exam_date: The date that the exam will be given
        :param allow_same_tags: Flag to set whether or not same tagged questions should be allowed.
        :param existing_questions: List if Questions IDs that must be included in the exam.
        """
        try:
            assert (isinstance(number_of_questions, int))
            self.numQuest = number_of_questions
            self.ILOUsed = list(intended_learning_outcome_used)

            assert (isinstance(course_code, str))
            self.course_code = course_code

            assert (isinstance(course_version, float))
            self.course_version = course_version

            assert (isinstance(exam_date, date))
            self.exam_date = exam_date

            assert (isinstance(allow_same_tags, bool))
            self.allow_same_tags = allow_same_tags

        except AssertionError as err:
            print("Generate Questions By Goal init: " + str(err))
            return

        self.ExamDB = examdb
        self._exam_id = {
            'exam_id': '',
            'question_ids': [],
            'declaration_id': [],
            'bibliography_id': []
        }

        self._objects = {'Declarations': [],
                         'Questions': [],
                         }
        self._days = 365  # Number of days that a question is "quarantined".

        if existing_questions:
            for _qid in existing_questions:
                self._exam_id['question_ids'].append(_qid)
                self._add_question_to_exam(_qid)
            self.numQuest -= len(existing_questions)

        if self.numQuest > 0:  # If there are more questions to add, run generator algorithm
            self._gen_questions_by_goals()

    def set_allow_same_tags(self, allow_same_tags):
        """Set flag if same tagged questions should be allowed in the exam."""
        assert isinstance(allow_same_tags, bool)
        self.allow_same_tags = allow_same_tags

    def get_allow_same_tags(self):
        """Returns whether or not same tagged questions are allowed"""
        return self.allow_same_tags

    def similar_question_exist(self, question):
        """
        Ensures that there are no similar quesitons in the exam. This is done using two
        checks. The first is based on the tag each question is given. All questions with same tag, are
        considered similar. Next a check is done to see if user have manually defined any similar question as well
        using the "Not in Same Exam".
        :param question: Question ID on potential question to use
        :return: a list over similar questions
        """

        similar = self.ExamDB.similar_question_used(question, self.allow_same_tags)
        if similar:
            for usedQuestion in self._exam_id['question_ids']:
                for similarQuestion in similar:
                    if usedQuestion == similarQuestion:
                        return True
        return False

    def _get_questions_for_ilo(self, ilo, number_of_questions):
        assert (isinstance(ilo, str))
        assert (isinstance(number_of_questions, int))
        assert (isinstance(self.exam_date, date))

        # Get questions that are connected to the requested ILO
        questions_by_goal = self.ExamDB.get_questions_by_ilo(ilo,
                                                             self.course_code,
                                                             self.course_version)
        assert (isinstance(questions_by_goal, list))

        while number_of_questions > 0:
            if len(questions_by_goal) < 1:  # No available questions in dataset.
                print('No usable questions for ilo %s'
                      % (ilo,))
                return None

            # Get _random _question from dataset where question is older than one year
            _question = random.choice(questions_by_goal)
            assert (isinstance(_question, tuple))

            # Check when question was last used.
            _last_used = self.ExamDB.get_question_last_used(_question[0])

            # Check if _question already been taken or a similar question have been
            # used
            if _question[0] in self._exam_id['question_ids'] or \
                    self.similar_question_exist(_question[0]):
                questions_by_goal.remove(_question)

            # Check if the question have been used for self._days number of days.
            elif _last_used > self.exam_date - timedelta(days=self._days):
                questions_by_goal.remove(_question)

            # Question can be added to Exam.
            else:
                self._add_question_to_exam(_question[0])
                questions_by_goal.remove(_question)
                number_of_questions -= 1

    def _add_question_to_exam(self, _question_id):
        """
        Based on question ID, create a Question object and add this question to the exam.
        :param _question_id: The question ID for the question that should be added.
        :return:
        """
        # Add question to current exams question dataset.
        assert (isinstance(_question_id, str))
        question = Question()
        question.load_from_database(*self.ExamDB.get_questions_by_id(_question_id))

        self._objects["Questions"].append(question)
        self._exam_id['question_ids'].append(_question_id)

        return

    # noinspection PyProtectedMember
    def _gen_questions_by_goals(self):
        """
        Retrieves random questions from database based on specified course
        goals and number of questions specified for the exam.

        Evenly distributes the number of questions per ilo and then get the
        number of questions based on last used.
        """

        try:
            num_questions_per_goal = int(floor(self.numQuest / len(self.ILOUsed)))

            # Ensure that the number of questions requested are less than unique ILO's to be used.
            assert ((self.numQuest / len(self.ILOUsed)) >= 1)

        except ZeroDivisionError:
            print("No ILO's selected, or number of question in exam is set to 0")
            return

        except AssertionError:
            print("There aren't enough questions for the number of ILO's chosen, increase the number of questions " \
                  + "or reduce the number of ILO's covered in this exam")
            return

        rest = self.numQuest % len(self.ILOUsed)

        for ilo in self.ILOUsed:
            # Retrieve all questions that belongs to ilo
            self._get_questions_for_ilo(ilo[0], num_questions_per_goal)

        while rest > 0:
            ilo = random.choice(self.ILOUsed)
            self._get_questions_for_ilo(ilo[0], 1)
            rest -= 1

        return

    def get_questions(self):
        """
        A Generator that will return all the questions that have been selected for this exam.
        :return: Question objects
        """
        for q in self._objects["Questions"]:
            yield (q)

        return
