#!/usr/bin/env python
# coding:utf-8
# noinspection PyUnresolvedReferences
from gi.repository import Gtk

__author__ = "Lennart Franked"
__email__ = "lennart.franked@miun.se"
__version__ = "0.5"

"""
"""


# noinspection PyUnusedLocal
class Handler:
    def __init__(self, gui):
        self.gui = gui

    def notinsameexamwin_delete_event_cb(self, *args):
        self.gui.close_not_in_same_exam_window()
        return True

    def savenisebtn_clicked_cb(self, button):
        self.gui.save_not_in_same_exam_selection()
        return True

    def cancelnisebtn_clicked_cb(self, button):
        self.gui.close_not_in_same_exam_window()
        return True

    def addnisebtn_clicked_cb(self, button):
        self.gui.add_new_not_in_same_exam()
        return True

    def notinsameexambtn_clicked_cb(self, button):
        self.gui.open_not_in_same_exam_window()
        return True

    @staticmethod
    def onDeleteWindow(*args):
        Gtk.main_quit(*args)
        return True

    def opensavedialog(self, button):
        self.gui.open_save_dia('MainWindow')
        return True

    def reveal(self, button):
        self.gui.reveal()
        return True

    def revealProfile(self, button):
        self.gui.reveal_profile()
        return True

    def newexam_clicked_cb(self, button):
        self.gui.new_exam()
        return True

    def settings_btn_activate_cb(self, button):
        self.gui.open_settings_window()
        return True

    def settings_close_btn_clicked_cb(self, button):
        self.gui.close_settings_window()
        return True

    def on_settings_save_btn_clicked(self, button):
        self.gui.save_settings()
        return True

    def settings_delete_event_cb(self, *args):
        self.gui.close_settings_window()
        return True

    def profileComboBox_changed_cb(self, *args):
        self.gui.profile_combo_changed()

    def saveprofile_clicked_cb(self, button):
        self.gui.save_profile()
        return True

    def close_clicked_cb(self, button):
        self.onDeleteWindow()
        return True

    def addcourse_clicked_cb(self, button):
        self.gui.add_new_course_entry()
        return True

    def selectcourse_delete_event_cb(self, *args):
        self.gui.close_course_selection()
        return True

    def course_code_popover_clicked_cb(self, *args):
        self.gui.open_course_selection()
        return True

    def cancelcoursebtn_clicked_cb(self, button):
        self.gui.cancel_course_selection()
        return True

    def savecoursebtn_clicked_cb(self, button):
        self.gui.save_course_selection()
        return True

    def adddocclass_clicked_cb(self, button):
        self.gui.add_new_docclass()
        return True

    def docclassentry_icon_press_cb(self, *args):
        self.gui.open_docclass_selection()
        return True

    def savedocclassbtn_clicked_cb(self, *args):
        self.gui.save_docclass_selection()
        return True

    def canceldocclassbtn_clicked_cb(self, *args):
        self.gui.cancel_docclass_selection()
        return True

    def selectdocclass_delete_event_cb(self, *args):
        self.gui.close_docclass_selection()
        return True

    def addcoursegoal_clicked_cb(self, button):
        self.gui.add_new_ilo()
        return True

    def selectcoursegoal_delete_event_cb(self, *args):
        self.gui.close_coursegoal_selection()
        return True

    def cancelILObtn_clicked_cb(self, *args):
        self.gui.cancel_coursegoal_selection()
        return True

    def saveILObtn_clicked_cb(self, button):
        self.gui.save_coursegoal_selection()
        return True

    def addauthor_clicked_cb(self, button):
        self.gui.add_new_author()

    def selectauthors_delete_event_cb(self, *args):
        self.gui.close_authors_selection()
        return True

    def cancelauthorsbtn_clicked_cb(self, button):
        self.gui.cancel_authors_selection()
        return True

    def saveauthorsbtn_clicked_cb(self, button):
        self.gui.close_authors_selection()
        return True

    def save_exam_btn_clicked_cb(self, button):
        self.gui.save_loaded_exam()
        return

    def menu_button_cal_popover_clicked_cb(self, *args):
        self.gui.open_calendar()
        return True

    def calendar_day_selected_double_click_cb(self, *args):
        self.gui.choose_date()
        return True

    def calendar_delete_event_cb(self, *args):
        self.gui.close_calendar()
        return True

    def generate_clicked_cb(self, button):
        self.gui.generate_new_exam()
        return True

    def create_exam_btn_clicked_cb(self, button):
        self.gui.create_exam()
        return True

    def addinstructions_clicked_cb(self, button):
        self.gui.add_new_instruction()
        return True

    def instructionEntry_icon_press_cb(self, *args):
        self.gui.open_instruction_selection()
        return True

    def saveinstructionbtn_clicked_cb(self, *args):
        self.gui.save_instruction_selection()
        return True

    def cancelinstructionbtn_clicked_cb(self, *args):
        self.gui.cancel_instruction_selection()
        return True

    def selectinstructions_delete_event_cb(self, *args):
        self.gui.close_instruction_selection()
        return True

    def qwsavebtn_clicked_cb(self, button):
        self.gui.save_question_as_draft()
        self.gui.save_question_to_db()

    def glpfactive(self, *args):
        self.gui.gl_pf_switch()
        return True

    def on_glpercentswitch_notify(self, *args):
        self.gui.gl_percent_switch()

    def percentlabel_notify_cb(self, *args):
        self.gui.gl_percent_switch()

    def ilo_based_grading_switch_notify_cb(self, *args):
        self.gui.ilo_based_grading()

    def qwokbtn_clicked_cb(self, button):
        self.gui.close_add_question_window()
        return True

    def on_questionviewer_key_release_event(self, widget, event):
        self.gui.save_question(widget, event)
        return True

    def on_recommended_reading_viewer_key_release_event(self, widget, event):
        self.gui.save_question(widget, event)
        return True

    def manage_questions_btn_clicked_cb(self, button):
        self.gui.open_add_question_window()
        return True

    def manage_questions_window_delete_event_cb(self, *args):
        self.gui.close_add_question_window()
        return True

    def qwcpybtn_clicked_cb(self, button):
        self.gui.copy_question()
        return True

    def qwcancel_clicked_cb(self, button):
        self.gui.close_add_question_window()
        return True

    def on_question_filter_entry_search_changed(self, data):
        self.gui.question_id_filter(data.get_text())
        return True

    def newquestion_clicked_cb(self, button):
        self.gui.new_question()
        return True

    def showdeclarations_delete_event_cb(self, *args):
        self.gui.close_declaration_window()
        return True

    def showdeclarationbtn_clicked_cb(self, button):
        self.gui.open_declaration_window()
        return True

    def savedeclarebtn_clicked_cb(self, button):
        self.gui.save_declaration_selection()
        return True

    def adddeclare_clicked_cb(self, button):
        self.gui.new_declaration()
        return True

    def canceldeclarebtn_clicked_cb(self, button):
        self.gui.cancel_declaration_selection()
        return True

    def on_question_package_req_btn_clicked(self, *args):
        self.gui.open_question_package_requirement_window()
        return True

    def on_save_question_requirement_btn_clicked(self, *args):
        self.gui.save_question_package_requirement()
        return True

    def on_cancel_question_requirement_btn_clicked_cb(self, *args):
        self.gui.close_question_requirement_window()
        return True

    def on_add_question_requirement_btn_clicked(self, *args):
        self.gui.add_new_question_package_requirement()
        return

    def showquestionrequirement_delete_event_cb(self, *args):
        self.gui.close_question_requirement_window()
        return True

    def on_import_questions_btn_clicked(self, button):
        self.gui.open_select_question_folder('add_question_window')
        return True

    def on_export_questions_btn_clicked(self, button):
        self.gui.export_questions()
        return True

    def on_generate_template_btn_clicked(self, button):
        self.gui.generate_exam_result_template()
        return True

    def on_import_exam_results_clicked(self, button):
        self.gui.import_exam_results_diag()
        return True

    def questionlangentry_changed_cb(self, *args):
        self.gui.question_language_entry_modified()
        return True

    def on_force_edit_clicked(self, button):
        self.gui.force_edit_question()
        return True

    def usablecheck_toggled_cb(self, *args):
        self.gui.question_usable_entry_modified()
        return True

    def add_question_to_exam_btn_clicked_cb(self, *args):
        self.gui.add_question_to_exam()
        # Add a question to exam list
        return True

    def remove_question_to_exam_btn_clicked_cb(self, *args):
        # Remove a question from exam list
        self.gui.remove_question_from_exam()
        return True

    def loadexam_clicked_cb(self, *args):
        self.gui.open_exam_window()
        return True

    def loadExamWindow_delete_event_cb(self, *args):
        self.gui.close_exam_window()
        return True

    def canceloadexambtn_clicked_cb(self, button):
        self.gui.close_exam_window()
        return True

    def saveloadexambtn_clicked_cb(self, button):
        self.gui.load_exam()
        return True

    def bibliographyeditorwin_delete_event_cb(self, *args):
        self.gui.close_bibliography_editor()
        return True

    def bibeditbtn_activate_cb(self, *args):
        self.gui.open_bibliography_editor()
        return True

    def bibeditsavebtn_clicked_cb(self, button):
        self.gui.save_bibliography_editor()
        return True

    def bibeditcancelbtn_clicked_cb(self, button):
        self.gui.cancel_bibliography_editor()
        return True

    def newBib_clicked_cb(self, button):
        self.gui.new_bibliography()
        return True

    def saveeditedbib_clicked_cb(self, button):
        self.gui.save_bibliography_to_db()
        return True

    def importfilebtn_clicked_cb(self, button):
        self.gui.open_select_file_dia('bibliographyeditorwin')

    def packagebtn_activate_cb(self, *args):
        self.gui.open_package_manager()
        return True

    def packageManagerWindow_delete_event_cb(self, *args):
        self.gui.close_package_manager()
        return True

    def packagemanAddbtn_clicked_cb(self, *args):
        self.gui.new_package()
        return True

    def packagemanOkbtn_clicked_cb(self, *args):
        self.gui.save_package_manager()

    def packagemanCanceltbn_clicked_cb(self, *args):
        self.gui.cancel_package_manager()
        return True

    def addpreamblepackagebtn_clicked_cb(self, *args):
        self.gui.new_preamble_packages()
        return True

    def preamblePackageCombo_changed_cb(self, *args):
        self.gui.preamble_package_combo_changed()
        return True

    def profileAuthorEntry_icon_press_cb(self, *args):
        self.gui.open_authors_selection()

    def profileILOEntry_icon_press_cb(self, *args):
        self.gui.open_coursegoal_selection()
        return True

    def on_generate_grade_report_clicked(self, button):
        self.gui.generate_display_grading_reports()
        return True

    def create_database_btn_clicked_cb(self, button):
        self.gui.create_database()
        return True

    def on_exam_view_switcher_switch_page(self, *args):
        notebook, page, page_num = args
        self.gui.switch_page(page_num)
        return True
