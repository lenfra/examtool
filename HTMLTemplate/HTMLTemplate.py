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

    def _generate_student_summary(self, student, recommended_reading_path=None, pass_limit=None):
        """
        Method to generate student html pages.
        :param student: StudentExamGrade object
        :return: a list in following format [{"student_id":student_id,
                                            "URL": 'url to student html page',
                                            "data": html source}
                                          ]
        """
        _new_abs_filename = os.path.join(self._file_path, self._exam_id + '_' + self._exam_date
                                         + '_' + student.get_student_id() + '.html')

        _student_js_path = os.path.join(self._exam_id + '_' + self._exam_date
                                         + '_' + student.get_student_id() + '.js')

        _exam_js_path = os.path.join(self._exam_id + '_' + self._exam_date + '.js')

        student_template = self.env.get_template('student_template_js.html')

        _output = student_template.render(student_id = student.get_student_id(),
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

        return {'student_id': student.get_student_id(),
                'URL': _new_abs_filename,
                'data': student_html_code}

    def generate_html(self, context_dict):
        #  Generate Exam Report
        students_summary_html = []

        for _student in self._student_list:
            students_summary_html.append(self._generate_student_summary(_student))

        # Generate Exam Summary
        _number_of_passed_students = context_dict['exam_summary']["P"] + context_dict['exam_summary']["E"] + \
                                     context_dict['exam_summary']["D"] + context_dict['exam_summary']["C"] + \
                                     context_dict['exam_summary']["B"] + context_dict['exam_summary']["A"]

        _output = self.template.render(exam_js_path = self._exam_data_path,
                                       exam_id=self._exam_id,
                                       course_name=self._course_name,
                                       course_code=self._course_code,
                                       exam_date=self._exam_date,
                                       total_pass=_number_of_passed_students,
                                       total_fail=context_dict['exam_summary']['F'],
                                       total_fx=context_dict['exam_summary']['Fx'],
                                       total_e=context_dict['exam_summary']['E'],
                                       total_d=context_dict['exam_summary']['D'],
                                       total_c=context_dict['exam_summary']['C'],
                                       total_b=context_dict['exam_summary']['B'],
                                       total_a=context_dict['exam_summary']['A'],
                                       total_fail_priv=context_dict['exam_summary_priv']['F'],
                                       total_fx_priv=context_dict['exam_summary_priv']['Fx'],
                                       total_e_priv=context_dict['exam_summary_priv']['E'],
                                       total_d_priv=context_dict['exam_summary_priv']['D'],
                                       total_c_priv=context_dict['exam_summary_priv']['C'],
                                       total_b_priv=context_dict['exam_summary_priv']['B'],
                                       total_a_priv=context_dict['exam_summary_priv']['A'],
                                       failed_tags=context_dict['exam_tags']['failed_tags'],
                                       passed_tags=context_dict['exam_tags']['passed_tags'],
                                       strong_tags=context_dict['exam_tags']['strong_tags'],
                                       ILO=context_dict["ilo_summary"],
                                       students=students_summary_html,
                                       pass_limit=context_dict["pass_limit"],
                                       ladok_report=context_dict["ladok_summary"]
                                       )

        create_dir(self._file_path)

        _new_abs_filename = os.path.join(self._file_path, self._exam_id + '_' + self._exam_date + '.html')

        with io.open(_new_abs_filename, 'w', encoding='utf8') as _tex_file:
            _tex_file.write(_output)

        return _new_abs_filename
