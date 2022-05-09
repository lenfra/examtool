# -*- coding: utf-8 -*-
from GUI.Messagedialogue import MessageDialogWindow

import openpyxl
from datetime import datetime, date
import os


class ExamResultTemplate:
    def __init__(self, connector, settings, exam_id=None, exam_date=None, course_id=None):
        self.cnx = connector
        self.Settings = settings

        self.question_ids = []

        self._exam_id = exam_id
        self._exam_date = exam_date

        self._course_id = course_id
        self._students = []

    def set_question_ids(self, question_ids):
        self.question_ids = question_ids
        return

    def get_question_ids(self):
        return self.question_ids

    def set_exam_id(self, exam_id):
        self._exam_id = exam_id

    def get_exam_id(self):
        return self._exam_id

    def set_exam_date(self, exam_date):
        self._exam_date = exam_date

    def get_exam_date(self):
        return self._exam_date

    def set_course_id(self, _course_id):
        self._course_id = _course_id

    def get_course_id(self):
        return self._course_id

    def append_student(self, student):
        self._students.append(student)

#TODO: Rewrite this. Very long and messy.
    def generate_template(self):
        _message_dialogue = MessageDialogWindow()

        try:
            assert (isinstance(self._course_id, str))
            assert (isinstance(self._exam_date, date))
            assert (isinstance(self._exam_id, str))
        except AssertionError as err:
            print(err)
            return

        if not self.question_ids:
            print('No question IDs')
            return

        _template_name = '%s_%s.xlsx' % (self._course_id,
                                         datetime.strftime(self._exam_date,
                                                           '%Y%m%d')
                                         )
        _new_file_path = self.Settings.get_program_path() + '/' + 'Courses/' + \
                         self._course_id + '/' + 'ExamResults/'

        if not os.path.isdir(_new_file_path):  # If folder don't exist, create it.
            try:
                os.makedirs(_new_file_path, exist_ok=True)
            except OSError:
                print('Unable to create file path %s' % _new_file_path)

        _new_abs_filename = os.path.join(_new_file_path, _template_name)

        if os.path.isfile(_new_abs_filename):
            if not _message_dialogue.confirmation_dialogue("File already exist", "Overwrite?"):
                return _new_abs_filename

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Result"

        _heading = ['Course: %s' % self._course_id, 'Exam ID: %s' % self._exam_id,
                    'Examdate: %s' % datetime.strftime(self._exam_date, '%Y-%m-%d')]
        worksheet.append(_heading)
        worksheet.append([])

        _questions = ['Student Code:']
        for _q in self.question_ids:
            _questions.append(_q)
            _questions.append('Teacher Comment')

        worksheet.append(_questions)

        if self._students:
            for _s in self._students:
                _student_row = [_s.get_student_id()]
                for _q in self.question_ids:
                    _result = _s.get_question_grade(_q)
                    _student_row.append(_result["earned_points"])
                    _student_row.append(_result["teacher_comment"])
                worksheet.append(_student_row)

        workbook.save(_new_abs_filename)

        return _new_abs_filename
