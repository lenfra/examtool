# -*- coding: utf-8 -*-
import io
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ExamClasses.BibliographyClass import Bibliography

from bs4 import BeautifulSoup

def create_dir(path):
    if not os.path.isdir(path):  # If folder don't exist, create it.
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            print('Unable to create file path %s' % path)
    return

class HTMLTemplate:
    def __init__(self, exam_db, db_query, path, exam_id, course_name, course_code, exam_date, exam_data_path, student_list):

        self._examDB = exam_db
        self._db_query = db_query
        self._exam_id = exam_id
        self._course_code = course_code
        self._course_name = course_name
        self._exam_date = exam_date
        self._student_list = student_list

        self.env = Environment(
            loader=FileSystemLoader('Templates'),
            autoescape=select_autoescape(['html'])
        )

        self.template = self.env.get_template('template.html')

        self._file_path = path
        self._exam_data_path = exam_data_path
        return

    def _generate_student_summary(self, student):
        """
        Method to generate student html pages.
        :param student: StudentExamGrade object
        :return: a list in following format [{"student_id":student_id,
                                            "URL": 'url to student html page',
                                            "data": html source}
                                          ]
        """
        _new_abs_filename = os.path.join(self._file_path, self._exam_id + '_' + self._exam_date
                                         + '_' + student.get_student_id_stripped() + '.html')

        _student_js_path = os.path.join(self._exam_id + '_' + self._exam_date
                                         + '_' + student.get_student_id_stripped() + '.js')

        _exam_js_path = os.path.join(self._exam_id + '_' + self._exam_date + '.js')

        student_template = self.env.get_template('student_template_js.html')

        _output = student_template.render(student_id = student.get_student_id_stripped(),
                                          exam_id = self._exam_id,
                                          exam_js_path = _exam_js_path,
                                          student_js_path = _student_js_path)

        create_dir(self._file_path)

        with io.open(_new_abs_filename, 'w', encoding='utf8') as _student_html_file:
            _student_html_file.write(_output)

        code = BeautifulSoup(_output, "lxml")
        student_html_code = code.body
        student_script_code = code.find_all('script')
        student_html_code = '\n'.join(str(student_html_code).splitlines()[1:-1]) + '\n' + \
                            str(student_script_code[1]) + '\n' +\
                            str(student_script_code[6]) + '\n'

        return {'student_id': student.get_student_id_stripped(),
                'URL': _new_abs_filename,
                'data': student_html_code}

    def generate_html(self):
        #  Generate Exam Report
        students_summary_html = []

        for _student in self._student_list:
            students_summary_html.append(self._generate_student_summary(_student))

        # Generate Exam Summary
        _output = self.template.render(exam_js_path = self._exam_data_path,
                                       exam_id=self._exam_id,
                                       students=students_summary_html,
                                       )

        create_dir(self._file_path)

        _new_abs_filename = os.path.join(self._file_path, self._exam_id + '_' + self._exam_date + '.html')

        with io.open(_new_abs_filename, 'w', encoding='utf8') as _tex_file:
            _tex_file.write(_output)

        return _new_abs_filename
