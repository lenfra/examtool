# -*- coding: utf-8 -*-
import io
import os
import json
import subprocess

from ExamClasses.BibliographyClass import Bibliography

def build_htlatex(path):
    if path is None:
        return

    if not os.path.isfile(path):
        return

    file_path = os.path.dirname(path)

    build_reading = subprocess.Popen(path, cwd=file_path, shell=True)
    build_reading.wait()

def create_dir(path):
    if not os.path.isdir(path):  # If folder don't exist, create it.
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            print('Unable to create file path %s' % path)


class JSON_gen:
    def __init__(self, exam_db, db_query, settings, exam_id, course_name, course_code, exam_date, student_list):

        self._examDB = exam_db
        self._db_query = db_query
        self._settings = settings
        self._exam_id = exam_id
        self._course_code = course_code
        self._course_name = course_name
        self._exam_date = exam_date
        self._student_list = student_list

        self._file_path = self._settings.get_program_path() + '/' + 'Courses/' + \
                          self._course_code + '/ExamResults/HTML/Students'

        return

    def _generate_recommended_reading_json(self, recommended_reading):
        """
        Method to generate students reading instruction in JSON-format
        :param recommended_reading: The bibliography IDs
        :param bibliography_path: Filepath for where the bibliography will be written
        :return:
        """

        if not recommended_reading:
            return None

        _bibliography_list = []

        merged_recommended_reading = []

        # Grab all citations from recommended reading and merge them
        for _bib in recommended_reading:
            _new_bib = True
            if merged_recommended_reading:
                for _existing_bib in merged_recommended_reading:
                    if _bib['bibliography'] == _existing_bib['bibliography']:
                        _new_bib = False
                        for _opt in _bib['optional']:
                            if not _opt in _existing_bib['optional']:
                                _existing_bib['optional'].append(_opt)
                if _new_bib:
                    merged_recommended_reading.append(_bib)
            else:
                merged_recommended_reading.append(_bib)

        # Get bibliography objects for each bibliography ID and add optionals
        for _bib in merged_recommended_reading:
            _bibliography = Bibliography()
            _bibliography.load_from_database(
                *self._examDB.get_bibliography(_bib['bibliography'])[0])
            _bib_json = _bibliography.get_raw_bibliography_data()
            _bib_json['optionals'] = _bib['optional']
            _bibliography_list.append(_bib_json)

        return _bibliography_list

    def _generate_student_json_summary(self, student, recommended_reading_json):
        """
        Method to generate student html pages.
        :param student: StudentExamGrade object
        :return: a list in following format [{"student_id":student_id,
                                            "URL": 'url to student html page',
                                            "data": html source}
                                          ]
        """
        #  Made a copy, otherwise it will overwrite the existing student object used in HTMLTemplate.
        _student_json_output = student.get_summary().copy()

        _student_json_output["recommended_reading"] = recommended_reading_json

        create_dir(self._file_path)

        _new_abs_filename = os.path.join(self._file_path, self._exam_id + '_' + self._exam_date
                                         + '_' + student.get_student_id() + '.json')

        with io.open(_new_abs_filename, 'w', encoding='utf8') as _student_json_file:
            json.dump(_student_json_output, _student_json_file)

    def gen_json(self):
        #  Generate Exam Report

        for _student in self._student_list:
            _student_bibliography_json = self._generate_recommended_reading_json(
                    _student.get_summary()["recommended_reading"])

            self._generate_student_json_summary(_student,
                                                _student_bibliography_json)
