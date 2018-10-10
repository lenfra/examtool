#!/usr/bin/env python
# coding:utf-8

import re
from ExamClasses.QuestionClass import Question
from ExamClasses.PackageClass import Package
from ExamClasses.GraphicsClass import Graphics
from Parser.BibParser import BibParser
from GUI.Messagedialogue import MessageDialogWindow

import codecs
import os
from urllib.parse import urlparse
from urllib.request import urlretrieve
import shutil
import warnings

__author__ = "Lennart Franked"
__email__ = "lennart.franked@miun.se"
__version__ = "0.5"

"""
"""


class LatexParser:
    def __init__(self, connector, settings):

        self._course_information = {
            'course_code': '',
            'course_version': '',
            'table': 'Questions',
            'language': 'ENG',
        }
        self._file_info = {
            'filepath': '',
            'filename': '',
        }

        self.Settings = settings

        self._question_error = 0

        self.question_list = []
        self.questions_without_Goal = []

        self._temp_package_store = []

        self.bibliography_parser = BibParser()
        self._bibliography_paths = []

        self._points = re.compile('\[(.+?)\]')

        self._cite = re.compile(r'\\cite(?P<optional>\[.*?\])*'
                                r'(?P<bibliography>\{.+?\})')

        self._include_graphics = re.compile(r'\\includegraphics(?P<optional>\[.*?\])*'
                                            r'(?P<graphics_path>\{.+?\})')

        self._package_requirement = re.compile(r'\\usepackage(?P<optional>\[.*?\])*'
                                               r'(?P<package>\{.+?\})')

        self._bibliography_path = re.compile('(\\bibliography|\\addbibresource)\{(.+?)\}')

        self.parse_points = re.compile(r'(?P<number>[0-9]*)?(?P<half>\\half)*')

        self._question_exist = False

        self.cnx = connector
        self.ExamDB = None

    def set_examdb(self, examdb):
        self.ExamDB = examdb
        return

    def run(self, data, usable):
        self.parse(data, usable)
        self.check_questions_for_declarations()
        return

    def parse_from_file(self, filename, course, course_version):
        self._course_information['course_code'] = course
        self._course_information['course_version'] = course_version
        data = ""

        self._file_info['filepath'] = os.path.dirname(filename)
        self._file_info['filename'] = os.path.basename(filename)

        with codecs.open(filename, 'r', 'utf8') as fp:
            data += fp.read()

        self.run(data, True)

        return self.question_list

    def parse_data(self, data, course, course_version, usable):
        self._course_information['course_code'] = course
        self._course_information['course_version'] = course_version
        self.run(data, usable)

        return self.question_list

    def database_query(self, query):
        # noinspection PyUnresolvedReferences
        self.cursor.execute(query)
        if 'SELECT' in query:
            # noinspection PyUnresolvedReferences
            return self.cursor.fetchall()

        else:
            self.cnx.commit()
            return

    @staticmethod
    def search_keyword(key, data):
        keyword = re.escape(key)
        pattern = re.compile(r'(.*%s.*)' % keyword)

        if pattern.search(data):
            return True
        return False

    def set_usable(self, question):
        """
        Method used for setting a question as usable or not. If error exist, set question as unusable, otherwise usable.
        :param question: The question object
        :return:
        """
        if self._question_error > 0:
            question.set_usable(False)
        else:
            question.set_usable(True)

    def add_points(self, question, line):
        if not question:
            return
        if not line:
            return

        _total_points = 0
        po = self._points.findall(line)
        if po:
            _parsed_points = self.parse_points.search(po[0])
            if _parsed_points.group('number'):
                _total_points += int(_parsed_points.group('number'))

            elif _parsed_points.group('half'):
                _total_points += 0.5
            else:
                warnings.warn('Invalid point')
                _messagedia = MessageDialogWindow()
                _messagedia.information_dialogue('Invalid Points',
                                                 'Points given isn\'t valid')
                self._question_error += 1
                self.set_usable(question)
                return

        question.append_points(_total_points)
        self.set_usable(question)

    def check_points(self, question):
        if question.get_points() == 0:
            self._question_error += 1
            warnings.warn('Question don\'t have any points set')

    def check_questions_for_declarations(self):
        cursor = self.cnx.cursor()
        cursor.execute("SELECT distinct * \
                            FROM Declarations")
        declarations = cursor.fetchall()
        cursor.close()

        for q in self.question_list:
            for d in declarations:
                if self.search_keyword(d[2], q.get_question_code()) \
                        is not False:
                    q.append_declaration_requirement(d[0])
        return

    def retrieve_goal_by_label(self, question, line):
        relabel = re.compile(r'\\label\{q:(.+?)\}')
        label = relabel.findall(line)
        cursor = self.cnx.cursor()

        try:
            modlabel = '%' + label[0] + '%'

            cursor.execute("SELECT goal "
                           "FROM ILO "
                           "WHERE course_code='%s' "
                           "AND course_version='%s' "
                           "AND (ILO.tags) LIKE ('%s')"
                           % (self._course_information['course_code'],
                              self._course_information['course_version'],
                              modlabel)
                           )
            goal = cursor.fetchall()
            cursor.close()

            if not goal:  # If no goal has been identified, raise a warning and mark question as not usable
                warnings.warn('LabelError')
                _messagedia = MessageDialogWindow()

                _messagedia.information_dialogue('Label Error',
                                                 'Unable to find a course goal for label %s' % (label[0],))
                self._question_error += 1
                self.set_usable(question)

            else:
                question.append_to_ilo(goal[0][0])
                question.set_course_information(self._course_information['course_code'],
                                                self._course_information['course_version'])

                question.append_tags(label[0])
                self.set_usable(question)
            return

        except IndexError as err:
            print(err)
            return

    def _new_question(self, line, usable):
        """
        Creates a new question object
        :param line: The line to parse
        :return: object from class Question()
        """
        _question = None

        if not self._question_exist:  # First occurrence of question in file
            _question = Question()
            if not usable:
                self._question_error = 1
            else:
                self._question_error = 0

            # Check if package requirement exists.
            if self._temp_package_store:
                for _p in self._temp_package_store:
                    _question.append_package_requirement(_p[0], _p[1])
                self._temp_package_store = []

            self.question_list.append(_question)
            self._question_exist = True

        elif self._question_exist:  # New _question in file
            _question = Question()
            self._question_error = 0

            if self._temp_package_store:
                for _p in self._temp_package_store:
                    _question.append_package_requirement(_p[0], _p[1])
                self._temp_package_store = []

            self.question_list.append(_question)

        if self._points.search(line):
            self.add_points(_question, line)

        return _question

    def append_citation(self, line):
        """
        Parse line for citation, and returns the Bibliography-ID. Used to generate bibtex-file.
        :param line: Text to be parsed
        :return: List of Bibliography_dicts in form [{'optional': [],'bibliography': '',}]
        """
        if not line:
            return None

        if not self._cite.search(line):
            return None

        _optionals = None
        _citations = []

        bibliography = self._cite.findall(line)

        for _bib in bibliography:
            _bibliography_requirement = {'optional': [],
                                         'bibliography': '',
                                         }
            if _bib[0]:
                _optionals = re.sub('\[|\]', '', _bib[0])

            _bibliography_requirement['bibliography'] = re.sub('\{|\}', '', _bib[1])
            if _optionals:
                for opt in _optionals.split(','):
                    _bibliography_requirement['optional'].append(opt)
            _citations.append(_bibliography_requirement)

        return _citations

    def _append_graphics(self, line, question):
        """
        Parse line for \includegraphics, if not in work dir, move graphics and rewrite file path.
        :param line: line to be parsed
        :param question: question to append graphics requirement to
        :return: True if graphics exist.
        """

        # TODO: Handle relative paths, add and remove from DB.
        _graphics_data = {
            'graphics_path': '',
            'graphics_id': '',
            'optional': '',
        }

        _graphics_path = self._include_graphics.search(line)

        if _graphics_path.group('optional'):
            _graphics_data['optional'] = re.sub('\[|\]', '',
                                                _graphics_path.group('optional'))

            _graphics_data['graphics_path'] = re.sub('\{|\}', '',
                                                     _graphics_path.group('graphics_path'))

        _graphics_dirname = os.path.dirname(_graphics_data['graphics_path'])
        _graphics_filename = os.path.basename(_graphics_data['graphics_path'])

        _graphics = Graphics()

        if self.ExamDB.graphics_exist(_graphics_filename):
            _graphics.load_from_database(*self.ExamDB.get_graphics(_graphics_filename)[0])
            _graphics.set_optional(_graphics_data['optional'])

        else:
            _new_filepath = self.Settings.get_program_path() + '/' + 'Courses/' + \
                            self._course_information['course_code'] + '/' + 'Graphics/'

            if not os.path.isdir(_new_filepath):  # If folder don't exist, create it.
                try:
                    os.makedirs(_new_filepath, exist_ok=True)
                except OSError:
                    print('Unable to create filepath %s' % _new_filepath)

            _given_path = urlparse(_graphics_data['graphics_path'])

            if _given_path.scheme in ['http', 'https', 'ftp']:  # IS URL
                _new_abs_filename = os.path.join(_new_filepath, _graphics_filename)
                try:
                    urlretrieve(_graphics_data['graphics_path'],
                                _new_abs_filename)
                except OSError:
                    print('Unable to save graphics from URL: %s' %
                          (_graphics_data['graphics_path']))

            else:  # Is local file
                # Deal with relative filepaths when importing files.
                if not _graphics_dirname:  # If graphics is in workdir
                    _graphics_dirname = self._file_info['filepath']

                if not os.path.isdir(_graphics_dirname):  # If graphics is in relative filepath
                    _graphics_dirname = os.path.relpath(_graphics_dirname, self._file_info['filepath'])

                _old_abs_filename = os.path.join(_graphics_dirname, _graphics_filename)

                _new_abs_filename = os.path.join(_new_filepath, _graphics_filename)

                if not os.path.isfile(_new_abs_filename):
                    try:
                        shutil.copy(_old_abs_filename, _new_abs_filename)

                    except FileNotFoundError:
                        print('File not found')

            # Add graphics to DB
            _graphics.set_id(_graphics_filename)
            _graphics.set_optional(_graphics_data['optional'])
            _graphics.set_uri(_new_abs_filename)
            _graphics.set_connector(self.cnx)
            _graphics.insert_into_database()

        if question:
            question.append_question(_graphics.generate_include_code())
            question.append_graphics_requirement(_graphics.get_id())

        return True

    def _append_package(self, line):
        """
        Parse line for package requirement
        :param line: Line to be parsed
        :return:
        """
        _package = self._package_requirement.search(line)

        _pack_req = {'optional': None,
                     'package': '',
                     }

        if _package.group('optional'):
            _pack_req['optional'] = re.sub('\[|\]', '',
                                           _package.group('optional'))

        _pack_req['package'] = re.sub('\{|\}', '',
                                      _package.group('package'))
        if self.ExamDB:
            # Retrieive package ID, if package don't exist, None is returned.
            if _pack_req['package'] is None:
                return

            _csv_packages = _pack_req['package'].split(',')

            for _p in _csv_packages:
                _id = self.ExamDB.package_exist(_p)
                if not _id:
                    # If package previously don't exist, add package to DB.
                    _new_package = Package()
                    _new_package.set_id(self.ExamDB.gen_id("package"))
                    _new_package.set_package_data(_pack_req['package'])
                    _new_package.set_options(_pack_req['optional'])
                    _new_package.set_connector(self.cnx)
                    _new_package.insert_into_database()
                    _id = _new_package.get_id()

                # Add package ID and _question specific optionals as package requirement.
                self._temp_package_store.append([_id, _pack_req['optional']])

    @staticmethod
    def _question_append_line(_question, line):
        """
        Append question line
        :param _question: The question object that the line should be appended to
        :param line: The question line that should be appended
        :return:
        """
        _ignore_ilo_info = re.compile(r'(\\emph\{\(ILO: (.+?)\)\})')
        if _ignore_ilo_info.search(line):
            line = re.sub(r'(\\emph\{\(ILO: (.+?)\)\})', '', line)
        _question.append_question(line)

    @staticmethod
    def _question_append_solution(_question, line):
        """
        Append solution to question
        :param _question: The question object that solution line should be appended to
        :param line: The line containing part of the solution.
        :return:
        """
        _ignore_question_id = re.compile(r'(\\textbf\{for question (.+?) \})')
        if not _ignore_question_id.search(line):
            if _question:
                _question.append_answer(line)

    def append_bibliography(self, line, question=None):
        """
        Read a bibliography file and add each bibtex entry to DB.
        :param line: Line containing searchpath for bibtex file.
        :param question: Question to append bibliography requirement to
        :return:
        """
        # Load bibliography from _question
        path = self._bibliography_path.search(line)
        bibpath = path.group(2)
        biblist = self.bibliography_parser.load_bibtex_from_file(bibpath)
        if self.ExamDB:
            for bib in biblist:
                if not self.ExamDB.bibliography_exist(
                        bib.get_bibliography_id()):
                    bib.set_connector(self.cnx)
                    bib.insert_into_database()

                if question:
                    question.append_bibliography_requirement(bib.get_bibliography_id())

    def parse(self, data, usable):
        _solution_exist = False
        _graphics_exist = False

        _relabel = re.compile(r'\\label\{q:(.+?)\}')
        _new_question = re.compile(r'\\question')
        _begin_questions = re.compile(r'\\begin\{questions\}')
        _end_questions = re.compile(r'\\end\{questions\}')
        _start_solution = re.compile(r'(\\begin\{solution\})')
        _part_question = re.compile(r'\\part')
        _end_solution = re.compile(r'(\\end\{solution\})')

        _question = None
        for line in data.splitlines(True):
            if self._package_requirement.search(line):
                self._append_package(line)

            elif _begin_questions.search(line):  # If encountering \begin{questions},
                # indicates a full exam is being loaded.
                self._temp_package_store = []
                _question = None  # Ensure that question is removed.

            elif _end_questions.search(line):
                _question = None

            elif _new_question.search(line):  # search for '\question' in line.
                _question = self._new_question(line, usable)
                self._question_append_line(_question, line)
                if _relabel.search(line):
                    self.retrieve_goal_by_label(_question, line)

            elif _part_question.search(line):
                if self._points.search(line):
                    self.add_points(_question, line)
                    self._question_append_line(_question, line)

            elif _relabel.search(line):
                self.retrieve_goal_by_label(_question, line)
                self._question_append_line(_question, line)

            elif self._cite.search(line):
                if _question:
                    _citations = self.append_citation(line)
                    for _bib in _citations:
                        _question.append_bibliography_requirement(_bib)
                        
                    if _solution_exist:
                        self._question_append_solution(_question, line)
                    else:
                        self._question_append_line(_question, line)

            elif _start_solution.search(line):  # Find solution to _question
                self.check_points(_question)
                _solution_exist = True

            elif _end_solution.search(line):  # Find solution to _question
                _solution_exist = False

            elif _solution_exist:
                self._question_append_solution(_question, line)

            elif self._include_graphics.search(line):
                _graphics_exist = self._append_graphics(line, _question)
                if _solution_exist:
                    self._question_append_solution(_question, line)
                else:
                    self._question_append_line(_question, line)

            elif self._bibliography_path.search(line):
                if _question:
                    self.append_bibliography(line, _question)

            elif _question and not _solution_exist:
                self._question_append_line(_question, line)

        if not _graphics_exist:
            if _question:
                _question.set_graphics_requirement('')

        return True
