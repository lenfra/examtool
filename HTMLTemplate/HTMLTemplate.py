# -*- coding: utf-8 -*-
import io
import os
import subprocess
import multiprocessing

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ExamClasses.BibliographyClass import Bibliography

from bs4 import BeautifulSoup


def build_htlatex(path):
    if path is None:
        return

    if not os.path.isfile(path):
        return

    file_path = os.path.dirname(path)

    build_reading = subprocess.Popen(path, cwd=file_path, shell=True)
    build_reading.wait()


class HTMLTemplate:
    def __init__(self, exam_db, db_query, settings, exam_id, course_name, course_code, exam_date, student_list):

        self._examDB = exam_db
        self._db_query = db_query
        self._settings = settings
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

        self._file_path = None

        return

    def _generate_latex_reading_instructions(self, recommended_reading, bibliography_path):
        """
        Method to generate the LaTeX code for the students reading instruction
        :param recommended_reading: The reading instructions
        :param bibliography_path: Filepath for where the bibliography will be written
        :return:
        """

        _bibIDs = set()
        _bibliography_list = []

        reading_instructions = "\\documentclass{article} \n" \
                               + "\\usepackage[natbib,style=alphabetic,maxbibnames=99,backend=bibtex]{biblatex}\n" \
                               + "\\addbibresource{%s}\n" % bibliography_path \
                               + "\\begin{document}\n"

        reading_instructions_bibliography = ""

        if recommended_reading:
            reading_instructions = reading_instructions \
                                   + "The following recommended reading instructions have been generated " \
                                   + "based on your exam result.\n" \
                                   + "\\begin{itemize}\n"
            # Grab all citations from recommended reading
            for _bib in recommended_reading:
                _bibIDs.add(_bib['bibliography'])

                _optionals = ' '
                if _bib['optional']:
                    _optionals = ''
                    for _opt in _bib['optional']:
                        _optionals = _optionals + _opt + ','

                reading_instructions = reading_instructions + "\\item " + "\\cite[" + _optionals[:-1] + "]" \
                                       + "{" + str(_bib['bibliography']) + "}" + "\n"

            reading_instructions = reading_instructions \
                                   + "\\end{itemize}" \
                                   + "\n"
        # Get bibliography objects for each bibliography ID
        for _bib in _bibIDs:
            if _bib:
                _bibliography = Bibliography()
                _bibliography.load_from_database(
                    *self._examDB.get_bibliography(_bib)[0])
                _bibliography_list.append(_bibliography)

        for _bib in _bibliography_list:
            reading_instructions_bibliography = reading_instructions_bibliography + _bib.get_bibliography_data()

        reading_instructions = reading_instructions \
                               + "\\printbibliography\n" \
                               + "\\end{document}"

        return reading_instructions, reading_instructions_bibliography

    def _generate_recommended_reading_script_path(self, student_id, recommended_reading):
        """
        Method to generate the HTML-code for recommended reading to the students.
        :param student_id: Student ID
        :param recommended_reading: Reading instructions.
        :return:  HTML-code containing recommended reading for student_id
        """

        if not recommended_reading:
            return None

        # Create file paths
        _file_path = self._settings.get_program_path() + '/' + 'Courses/' + \
                     self._course_code + '/ExamResults/HTML/Students/Reading/'

        if not os.path.isdir(_file_path):  # If folder don't exist, create it.
            try:
                os.makedirs(_file_path, exist_ok=True)
            except OSError:
                print('Unable to create file path %s' % _file_path)

        _bibliography_path = os.path.join(_file_path, student_id + '.bib')
        _reading_instructions_tex_path = os.path.join(_file_path, student_id + '.tex')
        _latex_build_script_path = os.path.join(_file_path, student_id + '.sh')

        # Generate LaTeX code
        recommended_reading_text, recommended_reading_bibliography = self._generate_latex_reading_instructions(
            recommended_reading, _bibliography_path)

        # Write reading_instructions
        with io.open(_reading_instructions_tex_path, 'w+', encoding='utf8') as _tex_file:
            _tex_file.write(recommended_reading_text)

        with io.open(_bibliography_path, 'w+', encoding='utf8') as _bibliography_file:
            _bibliography_file.write(recommended_reading_bibliography)

        _build_script = "#/bin/sh \n" \
                        "htlatex %s && bibtex %s && htlatex %s" % (
                            student_id + '.tex', student_id + '.aux', student_id + '.tex')

        with io.open(_latex_build_script_path, 'w+', encoding='utf8') as _script:
            _script.write(_build_script)

        os.chmod(_latex_build_script_path, 0o755)

        return _latex_build_script_path

    def _generate_student_summary(self, student, recommended_reading_path, pass_limit):
        """
        Method to generate student html pages.
        :param student: StudentExamGrade object
        :return: a list in following format [{"student_id":student_id,
                                            "URL": 'url to student html page',
                                            "data": html source}
                                          ]
        """

        # Read HTML
        if os.path.isfile(recommended_reading_path):
            with io.open(recommended_reading_path, 'r', encoding='utf8') as _html_file:
                html_code = _html_file.read()
        else:
            html_code = None

        if html_code is not None:
            code = BeautifulSoup(html_code, "lxml")
            html_code = code.body
            html_code = '\n'.join(str(html_code).splitlines()[1:-1])

        student_template = self.env.get_template('student_template.html')

        _output = student_template.render(course_name=self._course_name,
                                          course_code=self._course_code,
                                          exam_date=self._exam_date,
                                          student_id=student.get_student_id().replace("-", ""),
                                          summary=student.get_summary(),
                                          recommended_reading=html_code,
                                          pass_limit=pass_limit
                                          )

        self._file_path = self._settings.get_program_path() + '/' + 'Courses/' + \
                          self._course_code + '/ExamResults/HTML/Students'

        if not os.path.isdir(self._file_path):  # If folder don't exist, create it.
            try:
                os.makedirs(self._file_path, exist_ok=True)
            except OSError:
                print('Unable to create file path %s' % self._file_path)

        _new_abs_filename = os.path.join(self._file_path, self._exam_id + '_' + self._exam_date
                                         + '_' + student.get_student_id() + '.html')

        with io.open(_new_abs_filename, 'w', encoding='utf8') as _student_html_file:
            _student_html_file.write(_output)

        code = BeautifulSoup(_output, "lxml")
        student_html_code = code.body
        student_html_code = '\n'.join(str(student_html_code).splitlines()[1:-1])

        return {'student_id': student.get_student_id(),
                'URL': _new_abs_filename,
                'data': student_html_code}

    def generate_html(self, context_dict):
        #  Generate Exam Report
        students_summary_html = []
        student_recommended_reading_build_script = []

        self._file_path = self._settings.get_program_path() + '/' + 'Courses/' + \
                          self._course_code + '/ExamResults/HTML/Students'

        #  Generate build scripts for students recommended reading
        for _student in self._student_list:
            _recommended_reading_build_script_path = self._generate_recommended_reading_script_path(
                _student.get_student_id().replace("-", ""),
                _student.get_summary()["recommended_reading"])

            student_recommended_reading_build_script.append(_recommended_reading_build_script_path)

        # Build HTML

        pool = multiprocessing.Pool(4)
        pool.map(build_htlatex, student_recommended_reading_build_script)

        #  Generate student HTML feedback
        read_file_path = self._file_path + '/Reading/'
        for _student in self._student_list:
            _reading_instruction_html_path = os.path.join(read_file_path,
                                                          _student.get_student_id().replace("-", "") + '.html')
            students_summary_html.append(self._generate_student_summary(_student,
                                                                        _reading_instruction_html_path,
                                                                        context_dict["pass_limit"]))

        # Clean up
        if os.path.exists(read_file_path):
            subprocess.call('rm *', cwd=read_file_path, shell=True)

        # Generate Exam Summary
        _number_of_passed_students = context_dict['exam_summary']["P"] + context_dict['exam_summary']["E"] + \
                                     context_dict['exam_summary']["D"] + context_dict['exam_summary']["C"] + \
                                     context_dict['exam_summary']["B"] + context_dict['exam_summary']["A"]


        _output = self.template.render(course_name=self._course_name,
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
                                       ILO=context_dict["ILO"],
                                       students=students_summary_html,
                                       pass_limit=context_dict["pass_limit"],
                                       ladok_report=context_dict["ladok_report"]
                                       )

        _file_path = self._settings.get_program_path() + '/' + 'Courses/' + \
                     self._course_code + '/ExamResults/HTML/'

        if not os.path.isdir(_file_path):  # If folder don't exist, create it.
            try:
                os.makedirs(_file_path, exist_ok=True)
            except OSError:
                print('Unable to create file path %s' % _file_path)

        _new_abs_filename = os.path.join(_file_path, self._exam_id + '_' + self._exam_date + '.html')

        with io.open(_new_abs_filename, 'w', encoding='utf8') as _tex_file:
            _tex_file.write(_output)

        return _new_abs_filename
