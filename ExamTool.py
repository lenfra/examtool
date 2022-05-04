# !/usr/bin/env python3
# coding:utf-8


import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')

import json

from datetime import datetime
from Database.ExamDB import ExamDB

from Parser.LatexParser import LatexParser
from Parser.BibParser import BibParser

from ExamClasses.SettingsClass import Settings
from ExamClasses.ExamClass import Exam
from ExamClasses.QuestionClass import Question
from ExamClasses.AuthorClass import Author
from ExamClasses.CourseClass import Course
from ExamClasses.CourseGoalClass import ILO
from ExamClasses.DeclarationClass import Declaration
from ExamClasses.BibliographyClass import Bibliography
from ExamClasses.PreambleClasses import DocumentClass
from ExamClasses.PreambleClasses import Instructions
from ExamClasses.Profile import Profile
from ExamClasses.StudentExamGrade import StudentExamGrade

from Statistics.GenerateExamStatistics import GenerateExamStatistics
from Statistics.GenerateQuestionStatistics import GenerateQuestionStatistics

from HTMLTemplate.HTMLTemplate import HTMLTemplate
from HTMLTemplate.JSON_gen import JSON_gen

from ExamClasses.PackageClass import Package
from ExamClasses.DefPackageClass import PreamblePackages

from Parser.ExamResultTemplate import ExamResultTemplate
from Parser.ExamResultParser import ExamResultParser

from GUI.Messagedialogue import MessageDialogWindow
from GUI.GuiHandlers import Handler

from QuestionGenerators.QuestionGeneratorByGoal import GenerateQuestionsByGoal
import io

import os
import subprocess
import re
import random

from fnmatch import fnmatch

# noinspection PyUnresolvedReferences
from gi.repository import Gtk, GtkSource, GObject, Gdk, GLib

import webbrowser



__author__ = "Lennart Franked"
__email__ = "lennart.franked@miun.se"
__version__ = "0.8"

"""
"""


# noinspection PyAttributeOutsideInit,PyUnusedLocal

class Gui:
    def __init__(self):

        # Init GUI
        GObject.type_register(GtkSource.View)
        self.ExamDB = ExamDB()

        # Load glade-file
        self.builder = Gtk.Builder()
        self.builder.add_from_file("GUI/ExamGUIGlade.glade")
        self.builder.connect_signals(Handler(self))

        self._retrieve_objects()
        self._set_globals()
        self._load_config()

        self._connected_to_database = False

        # Connect to database
        self._connected_to_database = self._db_settings_exist()

        # Setup syntax highlighting for text viewer
        self._setup_syntax_highlighting()

        self.new_exam()

        self.window = self.builder.get_object("MainWindow")

        # Create the tree views
        self._create_author_list()
        self._create_course_list()
        self._create_ilo_list()
        self._create_docclass_list()
        self._create_instructions_list()
        self._create_question_id_list()
        self._create_question_id_in_exam_list()
        self._create_declaration_list()
        self._create_bibliography_list()
        self._create_preamble_package_list()
        self._create_package_id_list()
        self._setup_profile_combo_box()
        self._setup_combo_box()
        self._create_not_in_same_exam_list()
        self._create_old_exam_list()
        self._create_quest_package_req_list()

        # Retrieve default data from DB
        self.get_init_data_from_db()

        self.window.show_all()
        Gtk.main()

    def get_init_data_from_db(self):
        """
        Runs at start to retrieve initial data from the database, such as
        document classes, available instructions, authors, courses, profiles,
        gradelimits and preambles.
        """
        if self._connected_to_database:
            self._get_docclass()
            self._get_instructions()
            self._get_authors()
            self._get_courses()
            self._get_profile_list()
            self._get_gradelimits()
            self._get_preamble_package_list()

    def _set_globals(self):
        """
        Run at start, setting all global parameters needed.
        """

        self.Settings = None
        self.Exam = None
        self._exam_saved = False

        self.preamble = {"Instruction": None,
                         "Document_Class": None,
                         "default_package_id": None,
                         }

        self.edited_course_list_path = []

        self.edited_ilo_path = []

        self.edited_author_list_path = []

        self.edited_package_list_path = []

        self.edited_document_class_list_path = []

        self.edited_instruction_list_path = []

        self.edited_declaration_list_path = []

        self.edited_bibliography_list_path = []

        self.edited_not_in_same_exam_list_path = []

        self.grade_entries = [
            [self.fx_entry, "Fx"],
            [self.pass_entry, "Pass"], [self.d_entry, "D"],
            [self.c_entry, "C"], [self.b_entry, "B"],
            [self.a_entry, "A"]
        ]

        self.question_filter_data = None
        self.question_drafts = set()
        self.selected_question_id = []

        self.loaded_question = None

        self.bibliography_drafts = set()
        self.selected_bibliography_id = []
        self.loaded_bibliography = {"path": None,
                                    "bibliography": None,
                                    }

        self.package_used = set()
        self.package_drafts = set()
        self.selected_package = []
        self.preamble_package_drafts = set()
        self.selected_preamble_package = []
        self.loaded_preamble_package = []

        self.authors_used = set()
        self.selected_author = None
        self.authors_selector = self.authors_view.get_selection()

        self.selected_question_package_requirement = None

        self.exam_to_load = None
        self.selected_old_exam = None
        self.selected_course = [None, None]
        self._course_code_used = None

        self.loaded_profile = None

    def _load_config(self):
        """
        Run at start. Reads the configuration file located in program path,
        includes amongst other, the location to the database.
        """
        self.Settings = Settings()
        self.Settings.load_config()
        self.select_program_path_btn.set_current_folder(self.Settings.get_program_path())
        self.select_database_btn.set_filename(self.Settings.get_database_path())
        return True

    def _db_settings_exist(self):
        """
        Run at start. Connects to the SQLite database.
        """
        if os.path.isfile(self.Settings.get_database_path()):
            self.dbQuery = self.ExamDB.connect_to_db(self.Settings.get_database_path())
            if self.dbQuery:
                return True

        return False

    def _setup_profile_combo_box(self):
        """
        Run at start. Loads the combo box that will list available exam
        profiles.
        """
        _cell = Gtk.CellRendererText()
        self.profile_combo_box.pack_start(_cell, True)
        self.profile_combo_box.add_attribute(_cell, 'text', 2)
        self.profile_combo_box.set_id_column(2)

    def _get_profile_list(self):
        """
        Retrieves the list of available profiles.
        """
        self.profile_list.clear()
        _available_profiles = self.ExamDB.get_available_profiles()
        for profile in _available_profiles:
            self.profile_list.append(profile)
        # Check if there is a course selected.
        if self.selected_course is not None:
            if self.selected_course[1] is not None:
                _course_code = self.selected_course[1].get_course_code()
                _course_ver = self.selected_course[1].get_course_version()
                _profile_name = ('%s%s' % (_course_code, _course_ver))
                self.profile_combo_box.set_active_id(_profile_name)

        # If not apply default.
        else:
            self.profile_combo_box.set_active_id('default0.0')

    def save_profile(self):
        """
        Takes the changes done by user and saves it to the database.
        """
        if self.loaded_profile:
            self.loaded_profile.set_default_packages(
                self.preamble["default_package_id"])
            self.loaded_profile.set_document_class(
                self.preamble['Document_Class'])
            self.loaded_profile.set_instructions(self.preamble["Instruction"])

            _profile_exam_aids_start_iter = self.profile_exam_aids.get_start_iter()
            _profile_exam_aids_end_iter = self.profile_exam_aids.get_end_iter()

            self.loaded_profile.set_exam_aids(
                self.profile_exam_aids.get_text(_profile_exam_aids_start_iter,
                                                _profile_exam_aids_end_iter,
                                                True)
            )
            self.loaded_profile.set_type_of_exam(
                self.profile_type_of_exam_entry.get_text())
            self.loaded_profile.set_time_limit(
                self.profile_exam_time_entry.get_text())
            self.loaded_profile.set_authors(self.profile_author_entry.get_text())
            self.loaded_profile.set_language(
                self.profile_language_entry.get_text())
            self.loaded_profile.set_number_of_questions(
                self.profile_number_of_questions_entry.get_text())
            self.loaded_profile.set_ilo(
                self.profile_course_goals_entry.get_text())
            self.loaded_profile.set_allow_same_tags(self.allow_same_tags.get_active())
            self.save_gradelimits_to_profile()
            self.loaded_profile.set_connector(self.dbQuery.get_connector())
            self.loaded_profile.update_database()
        return None

    def profile_combo_changed(self):
        """
        Triggers when the profile have been changed. Will load the selected
        profile.
        """
        _iter = self.profile_combo_box.get_active_iter()
        if _iter is not None:
            course_code = self.profile_list[_iter][0]
            course_version = self.profile_list[_iter][1]
            self._get_profile(course_code, course_version)
            self.load_profile()

    def _get_profile(self, course_code, course_version):
        """
        Called by profile_combo_changed(). Retrieves the profile from the
        database that belongs to the current course.

        :param course_code: The course code of the profile to load
        :param course_version: The course version of the course of the profile
        to load.
        """
        # Remove previously loaded profile if there is one.
        if self.loaded_profile:
            del self.loaded_profile

        self.loaded_profile = Profile(course_code, course_version)
        if course_code:
            self.loaded_profile.load_from_database(*self.ExamDB.get_profile(course_code,
                                                                            course_version))

    def load_profile(self):
        """
        Called by profile_combo_changed() after the profile has been retrieved.
        Takes the retrieved profile and changes the settings accordingly.
        """
        if not self.loaded_profile:
            self._get_profile(None, None)

        self.set_gradelimits_from_profile()

        # Setup documentclass
        _iter = self._search_store(self.document_class_list,
                                   self.loaded_profile.get_document_class())
        if _iter is not None:
            self.docclass_selector.select_iter(_iter)
            self.document_class_view.row_activated(
                self.document_class_list.get_path(_iter),
                self.document_class_view.get_column(0)
            )

        # Instructions
        _iter = self._search_store(self.instruction_list,
                                   self.loaded_profile.get_instructions())
        if _iter is not None:
            self.instruction_selector.select_iter(_iter)

            self.instruction_view.row_activated(
                self.instruction_list.get_path(_iter),
                self.instruction_view.get_column(0))

        # Default Packages
        _iter = self._search_store(self.preamble_package_list,
                                   self.loaded_profile.get_default_packages())
        if _iter is not None:
            self.preamble_package_combo.set_active_iter(_iter)

        # Examaids
        if self.loaded_profile.get_exam_aids() is None:
            self.profile_exam_aids.set_text('')
        else:
            self.profile_exam_aids.set_text(self.loaded_profile.get_exam_aids())

        # Type of Exam
        if self.loaded_profile.get_type_of_exam() is None:
            self.profile_type_of_exam_entry.set_text('')
        else:
            self.profile_type_of_exam_entry.set_text(self.loaded_profile.get_type_of_exam())

        # Timelimit
        if self.loaded_profile.get_time_limit() is None:
            self.profile_exam_time_entry.set_text('')
        else:
            self.profile_exam_time_entry.set_text(self.loaded_profile.get_time_limit())

        # Authors
        self.authors_used = set() # Reset list of authors
        if self.loaded_profile.get_authors() is None:
            self.profile_author_entry.set_text('')
        else:
            self.profile_author_entry.set_text(self.loaded_profile.get_authors())
            for _a in re.split('\s|,', self.loaded_profile.get_authors()):
                self.authors_used.add(_a)

        # Language
        if self.loaded_profile.get_language() is None:
            self.profile_language_entry.set_text('')
        else:
            self.profile_language_entry.set_text(self.loaded_profile.get_language())

        # Number of questions
        if self.loaded_profile.get_number_of_questions() is None:
            self.profile_number_of_questions_entry.set_text('')
        else:
            self.profile_number_of_questions_entry.set_text(str(self.loaded_profile.get_number_of_questions()))

        # Exam date
        if self.loaded_profile.get_exam_date() is None:
            self.exam_date_entry.set_text(datetime.today().strftime('%Y-%m-%d'))
        else:
            self.exam_date_entry.set_text(self.loaded_profile.get_exam_date())

        # Course goals
        if self.loaded_profile.get_ilo() is not None:
            for _i in self.loaded_profile.get_ilo().split(' '):
                # Check to handle case where no ILO is loaded.
                _ilo_id = self.ExamDB.get_ilo_by_id(_i)
                if _ilo_id:
                    self.Exam.append_ilo((_i, _ilo_id[0][3]))

            self.profile_course_goals_entry.set_text(self.loaded_profile.get_ilo())

        if self.loaded_profile.get_allow_same_tags():
            self.allow_same_tags.set_active(self.loaded_profile.get_allow_same_tags())

    @staticmethod
    def _search_store(_model, _value, _value2=None):
        """
        Static method used for searching GTK stores for a certain value.
        :param _model: The store that contains the searched value
        :param _value: The value that is searched for
        :param _value: Should this be removed???

        :return: Returns the iterator to the location of that value in _model
        """
        _iter = _model.get_iter_first()
        while _iter:
            if _model.get_value(_iter, 0) == _value:
                if _value2 is not None:
                    if _model.get_value(_iter, 1) == _value2:
                        return _iter
                else:
                    return _iter

            _iter = _model.iter_next(_iter)

    def _retrieve_objects(self):
        """
        Retrieving all the objects used to get user input about exam
        information.
        """
        # ExamInformation
        self.course_code_label = self.builder.get_object("course_label")
        self.exam_date_entry = self.builder.get_object("exam_date_label")
        self.calendar = self.builder.get_object("calendar")
        self.cal_popover = self.builder.get_object("cal_popover")
        self.save_dialogue = self.builder.get_object("savedialog")

        self.settings_windows = self.builder.get_object("settings")
        self.select_database_btn = self.builder.get_object("select_database_btn")
        self.select_program_path_btn = self.builder.get_object("select_program_path_btn")
        self.create_database_btn = self.builder.get_object("create_database_btn")

        self.database_entry = self.builder.get_object("dbentry")
        self.preamble_package_combo = self.builder.get_object(
            "preamblePackageCombo")

        self.course_list = self.builder.get_object("courselist")
        self.select_course = self.builder.get_object("select_course_popover")
        self.course_view = self.builder.get_object("courseview")

        self.ilo_list = self.builder.get_object("coursegoallist")
        self.select_course_goal = self.builder.get_object("selectcoursegoal")
        self.ilo_tree_view = self.builder.get_object("coursegoaltreeview")

        self.document_class_entry = self.builder.get_object("docclassentry")
        self.select_document_class = self.builder.get_object("selectdocclass")
        self.document_class_view = self.builder.get_object("docclassview")
        self.document_class_list = self.builder.get_object("docclasslist")

        self.author_list = self.builder.get_object("authorlist")
        self.select_authors = self.builder.get_object("selectauthors")
        self.authors_view = self.builder.get_object("authorsview")

        self.select_instructions = (
            self.builder.get_object("selectinstructions")
        )
        self.instruction_entry = self.builder.get_object("instructionEntry")
        self.instruction_list = self.builder.get_object("instructionslist")
        self.add_instruction = self.builder.get_object("addinstructions")
        self.instruction_view = self.builder.get_object("instructionview")

        self.properties_notebook = self.builder.get_object("propnotebook")

        self.grade_limit_window = \
            self.builder.get_object("gradelimitwindow")
        self.grade_comment_buffer = self.builder.get_object("grade_comment_buffer")

        self.grade_limit_pass_fail_switch = self.builder.get_object("grade_limit_pass_fail_switch")
        self.grade_limit_in_percent_switch = self.builder.get_object("grade_limit_in_percent_switch")
        self.ilo_based_grading_switch = self.builder.get_object("ilo_based_grading_switch")

        self.fx_entry = self.builder.get_object("Fxentry")
        self.pass_entry = self.builder.get_object("Passentry")
        self.d_entry = self.builder.get_object("Dentry")
        self.c_entry = self.builder.get_object("Centry")
        self.b_entry = self.builder.get_object("Bentry")
        self.a_entry = self.builder.get_object("Aentry")

        self.exam_summary_buffer = self.builder.get_object("exam_summary_buffer")

        self.manage_questions_window = self.builder.get_object("manage_questions_window")
        self.manage_questions_btn = self.builder.get_object("manage_questions_btn")

        self.question_id_list = self.builder.get_object("question_id_list")
        self.question_id_viewer = self.builder.get_object("question_id_viewer")

        self.question_id_in_exam_list = self.builder.get_object("question_id_in_exam_list")
        self.question_id_in_exam_viewer = self.builder.get_object("question_id_in_exam_viewer")

        self.student_answer_entry = self.builder.get_object("student_answer_entry")
        self.question_average_score_entry = self.builder.get_object("question_average_score_entry")
        self.question_last_used_entry = self.builder.get_object("question_last_used_entry")

        self.question_viewer = self.builder.get_object("questionviewer")

        self.force_edit_btn = self.builder.get_object("force_edit_btn")
        self.allow_same_tags = self.builder.get_object("allow_same_tags")

        self.question_package_requirement = self.builder.get_object(
            "show_question_package_requirement")

        self.scrolled_window = self.builder.get_object("scrolledwindow")

        self.question_package_requirement_list = \
            self.builder.get_object("question_package_requirement_list")
        self.question_package_requirement_view = \
            self.builder.get_object("question_package_requirement_view")

        self.select_question_folder_window = self.builder.get_object(
            "selectquestionfolderwin")

        self.question_language_entry = (
            self.builder.get_object("question_language_entry")
        )
        self.usable_check = self.builder.get_object("usablecheck")

        self.question_save_draft_button = self.builder.get_object("qwsavebtn")

        self.question_filter_entry = self.builder.get_object("question_filter_entry")
        self.question_filter_completion = self.builder.get_object("question_filter_completion")
        self.question_filter_completion_store = self.builder.get_object("question_filter_store")

        self.show_declarations = self.builder.get_object("showdeclarations")

        self.declaration_list = self.builder.get_object("declarationlist")
        self.declaration_view = self.builder.get_object("declarationview")

        self.bibliography_list = self.builder.get_object("bibliographylist")
        self.show_bibliography = self.builder.get_object("showBibliography")

        self.not_in_same_exam_view = self.builder.get_object("notinsameexamview")
        self.not_in_same_exam_window = self.builder.get_object("notinsameexamwin")
        self.not_in_same_exam_list = self.builder.get_object("notinsameexamlist")

        self.confirmation_dialogue = self.builder.get_object("confirmdia")

        self.load_exam_window = self.builder.get_object("loadExamWindow")

        self.old_exam_viewer = self.builder.get_object("oldexamviewer")
        self.old_exam_scrolled_window = self.builder.get_object("old_exam_scrolled_window")

        self.bibliography_editor_window = (
            self.builder.get_object("bibliographyeditorwin")
        )
        self.bibliography_list = self.builder.get_object("bibliographylist")
        self.bibliography_id_viewer = self.builder.get_object("bibIDViewer")

        self.package_id_view = self.builder.get_object("packageIDView")

        self.package_manager_window = self.builder.get_object(
            "packageManagerWindow")

        self.preamble_package_viewer = self.builder.get_object(
            "preamblePackageViewer")

        self.preamble_package_list = self.builder.get_object(
            "preamblepackagelist")

        self.package_list = self.builder.get_object("packagelist")
        self.select_file_dialogue = self.builder.get_object("selectFileDialogue")

        self.profile_combo_box = self.builder.get_object("profileComboBox")
        self.profile_list = self.builder.get_object("profileList")
        self.profile_author_entry = self.builder.get_object("profileAuthorEntry")
        self.profile_course_goals_entry = (
            self.builder.get_object("profileILOEntry")
        )
        self.profile_exam_aids = self.builder.get_object(
            "exam_aids_buffer")
        self.profile_type_of_exam_entry = self.builder.get_object(
            "profileTypeOfExamEntry")
        self.profile_exam_time_entry = self.builder.get_object(
            "profileExamTimeEntry")
        self.profile_language_entry = self.builder.get_object(
            "profileLanguageEntry")
        self.profile_number_of_questions_entry = self.builder.get_object(
            "profileNumQuestionsEntry")

        self.generate_reports_window = self.builder.get_object("generate_reports_window")

    def _setup_syntax_highlighting(self):
        """
        Setup syntax highlighing. Start by creating a GTK source buffer to store
        the LaTeX-code. Next create a language manager that defines what
        language will be stored in the source buffer. Define language to 'latex'
        and connect this language manager to the source buffer.
        Finally get the source viewer from glade and connect to source buffer to
        it.
        """
        self.buffer_latex = GtkSource.Buffer()
        self.language_manager = GtkSource.LanguageManager()
        self.buffer_latex.set_language(self.language_manager.get_language('latex'))
        self.exam_viewer = self.builder.get_object("examviewer")
        self.exam_viewer.set_buffer(self.buffer_latex)

        self.buffer_question = GtkSource.Buffer()

        self.buffer_question.connect('begin-user-action',
                                     self.question_has_been_modified)

        self.buffer_question.set_language(
            self.language_manager.get_language('latex'))

        self.question_viewer.set_buffer(self.buffer_question)

        self.buffer_bibliography = GtkSource.Buffer()

        self.buffer_bibliography.connect('begin-user-action',
                                         self.bibliography_has_been_modified)

        self.buffer_bibliography.set_language(
            self.language_manager.get_language('bibtex'))

        self.bibliography_viewer = self.builder.get_object("bibliographyviewer")

        self.bibliography_viewer.set_buffer(self.buffer_bibliography)

    def new_exam(self):
        """
        Empty all the variables and clear the user input.
        """
        if not self._connected_to_database:
            return False

        if self.Exam:
            del self.Exam  # Remove old exam-object
        if self.selected_course:
            self.selected_course = None
        self._exam_saved = False

        self.Exam = Exam()

        self.Exam.set_connector(self.dbQuery.get_connector())
        self.course_code_label.set_text("Course")
        self.profile_type_of_exam_entry.set_text("")
        self.profile_author_entry.set_text("")
        self.exam_date_entry.set_text("Exam date")
        self.profile_language_entry.set_text("")
        self.profile_exam_time_entry.set_text("")
        self.profile_exam_aids.set_text("")
        self.profile_number_of_questions_entry.set_text(str(0))
        self.profile_course_goals_entry.set_text("")
        self.buffer_latex.set_text("")
        self.profile_combo_box.set_active_id("default0.0")
        self.reset_gradelimits()
        self.exam_summary_buffer.set_text("")

        return True

    def _course_loaded(self):
        if self.course_code_label.get_text():
            for r in self.course_list:  # Search to see if course code exist
                if r[0] == self.course_code_label.get_text():
                    return True
        else:
            print("Please enter course code")
            return False

    def reveal(self):
        """
        This method reveals or unreveals the user-input field in the GUI to
        give it that lean fancy look.
        """
        _arrow = self.builder.get_object("expand")
        _revealer = self.builder.get_object("revealer")
        _revealer.set_reveal_child(True)

        if _revealer.get_child_revealed():
            _revealer.set_reveal_child(False)
            _arrow.set_label("<")
        else:
            _revealer.set_reveal_child(True)
            _arrow.set_label(">")

    def reveal_profile(self):
        """
        This method reveals or unreveals the Profile settings §in the GUI to
        give it that lean fancy look.
        """
        _arrow = self.builder.get_object("expandProfile")
        _revealer = self.builder.get_object("revealProfile")
        _revealer.set_reveal_child(False)

        if _revealer.get_child_revealed():
            _revealer.set_reveal_child(False)
            _arrow.set_label(">")
            size = self.window.get_size()
            self.window.resize(1, size[1])
        else:
            _revealer.set_reveal_child(True)
            _arrow.set_label("<")

    @staticmethod
    def _cell_renderer_text_generator(treeview, columns, function=None):
        """
        Generates the list for treeview. Input for the function is the treeview
        followed by a list of list that should be according to the following
        format:
            [ID, isEditable, isSortable, isVisible] Finally the function that should be
            called when column is edited.
        """
        _position = 0
        for _column in columns:
            cell = {"ID": _column[0],
                    "Editable": _column[1],
                    "Sortable": _column[2],
                    "Visible": _column[3]
                    }

            _text_renderer = Gtk.CellRendererText()
            _column_text = Gtk.TreeViewColumn(
                cell["ID"], _text_renderer, text=_position)
            if cell["Sortable"]:
                _column_text.set_sort_column_id(0)

            _column_text.set_visible(cell["Visible"])

            _text_renderer.props.wrap_width = 500
            _text_renderer.props.wrap_mode = Gtk.WrapMode.WORD
            _text_renderer.set_property("editable", cell["Editable"])

            if function:
                _text_renderer.connect("edited", function, _position)
            treeview.append_column(_column_text)
            _position += 1
        return True

    @staticmethod
    def compare(model, row1, row2, __data=None):
        # Custom sort function to handle issue with lexikograpgical sorting.
        # Sorts based on trailing integers in a string.
        relabel = re.compile(r'([0-9]*$)')
        sort_column, _ = model.get_sort_column_id()

        value1 = model.get_value(row1, sort_column)
        sortvalue1 = relabel.findall(value1)[0]
        # Fix TypeError if value becomes '' by setting it to 0.
        if sortvalue1 == '':
            sortvalue1 = 0

        value2 = model.get_value(row2, sort_column)
        sortvalue2 = relabel.findall(value2)[0]
        if sortvalue2 == '':
            sortvalue2 = 0

        if int(sortvalue1) < int(sortvalue2):
            return -1
        elif sortvalue1 == sortvalue2:
            return 0
        else:
            return 1

    @staticmethod
    def compare_date(model, row1, row2, __data=None):
        """
        Comparison func to sort old exams based on date. Latest exams should be displayed first.
        :param model: Treemodel
        :param row1: First row to compare
        :param row2: Second row to compare
        :param __data: User data
        :return: -1 if row1 > row2, 0 if row1 = row2, 1 if row1 < row2
        """
        _val1 = model.get_value(row1, 2)
        _val2 = model.get_value(row2, 2)
        if _val1 == _val2:
            return 0
        if _val1 > _val2:
            return -1
        else:
            return 1

    def on_list_key_press(self, widget, event):
        _messagedia = MessageDialogWindow()
        _keyname = Gdk.keyval_name(event.keyval)
        if _keyname:
            _func = getattr(self, '%s_dialogue' % widget.get_name(), None)
            if _keyname == 'Delete':
                _func(_messagedia)

    def save_question(self, widget, event):
        # Allow the use of Ctrl-s to save question, instead of having to press button.
        _keyname = Gdk.keyval_name(event.keyval)
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if _keyname == 's':
                self.save_question_as_draft()
                self.save_question_to_db()

    def bibliographyeditor_dialogue(self, messagedia):
        if (self.bibliography_list is None) or \
                (self.loaded_bibliography["bibliography"] is None):
            return

        _bib_id = self.loaded_bibliography["bibliography"].get_bibliography_id()
        _bib_used = self.ExamDB.bibliography_used(_bib_id)

        # Check if bibliography is used in question. This might not work particularly well, if reference is used in
        # multiple questions. Fix this!
        if _bib_used:
            messagedia.information_dialogue(
                'Unable to delete %s.' % _bib_id[0],
                'This bibliography is used for question %s' % _bib_used[0][1])
        else:
            if messagedia.confirmation_dialogue(
                    'Are you sure?', 'This will permanently remove '
                                     '%s' % _bib_id):
                self.loaded_bibliography["bibliography"].set_connector(self.dbQuery.get_connector())
                self.loaded_bibliography["bibliography"].remove_from_database()

                # Remove bib from draft.
                for _b in self.bibliography_drafts.copy():
                    if _b.get_bibliography_id() == _bib_id:
                        self.bibliography_drafts.discard(_b)

                self.get_bibliography()

    def course_viewer_dialogue(self, messagedia):
        _list = self.selected_course[0][0]
        _path = self.selected_course[0][1]

        if _list is None:
            return

        if self.selected_course[1] is None:  # Only draft
            _list.remove(_path)
        else:
            if self.selected_course[1].get_in_database():
                if self.ExamDB.course_used(
                        self.selected_course[1].get_course_code(),
                        self.selected_course[1].get_course_version()):

                    messagedia.information_dialogue(
                        'Unable to delete %s.' %
                        self.selected_course[1].get_course_code(),
                        'An exam for this course exist')
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?', 'This will permanently remove '
                                             '%s' % (self.selected_course[1].get_course_code())):
                        self.selected_course[1].set_connector(
                            self.dbQuery.get_connector())

                        if self.course_code_label.get_text() == self._course_code_used:
                            self.course_code_label.set_text('Course')

                        self.selected_course[1].remove_from_database()
                        self._get_courses()
                        self.load_profile()

    def authorsview_dialogue(self, messagedia):
        _list = self.selected_author[0][0]
        _path = self.selected_author[0][1]

        if _list is None:
            return

        if self.selected_author[1] is None:
            _list.remove(_path)
        else:
            if self.selected_author[1].get_in_database():
                if self.ExamDB.author_used(
                        self.selected_author[1].get_id()):

                    messagedia.information_dialogue(
                        'Unable to delete %s.' %
                        self.selected_author[1].get_id(),
                        'This author is associated with an existing '
                        'ExamClass.')
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?', 'This will permanently remove '
                                             'entry for %s' % self.selected_author[1].get_id()):
                        self.selected_author[1].set_connector(
                            self.dbQuery.get_connector())
                        self.selected_author[1].remove_from_database()
                        self._get_authors()

    def coursegoalview_dialogue(self, messagedia):
        _list = self.selected_ilo[0][0]
        _path = self.selected_ilo[0][1]

        if _list is None:
            return

        if self.selected_ilo[1] is None:
            _list.remove(_path)
        else:
            if self.selected_ilo[1].get_in_database():
                if self.ExamDB.have_ilo_been_used(
                        self.selected_ilo[1].get_goal()):

                    messagedia.information_dialogue(
                        'Unable to delete %s.' %
                        self.selected_ilo[1].get_goal(),
                        'This author is associated with an existing'
                        'ExamClass.')
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?', 'This will permanently remove'
                                             'entry for %s' % self.selected_ilo[1].get_goal()):
                        self.selected_ilo[1].remove_from_database()

    def docclassview_dialogue(self, messagedia):
        _list = self.selected_docclass[0][0]
        _path = self.selected_docclass[0][1]

        if _list is None:
            return

        if self.selected_docclass[1] is None:
            _list.remove(_path)
        else:
            if self.selected_docclass[1].get_in_database():
                if self.ExamDB.docclass_used(
                        self.selected_docclass[1].get_document_class_id()):

                    messagedia.information_dialogue(
                        'Unable to delete %s.' %
                        self.selected_docclass[1].get_document_class_id(),
                        'This documentclass is associated with an existing '
                        'ExamClass.')
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?', 'This will permanently remove '
                                             'entry for %s' % self.selected_docclass[1].get_document_class_id()):
                        self.selected_docclass[1].remove_from_database()
                        _list.remove(_path)

    def instructionview_dialogue(self, messagedia):
        _list = self.selected_instruction[0][0]
        _path = self.selected_instruction[0][1]

        if _list is None:
            return

        if self.selected_instruction[1] is None:
            _list.remove(_path)
        else:
            if self.selected_instruction[1].get_in_database():
                if self.ExamDB.instruction_used(
                        self.selected_instruction[1].get_instruction_id()):

                    messagedia.information_dialogue(
                        'Unable to delete %s.' %
                        self.selected_instruction[1].get_instruction_id(),
                        'This instruction is associated with an existing ExamClass.')
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?',
                            'This will permanently remove entry for %s' %
                            self.selected_instruction[1].get_instruction_id()
                    ):
                        self.selected_instruction[1].remove_from_database()
                        _list.remove(_path)

    def declarationview_dialogue(self, messagedia):
        _list = self.selected_declaration[0][0]
        _path = self.selected_declaration[0][1]

        if _list is None:
            return

        if self.selected_declaration[1] is None:
            _list.remove(_path)
        else:
            if self.selected_declaration[1].get_in_database():
                _question = self.ExamDB.declaration_used(
                    self.selected_declaration[1].get_id())
                if _question:
                    messagedia.information_dialogue(
                        'Unable to delete %s.' %
                        self.selected_declaration[1].get_id(),
                        'This declaration is associated with questions %s.' %
                        _question)
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?',
                            'This will permanently remove entry for %s' %
                            self.selected_declaration[1].get_id()):
                        self.selected_declaration[1].remove_from_database()
                        _list.remove(_path)

    def notinsameexamview_dialogue(self, messagedia):
        _model = self.selectedNISE[0][0]  # Treemodel
        _path = self.selectedNISE[0][1]  # Path
        _iter = _model.get_iter(_path)
        _similarID = _model[_path][1]

        if _model is None:
            return

        if self.loaded_question is None:  # If no _question object exist
            _model.remove(_iter)
        else:
            if self.loaded_question.get_in_database():
                if messagedia.confirmation_dialogue('Are you sure?'):
                    self.loaded_question.remove_similar(_similarID)

                    _model.remove(_iter)
                    self.question_has_been_modified()

    def packageview_dialogue(self, messagedia):
        _list = self.selected_package[0][0]
        _iter = self.selected_package[0][1]
        _package = self.selected_package[1]

        if _list is None:
            return

        if _package is None:
            _list.remove(_iter)
        else:
            if _package.get_in_database():
                if self.ExamDB.package_used(_package.get_id()):
                    messagedia.information_dialogue(
                        'Unable to delete %s.' % _package.get_id(),
                        'This package has been used in an exam')
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?', 'This will permanently remove this package'):
                        _package.set_connector(self.dbQuery.get_connector())
                        _package.remove_from_database()
                        self.package_drafts.remove(_package)
                        _list.remove(_iter)
                        self.selected_package[1] = None  # Ensure that package can't be removed twice.

    def preamble_packageview_dialogue(self, messagedia):
        _list = self.selected_preamble_package[0][0]
        _iter = self.selected_preamble_package[0][1]
        _preamble_package = self.selected_preamble_package[1]

        if _list is None:
            return

        if _preamble_package is None:
            _list.remove(_iter)
        else:
            if _preamble_package.get_in_database():
                if self.ExamDB.preamble_package_already_used(
                        _preamble_package.get_id()):
                    messagedia.information_dialogue(
                        'Unable to delete %s.' %
                        _preamble_package.get_id(),
                        'This package has been used in an exam')
                else:
                    if messagedia.confirmation_dialogue(
                            'Are you sure?', 'This will permanently remove this package'):
                        _preamble_package.set_connector(
                            self.dbQuery.get_connector()
                        )
                        _preamble_package.remove_from_database()
                        self.preamble_package_drafts.remove(_preamble_package)
                        _list.remove(_iter)

    def question_id_view_dialogue(self, messagedia):
        _question = self.get_question_id_from_drafts(
            self.loaded_question.get_question_id())
        if not _question:
            _question = self.loaded_question

        _path = self.get_liststore_path(self.question_id_list, _question.get_question_id())

        if _question.get_editable():
            if messagedia.confirmation_dialogue(
                    'Are you sure?', 'This will permanently remove this question'):
                _question.set_connector(self.dbQuery.get_connector())
                # Remove question from DB
                _question.remove_from_database()

                # Remove from list
                self.question_id_list.remove(
                    self.question_id_list.get_iter(_path)
                )
                self.selected_question_id = None

        else:
            messagedia.information_dialogue('Unable to delete %s.' % _question.get_question_id(),
                                            'This question has been used in an exam')
        return

    def oldexamviewer_dialogue(self, messagedia):
        if not self.selected_old_exam:
            return

        if self.exam_to_load is None:  # Trying to remove a parent
            return

        _TempExam = Exam()

        _TempExam.load_exam_info_from_database(*self.ExamDB.get_exam_info_by_id(self.exam_to_load))

        if messagedia.confirmation_dialogue(
                'Are you sure?', 'This will permanently remove entry for %s' % _TempExam.get_exam_id()):
            _TempExam.set_connector(self.dbQuery.get_connector())
            _TempExam.remove_exam(keep_results=False)

            _iter = self._old_exam_list_treestore.get_iter(self.selected_old_exam[1])

            self._old_exam_list_treestore.remove(_iter)
            del _TempExam
            self.selected_old_exam = self.exam_to_load = None

        return

    def question_package_requirement_view_dialogue(self, messagedia):
        _model = self.selected_question_package_requirement[0][0]  # Treemodel
        _path = self.selected_question_package_requirement[0][1]  # Path
        _iter = _model.get_iter(_path)
        _package_id = _model[_path][0]
        _question = self.selected_question_package_requirement[1]  # Question object on selected _path.

        if _model is None:
            return

        if _question is None:  # If no _question object exist
            _model.remove(_iter)
        else:
            if _question.get_in_database():
                if messagedia.confirmation_dialogue('Are you sure?'):
                    _question.remove_package_requirement(_package_id)

                    _model.remove(_iter)
                    self.question_has_been_modified()

    def open_settings_window(self):
        self.settings_windows.show_all()

    def save_settings(self):
        self.Settings.set_program_path(self.select_program_path_btn.get_filename())
        self.Settings.set_database_path(self.select_database_btn.get_filename())
        self.Settings.save_config()
        self._connected_to_database = self._db_settings_exist()
        self.new_exam()
        self.get_init_data_from_db()
        self.settings_windows.hide()

    def close_settings_window(self):
        self.settings_windows.hide()

    def create_database(self):
        database_file_name = ""

        extension_filter = Gtk.FileFilter()
        extension_filter.set_name("SQLite3 Database")
        extension_filter.add_pattern("*.sqlite3")

        fcd = Gtk.FileChooserDialog(title=None,
                                    parent=None,
                                    action=Gtk.FileChooserAction.SAVE)

        fcd.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        fcd.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

        fcd.add_filter(extension_filter)

        fcd.set_current_folder(self.select_program_path_btn.get_filename())
        fcd.set_current_name('ExamDB.sqlite3')

        self.response = fcd.run()

        if self.response == Gtk.ResponseType.OK:
            database_file_name = fcd.get_filename()

        fcd.destroy()
        if os.path.splitext(database_file_name)[1]:

            # If wrong extension is set, change it. Should I force this??
            if not os.path.splitext(database_file_name)[1] == 'sqlite3':
                database_file_name = re.sub(os.path.splitext(database_file_name)[1], '.sqlite3', database_file_name)
        else:
            database_file_name += '.sqlite3'

        # Create database
        sql_script = os.path.dirname(os.path.realpath(__file__)) + "/Database/create_exam_db_with_data.sql"
        try:
            os.system("sqlite3 " + database_file_name + " < " + sql_script)

        except OSError as error:
            if error.errno == os.errno.ENOENT:
                print('create_database(): SQlite could not be found')
                return
            else:
                print('create_database(): %s' % error)

        # Set new database
        self.Settings.set_database_path(database_file_name)
        self.select_database_btn.set_filename(database_file_name)

        return

    def open_authors_selection(self):

        #       Reveal the window containing the course goals, to allow the user to
        #       select which course goals the exam should cover.

        self._get_authors()
        self.select_authors.show_all()

    def _create_author_list(self):
        """
        """
        _columns = [["ID", True, False, True], ["Name", True, False, True], ["E-Mail", True, False, True],
                    ["Phone", True, False, True]]

        self.authors_view.set_property("activate-on-single-click", True)
        self.authors_view.connect("row-activated", self._author_is_selected)
        self.authors_view.connect("key-release-event", self.on_list_key_press)

        self._cell_renderer_text_generator(self.authors_view, _columns,
                                           self._author_text_edited)

        _renderer_toggle = Gtk.CellRendererToggle()
        _renderer_toggle.connect("toggled", self._on_author_cell_toggled)
        column_toggle = Gtk.TreeViewColumn(
            "Select", _renderer_toggle, active=4)
        self.authors_view.append_column(column_toggle)

    def _on_author_cell_toggled(self, __widget, path):
        """
        Toggles and untoggles the button from course goal dialogue
        """
        self.author_list[path][4] = not self.author_list[path][4]
        if self.author_list[path][4]:
            self.authors_used.add(self.author_list[path][0])
        else:
            for a in self.authors_used.copy():
                if a == self.author_list[path][0]:
                    self.authors_used.remove(a)

    def _author_text_edited(self, __widget, path, text, cell):
        self.author_list[path][cell] = text
        self.edited_author_list_path.append([path, cell])

    def _author_is_selected(self, __treeview, path, __column, __data=None):
        _model = self.author_list
        _author = Author()
        if path is not None:
            try:
                _author.load_from_database(
                    *self.ExamDB.get_author(_model[path][0])[0]
                )

            except TypeError or IndexError as err:
                print("_author_is_selected(): %s" % err)
                self.selected_author = [[_model, path], None]
                return

        self.selected_author = [[_model, path], _author]

    def add_new_author(self):
        _authorIter = self.author_list.append(['', '', '', '', False])
        _authorpath = self.author_list.get_path(_authorIter)

        self.authors_selector.select_path(_authorpath)
        self.authors_view.scroll_to_cell(_authorpath)

    def _get_authors(self):
        """
        Populate the liststore authorslist with the available _authors.
        """
        _authors = self.ExamDB.retrieve_authors()
        if _authors is not None:
            self.author_list.clear()  # Resets the liststore
            for a in _authors:
                if a[0] in self.authors_used:
                    author = [a[0], a[1], a[2], a[3], True]
                    self.author_list.append(author)
                else:
                    author = [a[0], a[1], a[2], a[3], False]
                    self.author_list.append(author)

    def _add_new_author_to_db(self):
        # Save new _author information in dictionary for adding to database.
        _unique_list = [list(t) for t in
                        set(map(tuple, self.edited_author_list_path))]
        _authorchanged = set([])

        for p in _unique_list:
            _authorchanged.add(p[0])
        for _a in _authorchanged:
            _author = Author()
            _author.set_connector(self.dbQuery.get_connector())
            if self.author_list[_a][0]:
                _author.set_id_author(self.author_list[_a][0])

            for u in _unique_list:
                if u[0] == _a:
                    _authorentry = int(_a)

                    if u[1] == 0:
                        _author.set_id_author(
                            self.author_list[_authorentry][u[1]])

                    elif u[1] == 1:
                        _author.set_name(self.author_list[_authorentry][u[1]])

                    elif u[1] == 2:
                        _author.set_email(self.author_list[_authorentry][u[1]])

                    elif u[1] == 3:
                        _author.set_phone(self.author_list[_authorentry][u[1]])

            if _author.get_id() is None:
                print("Please insert authorID")
                return False

            try:
                if self.ExamDB.author_exist(_author.get_id()):
                    _author.update_database()
                else:
                    _author.insert_into_database()
            except TypeError as err:
                print("_add_new_author_to_db(): %s" % err)
                return

    def _gen_author_entry(self):
        _authors = ''
        _length = len(self.authors_used)
        _ctr = 1
        for _g in self.authors_used:
            if _ctr < _length:
                _authors += _g + ' '
                _ctr += 1
            elif _ctr == _length:
                _authors += _g

        self.profile_author_entry.set_text(_authors)

    def cancel_authors_selection(self):
        self.edited_author_list_path = []
        self.select_authors.hide()

    def close_authors_selection(self):
        self._add_new_author_to_db()

        self.profile_author_entry.set_text("")
        self._gen_author_entry()

        self.select_authors.hide()

    def open_calendar(self):
        # If an exam is loaded, select the exam date in the calendar
        if self.Exam.get_exam_date():
            _exam_date = self.Exam.get_exam_date()

            self.calendar.select_month(_exam_date.month - 1,
                                       _exam_date.year)

            self.calendar.select_day(_exam_date.day)

        # Otherwise select today's date
        else:
            self.calendar.select_month(datetime.now().month - 1,
                                       datetime.now().year)
            self.calendar.select_day(datetime.now().day)

        self.cal_popover.show_all()

    def close_calendar(self):
        self.cal_popover.hide()

    def choose_date(self):
        _year, _month, _day = self.calendar.get_date()
        self.exam_date_entry.set_text("%s-%s-%s" % (_year, _month + 1, _day))

        self.close_calendar()

    def open_course_selection(self):
        """
        Get available courses
        """
        self._get_courses()

    def _create_course_list(self):
        """
        Create the list used for displaying the courses.
        """
        _columns = []
        self._course_selector = self.course_view.get_selection()
        self.course_view.set_property("activate-on-single-click", True)
        self.course_view.connect("row-activated", self._course_is_selected)

        self.course_view.connect("key-release-event", self.on_list_key_press)

        _columns.append(["Course Code", True, False, True])
        _columns.append(["Course Version", True, False, True])
        _columns.append(["Course name Swedish", True, False, True])
        _columns.append(["Course name English", True, False, True])
        _columns.append(["Course credits", True, False, True])
        _columns.append(["Course progression", True, False, True])

        self._cell_renderer_text_generator(self.course_view, _columns,
                                           self._course_text_edited)
        self.course_view.get_column(0).clicked()

    def _course_is_selected(self, __treeview, path, __column):
        _model = self.course_list
        _course = Course()

        if path is not None:
            self._course_code_used = _model[path][0]
            self._course_version_used = _model[path][1]

            if self._course_code_used == (None or '') or self._course_version_used == (None or ''):
                self.selected_course = [[_model, path], None]
                return

            else:
                try:
                    _course.load_from_database(
                        *self.ExamDB.retrieve_courses(self._course_code_used,
                                                      self._course_version_used)[0])
                    if _course is None:
                        _course = None

                except IndexError as err:
                    print('_course_is_selected(): %s' % err)
                    return False

            self.selected_course = [[_model, path], _course]

    def _course_text_edited(self, __widget, path, text, cell):
        self.course_list[path][cell] = text
        self.edited_course_list_path.append([path, cell])

    def _get_courses(self):
        """
        Populate the liststore courselist with available courses. Convert the
        floats to string to avoid messing with redefining cellrenderers...
        That can be a project for another day.
        """
        if not self.ExamDB:
            return False

        else:
            self.course_list.clear()  # Resets the liststore
            _courses = self.ExamDB.retrieve_courses()
            if _courses is not None:

                for c in _courses:
                    _version = str(c[1])
                    _credit = str(c[4])
                    _course = [c[0], _version, c[2], c[3], _credit, c[5]]
                    self.course_list.append(_course)

    def add_new_course_entry(self):
        _courseIter = self.course_list.append(['', '', '', '', '', ''])
        _coursepath = self.course_list.get_path(_courseIter)

        _selector = self.course_view.get_selection()
        _selector.select_path(_coursepath)
        self.course_view.scroll_to_cell(_coursepath)

    def add_new_course_to_db(self):
        """
        Search through list of changed cells in courselist and put them in an
        appropriate dictionary, that will later be used to add information to
        database.
        """
        if not self.edited_course_list_path:
            return

        _course = None

        _uniqueList = [list(t) for t in
                       set(map(tuple, self.edited_course_list_path))]
        _coursechanged = set([])

        for _p in _uniqueList:
            _coursechanged.add(_p[0])

        for _e in _coursechanged:
            _course = Course()
            _course.set_connector(self.dbQuery.get_connector())

            if self.course_list[_e][0]:
                _course.set_course_code(self.course_list[_e][0])

            for _u in _uniqueList:
                if _u[0] == _e:
                    c = int(_e)
                    if _u[1] == 1:
                        _course.set_course_version(self.course_list[c][_u[1]])
                    if _u[1] == 2:
                        _course.set_course_name_sve(self.course_list[c][_u[1]])
                    elif _u[1] == 3:
                        _course.set_course_name_eng(self.course_list[c][_u[1]])
                    elif _u[1] == 4:
                        _course.set_course_credit(self.course_list[c][_u[1]])
                    elif _u[1] == 5:
                        _course.set_course_progression(self.course_list[c][_u[1]])

            if _course.get_course_code() is None:
                print("Please insert course code")
                return False

            if _course.get_course_version() is None:
                print('please enter course version')
                return False

            elif self.ExamDB.course_exist(_course.get_course_code(),
                                          _course.get_course_version()):
                _course.update_database()

            else:
                _course.insert_into_database()

        self.edited_course_list_path = []
        self._course_code_used = _course.get_course_code()

    def save_course_selection(self):

        # Check if there is anything to save to database
        self.add_new_course_to_db()

        # If no course is selected, just close the window.
        if not self.selected_course:
            self._get_profile_list()
            self.close_course_selection()
            return

        if self._course_code_used:
            self.course_code_label.set_text(self._course_code_used)

        # Search profileList for a course specific profile.

        _iter = self._search_store(self.profile_list,
                                   self.selected_course[1].get_course_code(),
                                   self.selected_course[1].get_course_version())

        # If no profile is found, create one and add to the DB.
        if _iter is None:
            course_profile = Profile(self.selected_course[1].get_course_code(),
                                     self.selected_course[1].get_course_version())
            course_profile.set_connector(self.dbQuery.get_connector())
            course_profile.insert_into_database()

        # Update profileList and load course profile.
        self._get_profile_list()

        self.close_course_selection()

    def cancel_course_selection(self):
        self._course_code_used = ""
        self._course_version_used = ""
        self.edited_course_list_path = []
        self.course_code_label.set_text("Course")
        self.select_course.hide()

    def close_course_selection(self):
        """
        Hides the window containing the course goals.
        """
        self.select_course.hide()

    def open_coursegoal_selection(self):
        """
        Unhides the window containing the course goals, to allow the user to
        select which course goals the exam should cover.
        """
        self._get_ilo()
        self.select_course_goal.show_all()

    def _get_ilo(self):
        """
        Populate the liststore coursegoallist with the ILO based on
        what the user inputed.
        """

        if self._course_loaded():
            if self.ExamDB:
                self.ilo_list.clear()  # Resets the liststore
                _goals = self.ExamDB.get_ilos_for_course(self._course_code_used,
                                                         self._course_version_used)

                if _goals is None:
                    return

                for _g in _goals:
                    if self.Exam.is_ilo_used(_g[0]):
                        goal = [_g[0], _g[1], _g[2], True]
                    else:
                        goal = [_g[0], _g[1], _g[2], False]

                    self.ilo_list.append(goal)

            else:
                return False
        else:
            self.ilo_list.clear()  # Resets the liststore

    def _create_ilo_list(self):
        """
        Create list to hold course goals
        """
        self.ilo_tree_view = self.builder.get_object("coursegoaltreeview")

        _columns = [["ID", False, True, True], ["Course Goal", True, False, True], ["Tags", True, False, True]]

        self.ilo_tree_view.set_property("activate-on-single-click", True)
        self.ilo_tree_view.connect("row-activated",
                                   self._ilo_have_been_selected)

        self.ilo_tree_view.connect("key-release-event",
                                   self.on_list_key_press)

        self._cell_renderer_text_generator(self.ilo_tree_view, _columns,
                                           self._ilo_have_been_edited)

        self.ilo_tree_view.get_column(0).clicked()

        _renderer_toggle = Gtk.CellRendererToggle()

        _renderer_toggle.connect("toggled", self._on_ilo_cell_toggled)

        _columnToggle = Gtk.TreeViewColumn("Select", _renderer_toggle,
                                           active=3)

        self.ilo_tree_view.append_column(_columnToggle)

    def _ilo_have_been_edited(self, __widget, path, text, cell):
        self.ilo_list[path][cell] = text
        self.edited_ilo_path.append([path, cell])

    def _ilo_have_been_selected(self, __treeview, path, __column, __data=None):
        _model = self.ilo_list
        _ilo = ILO()
        try:
            if path is not None:
                if (_model[path][0]) == (None or ''):
                    self.selected_ilo = [[_model, path], None]
                    return

                else:
                    if (_model[path][0]) is None:
                        _ilo = None

                    else:
                        _ilo.load_from_database(
                            *self.ExamDB.get_ilo_by_id(_model[path][0])[0])
                        _ilo.set_in_database(True)

                    self.selected_ilo = [[_model, path], _ilo]
        except IndexError as err:
            return

    def _on_ilo_cell_toggled(self, __widget, path):
        """
        Toggles and untoggles the button from course goal dialogue
        """
        self.ilo_list[path][3] = not self.ilo_list[path][3]
        _ilo = self.ilo_list[path][0]
        if self.ilo_list[path][3]:
            self.Exam.append_ilo((_ilo, self.ExamDB.get_ilo_by_id(_ilo)[0][3]))
        else:
            self.Exam.remove_ilo((_ilo, self.ExamDB.get_ilo_by_id(_ilo)[0][3]))

    def add_new_ilo(self):
        _ID = self.ExamDB.gen_id('coursegoal', self._course_code_used,
                                 self._course_version_used)
        _ilo_iter = self.ilo_list.append([_ID, '', '', False])
        _ilo_path = self.ilo_list.get_path(_ilo_iter)

        _selector = self.ilo_tree_view.get_selection()
        _selector.select_path(_ilo_path)
        self.ilo_tree_view.scroll_to_cell(_ilo_path)

    def add_new_ilo_to_db(self):
        _uniqueList = [list(t) for t in
                       set(map(tuple, self.edited_ilo_path))]
        _modified_ilos = set([])
        self.new_ilo_list = []

        for _p in _uniqueList:
            _modified_ilos.add(_p[0])

        for _e in _modified_ilos:
            _coursegoal = ILO()
            _coursegoal.set_connector(self.dbQuery.get_connector())
            _coursegoal.set_goal(self.ilo_list[_e][0])

            _coursegoal.set_course_code(self._course_code_used)
            _coursegoal.set_course_version(self._course_version_used)

            for _u in _uniqueList:
                if _u[0] == _e:
                    course = int(_e)
                    if _u[1] == 1:
                        _coursegoal.set_description(
                            self.ilo_list[course][_u[1]])
                    elif _u[1] == 2:
                        _coursegoal.set_tags(self.ilo_list[course][_u[1]])
            if self.ExamDB.course_goal_exists(_coursegoal.get_goal()):
                _coursegoal.update_database()
            else:
                _coursegoal.insert_into_database()

        self.edited_ilo_path = []

    def save_coursegoal_selection(self):
        _ILO = ''
        _length = len(self.Exam.get_ilo())
        _ctr = 1
        for _g in self.Exam.get_ilo():
            if _ctr < _length:
                _ILO += _g[0] + ' '
                _ctr += 1
            elif _ctr == _length:
                _ILO += _g[0]

        self.profile_course_goals_entry.set_text(_ILO)

        self.add_new_ilo_to_db()
        self.close_coursegoal_selection()

    def cancel_coursegoal_selection(self):
        self.edited_ilo_path = []
        self.new_ilo_list = []
        self.select_course_goal.hide()

    def close_coursegoal_selection(self):
        """
        Hides the window containing the course goals.
        """
        self.select_course_goal.hide()

    def get_preamble_packages(self):
        # Support method for saveExamDialogueinfo. Retrieves all packages from
        # defaultpackage and adds them to the exam class.

        _package_list = self.ExamDB.get_preamble_packages(
            self.preamble["default_package_id"])
        for _pack in _package_list:
            _package = Package()
            _package.load_from_database(_pack[0], _pack[1], _pack[2])
            self.Exam.append_package_requirements(_package)

    def open_docclass_selection(self):
        self._get_docclass()
        self.select_document_class.show_all()
        return

    def _create_docclass_list(self):
        """
        Retrieves the treeviewer from Glade. After which it will create a
        GTKCellRendererText. Next it creates a column to be put into the
        questionIDViewer with GTK.TreeViewColumn and connects the which position from
        treestore it should store in this column. Start by adding GoalID and
        course goal description. Next create a toogle-button and connect it to
        the function _onCourseGoalCellToggled, that toggles and untoggles the
        button.
        """
        _columns = []

        self.docclass_selector = self.document_class_view.get_selection()

        self.document_class_view.set_property("activate-on-single-click", True)
        self.document_class_view.connect("row-activated", self.docclass_selected)

        self.document_class_view.connect("key-release-event", self.on_list_key_press)

        _columns.append(["ID", False, True, True])
        _columns.append(["Document Class", True, False, True])
        _columns.append(["Options", True, False, True])

        self._cell_renderer_text_generator(self.document_class_view,
                                           _columns,
                                           self._docclass_edited)

    def docclass_selected(self, __treeview, path, __column):
        _docclass = DocumentClass()
        if path is not None:
            self.preamble['Document_Class'] = self.document_class_list[path][0]
        try:
            _docclass.load_from_database(*self.ExamDB.get_document_class(
                self.preamble['Document_Class'])[0])

        except TypeError as err:
            print("docclass_selected(): %s" % err)
            self.selected_docclass = [[self.document_class_list, path], None]
            return

        self.selected_docclass = [[self.document_class_list, path], _docclass]
        self.document_class_entry.set_text(self.preamble['Document_Class'])

    def _docclass_edited(self, __widget, path, text, cell):
        self.document_class_list[path][cell] = text
        self.edited_document_class_list_path.append([path, cell])

    def _get_docclass(self):
        """
        This method is run once the dbconnection have been established.
        Populate the liststore docclasslist with the available
        _documentclasses.
        """

        _documentclasses = self.ExamDB.get_document_class()

        if _documentclasses is not None:
            self.document_class_list.clear()  # Resets the liststore
            for _docclass in _documentclasses:
                if _docclass[0] == self.preamble['Document_Class']:
                    dc = [_docclass[0], _docclass[1], _docclass[2], True]
                    self.document_class_list.append(dc)

                else:
                    dc = [_docclass[0], _docclass[1], _docclass[2], False]
                    self.document_class_list.append(dc)

    def save_docclass_selection(self):
        self.add_new_docclass_to_db()
        self.select_document_class.hide()
        return

    def cancel_docclass_selection(self):
        self.edited_document_class_list_path = []
        self.select_document_class.hide()
        return

    def close_docclass_selection(self):
        self.select_document_class.hide()
        return

    def add_new_docclass(self):
        _docclassID = self.ExamDB.gen_id('docclass')
        _docclassIter = self.document_class_list.append([_docclassID, '', '', False])

        _docclassPath = self.document_class_list.get_path(_docclassIter)
        _selector = self.document_class_view.get_selection()
        _selector.select_path(_docclassPath)
        self.document_class_view.scroll_to_cell(_docclassPath)

    def add_new_docclass_to_db(self):
        _uniqueList = [list(t) for t in
                       set(map(tuple, self.edited_document_class_list_path))]
        _docclasschanged = set([])

        for _p in _uniqueList:
            _docclasschanged.add(_p[0])

        for _e in _docclasschanged:
            _class = int(_e)
            _docclass = DocumentClass()
            _docclass.set_connector(self.dbQuery.get_connector())
            _doc_id = self.document_class_list[_class][0]
            for _u in _uniqueList:
                if _u[0] == _e:

                    if _u[1] == 0:
                        _docclass.set_document_class_id(
                            self.document_class_list[_class][_u[1]])
                    if _u[1] == 1:
                        _docclass.set_document_class(
                            self.document_class_list[_class][_u[1]])

                    elif _u[1] == 2:
                        _docclass.set_options(self.document_class_list[_class][_u[1]])

            if self.ExamDB.document_class_exists(_doc_id):
                _docclass.update_database()

            else:
                _docclass.set_document_class_id(_doc_id)
                _docclass.insert_into_database()

        self.edited_document_class_list_path = []

    def open_instruction_selection(self):
        self._get_instructions()
        self.select_instructions.show_all()
        return

    def _create_instructions_list(self):
        """
        Retrieves the treeviewer from Glade. After which it will create a
        GTKCellRendererText. Next it creates a column to be put into the
        treeview with GTK.TreeViewColumn and connects the which position from
        treestore it should store in this column. Start by adding GoalID and
        course goal description.
        """

        self.instruction_selector = self.instruction_view.get_selection()
        self.instruction_view.set_property("activate-on-single-click", True)
        self.instruction_view.connect("row-activated", self.instruction_selected)

        self.instruction_view.connect("key-release-event", self.on_list_key_press)

        _columns = [["ID", True, False, True], ["Language", True, False, True], ["Instruction", True, False, True]]

        self._cell_renderer_text_generator(
            self.instruction_view, _columns, self._instructions_edited)

    def instruction_selected(self, __treeview, path, __column):

        if path is not None:
            self.preamble["Instruction"] = self.instruction_list[path][0]

        _instruction = Instructions()

        try:
            _instruction.load_from_database(
                *self.ExamDB.get_instructions(
                    self.preamble["Instruction"])[0])

        except TypeError as err:
            print("instruction_selected(): %s" % err)
            self.selected_instruction = [[self.instruction_list, path], None]
            return

        self.selected_instruction = [
            [self.instruction_list, path], _instruction]
        self.instruction_entry.set_text(self.preamble["Instruction"])

    def _instructions_edited(self, __widget, path, text, cell):
        self.instruction_list[path][cell] = text
        self.edited_instruction_list_path.append([path, cell])
        _iter = self.instruction_list.get_iter(path)

    def _get_instructions(self):
        """
        """
        _instructions = self.ExamDB.get_instructions()

        if _instructions is not None:
            self.instruction_list.clear()  # Resets the liststore
            for instr in _instructions:
                instruction = [instr[0], instr[1], instr[2], False]
                self.instruction_list.append(instruction)

    def save_instruction_selection(self):
        self.add_new_instructions_to_db()
        self.select_instructions.hide()
        return

    def add_new_instruction(self):
        _instrID = self.ExamDB.gen_id('instr')
        _instrIter = self.instruction_list.append([_instrID, '', '', False])
        _instrPath = self.instruction_list.get_path(_instrIter)

        _selector = self.instruction_view.get_selection()
        _selector.select_path(_instrPath)
        self.instruction_view.scroll_to_cell(_instrPath)

    def add_new_instructions_to_db(self):
        _uniqueList = [list(t) for t in
                       set(map(tuple, self.edited_instruction_list_path))]
        _instructionchanged = set([])

        for _p in _uniqueList:
            _instructionchanged.add(_p[0])

        for _e in _instructionchanged:
            _instr = int(_e)
            _instr_id = self.instruction_list[_instr][0]
            _instruction = Instructions()
            _instruction.set_connector(self.dbQuery.get_connector())
            for _u in _uniqueList:
                if _u[0] == _e:
                    if _u[1] == 0:
                        _instruction.set_instruction_id(
                            self.instruction_list[_instr][_u[1]])
                    if _u[1] == 1:
                        _instruction.set_language(
                            self.instruction_list[_instr][_u[1]])
                    elif _u[1] == 2:
                        _instruction.set_instruction_data(
                            self.instruction_list[_instr][_u[1]])

            if self.ExamDB.instruction_exist(_instruction.get_instruction_id()):
                _instruction.update_database()
            else:
                _instruction.set_instruction_id(_instr_id)
                _instruction.insert_into_database()

        self.edited_instruction_list_path = []

    def cancel_instruction_selection(self):
        self.edited_instruction_list_path = []
        self.select_instructions.hide()
        return

    def close_instruction_selection(self):
        self.select_instructions.hide()
        return

    def _setup_combo_box(self):
        _cell = Gtk.CellRendererText()
        self.preamble_package_combo.pack_start(_cell, True)
        self.preamble_package_combo.add_attribute(_cell, 'text', 0)

    def preamble_package_combo_changed(self):
        _iter = self.preamble_package_combo.get_active_iter()
        if _iter is not None:
            self.preamble["default_package_id"] = \
                self.preamble_package_list[_iter][0]

    def _get_gradelimits(self):
        for _gradeentry in self.grade_entries:
            _entry, _grade = _gradeentry
            _entry.set_editable(True)

            if self.Exam.get_grade_limits(_grade) is None:
                _entry.set_text("")
            else:
                _entry.set_text(self.Exam.get_grade_limits(_grade))

        self.grade_limit_pass_fail_switch.set_state(self.Exam.get_grade_limits("PF"))
        self.grade_limit_in_percent_switch.set_state(self.Exam.get_grade_limits("Percent"))
        self.ilo_based_grading_switch.set_state(self.Exam.get_grade_limits("ILO_based_grading"))

    def _set_pass_fail_only(self):
        self.Exam.set_grade_limits("PF", True)
        for _gradeentry in self.grade_entries:
            _entry, _grade = _gradeentry
            if _grade == "Pass":
                _entry.set_editable(True)
            else:
                if not _entry.get_text() == "":
                    _entry.set_placeholder_text(_entry.get_text())

                if _entry.get_placeholder_text is None:
                    _entry.set_placeholder_text("")

                _entry.set_editable(False)
                _entry.set_text("")

        return

    def _set_f_to_a_scale(self):
        self.Exam.set_grade_limits("PF", False)
        for _gradeentry in self.grade_entries:
            _entry, _grade = _gradeentry
            _entry.set_editable(True)

            if _entry.get_placeholder_text() is None:
                _entry.set_placeholder_text("")

            if not _entry.get_placeholder_text() == "":
                _entry.set_text(_entry.get_placeholder_text())

        return

    def gl_pf_switch(self):
        if self.grade_limit_pass_fail_switch.get_state():  # IF PASS/FAIL only
            self._set_pass_fail_only()
        else:
            self._set_f_to_a_scale()

        if self._exam_saved:
            self.save_gradelimits_to_exam()
            self.print_out_exam()

    def gl_percent_switch(self):
        if self.grade_limit_in_percent_switch.get_state():  # IF Percent
            self.Exam.set_grade_limits('Percent', True)
        else:
            self.Exam.set_grade_limits('Percent', False)

        if self._exam_saved:
            self.save_gradelimits_to_exam()
            self.print_out_exam()

    def ilo_based_grading(self):
        if self.ilo_based_grading_switch.get_state():
            self.Exam.set_grade_limits('ILO_based_grading', True)
        else:
            self.Exam.set_grade_limits('ILO_based_grading', False)

        if self._exam_saved:
            self.save_gradelimits_to_exam()
            self.print_out_exam()

    def save_gradelimits_to_exam(self):
        if self.grade_limit_in_percent_switch.get_state():
            self.Exam.set_grade_limits('Percent', True)
        else:
            self.Exam.set_grade_limits('Percent', False)

        if self.grade_limit_pass_fail_switch.get_state():
            self.Exam.set_grade_limits('PF', True)
        else:
            self.Exam.set_grade_limits('PF', False)

        if self.ilo_based_grading_switch.get_state():
            self.Exam.set_grade_limits('ILO_based_grading', True)
        else:
            self.Exam.set_grade_limits('ILO_based_grading', False)

        for gradeentry in self.grade_entries:
            _entry, _grade = gradeentry
            if _entry.get_text() == "":
                self.Exam.set_grade_limits(_grade, None)
            else:
                self.Exam.set_grade_limits(_grade, _entry.get_text())

        _start_iter = self.grade_comment_buffer.get_start_iter()
        _end_iter = self.grade_comment_buffer.get_end_iter()

        self.Exam.set_grade_comment(self.grade_comment_buffer.get_text(_start_iter, _end_iter, True))

    def reset_gradelimits(self):
        _grades = {"PF": False,
                   "Percent": False,
                   "ILO_based_grading": False,
                   "Fx": "0",
                   "Pass": "0",
                   "D": "0",
                   "C": "0",
                   "B": "0",
                   "A": "0",
                   }

        for _key, _value in _grades.items():
            if _key == 'Percent':
                self.grade_limit_in_percent_switch.set_state(_value)

            if _key == 'PF':
                self.grade_limit_pass_fail_switch.set_state(_value)

            if _key == 'ILO_based_grading':
                self.ilo_based_grading_switch.set_state(_value)

            for _entry, _grade in self.grade_entries:
                if _key == _grade:
                    if _value is None:
                        _value = ''
                    if isinstance(_value, float):
                        _value = str(int(_value))

                    _entry.set_text(_value)

        self.grade_comment_buffer.set_text("")

    def set_gradelimits_from_exam(self):
        _grades = self.Exam.get_grade_limits()
        for _key, _value in _grades.items():
            if _key == 'Percent':
                self.grade_limit_in_percent_switch.set_state(_value)
            if _key == 'PF':
                self.grade_limit_pass_fail_switch.set_state(_value)

            if _key == 'ILO_based_grading':
                self.ilo_based_grading_switch.set_state(_value)

            for _entry, _grade in self.grade_entries:
                if _key == _grade:
                    if _value is None:
                        _value = ''
                    if isinstance(_value, float):
                        _value = str(int(_value))

                    _entry.set_text(_value)

        self.grade_comment_buffer.set_text(self.Exam.get_grade_comment())

    def save_gradelimits_to_profile(self):
        """
        Saves the current grade limits to database.
        :return:
        """
        if self.grade_limit_in_percent_switch.get_state():
            self.loaded_profile.set_grade_limits('Percent', True)
        else:
            self.loaded_profile.set_grade_limits('Percent', False)

        if self.grade_limit_pass_fail_switch.get_state():
            self.loaded_profile.set_grade_limits('PF', True)
        else:
            self.loaded_profile.set_grade_limits('PF', False)

        if self.ilo_based_grading_switch.get_state():
            self.loaded_profile.set_grade_limits('ILO_based_grading', True)
        else:
            self.loaded_profile.set_grade_limits('ILO_based_grading', False)

        for gradeentry in self.grade_entries:
            _entry, _grade = gradeentry
            if _entry.get_text() == "" or _entry.get_text() is None:
                self.loaded_profile.set_grade_limits(_grade, None)
            else:
                self.loaded_profile.set_grade_limits(_grade, _entry.get_text())

        _start_iter = self.grade_comment_buffer.get_start_iter()
        _end_iter = self.grade_comment_buffer.get_end_iter()

        self.loaded_profile.set_grade_comment(self.grade_comment_buffer.get_text(_start_iter, _end_iter, True))

    def set_gradelimits_from_profile(self):
        """
        Grab default grade limits from database, and loads them into the GUI.
        :return:
        """
        if not self.loaded_profile.get_grade_limits():
            return False

        _grades = self.loaded_profile.get_grade_limits()
        for _key, _value in _grades.items():
            if _key == 'Percent':
                self.grade_limit_in_percent_switch.set_state(_value)

            if _key == 'PF':
                self.grade_limit_pass_fail_switch.set_state(_value)

            if _key == 'ILO_based_grading':
                self.ilo_based_grading_switch.set_state(_value)

            for _entry, _grade in self.grade_entries:
                if _key == _grade:
                    if _value is None:
                        _value = ''
                    if isinstance(_value, float):
                        _value = str(int(_value))

                    _entry.set_text(_value)

        if self.loaded_profile.get_grade_comment():
            self.grade_comment_buffer.set_text(self.loaded_profile.get_grade_comment())
        else:
            self.grade_comment_buffer.set_text("")

        return True

    def open_add_question_window(self):
        """
        Method used for opening the manage questions window.
        :return:
        """
        if self._course_loaded():
            self._get_question_ids()
            self._get_question_in_exam_ids()
            self.Exam.set_language(self.profile_language_entry.get_text())
            self.reset_question_inputs()

            _model = self.question_id_viewer.get_model()
            _first_iter = _model.get_iter_first()
            if _first_iter is not None:
                self.question_id_viewer.row_activated(
                    _model.get_path(_first_iter),
                    self.question_id_viewer.get_column(0))

            self.manage_questions_window.show_all()

    def new_question_id_selected(self, __treeview, path, __column, __data=None):
        try:
            if path:
                self.selected_question_id = [path,
                                             self.question_filter[path][1]]  # MOD
                _question_id_selector = self.question_id_in_exam_viewer.get_selection()
                _question_id_selector.unselect_all()

        except TypeError as err:
            print("new_question_id_selected(): %s " % err)

        self.load_question()

    def question_id_in_exam_selected(self, __treeview, path, __column, __data=None):
        try:
            if path:
                self.selected_question_id = [path,
                                             self.question_id_in_exam_list[path][0]]
                _question_id_selector = self.question_id_viewer.get_selection()
                _question_id_selector.unselect_all()

        except TypeError as err:
            print("question_id_in_exam_selected(): %s" % err)

        self.load_question()

    def _create_question_id_list(self):
        """
        Generate the list that will hold the questionIDs so that user can
        select which question to modify.
        """
        # Set sorting order for liststore.
        self.question_id_list.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.question_id_list.set_sort_func(0, self.compare, None)

        # Add filtering
        self.question_filter = self.question_id_list.filter_new()
        self.question_filter.set_visible_func(self.question_filter_func, data=None)

        # Connect sorted and filtered model to viewer
        self.question_id_viewer.set_model(self.question_filter)

        self.question_id_viewer.set_property("activate-on-single-click", True)
        self.question_id_viewer.connect("row-activated",
                                        self.new_question_id_selected)

        self.question_id_viewer.connect("key-release-event",
                                        self.on_list_key_press)

        _question_id_renderer = Gtk.CellRendererText()
        _column_text = Gtk.TreeViewColumn("QuestionID",
                                          _question_id_renderer,
                                          markup=0)
        self.question_id_viewer.append_column(_column_text)

        self.question_filter_completion.set_model(self.question_filter_completion_store)
        self.question_filter_completion.set_text_column(0)

    def _create_question_id_in_exam_list(self):
        """
        Setup the GtkListStore that should list all questions currently selected to an exam.
        :return:
        """

        self.question_id_in_exam_viewer.connect("row-activated",
                                                self.question_id_in_exam_selected)

        self.question_id_in_exam_viewer.set_property("activate-on-single-click", True)

        self._cell_renderer_text_generator(self.question_id_in_exam_viewer, [["QuestionID", False, False, True]])
        return

    def question_filter_func(self, model, iterator, data):
        """
        Method for filtering questions
        model[iterator][1] -- Question ID
        model[iterator][2] -- Tags
        model[iterator][3] -- ILO
        :param model:
        :param iterator:
        :param data:
        :return:
        """
        if self.question_filter_data is None or self.question_filter_data == '':
            return True

        elif model[iterator][1] == self.question_filter_data:
            return True

        elif model[iterator][2]:
            for _tag in json.loads(model[iterator][2]):
                if _tag == self.question_filter_data:
                    return True

        if model[iterator][3]:
            for _ilo in json.loads(model[iterator][3]):
                if _ilo == self.question_filter_data:
                    return True

    def question_id_filter(self, filter_value):
        self.question_filter_data = filter_value
        self.question_filter.refilter()
        return

    def append_to_question_id_store(self, question, status=None):
        """
        Adds the question to the id store, also sets the formatting, based on if the question has been used recently
        or have already appeared in an exam.

        :param question: [Questions.idQuestions, Questions.tags,Questions_has_ILO.goal]
        :param status: 'recent': Question should be marked with red.
                       'used': Question should be marked in bold.
                       'draft': Question should be marked in cursive.
                       'no_ilo': Question should be greyed.
                       'unusable': Question should be greyed and in cursive.
                       else question will be added without any modification.
        :return: iterator to appended question
        """
        _iter = None
        try:
            if status == 'recent':
                _iter = self.question_id_list.append(
                    ['<b><span foreground="red">%s</span></b>'
                     % question[0], question[0],
                     question[1], json.dumps(question[2])])

            if status == 'used':
                _iter = self.question_id_list.append(
                    ['<b>%s</b>' % question[0],
                     question[0], question[1], json.dumps(question[2])])

            if status == 'draft':
                _iter = self.question_id_list.append(
                    ['<i>%s</i>' % question[0], question[0],
                     question[1], json.dumps(question[2])])

            if status == 'no_ilo':
                _iter = self.question_id_list.append(
                    ['<span foreground="grey">%s</span>'
                     % question[0], question[0],
                     question[1], ''])

            if status == 'unusable':
                _iter = self.question_id_list.append(
                    ['<span foreground="grey"><i>%s</i></span>'
                     % question[0], question[0],
                     question[1], ''])

            elif status is None:
                _iter = self.question_id_list.append([question[0], question[0],
                                                      question[1], json.dumps(question[2])])
        except TypeError as err:
            print("append_to_question_id_store(): %s" % err)

        return _iter

    def modify_question_id_store(self, question, status=None):
        """
        Method used when a specific questions status should be modified. For example, when modifying a question.

        :param question: question_id
        :param status: 'recent': Question should be marked with red.
                       'used': Question should be marked in bold.
                       'draft': Question should be marked in cursive.
                       'no_ilo': Question should be greyed.
                       'unusable': Question should be greyed and in cursive.
                       else question will be added without any modification.
        :return:
        """
        _path = self.get_liststore_path(self.question_id_list, question)

        try:
            if status == 'recent':
                self.question_id_list[_path][0] = '<b><span foreground="red">%s</span></b>' % question

            if status == 'used':
                self.question_id_list[_path][0] = '<b>%s</b>' % question

            if status == 'draft':
                self.question_id_list[_path][0] = '<i>%s</i>' % question

            if status == 'no_ilo':
                self.question_id_list[_path][0] = '<span foreground="grey">%s</span>' % question

            if status == 'unusable':
                self.question_id_list[_path][0] = '<span foreground="grey"><i>%s</i></span>' % question

            elif status is None:
                self.question_id_list[_path][0] = question

        except TypeError as err:
            print("modify_question_id_store(): %s" % err)

        return

    def get_question_id_from_drafts(self, question_id):
        for _q in self.question_drafts:
            if _q.get_question_id() == question_id:
                return _q
        return None

    def _get_question_in_exam_ids(self):
        """
        Add existing questions in exam to treestore
        :return:
        """
        self.question_id_in_exam_list.clear()  # Reset the liststore

        if self.Exam.get_question_ids():
            for _q in self.Exam.get_question_ids():
                self.question_id_in_exam_list.append([_q])
        return

    def get_question_usage_status(self, question_id):
        if not self.ExamDB.question_usable(question_id):
            return 'unusable'

        if self.ExamDB.question_already_used(question_id):
            if self.ExamDB.recently_used(question_id):
                return 'recent'
            else:
                return 'used'

        return None

    def _add_questions_to_question_list(self, question_ids, question_without_ilo):
        """
        Takes a list of questions that are connected to a specific course, and adds these to the list of questions
        in the manage questions window.
        :param question_ids: A list of question IDs for questions that are connected to an ILO.
        :param question_without_ilo: A list of question IDs for questions that do not belong to an ILO.
        :return:
        """
        _unique_list = set()
        if question_ids:
            for _qid in question_ids:
                # Check if question in draft to avoid double loading
                if not self.get_question_id_from_drafts(_qid[0]):
                    _status = self.get_question_usage_status(_qid[0])
                    self.append_to_question_id_store(_qid, _status)

                # Populate liststore for filter completion
                self.question_filter_completion_store.append([_qid[0]])
                for _tag in json.loads(_qid[1]):
                    _unique_list.add(_tag)
                for _goal in _qid[2]:
                    _unique_list.add(_goal)

            if question_without_ilo:
                for _qid in question_without_ilo:
                    if not self.get_question_id_from_drafts(_qid):
                        self.append_to_question_id_store([_qid[0], _qid[1], None], 'no_ilo')
                        self.question_filter_completion_store.append([_qid[0]])
                        for _tag in json.loads(_qid[1]):
                            _unique_list.add(_tag)

        return _unique_list

    def _get_question_ids(self):
        if self.ExamDB:
            # Cleanup
            self.question_id_list.clear()  # Resets the liststore
            self.question_filter_completion_store.clear()  # Resets the liststore for entry completion.

            # Load questions from DB.
            _question_ids = self.ExamDB.get_question_ids(self._course_code_used,
                                                         self._course_version_used)

            _question_without_ilo = self.ExamDB.get_questions_without_ilo(self._course_code_used,
                                                                          self._course_version_used)

            # Add all questions to a list, with the correct formatting based on each questions state.
            _unique_list = self._add_questions_to_question_list(_question_ids, _question_without_ilo)

            # Append the questions to the question ID list.
            for _i in _unique_list:
                self.question_filter_completion_store.append([_i])

            # Load drafts.
            if not self.question_drafts:
                return
            else:
                for _q in self.question_drafts:
                    self.append_to_question_id_store(
                        [_q.get_question_id(), _q.get_question_id(),
                         _q.get_tags(), _q.get_ilo()[2]], 'draft'
                    )
            return

    def question_editable(self, editable):
        if not editable:
            self.question_language_entry.set_editable(False)
            self.usable_check.set_sensitive(False)
            self.question_viewer.set_editable(False)
            self.question_save_draft_button.set_sensitive(False)
        else:
            self.question_language_entry.set_editable(True)
            self.usable_check.set_sensitive(True)
            self.question_viewer.set_editable(True)
            self.question_save_draft_button.set_sensitive(True)
        return

    def force_edit_question(self):
        _messagedia = MessageDialogWindow()

        if _messagedia.confirmation_dialogue(
                'Are you sure?', 'This question is used in one or several exams. \n'
                                 'By modifiying this, you will later not be able to recreate the exact exam '
                                 'that was given.'):
            self.load_question(force_edit=True)
            return

    def add_question_to_exam(self):
        """
        Add loaded question to Exam.
        :return:
        """
        if self.loaded_question:
            self.Exam.append_questions(self.loaded_question)
            self.question_id_in_exam_list.append([self.loaded_question.get_question_id()])

    def remove_question_from_exam(self):
        if self.loaded_question:
            if self.Exam.question_in_exam(self.loaded_question.get_question_id()):
                _iter = self.question_id_in_exam_list.get_iter(self.selected_question_id[0])
                self.Exam.remove_questions(self.loaded_question.get_question_id())
                self.question_id_in_exam_list.remove(_iter)
                self.selected_question_id = None

    def load_question_from_db(self, question_id, force_edit):
        """
        Load a question from the database and store it in a QuestionClass object.
        :param question_id: The question ID for the question to load.
        :param force_edit: Boolean value, used to set whether or not this question can be edited.
        :return: A question class object if the question has been found in the Database, otherwise None.
        """
        try:
            assert (isinstance(question_id, str))

            if self.ExamDB.question_exists(question_id):
                _question_data = self.ExamDB.get_questions_by_id(question_id)
                if _question_data:
                    _question = Question()
                    _question.load_from_database(*_question_data)
                    _question.set_in_database(True)

                    if self.ExamDB.question_already_used(question_id):
                        self.force_edit_btn.set_sensitive(True)
                        # Should forced edit be allowed?
                        if not force_edit:
                            _question.set_editable(False)
                        else:
                            _question.set_editable(True)

                    return _question

            return None

        except TypeError as err:
            print("load_question(): %s" % err)
            return None

        except AssertionError as err:
            print("load_question_from_db(): %s" % err)
            return None

    def load_question_without_ilo(self, question_id):
        _question_data = self.ExamDB.get_questions_without_ilo_by_id(question_id, self._course_code_used,
                                                                     self._course_version_used)
        if not _question_data:
            return None

        _question = Question()
        _question.load_from_database(*_question_data)
        _question.set_in_database(True)

        return _question

    def display_question(self):
        """
        Method used for displaying a loaded question in the GUI.
        :return:
        """
        if self.loaded_question.get_editable():
            self.question_editable(True)
        else:
            self.question_editable(False)

        self.question_language_entry.set_text(self.loaded_question.get_language())
        self.usable_check.set_active(self.loaded_question.get_usable())
        self.buffer_question.set_text(self.loaded_question.get_question_code())

        # Get question score statistics
        _question_data = self.ExamDB.get_question_scores(self.loaded_question.get_question_id())

        question_statistic = GenerateQuestionStatistics(self.loaded_question.get_question_id(),
                                                        _question_data["max_point"],
                                                        _question_data["question_data"])

        self.student_answer_entry.set_text(str(question_statistic.get_cardinality()))
        self.question_average_score_entry.set_text(question_statistic.get_stat_str())
        self.question_last_used_entry.set_text(self.loaded_question.get_last_used_str())

    def load_question(self, force_edit=False):
        """
        Method used for loading a selected question
        :param force_edit: Sets whether or not the question should be editable.
        :return: None
        """
        _question_id = self.selected_question_id[1]

        # Save previous _question.
        if self.loaded_question is not None:
            if self.loaded_question.get_modified():
                self.save_question_as_draft()

        if self.selected_question_id is None:
            print("Select a question")
            return

        # Disable edit button, this should only be available when opening used questions.
        self.force_edit_btn.set_sensitive(False)

        # Start by checking amongst drafts, since these are the working
        # material.
        _question = self.get_question_id_from_drafts(_question_id)

        # If the question ID is not in draft, check the database.
        if not _question:
            _question = self.load_question_from_db(_question_id, force_edit)

        # If the question still isn't found, check amongst questions that don't have an ILO.
        if _question is None:
            _question = self.load_question_without_ilo(_question_id)

        # Throwing in the towel
        if _question is None:
            print('Still no %s, I give up' % _question_id)

        self.loaded_question = _question
        self.display_question()

    def question_has_been_modified(self, __data=None):
        """
        Method called whenever a question has been edited through the GUI.
        :param __data:
        :return:None
        """

        if self.loaded_question is None or not self.loaded_question.get_editable():
            return

        else:
            self.loaded_question.set_modified(True)
            self.modify_question_id_store(self.loaded_question.get_question_id(), 'draft')

    def question_language_entry_modified(self):
        """
        Method called whenever the language entry has been modified through the GUI.
        :return: None
        """

        if self.loaded_question is None:
            return

        if self.loaded_question.get_language() != self.question_language_entry.get_text():
            self.question_has_been_modified()

    def question_usable_entry_modified(self):
        """
        Method called whenever the loaded question has been tagged as usable or not usable through the GUI.
        :return: None
        """
        if self.loaded_question:
            if self.loaded_question.get_usable() != self.usable_check.get_active():
                self.question_has_been_modified()

    def parse_edited_question(self):
        """
        Parses the question text buffer and loads it into a temporary QuestionClass object.
        :return: A QuestionClass object
        """
        _parse_question = LatexParser(self.dbQuery.get_connector(), self.Settings)
        _parse_question.set_examdb(self.ExamDB)

        _start_iter = self.buffer_question.get_start_iter()
        _end_iter = self.buffer_question.get_end_iter()

        _temp_question = None

        try:
            _temp_question = _parse_question.parse_data(self.buffer_question.get_text(
                _start_iter, _end_iter, True),
                self._course_code_used,
                self._course_version_used,
                self.usable_check.get_active()
            )

            # _temp_question[0].set_usable(self.usable_check.get_active())
            _temp_question[0].set_in_database(self.loaded_question.get_in_database())

        except Warning as err:
            print('save_question_as_draft(): %s' % err)
            return None

        return _temp_question

    def save_question_as_draft(self):
        """
        Method used for saving the loaded question as a draft, if it has been modified.
        :return: None
        """
        # Is there a question loaded.
        if not self.loaded_question:
            return False

        # If so, load it.
        _question_id = self.loaded_question.get_question_id()
        _usable = self.loaded_question.get_usable()

        # If the question hasn't been modified, do nothing.
        if not self.loaded_question.get_modified():
            return False

        _temp_question = self.parse_edited_question()

        # If the parse didn't succeed, return None.
        if not _temp_question:
            return None

        _temp_question[0].set_question_id(_question_id)

        self.loaded_question.import_question(*_temp_question[0].export_question())

        del _temp_question

        self.question_drafts.add(self.loaded_question)

        return

    @staticmethod
    def get_liststore_path(model, question_id):
        for _row in model:
            if _row[1] == question_id:
                _iter = _row.iter
                return model.get_path(_iter)

    def save_question_to_db(self):
        """
        Saves the questions in draft to the database.
        :return:
        """
        if self.question_drafts is None:
            return False
        else:
            for _draft in self.question_drafts.copy():
                if _draft.get_modified() and _draft.get_ilo():
                    _draft.set_connector(self.dbQuery.get_connector())
                    _draft.set_exam_database(self.ExamDB)
                    if _draft.get_in_database():  # Question has been modified.
                        _draft.update_database()
                    else:  # New question.
                        _draft.insert_into_database()

                    _draft.set_modified(False)
                    _qid = _draft.get_question_id()
                    self.modify_question_id_store(_qid, self.get_question_usage_status(_qid))

                    self.question_drafts.remove(_draft)
                    self.load_question()

    def import_questions(self, folder):
        """
        Method for importing tex-files with questions into the database.
        :param folder: Path to where the tex-files are located
        :return:
        """
        _parse = LatexParser(self.dbQuery.get_connector(), self.Settings)
        _parse.set_examdb(self.ExamDB)
        _root = folder
        _pattern = "*.tex"
        _questions = []
        for _path, _subdirs, _files in os.walk(_root):
            for _name in _files:
                if fnmatch(_name, _pattern):
                    _filename = os.path.join(_path, _name)
                    _questions = _parse.parse_from_file(_filename,
                                                        self._course_code_used,
                                                        self._course_version_used)

        for _q in _questions:
            new_question_id = self.ExamDB.gen_id("question",
                                                 self._course_code_used,
                                                 self._course_version_used)
            _q.set_question_id(new_question_id)
            _q.set_language(self.question_language_entry.get_text())
            # _q.set_usable(self.usable_check.get_active())
            _q.set_modified(True)
            self.question_drafts.add(_q)

        self.save_question_to_db()
        self._get_question_ids()

        return

    def export_questions(self):
        _all_flag = False
        _response = None

        _messagedia = MessageDialogWindow()

        for _i in self.question_filter:  # List filtered questions
            _export_code = ''
            _question_to_export = Question()
            _question_to_export.load_from_database(*self.ExamDB.get_questions_by_id(_i[1]))
            _package_req = _question_to_export.get_package_requirement()
            _decl_req = _question_to_export.get_declaration_requirement()
            _question_id = _i[1]
            _course_code = _question_to_export.get_course_code()

            if _package_req:
                for _p in _package_req:
                    _package = Package()
                    _package.load_from_database(*self.ExamDB.get_package_list(_p[0])[0])
                    _package.set_options(_p[1])
                    _export_code += _package.gen_package_code() + "\n"

            if _decl_req:
                for _d in _decl_req:
                    _declaration = Declaration()
                    _declaration.load_from_database(*self.ExamDB.get_declarations(_d[0])[0])
                    _export_code += _declaration.gen_declaration_code()

            _export_code += _question_to_export.get_question_code()

            _new_filepath = self.Settings.get_program_path() + '/' + 'Courses/' + \
                            _course_code + '/' + 'Questions/' + '/'

            if not os.path.isdir(_new_filepath):  # If folder don't exist, create it.
                try:
                    os.makedirs(_new_filepath, exist_ok=True)
                except OSError as err:
                    print('export_questions(): %s' % err)
                    print('Unable to create filepath %s' % _new_filepath)

            _new_abs_filename = os.path.join(_new_filepath, _question_id + '.tex')

            if not os.path.isfile(_new_abs_filename):
                try:
                    with io.open(_new_abs_filename, 'w+', encoding='utf8') as _texfile:
                        _texfile.write(_export_code)
                except FileNotFoundError:
                    _messagedia.information_dialogue('File not found', 'Unable to write %s' % _question_id)

            else:
                if not _all_flag:
                    _response, _all_flag = _messagedia.confirmation_dialogue_all("%s exist" % _question_id,
                                                                                 'Overwrite?')

                if _response == Gtk.ResponseType.DELETE_EVENT:
                    break

                if _response == Gtk.ResponseType.YES:
                    try:
                        with io.open(_new_abs_filename, 'w+', encoding='utf8') as _texfile:
                            _texfile.write(_export_code)
                    except FileNotFoundError:
                        _messagedia.information_dialogue('File not found', 'Unable to write %s' % _question_id)

        _messagedia.information_dialogue('Export questions', 'Questions exported successfully to workdir')

        return True

    def copy_question(self):
        if self.loaded_question is None:
            print("Please load a _question to copy")
            return False

        # Copy loaded question to a new object.

        _question = Question()
        _question.import_question(*self.loaded_question.export_question())

        _question.set_editable(True)
        _question.set_question_id(self.ExamDB.gen_id("question",
                                                     self._course_code_used,
                                                     self._course_version_used))

        _question.append_not_in_same_exam_as(self.loaded_question.get_question_id())
        _question.set_in_database(False)

        self.question_language_entry.set_text(_question.get_language())
        self.usable_check.set_active(_question.get_usable())
        self.buffer_question.set_text(_question.get_question_code())

        _newquestioniter = self.append_to_question_id_store(
            [_question.get_question_id(),
             _question.get_question_id(), _question.get_tags(),
             _question.get_ilo()[2]], 'draft')

        self.question_drafts.add(_question)

    def reset_question_inputs(self):
        self.question_language_entry.set_text(self.Exam.get_language())
        self.buffer_question.set_text("")
        self.usable_check.set_active(True)

    def new_question(self):
        """
        Next retrieve the new ID for the question and append it to the
        liststore.
        Use the iter to retrieve the path to the new entry and focus both the
        selection and the view to this path.
        """
        # Clear filter
        self.question_filter_entry.set_text("")

        _parse_question = LatexParser(self.dbQuery.get_connector(), self.Settings)
        _parse_question.set_examdb(self.ExamDB)

        _textemplate = ''

        _new_question_id = None
        _newquestioniter = None

        with open("Templates/questiontemplate.tex") as fp:
            _textemplate += fp.read()

        _questions = _parse_question.parse_data(_textemplate,
                                                self._course_code_used,
                                                self._course_version_used,
                                                True)
        for _q in _questions:
            # Add question ID as a comment.
            _new_question_id = self.ExamDB.gen_id("question",
                                                  self._course_code_used,
                                                  self._course_version_used)
            _q.set_question_id(_new_question_id)
            _q.set_language(self.Exam.get_language())
            _q.set_modified(True)
            self.question_drafts.add(_q)

            _newquestioniter = self.append_to_question_id_store([_new_question_id, _new_question_id,
                                                                 _q.get_tags(), _q.get_ilo()[2]],
                                                                'draft')

        _selector = self.question_id_viewer.get_selection()
        _questionIDPath = self.question_id_list.get_path(_newquestioniter)
        _selector.select_path(_questionIDPath)

        self.question_id_viewer.scroll_to_cell(_questionIDPath)
        self.question_id_viewer.row_activated(
            _questionIDPath, self.question_id_viewer.get_column(0))
        return

    def close_add_question_window(self):
        # Cleanup
        self.selected_question_id = []
        self.loaded_question = None
        self.question_drafts = set()

        self.manage_questions_window.hide()

    def open_declaration_window(self):
        """
        """
        self._get_declarations()
        self.show_declarations.show_all()

    def _create_declaration_list(self):
        """
        """

        _columns = [["ID", True, False, True], ["Declaration", True, False, True], ["Tags", True, False, True]]

        self.declaration_view.connect("row-activated",
                                      self.declaration_selected)
        self.declaration_view.set_property("activate-on-single-click", True)

        self.declaration_view.connect("key-release-event", self.on_list_key_press)

        self._cell_renderer_text_generator(self.declaration_view,
                                           _columns,
                                           self._declaration_edited)

    def _declaration_edited(self, __widget, path, text, cell):
        self.declaration_list[path][cell] = text
        self.edited_declaration_list_path.append([path, cell])

    def declaration_selected(self, __treeview, path, __column, __data=None):
        _declare = Declaration()

        if path is not None:
            try:
                _declare.load_from_database(
                    *self.ExamDB.get_declarations(
                        self.declaration_list[path][0])[0]
                )
            except TypeError as err:
                print("declaration_selected(): %s" % err)
                self.selected_declaration = [[self.declaration_list, path], None]
                return

            self.selected_declaration = [[self.declaration_list, path], _declare]

    def _get_declarations(self):
        """
        This method is run when Declarationwindow is opened.
        Populate the liststore declarationlist with the available _declarations.
        """
        _declarations = self.ExamDB.get_declarations()
        if _declarations is not None:
            self.declaration_list.clear()  # Resets the liststore
            for _d in _declarations:
                _decl = [_d[0], _d[1], _d[2]]
                self.declaration_list.append(_decl)

    def new_declaration(self):
        _declID = self.ExamDB.gen_id('decl')
        _newDeclareIter = self.declaration_list.append([_declID, '', ''])
        _declarepath = self.declaration_list.get_path(_newDeclareIter)

        _selector = self.declaration_view.get_selection()
        _selector.select_path(_declarepath)
        self.question_id_viewer.scroll_to_cell(_declarepath)

    def add_new_declaration_to_db(self):
        # Save new author information in dictionary for adding to database.
        _uniqueList = [list(t) for t in
                       set(map(tuple, self.edited_declaration_list_path))]
        _declarationchanged = set([])

        for _p in _uniqueList:
            _declarationchanged.add(_p[0])
        for _d in _declarationchanged:
            _decl = int(_d)
            _declaration = Declaration()
            _declaration.set_connector(self.dbQuery.get_connector())
            _declaration.set_id(self.declaration_list[_decl][0])
            for _u in _uniqueList:
                if _u[0] == _d:
                    if _u[1] == 0:
                        _declaration.set_id(self.declaration_list[_decl][_u[1]])
                    elif _u[1] == 1:
                        _declaration.set_declaration_data(
                            self.declaration_list[_decl][_u[1]])
                    elif _u[1] == 2:
                        _declaration.set_tags(
                            self.declaration_list[_decl][_u[1]])

            if _declaration.get_id() is None:
                print("Please insert declarationID")
                return False

            elif self.ExamDB.declaration_exists(_declaration.get_id()):
                _declaration.update_database()
            else:
                _declaration.insert_into_database()

        self.edited_declaration_list_path = []

    def save_declaration_selection(self):
        self.add_new_declaration_to_db()
        self.show_declarations.hide()

    def cancel_declaration_selection(self):
        self.close_declaration_window()

    def close_declaration_window(self):
        self.edited_declaration_list_path = []
        self.show_declarations.hide()

    def open_not_in_same_exam_window(self):
        """
        """
        if self.loaded_question is None:
            print("Please select a question")
            return False
        else:
            self._get_not_in_same_exam()
            self.not_in_same_exam_window.show_all()

    def _create_not_in_same_exam_list(self):
        """
        """
        _textRenderer = Gtk.CellRendererText()
        _column_text = Gtk.TreeViewColumn(
            "Similiar Question", _textRenderer, text=1)

        self.not_in_same_exam_view.set_property("activate-on-single-click", True)
        self.not_in_same_exam_view.connect("row-activated", self.not_in_same_exam_selected)

        self.not_in_same_exam_view.connect("key-release-event",
                                           self.on_list_key_press)

        _column_text.set_sort_column_id(1)
        _textRenderer.set_property("editable", True)
        _textRenderer.connect("edited", self._not_in_same_exam_edited, 1)
        self.not_in_same_exam_view.append_column(_column_text)

    def not_in_same_exam_selected(self, __treeview, path, __column, __data=None):
        _model = self.not_in_same_exam_list

        if path is None:  # Should never happen since this check
            #              is done when view is opened.
            self.selectedNISE = [[_model, path], None]
            return

        self.selectedNISE = [[_model, path], self.loaded_question.get_question_id()]

    def _not_in_same_exam_edited(self, __widget, path, text, cell):
        self.not_in_same_exam_list[path][cell] = text
        self.edited_not_in_same_exam_list_path.append([path, cell])

    def _get_not_in_same_exam(self):
        #        This method is run when NotInSameExamwindow is opened.
        #        Populate the liststore notinsameexamlist with the available
        #        NotInSameExam.
        _similar = None
        self.not_in_same_exam_list.clear()  # Resets the liststore

        if self.loaded_question is None:
            return

        _similar = self.loaded_question.get_not_in_same_exam_as()

        if _similar:
            for _s in _similar:
                self.not_in_same_exam_list.append(
                    [self.loaded_question.get_question_id(), _s]
                )

    def add_new_not_in_same_exam(self):
        _qid = self.loaded_question.get_question_id()
        _niseIter = self.not_in_same_exam_list.append([_qid, ''])
        _nisePath = self.not_in_same_exam_list.get_path(_niseIter)

        selector = self.not_in_same_exam_view.get_selection()
        selector.select_path(_nisePath)
        self.question_id_viewer.scroll_to_cell(_nisePath)

    def add_new_not_in_same_exam_to_question(self):
        if not self.edited_not_in_same_exam_list_path:
            return None

        else:
            _uniqueList = [list(t) for t in
                           set(map(tuple, self.edited_not_in_same_exam_list_path))]
            _not_in_same_exam_changed = set([])

            for _p in _uniqueList:
                _not_in_same_exam_changed.add(_p[0])

            for _newNISEEntry in _not_in_same_exam_changed:
                for _u in _uniqueList:
                    if _u[0] == _newNISEEntry:
                        if _newNISEEntry is None:
                            break
                        _nise = int(_newNISEEntry)
                        if _u[1] == 1:
                            self.loaded_question.append_not_in_same_exam_as(
                                self.not_in_same_exam_list[_nise][_u[1]])
                            # Add question that should not be in the same exam as draft as well.
            self.edited_not_in_same_exam_list_path = []
            self.question_has_been_modified()

    def save_not_in_same_exam_selection(self):
        self.add_new_not_in_same_exam_to_question()
        self.not_in_same_exam_window.hide()

    def close_not_in_same_exam_window(self):
        self.edited_not_in_same_exam_list_path = []
        self.not_in_same_exam_window.hide()

    def open_select_question_folder(self, parent_name):

        if parent_name == 'add_question_window':
            _parent = self.manage_questions_window

        else:
            _parent = None
        # try:
        fcd = Gtk.FileChooserDialog(title=None,
                                    parent=_parent,
                                    action=Gtk.FileChooserAction.SELECT_FOLDER)
        fcd.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        fcd.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        self.response = fcd.run()

        if self.response == Gtk.ResponseType.OK:
            if parent_name == 'add_question_window':
                self.import_questions(fcd.get_filename())

        fcd.destroy()

    def _create_quest_package_req_list(self):
        self.quest_packagereq_selector = self.question_package_requirement_view.get_selection()
        self.question_package_requirement_view.set_property("activate-on-single-click", True)
        self.question_package_requirement_view.connect("row-activated", self._question_package_requirement_selected)

        self.question_package_requirement_view.connect("key-release-event", self.on_list_key_press)

        _columns = [["ID", True, True, False], ["Package", True, False, True], ["Options", True, False, True]]

        self._cell_renderer_text_generator(
            self.question_package_requirement_view, _columns, self._question_package_requirement_edited)

    def _question_package_requirement_selected(self, __treeview, path, __column):
        _model = self.question_package_requirement_list

        if path is None:  # Should never happen since this check
            #              is done when view is opened.
            self.selected_question_package_requirement = [[_model, path], None]
            return

        self.selected_question_package_requirement = [[_model, path], self.loaded_question.get_question_id()]

    def _question_package_requirement_edited(self, __widget, path, text, cell):
        self.question_package_requirement_list[path][cell] = text
        _package_id = self.ExamDB.package_exist(self.question_package_requirement_list[path][1])
        if _package_id:
            self.question_package_requirement_list[path][0] = _package_id
        else:
            self.question_package_requirement_list[path][0] = None

        self.question_has_been_modified()

    def open_question_package_requirement_window(self):
        """
        """
        if self.loaded_question is None:
            print("Please select a question")
            return False
        else:
            self._get_question_package_requirements()

            # Activate the first row, if available.
            if self.question_package_requirement_list.get_iter_first():
                _iter = self.question_package_requirement_list.get_iter_first()
                _path = self.question_package_requirement_list.get_path(_iter)
                _selector = self.question_package_requirement_view.get_selection()
                _selector.select_path(_path)
                _column = self.question_package_requirement_view.get_column(1)
                self.question_package_requirement_view.row_activated(_path, _column)

            self.question_package_requirement.show_all()

    def _get_question_package_requirements(self):
        #        This method is run when Question Package Requirement is opened.
        #        Populate the liststore question_package_requirement_list with the available
        #        question package requirements.

        self.question_package_requirement_list.clear()  # Resets the liststore

        if self.loaded_question is None:
            return

        question_package_requirements = self.loaded_question.get_package_requirement()

        if not question_package_requirements:
            return

        for _r in question_package_requirements:
            _package_id, _package_name, _package_options = self.ExamDB.get_package_list(_r[0])[0]
            self.question_package_requirement_list.append([_package_id, _package_name, _r[1]])

    def add_new_question_package_requirement(self):
        _iter = self.question_package_requirement_list.append(['', '', ''])
        _path = self.question_package_requirement_list.get_path(_iter)

        selector = self.question_package_requirement_view.get_selection()
        selector.select_path(_path)

    def update_question_package_requirements(self):

        # Empty questions package requirements
        self.loaded_question.set_package_requirement([])

        for _q in self.question_package_requirement_list:
            _pack_req = {'optional': _q[:][2],
                         'package': _q[:][1],
                         }

            if _pack_req['package'] is None:
                return

            _id = self.ExamDB.package_exist(_pack_req['package'])
            if not _id:
                # If package previously don't exist, add package to DB.
                _new_package = Package()
                _new_package.set_id(self.ExamDB.gen_id("package"))
                _new_package.set_package_data(_pack_req['package'])
                _new_package.set_connector(self.dbQuery.get_connector())
                _new_package.insert_into_database()
                _id = _new_package.get_id()

                self.loaded_question.append_package_requirement(_id, _pack_req['optional'])

        self.question_has_been_modified()

    def save_question_package_requirement(self):
        self.update_question_package_requirements()
        self.question_package_requirement.hide()

    def close_question_requirement_window(self):
        self.question_package_requirement.hide()

    def open_exam_window(self):
        self.get_old_exams()

        # Activate the first row by default.
        _treemodel = self.old_exam_viewer.get_model()
        _first_iter = _treemodel.get_iter_first()
        if _first_iter is not None:
            _path = _treemodel.get_path(_first_iter)
            _column = self.old_exam_viewer.get_column(0)
            self.old_exam_viewer.row_activated(_path, _column)

        # Open window
        self.load_exam_window.show_all()

    def _create_old_exam_list(self):
        self._old_exam_list_treestore = Gtk.TreeStore(str, str, str, str)
        self._old_exam_list_treestore.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        self._old_exam_list_treestore.set_sort_func(2, self.compare_date)

        self._oldexamSelector = self.old_exam_viewer.get_selection()
        self.old_exam_viewer.set_model(self._old_exam_list_treestore)
        self.old_exam_viewer.set_property("activate-on-single-click", True)
        self.old_exam_viewer.connect("row-activated", self.old_exam_selected)
        self.old_exam_viewer.connect("key-release-event",
                                     self.on_list_key_press)
        self.old_exam_viewer.connect("row-expanded", self.oldexamviewer_size_adjust)
        self.old_exam_viewer.connect("row-collapsed", self.oldexamviewer_size_adjust)

        _columns = [["Course Code", False, False, True],
                    ["Exam ID", False, False, True],
                    ["Exam Date", False, False, True],
                    ["Exam Type", False, False, True]
                    ]

        # Create a treestore to group exams nicer.

        self._cell_renderer_text_generator(
            self.old_exam_viewer, _columns)

        return

    def oldexamviewer_size_adjust(self, treeview, _iter, path):
        self.old_exam_viewer.scroll_to_cell(path, use_align=True)

    def old_exam_selected(self, __treeview, path, __column, __data=None):
        self.exam_to_load = self._old_exam_list_treestore[path][1]
        self.selected_old_exam = [self._old_exam_list_treestore, path]
        self.old_exam_viewer.scroll_to_cell(path, use_align=True)
        return

    def get_old_exams(self, course=None):
        self._old_exam_list_treestore.clear()

        for _course in self.ExamDB.get_old_exams():
            _course_id = _course[0]
            parent_iter = self._old_exam_list_treestore.append(None, [_course_id, None, None, None])
            for _old_exam in _course[1]:
                _old_exam.insert(0, None)
                _old_exam[2] = datetime.strftime(_old_exam[2], '%Y-%m-%d')  # Convert datetime to str
                self._old_exam_list_treestore.append(parent_iter, _old_exam)

        return

    def _create_bibliography_list(self):
        """
        """
        self.bibliography_id_viewer.set_property("activate-on-single-click", True)
        self.bibliography_id_viewer.connect("row-activated", self.bibliography_selected)
        self.bibliography_id_viewer.connect("key-release-event", self.on_list_key_press)

        _bibliography_id_renderer = Gtk.CellRendererText()
        _column_text = Gtk.TreeViewColumn("ID",
                                          _bibliography_id_renderer,
                                          markup=0)
        _column_text.set_sort_column_id(1)
        self.bibliography_id_viewer.append_column(_column_text)
        _column_text.clicked()

    def bibliography_selected(self, __treeview, path, __column, __data=None):
        try:
            if path:
                self.selected_bibliography_id = \
                    [path, self.bibliography_list[path][1]]

        except TypeError as err:
            print("bibliography_selected(): %s " % err)

        self.load_bibliography()

    def get_bibliography_from_drafts(self, bib_id):
        for _bib in self.bibliography_drafts:
            if _bib.get_bibliography_id() == bib_id:
                return _bib
        return None

    def save_bibliography_as_draft(self, _bibliography=None):
        if _bibliography is None:
            _bibID = self.loaded_bibliography["bibliography"].get_bibliography_id()
            _bibliography = self.get_bibliography_from_drafts(_bibID)

        if _bibliography is None:
            return False

        if not _bibliography.get_modified():
            self.bibliography_drafts.remove(_bibliography)
            return False

        _parse_bibliography = BibParser()

        _start_iter = self.buffer_bibliography.get_start_iter()
        _end_iter = self.buffer_bibliography.get_end_iter()

        _tempbibliography = _parse_bibliography.parse_data(
            self.buffer_bibliography.get_text(
                _start_iter, _end_iter, True)
        )
        if len(_tempbibliography) == 1:
            _bibliography.set_bibliography_data(
                _tempbibliography[0].get_raw_bibliography_data()
            )

            if _bibliography.get_bibliography_id() == 'NEW':
                _path = self.get_liststore_path(self.bibliography_list,
                                                _bibliography.get_bibliography_id()
                                                )

                _bibliography.set_bibliography_id(
                    _tempbibliography[0].get_bibliography_id()
                )

                self.bibliography_list[_path] = [
                    '<i>*%s</i>' % _bibliography.get_bibliography_id(),
                    _bibliography.get_bibliography_id()
                ]

    def bibliography_has_been_modified(self, *args):
        _bibliography_id = self.loaded_bibliography["bibliography"].get_bibliography_id()
        _bibliography = self.get_bibliography_from_drafts(_bibliography_id)

        if _bibliography is None or not _bibliography.get_editable():
            return

        else:
            _bibliography.set_modified(True)
            self.bibliography_list[self.loaded_bibliography["path"]] = (
                ['<i>*%s</i>' % _bibliography_id, _bibliography_id])

    def load_bibliography(self):
        """
        """
        _bibliography_id = self.selected_bibliography_id[1]

        #        Save previous question.
        if not self.loaded_bibliography["bibliography"] is None:
            self.save_bibliography_as_draft()

        if self.selected_bibliography_id is None:
            print("Select a bibliography")
            return

        # Start by checking amongst drafts, since these are the working
        # material.
        _bibliography = self.get_bibliography_from_drafts(_bibliography_id)

        # If the Bibliography is not in draft, check the database.
        if _bibliography is None:
            if self.ExamDB.bibliography_exist(_bibliography_id):
                _bibliography = Bibliography()
                try:
                    _bibliography.load_from_database(
                        *self.ExamDB.get_bibliography(_bibliography_id)[0])
                    # If question haven't been used, att to drafts.
                    _bibliography.set_in_database(True)

                    if self.ExamDB.bibliography_already_used(_bibliography_id):
                        _bibliography.set_editable(False)

                    self.bibliography_drafts.add(_bibliography)

                except TypeError as err:
                    print("load_bibliography(): %s" % err)
                    _bibliography = None

        if _bibliography is None:
            print('Still no %s, I give up' % _bibliography_id)
            return

        else:
            self.loaded_bibliography["path"] = self.selected_bibliography_id[0]
            self.loaded_bibliography["bibliography"] = (
                _bibliography
            )

            self.buffer_bibliography.set_text(
                _bibliography.get_bibliography_data())

    def new_bibliography(self):
        """
        """
        _parse_bibliography = BibParser()
        _textemplate = ''

        _selector = self.bibliography_id_viewer.get_selection()
        _new_question_iter = None
        with open("Templates/bibtemplate.bib") as fp:
            _textemplate += fp.read()

        _bibliography = _parse_bibliography.parse_data(_textemplate)
        for _bib in _bibliography:
            _bib.set_modified(True)
            self.bibliography_drafts.add(_bib)

            _new_question_iter = self.bibliography_list.append(['<i>*%s</i>' % _bib.get_bibliography_id(),
                                                                _bib.get_bibliography_id()])

        _bib_id_path = self.bibliography_list.get_path(_new_question_iter)
        _selector.select_path(_bib_id_path)

        self.bibliography_id_viewer.scroll_to_cell(_bib_id_path)
        self.bibliography_id_viewer.row_activated(_bib_id_path,
                                                  self.bibliography_id_viewer.get_column(0))
        return

    def is_bibliography_in_draft(self, bibliography_id):
        for _b in self.bibliography_drafts:
            if _b.get_bibliography_id() == bibliography_id[0]:
                return True
        return False

    def save_bibliography_to_db(self):
        self.save_bibliography_as_draft()
        if self.bibliography_drafts is None:
            return False
        else:
            for _bibliography in self.bibliography_drafts:
                if _bibliography.get_modified():
                    _bibliography.set_connector(self.dbQuery.get_connector())
                    if _bibliography.get_in_database():  # Question has been modified.
                        _bibliography.update_database()
                    else:  # New question.
                        _bibliography.insert_into_database()

                    _bibliography.set_modified(False)
                    _bid = _bibliography.get_bibliography_id()
                    _path = self.get_liststore_path(self.bibliography_list, _bid)
                    self.bibliography_list[_path] = [_bid, _bid]

    def get_bibliography(self):
        """
        This method is run when Bibliographywindow is opened.
        Populate the liststore bibliographylist with the available bibliography.
        """
        if self.ExamDB:
            # Cleanup
            self.bibliography_list.clear()  # Resets the liststore

            # Load questions from DB.
            _bibliography_id = self.ExamDB.get_bibliography()

            if _bibliography_id is not None:
                for _bid in _bibliography_id:
                    # Check if question in draft to avoid double loading
                    if not self.is_bibliography_in_draft(_bid):
                        if self.ExamDB.bibliography_already_used(_bid[0]):
                            self.bibliography_list.append(
                                ['<b>%s</b>' % _bid[0], _bid[0]])
                        else:
                            self.bibliography_list.append([_bid[0], _bid[0]])
            # Load drafts.
            if not self.bibliography_drafts:
                return
            else:
                for _bib in self.bibliography_drafts:
                    self.bibliography_list.append(['<i>%s</i>'
                                                   % _bib.get_bibliography_id(),
                                                   _bib.get_bibliography_id()])

    def import_bibliography_from_file(self, _file):
        _bib_parser = BibParser()
        _pattern = "*.bib"
        if fnmatch(os.path.basename(_file), _pattern):
            _bibliography_list = _bib_parser.load_bibtex_from_file(_file)
            if _bibliography_list:
                for _bib in _bibliography_list:
                    if not self.ExamDB.bibliography_exist(_bib.get_bibliography_id()):
                        _bib.set_connector(self.dbQuery.get_connector())
                        _bib.insert_into_database()
                    else:
                        print("Bibliography %s is already in database" % (_bib.get_bibliography_id(),))
        self.get_bibliography()
        return

    def close_exam_window(self):
        self.load_exam_window.hide()

    def open_select_file_dia(self, parent_name):
        if parent_name == 'bibliographyeditorwin':
            _parent = self.bibliography_editor_window
        else:
            _parent = None

        fcd = Gtk.FileChooserDialog(title=None,
                                    parent=_parent,
                                    action=Gtk.FileChooserAction.OPEN)
        fcd.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        fcd.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        self.response = fcd.run()

        if self.response == Gtk.ResponseType.OK:
            self.select_bibliography(fcd.get_filename())

        fcd.destroy()

    def select_bibliography(self, path):
        self.import_bibliography_from_file(path)
        self.get_bibliography()

    def open_bibliography_editor(self):
        self.get_bibliography()
        _model = self.bibliography_id_viewer.get_model()
        _first_iter = _model.get_iter_first()
        if _first_iter is not None:
            self.bibliography_id_viewer.row_activated(_model.get_path(_first_iter),
                                                      self.bibliography_id_viewer.get_column(0))
        self.bibliography_editor_window.show_all()
        return

    def save_bibliography_editor(self):
        self.close_bibliography_editor()
        return

    def cancel_bibliography_editor(self):
        self.close_bibliography_editor()
        return

    def close_bibliography_editor(self):
        self.selected_bibliography_id = []
        self.bibliography_drafts = set()
        self.bibliography_editor_window.hide()
        return

    def _package_is_selected(self, __treeview, path, __column, __data=None):
        _model = self.package_list
        _package = None

        if path is not None:
            for _pack in self.package_drafts:
                if _pack.get_id() == _model[path][0]:
                    _package = _pack

        if _package:
            _iter = self._search_store(_model, _package.get_id())
            self.selected_package = [[_model, _iter], _package]

    def _package_text_edited(self, __widget, path, text, cell):
        self.package_list[path][cell] = text
        _package = None

        for _pack in self.package_drafts:
            if _pack.get_id() == self.package_list[path][0]:
                _package = _pack

        if not _package:
            _package = Package()
            _package.set_id(self.package_list[path][0])
            self.package_drafts.add(_package)

        if cell == 1:
            _package.set_package_data(text)

        if cell == 2:
            _package.set_options(text)

    def _on_package_cell_toggled(self, __widget, path):
        """
        Toggles and untoggles the button from course goal dialogue
        """
        if self.loaded_preamble_package:
            self.loaded_preamble_package[1].set_list_changed(True)

            self.package_list[path][3] = not self.package_list[path][3]
            if self.package_list[path][3]:
                self.package_used.add(self.package_list[path][0])

            else:
                for _a in self.package_used.copy():
                    if _a == self.package_list[path][0]:
                        self.package_used.remove(_a)

    def new_package(self):
        _package = Package()
        _package.set_id(self.ExamDB.gen_id("package"))

        self.package_drafts.add(_package)
        self.package_list.append([_package.get_id(), "", "", False])

    def _create_package_id_list(self):
        """
        """
        _columns = [["ID", False, True, True], ["Package", True, False, True], ["Default Options", True, False, True]]

        self.package_id_view.set_property("activate-on-single-click", True)
        self.package_id_view.connect("row-activated", self._package_is_selected)

        self.package_id_view.connect("key-release-event", self.on_list_key_press)

        self._cell_renderer_text_generator(self.package_id_view, _columns,
                                           self._package_text_edited)
        self.package_list.set_sort_func(0, self.compare, None)

        self.package_id_view.get_column(0).clicked()
        _renderer_toggle = Gtk.CellRendererToggle()

        _renderer_toggle.connect("toggled", self._on_package_cell_toggled)

        column_toggle = Gtk.TreeViewColumn(
            "Select", _renderer_toggle, active=3)

        self.package_id_view.append_column(column_toggle)

    def is_preamble_package_in_draft(self, defpackage_id):
        for _prepack in self.preamble_package_drafts:
            if _prepack.get_id() == defpackage_id:
                return True
        return False

    def _create_preamble_package_list(self):
        """
        """
        self.preamble_package_viewer.set_property("activate-on-single-click",
                                                  True)

        self.preamble_package_viewer.connect("row-activated",
                                             self.preamble_package_selected)

        self.preamble_package_viewer.connect("key-release-event",
                                             self.on_list_key_press)

        _preamble_package_renderer = Gtk.CellRendererText()

        _column_text = Gtk.TreeViewColumn("ID",
                                          _preamble_package_renderer,
                                          markup=1)

        _preamble_package_renderer.set_property("editable", 1)
        _preamble_package_renderer.connect("edited",
                                           self._preamble_package_id_edited,
                                           1)
        _preamble_package_renderer.props.wrap_width = 400
        _preamble_package_renderer.props.wrap_mode = Gtk.WrapMode.WORD
        _column_text.set_sort_column_id(1)
        self.preamble_package_viewer.append_column(_column_text)

    def _preamble_package_id_edited(self, __widget, path, text, cell):
        self.preamble_package_list[path][0] = text
        self.selected_preamble_package[1].set_id(text)
        self.preamble_package_list[path][cell] = '<i>%s</i>' % text

    def preamble_package_selected(self, __treeview, path, __column, __data=None):
        _model = self.preamble_package_list
        _preamblePackages = None

        if path is not None:
            for _prepack in self.preamble_package_drafts:
                if _prepack.get_id() == _model[path][0]:
                    _preamblePackages = _prepack

        if _preamblePackages:
            _iter = self._search_store(_model, _preamblePackages.get_id())
            self.selected_preamble_package = [[_model, _iter], _preamblePackages]

        self.load_preamble_package()

    def load_preamble_package(self):
        """
        """
        if not self.selected_preamble_package:
            return

        # Save previous preamblepackage.
        if self.loaded_preamble_package:
            self.save_preamble_package()

        self.package_used.clear()

        self.loaded_preamble_package = self.selected_preamble_package

        # Mark packages connected to selected preamblePackage
        self._toggle_packages_from_loaded_preamble_package()

    def _toggle_packages_from_loaded_preamble_package(self):
        # Reset toggles
        for item in self.package_list:
            item[3] = False

        for _package in self.loaded_preamble_package[1].get_package_list():
            for item in self.package_list:
                if item[0] == _package:
                    self.package_used.add(_package)
                    item[3] = True

    def save_preamble_package(self):
        if self.loaded_preamble_package:
            if self.loaded_preamble_package[1].get_list_changed():
                self.loaded_preamble_package[1].set_package_list(self.package_used)
                self.loaded_preamble_package[1].set_list_changed(False)
                self.loaded_preamble_package[1].set_connector(
                    self.dbQuery.get_connector())
                self.loaded_preamble_package[1].save_to_database()

        return True

    def open_package_manager(self):
        self._get_preamble_package_list()
        self.get_package_list()

        _model = self.preamble_package_viewer.get_model()
        _first_iter = _model.get_iter_first()

        if _first_iter is not None:
            self.preamble_package_viewer.row_activated(
                _model.get_path(_first_iter),
                self.preamble_package_viewer.get_column(0))

        self.package_manager_window.show_all()
        return

    def get_package_list(self):
        if not self.ExamDB:
            return

        self.package_list.clear()

        _packages = self.ExamDB.get_package_list()

        if not _packages:
            return

        for _pack in _packages:
            _package = Package()
            _package.load_from_database(*_pack)
            self.package_list.append([_package.get_id(),
                                      _package.get_package_data(),
                                      _package.get_options(),
                                      False])

            self.package_drafts.add(_package)

    def _get_preamble_package_list(self):
        if not self.ExamDB:
            return
        if not self._connected_to_database:
            return

            # Cleanup
        self.preamble_package_list.clear()  # Resets the liststore

        for _preambledraft in self.preamble_package_drafts:
            self.preamble_package_list.append([_preambledraft.get_id(),
                                               _preambledraft.get_id()])

        _preamblePackageID = self.ExamDB.get_preamble_packages()

        if _preamblePackageID is not None:
            for _id in _preamblePackageID:
                # Check if question in draft to avoid double loading
                if not self.is_preamble_package_in_draft(_id[0]):
                    _preamblePackage = PreamblePackages()
                    _preamblePackage.set_id(_id[0])
                    _preamblePackage.load_from_database(
                        self.ExamDB.load_preamble_package(_id[0]))
                    if self.ExamDB.preamble_package_already_used(_id[0]):
                        self.preamble_package_list.append(
                            [_preamblePackage.get_id(),
                             '<b>%s</b>' % _preamblePackage.get_id()
                             ])
                    else:
                        self.preamble_package_list.append([
                            _preamblePackage.get_id(),
                            _preamblePackage.get_id()])

                    self.preamble_package_drafts.add(_preamblePackage)

    def new_preamble_packages(self):
        # Reset toggles
        _pre_packages = PreamblePackages()
        _pre_packages.set_id('newPreamblePackage')
        self.preamble_package_drafts.add(_pre_packages)
        _iter = self.preamble_package_list.append(
            [_pre_packages.get_id(), "<i>%s</i>" % _pre_packages.get_id()])
        _path = self.preamble_package_list.get_path(_iter)

        _selector = self.preamble_package_viewer.get_selection()
        _selector.select_path(_path)

        self.preamble_package_viewer.scroll_to_cell(_path)
        self.preamble_package_viewer.row_activated(
            _path, self.preamble_package_viewer.get_column(0))

    def save_package_manager(self):
        if self.package_drafts:
            for _package in self.package_drafts:
                _package.set_connector(self.dbQuery.get_connector())
                if _package.get_in_database():
                    _package.update_database()
                else:
                    _package.insert_into_database()

        self.save_preamble_package()
        self.package_drafts.clear()
        self.preamble_package_drafts.clear()
        self.close_package_manager()
        return

    def cancel_package_manager(self):
        self.close_package_manager()
        return

    def close_package_manager(self):
        self.package_manager_window.hide()
        return

    def save_loaded_exam(self):
        if self.Exam.get_exam_id() is None:
            return

        self.save_exam_dialogue_info()
        self.Exam.set_connector(self.dbQuery.get_connector())
        self.Exam.save_exam()

    def save_exam_dialogue_info(self):
        self._exam_saved = True

        if self.selected_course is None:
            return

        self.Exam.set_course(self.selected_course[1])

        _instruction = Instructions()
        _docclass = None

        try:
            _instruction.load_from_database(*self.ExamDB.get_instructions(
                self.preamble["Instruction"])[0])
        except IndexError:
            print('save_exam_dialogue_info(): No instructions available')
        try:
            _docclass = DocumentClass()
            _docclass.load_from_database(*self.ExamDB.get_document_class(
                self.preamble["Document_Class"])[0])
        except IndexError:
            print('save_exam_dialogue_info(): No document classes available')
        try:
            self.Exam.set_preamble([
                ['Instruction', _instruction],
                ['Document_Class', _docclass],
                ['default_package_id', self.preamble["default_package_id"]]
            ])

            self.Exam.set_exam_type(self.profile_type_of_exam_entry.get_text())
            self.Exam.set_exam_date(datetime.strptime(self.exam_date_entry.get_text(), '%Y-%m-%d'))
            self.Exam.set_language(self.profile_language_entry.get_text())
            self.Exam.set_time_limit(self.profile_exam_time_entry.get_text())

            # Add authors to Exam based on text entry
            self.Exam.set_authors([])
            _authors_list = self.profile_author_entry.get_text().split()
            for _a in _authors_list:
                _author = Author()
                _author.load_from_database(*self.ExamDB.get_author(_a)[0])
                self.Exam.append_authors(_author)

            _coursegoal_list = self.profile_course_goals_entry.get_text().split()
            self.Exam.set_ilo()
            for _cg in _coursegoal_list:
                self.Exam.append_ilo((_cg, self.ExamDB.get_ilo_by_id(_cg)[0][3]))

            _profile_exam_aids_start_iter = self.profile_exam_aids.get_start_iter()
            _profile_exam_aids_end_iter = self.profile_exam_aids.get_end_iter()

            self.Exam.set_exam_aids(self.profile_exam_aids.get_text(_profile_exam_aids_start_iter,
                                                                    _profile_exam_aids_end_iter,
                                                                    True))
            self.Exam.set_number_of_questions(
                self.profile_number_of_questions_entry.get_text()
            )

            self.save_gradelimits_to_exam()
            self.get_preamble_packages()

        except ValueError as err:
            print('save_exam_dialogue_info(): %s' % err)
            return

    def create_exam(self):
        """
        Create exam using selected questions
        :return:
        """
        self.generate()

    def generate_new_exam(self):
        """
        Generate a new exam, clearing existing questions first.
        :return:
        """
        self.Exam.clear_questions()
        self.generate()

    def generate(self):
        """
        Calls method _saveExamDialogueInfo to save the user input and send this
        to ExamDB object ExamDB to generate an exam based on input. The exam is not
        save at this stage, it only prints it into the textviewer.
        """
        # Clear old exam settings
        self.Exam.set_declaration_requirements(set([]))
        self.Exam.set_package_requirements([])
        self.Exam.set_authors([])
        self.Exam.set_total_points(0)

        # Instantiate parser
        _parseQuestion = LatexParser(self.dbQuery.get_connector(), self.Settings)
        _parseQuestion.set_examdb(self.ExamDB)

        # Get new Exam settings
        self.save_exam_dialogue_info()

        # Check if an exam is loaded or not.
        if self.Exam.get_course() is None:
            return

        self.Exam.set_file_path('bibtex_path', '')

        _decl = set()
        _bibIDs = set()

        _existing_question_id = self.Exam.get_question_ids()
        self.Exam.clear_questions()

        # Get questions
        _Generate_Questions_By_Goal = GenerateQuestionsByGoal(
            self.ExamDB,
            self.Exam.get_number_of_questions(),
            self.Exam.get_ilo(),
            self.Exam.get_course_code(),
            self.Exam.get_course_version(),
            self.Exam.get_exam_date(),
            self.allow_same_tags.get_active(),
            _existing_question_id
        )
        _temp_question_list = []

        for _question in _Generate_Questions_By_Goal.get_questions():
            if _question.get_declaration_requirement():
                for _d in _question.get_declaration_requirement():
                    _decl.add(_d[0])

            if _question.get_bibliography_requirement():
                for _bib in _question.get_bibliography_requirement():
                    _bibIDs.add(_bib['bibliography'])

            if _question.get_package_requirement():
                for _pack_req in _question.get_package_requirement():
                    _package_exist = False
                    for _p in self.Exam.get_package_requirements():
                        # If package already exist in Exam, add options
                        if _p.get_id() == _pack_req[0]:
                            _package_exist = True
                            # Split options to be able to compare each option
                            _exam_package_options = _p.get_options().split(',')
                            _question_package_options = _pack_req[1].split(',')
                            if _pack_req[1]:
                                for _q_pack_opt in _question_package_options:
                                    _option_exist = False
                                    for _e_pack_opt in _exam_package_options:
                                        if _q_pack_opt == _e_pack_opt:
                                            _option_exist = True

                                    # New option, add to existing package.
                                    if not _option_exist:
                                        _p.append_options(_q_pack_opt)

                    if not _package_exist:  # If package don't exist, add it to the Exam.
                        _package = Package()
                        _package.load_from_database(*self.ExamDB.get_package_list(_pack_req[0])[0])
                        _package.set_options(_pack_req[1])
                        self.Exam.append_package_requirements(_package)

            _temp_question_list.append(_question)

        # Add questions sorted by ILO.
        for q in sorted(_temp_question_list, key=lambda question: question._ilo):
            self.Exam.append_questions(q)

        del _temp_question_list

        # Check for declarations
        for _d in _decl:
            _declaration = Declaration()
            _declaration.load_from_database(*self.ExamDB.get_declarations(_d)[0])
            self.Exam.append_declaration_requirements(_declaration)

        # Parse exam aids for potential bibliography ids.
        if self.Exam.get_exam_aids():
            _bibliography = _parseQuestion.append_citation(self.Exam.get_exam_aids())
            if _bibliography:
                for _bib in _bibliography:
                    _bibIDs.add(_bib['bibliography'])

        # Check for _bibliography
        for _bib in _bibIDs:
            if _bib:
                _bibliography = Bibliography()
                _bibliography.load_from_database(
                    *self.ExamDB.get_bibliography(_bib)[0])
                self.Exam.append_bibliography_requirements(_bibliography)

        self.print_out_exam()

    def print_out_exam(self):
        self.buffer_latex.set_text('')
        try:
            self.buffer_latex.set_text(self.Exam.get_exam_code())

            _exam_stat = GenerateExamStatistics(self.ExamDB, self.Settings, [self.Exam])

            self.exam_summary_buffer.set_text('')

            for _stat in _exam_stat.exam_analysis():
                _end_iter = self.exam_summary_buffer.get_end_iter()
                self.exam_summary_buffer.insert(_end_iter, _stat[1])

        except TypeError as err:
            print('print_out_exam(): %s' % err)

        self.exam_viewer.activate()

    def open_save_dia(self, parent_name):
        """
        Opens the save file dialogue to get the path to where to save the exam.
        """
        if self.Exam.course is None:
            return

        if parent_name == 'MainWindow':
            _parent = self.window
        else:
            _parent = None

        fcd = Gtk.FileChooserDialog(title=None,
                                    parent=_parent,
                                    action=Gtk.FileChooserAction.SAVE)

        fcd.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        fcd.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

        fcd.set_current_name(
            '%s_%s.tex' %
            (self.Exam.course.get_course_code(),
             datetime.strftime(self.Exam.get_exam_date(),
                               '%Y%m%d')
             )
        )

        self.response = fcd.run()

        if self.response == Gtk.ResponseType.OK:
            self.save_file(fcd.get_filename())

        fcd.destroy()

    def save_file(self, _savefile):
        # Retrieves the path selected from the _savefile dialoge and calls the
        # methods save exam and write exam. Note that this method DO NOT take
        # into considerations any modifications made to the exam in the
        # textviewer.
        # Until this have been fixed, textviewer is not editable.

        _dirpath = os.path.dirname(_savefile)
        _bibfilename = os.path.basename(_savefile)
        _bibfilename = re.sub(r'.tex', r'.bib', _bibfilename)
        _absbibfilename = os.path.join(_dirpath, _bibfilename)
        _bibtexfilecontent = ''

        if not self.Exam.get_exam_id():  # If this is a new exam, generate ID, otherwise keep old.
            self.Exam.set_exam_id(
                self.ExamDB.gen_id(
                    'exam', self.Exam.course.get_course_code(), re.sub(
                        '\.', '', str(
                            self.Exam.course.get_course_version()))))

        self.Exam.save_exam()

        self.Exam.set_file_path('bibtex_path', _absbibfilename)

        _examcode = self.Exam.get_exam_code()

        if self.Exam.get_bibliography_requirements():
            for _bib in self.Exam.get_bibliography_requirements():
                _bibtexfilecontent = (_bibtexfilecontent +
                                      _bib.get_bibliography_data()
                                      )

        with io.open(_savefile, 'w+', encoding='utf8') as _texfile:
            _texfile.write(_examcode)

        with io.open(_absbibfilename, 'w+', encoding='utf8') as _bibfile:
            _bibfile.write(_bibtexfilecontent)

        return

    def close_savedia(self):
        self.save_dialogue.hide()

    def get_exam(self, exam_id):
        """
        Get an exam object based on exam id
        :param exam_id: The exam that we want
        :return: An exam object from ExamClass
        """
        if not self.ExamDB.exam_exist(exam_id):
            return

        exam = Exam()

        _declarations = set()
        _bibliography_id_list = set()

        # Load Exam meta data
        exam.load_exam_info_from_database(*self.ExamDB.get_exam_info_by_id(exam_id))

        # Grab course, and add to Exam
        course_code, course_version = self.ExamDB.get_course_information_by_exam(exam_id)

        _course = Course()
        _course.load_from_database(*self.ExamDB.retrieve_courses(course_code, course_version)[0])
        exam.set_course(_course)

        # Set Preamble
        _instruction_id, _document_class_id, default_package_id = self.ExamDB.get_exam_preamble_info(exam_id)
        _instruction = Instructions()
        _instruction.load_from_database(*self.ExamDB.get_instructions(_instruction_id)[0])

        _document_class = DocumentClass()
        _document_class.load_from_database(*self.ExamDB.get_document_class(_document_class_id)[0])

        exam.set_preamble([["Instruction", _instruction],
                           ["Document_Class", _document_class],
                           ["default_package_id", default_package_id]])

        # Load the questions.
        exam_question_id_list = self.ExamDB.get_exam_question_ids(exam_id)

        for _question_id in exam_question_id_list:
            _question = Question()
            _question.load_from_database(*self.ExamDB.get_questions_by_id(_question_id))
            if _question.get_declaration_requirement():
                for _declaration in _question.get_declaration_requirement():
                    _declarations.add(_declaration[0])

            if _question.get_bibliography_requirement():
                for _bibliography in _question.get_bibliography_requirement():
                    _bibliography_id_list.add(_bibliography['bibliography'])

            exam.append_questions(_question)

            for _ilo in _question.get_ilo()[2]:
                exam.append_ilo((_ilo, self.ExamDB.get_ilo_by_id(_ilo)[0][3]))

        # Load authors
        for _exam_author in self.ExamDB.get_exam_authors(exam_id):
            _author = Author()
            _author.load_from_database(*self.ExamDB.get_author(_exam_author)[0])
            exam.append_authors(_author)

        # Check for declarations
        for _declaration_id in _declarations:
            _declaration = Declaration()
            _declaration.load_from_database(*self.ExamDB.get_declarations(_declaration_id)[0])
            exam.append_declaration_requirements(_declaration)

        # Check for _bibliography
        for _bibliography_id in _bibliography_id_list:
            _bibliography = Bibliography()
            _bibliography.load_from_database(
                *self.ExamDB.get_bibliography(_bibliography_id)[0])
            exam.append_bibliography_requirements(_bibliography)

        return exam

    def load_exam(self):

        if not self.exam_to_load:
            return

        self.Exam = self.get_exam(self.exam_to_load)

        self.selected_course = [[None, None], self.Exam.get_course()]

        self._course_code_used = self.Exam.get_course().get_course_code()
        self._course_version_used = self.Exam.get_course().get_course_version()

        self.course_code_label.set_text(self.Exam.get_course().get_course_code())

        self.loaded_profile = Profile(self.Exam.get_course().get_course_code(),
                                      self.Exam.get_course().get_course_version())

        # Set global preamble variables.
        self.preamble["Instruction"] = self.Exam.get_preamble('Instruction')
        self.preamble["Document_Class"] = self.Exam.get_preamble('Document_Class')
        self.preamble["default_package_id"] = self.Exam.get_preamble('default_package_id')

        self.loaded_profile.load_from_database(self.preamble["Instruction"].get_instruction_id(),
                                               self.preamble["Document_Class"].get_document_class_id(),
                                               self.preamble["default_package_id"],
                                               self.Exam.get_author_ids(),
                                               self.Exam.get_ilo_ids_string(),
                                               self.Exam.get_exam_aids(),
                                               self.Exam.get_exam_type(),
                                               self.Exam.get_time_limit(),
                                               self.Exam.get_language(),
                                               self.Exam.get_number_of_questions(),
                                               self.Exam.get_exam_date().strftime('%Y-%m-%d'),
                                               self.Exam.get_grade_limits(),
                                               self.Exam.get_grade_comment(),
                                               False)

        self.load_profile()

        # Generate packages
        self.get_preamble_packages()
        self.set_gradelimits_from_exam()
        self._exam_saved = True

        # Load course information
        self._get_ilo()

        self.buffer_latex.set_text(self.Exam.get_exam_code())

        _exam_stat = GenerateExamStatistics(self.ExamDB, self.Settings, [self.Exam])

        self.exam_summary_buffer.set_text('')
        for _stat in _exam_stat.exam_analysis():
            _end_iter = self.exam_summary_buffer.get_end_iter()
            self.exam_summary_buffer.insert(_end_iter, _stat[1])

        self.close_exam_window()

        return True

    def get_students_from_exam(self, exam_id=None):
        """
        Generator method. Retrieves all student exam grades from a specific examID.
        :param exam_id: The Exam to get the grades from
        :return: StudentExamGrade objects
        """
        if not exam_id:
            exam_id = self.Exam.get_exam_id()

        student_list = self.ExamDB.get_students_for_exam(exam_id)

        if not student_list:
            return False

        # Create a StudentExamGrade object for each student, and populate it with the result.
        for _s in student_list:
            _student_exam_result = StudentExamGrade(student_id=_s[0],
                                                    exam_id=self.Exam.get_exam_id()
                                                    )
            for _r in self.ExamDB.get_student_result_from_exam(self.Exam.get_exam_id(), _s[0]):
                _student_exam_result.append_question_grade(*_r)

            _student_exam_result.calculate_result(self.Exam.get_grade_limits())

            yield _student_exam_result

    def generate_exam_result_template(self):
        """
        Generating a spreadsheet for inserting or updating the student result.
        If results are already existing, generate a filled in grading template, otherwise, generate an empty one.
        :return:
        """
        if not self.Exam:
            return None
        _messagedia = MessageDialogWindow()

        _template = ExamResultTemplate(self.dbQuery.get_connector(), self.Settings,
                                       self.Exam.get_exam_id(), self.Exam.get_exam_date(),
                                       self.Exam.get_course_code())
        _template.set_question_ids(self.Exam.get_question_ids())

        for _student in self.get_students_from_exam(self.Exam.get_exam_id()):
            _template.append_student(_student)

        _path = _template.generate_template()
        _response = _messagedia.open_dialogue('Grading Template', 'Grading template successfully created, Open?')

        if _response == Gtk.ResponseType.YES:
            _calc_program = subprocess.Popen(['localc', _path])
            _pid = _calc_program.pid

            if _messagedia.confirmation_dialogue("Import grades", "Would you like to import the grades?"):
                if self.import_exam_results_to_db(_path):
                    _messagedia.information_dialogue(
                        'Successfully imported grades for exam %s.' %
                        self.Exam.get_exam_id(), '')
            return
        else:
            return

    def import_exam_results_diag(self):
        """
        Imports a spreadsheet to the database. If results are already existing, it will update to latest version.
        :return:
        """
        _messagedia = MessageDialogWindow()

        fcd = Gtk.FileChooserDialog(title=None,
                                    parent=None,
                                    action=Gtk.FileChooserAction.OPEN)

        fcd.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        fcd.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        self.response = fcd.run()

        if self.response == Gtk.ResponseType.OK:
            if self.import_exam_results_to_db(fcd.get_filename()):
                _messagedia.information_dialogue(
                    'Successfully imported grades for exam %s.' %
                    self.Exam.get_exam_id(), '')
        fcd.destroy()

    def import_exam_results_to_db(self, filepath):
        _exam_parser = ExamResultParser(self.dbQuery.get_connector(),
                                        self.Settings,
                                        self.ExamDB
                                        )

        if _exam_parser.load_result(filepath):
            return True

        return False

    def generate_display_grading_reports(self):
        """
        Method used for generating reports. Called from GUI.
        :return:
        """

        # Base filepath for where to store HTML
        _file_path = self.Settings.get_program_path() + '/' + 'Courses/' + \
                     self.Exam.get_course_code() + '/ExamResults/HTML/' + self.Exam.get_exam_id() + "/"

        _students = []

        # Get list of distinct students from loaded exam, returned as StudentExamGrade-objects
        for _s in self.get_students_from_exam(self.Exam.get_exam_id()):
            _students.append(_s)

        _exam_stat = GenerateExamStatistics(self.ExamDB, self.Settings, [self.Exam])

        # Generate necessary data for later presenting in HTML-format
        if len(_students) > 0:

            exam_data_path = _exam_stat.write_exam_summary(_file_path, _students)

            html_template = HTMLTemplate(self.ExamDB, self.dbQuery, _file_path,
                                         self.Exam.get_exam_id(),
                                         self.Exam.get_course().get_course_name_eng(),
                                         self.Exam.get_course_code(),
                                         datetime.strftime(self.Exam.get_exam_date(), '%Y%m%d'),
                                         exam_data_path,
                                         _students
                                         )

            generate_student_json = JSON_gen(self.ExamDB,
                                             self.dbQuery,
                                             _file_path,
                                             self.Exam.get_exam_id(),
                                             datetime.strftime(self.Exam.get_exam_date(), '%Y%m%d'),
                                             _students)

            generate_student_json.gen_json()

            path_to_exam_result_html = "file://" + html_template.generate_html()


            webbrowser.open_new(path_to_exam_result_html)

            _messagedia = MessageDialogWindow()
            _response = _messagedia.confirmation_dialogue('Anonymize student id in DB?', 'Feedback reports are now generated, '
                                                                           'do you want to anonymize the student-id?')

            if _response:
                self.remove_student_link_from_results(self.Exam.get_exam_id())

            return

    def remove_student_link_from_results(self, exam_id):
        student_list = self.ExamDB.get_students_for_exam(exam_id)

        if not student_list:
            return False

        _counter = 0
        random.shuffle(student_list)
        for _s in student_list:
            _new_student_id = "student"+_counter
            self.ExamDB.update_student_id_from_exam_result(exam_id, _counter, _s[0], _new_student_id)
            _counter += 1

        return

def main():
    # noinspection PyUnusedLocal
    _gui = Gui()


if __name__ == '__main__':
    main()
