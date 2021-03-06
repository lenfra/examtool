# -*- coding: utf-8 -*-
import numpy as np


class GenerateExamStatistics:
    def __init__(self, exam_db, settings, exam_list):
        self.ExamDB = exam_db
        self.Settings = settings
        self.exam_list = exam_list
        self.exam_summary = {"P": 0,
                             "F": 0,
                             "Fx": 0,
                             "E": 0,
                             "D": 0,
                             "C": 0,
                             "B": 0,
                             "A": 0}

        self.exam_summary_diff_priv = {"P": 0,
                                       "F": 0,
                                       "Fx": 0,
                                       "E": 0,
                                       "D": 0,
                                       "C": 0,
                                       "B": 0,
                                       "A": 0}

        self.exam_tags = {"strong_tags": [],
                          "passed_tags": [],
                          "failed_tags": []
                          }
        return

    def _handle_failed_tags(self, student):
        """
        Method for saving the tags of the subjects that a student got zero points on.
        :param student: The StudentExamGrade object representing the student.
        :return:
        """
        _unique_tags = set()
        for _student_failed_tag in student.get_summary()["failed_tags"]:
            _found = False

            # If no tags exist yet, add it directly otherwise increment the existing tag by one.
            if not self.exam_tags["failed_tags"]:
                self.exam_tags["failed_tags"].append([_student_failed_tag[0],  # Tag
                                                      1,  # Count
                                                      1,  # Unique Students
                                                      [[_student_failed_tag[1], 1]]  # [Question ID, count]
                                                      ]
                                                     )
                _unique_tags.add(_student_failed_tag[0])

            else:
                for _i in range(len(self.exam_tags["failed_tags"])):
                    _searched_tag = self.exam_tags["failed_tags"][_i][0]
                    if _searched_tag == _student_failed_tag[0]:
                        _found = True

                        self.exam_tags["failed_tags"][_i][1] += 1
                        if _searched_tag not in _unique_tags:
                            self.exam_tags["failed_tags"][_i][2] += 1
                            _unique_tags.add(_searched_tag)

                        _qid_found = False
                        for _qid in range(len(self.exam_tags["failed_tags"][_i][3])):
                            if self.exam_tags["failed_tags"][_i][3][_qid][0] == _student_failed_tag[1]:
                                _qid_found = True
                                self.exam_tags["failed_tags"][_i][3][_qid][1] += 1
                        if not _qid_found:
                            self.exam_tags["failed_tags"][_i][3].append([_student_failed_tag[1], 1])

                if not _found:
                    self.exam_tags["failed_tags"].append([_student_failed_tag[0],  # Tag
                                                          1,  # Count
                                                          1,  # Unique Students
                                                          [[_student_failed_tag[1], 1]]]
                                                         # [Question ID, count]
                                                         )
                    _unique_tags.add(_searched_tag)

    def _handle_passed_tags(self, student):
        """
        Method for saving the tags of the subjects that a student passed. That is got at least a score of 0<
        :param student: The StudentExamGrade object representing the student.
        :return:
        """
        _unique_tags = set()
        for _student_passed_tag in student.get_summary()["passed_tags"]:
            _found = False

            # If no tags exist yet, add it directly
            if not self.exam_tags["passed_tags"]:
                self.exam_tags["passed_tags"].append([_student_passed_tag[0],  # Tag
                                                      1,  # Count
                                                      1,  # Unique Students
                                                      [[_student_passed_tag[1], 1]]  # [Question ID, count]
                                                      ]
                                                     )
                _unique_tags.add(_student_passed_tag[0])

            else:
                for _i in range(len(self.exam_tags["passed_tags"])):
                    _searched_tag = self.exam_tags["passed_tags"][_i][0]
                    if _searched_tag == _student_passed_tag[0]:
                        _found = True

                        self.exam_tags["passed_tags"][_i][1] += 1
                        if _searched_tag not in _unique_tags:
                            self.exam_tags["passed_tags"][_i][2] += 1
                            _unique_tags.add(_searched_tag)

                        _qid_found = False
                        for _qid in range(len(self.exam_tags["passed_tags"][_i][3])):
                            if self.exam_tags["passed_tags"][_i][3][_qid][0] == _student_passed_tag[1]:
                                _qid_found = True
                                self.exam_tags["passed_tags"][_i][3][_qid][1] += 1
                        if not _qid_found:
                            self.exam_tags["passed_tags"][_i][3].append([_student_passed_tag[1], 1])

                if not _found:
                    self.exam_tags["passed_tags"].append([_student_passed_tag[0],  # Tag
                                                          1,  # Count
                                                          1,  # Unique Students
                                                          [[_student_passed_tag[1], 1]]]
                                                         # [Question ID, count]
                                                         )
                    _unique_tags.add(_searched_tag)

    def _handle_strong_tags(self, student):
        """
        Method for saving the tags of the subjects that a student excelled. That is, got full score.
        :param student: The StudentExamGrade object representing the student.
        :return:
        """
        _unique_tags = set()
        for _student_strong_tag in student.get_summary()["strong_tags"]:
            _found = False

            # If no tags exist yet, add it directly
            if not self.exam_tags["strong_tags"]:
                self.exam_tags["strong_tags"].append([_student_strong_tag[0],  # Tag
                                                      1,  # Count
                                                      1,  # Unique Students
                                                      [[_student_strong_tag[1], 1]]  # [Question ID, count]
                                                      ]
                                                     )
                _unique_tags.add(_student_strong_tag[0])

            else:
                for _i in range(len(self.exam_tags["strong_tags"])):
                    _searched_tag = self.exam_tags["strong_tags"][_i][0]
                    if _searched_tag == _student_strong_tag[0]:
                        _found = True

                        self.exam_tags["strong_tags"][_i][1] += 1
                        if _searched_tag not in _unique_tags:
                            self.exam_tags["strong_tags"][_i][2] += 1
                            _unique_tags.add(_searched_tag)

                        _qid_found = False
                        for _qid in range(len(self.exam_tags["strong_tags"][_i][3])):
                            if self.exam_tags["strong_tags"][_i][3][_qid][0] == _student_strong_tag[1]:
                                _qid_found = True
                                self.exam_tags["strong_tags"][_i][3][_qid][1] += 1
                        if not _qid_found:
                            self.exam_tags["strong_tags"][_i][3].append([_student_strong_tag[1], 1])

                if not _found:
                    self.exam_tags["strong_tags"].append([_student_strong_tag[0],  # Tag
                                                          1,  # Count
                                                          1,  # Unique Students
                                                          [[_student_strong_tag[1], 1]]]
                                                         # [Question ID, count]
                                                         )
                    _unique_tags.add(_searched_tag)

    @staticmethod
    def sanitize(orig_data):
        """
        Takes a dictionary and adds a noise based on laplace distribution to its values.
        """

        sensitivity = 1
        epsilon = 2  # Use 2-differential privacy setting.
        priv = sensitivity / epsilon

        for key, val in orig_data.items():
            while True:
                data = int(round(np.random.laplace(0, priv))) + val
                if data >= 0:
                    orig_data[key] = data
                    break

    @staticmethod
    def convert_exam_grade_to_percentage(grades):
        count = 0

        for val in grades.values():
            count += val

        for key, val in grades.items():
            grades[key] = round((val / count) * 100, 0)

    def generate_exam_summary(self, student_list):
        """
        Calculates number of students passed and failed the exam.

        :param student_list: List of StudentExamGrade objects
        :return: Dictionaries in form {"<Grade>": <int>}
                                     , {
                                     "strong_tags": [[tag, count, #unique_students]],
                                     "passed_tags": [[tag, count, #unique_students]],
                                     "failed_tags": [[tag, count, #unique_students]]
                                     }
        """
        for student in student_list:

            # Count number of grades (A-F, P-F) by getting the pass status and
            # increment that value by one in the exam summary
            self.exam_summary[student.get_preliminary_grade()] += 1

            # If failed tags exist.
            if student.get_summary()["failed_tags"]:
                self._handle_failed_tags(student)

            # If passed tags exist.
            if student.get_summary()["passed_tags"]:
                self._handle_passed_tags(student)

            # If strong tags exist.
            if student.get_summary()["strong_tags"]:
                self._handle_strong_tags(student)

        # Sanitize the exam summary for publishing.
        self.exam_summary_diff_priv = self.exam_summary.copy()
        self.sanitize(self.exam_summary_diff_priv)

        # Show results in percentage
        self.convert_exam_grade_to_percentage(self.exam_summary)
        self.convert_exam_grade_to_percentage(self.exam_summary_diff_priv)

        # Sort lists
        self.exam_tags["failed_tags"].sort(key=lambda x: x[1], reverse=True)
        self.exam_tags["passed_tags"].sort(key=lambda x: x[1], reverse=True)
        self.exam_tags["strong_tags"].sort(key=lambda x: x[1], reverse=True)

        exam_ilo_summary = self.generate_ilo_summary(student_list)

        return self.exam_summary, \
               exam_ilo_summary, \
               self.exam_tags, \
               self.exam_summary_diff_priv

    def generate_report_for_ladok(self, student_list):
        """
        Generate a list of student-ID and what grade that student got, used for
        reporting results to Ladok.
        param: student_list: List of StudentExamGrade objects
        return: list of dictionaries in form[
                                        {student_id: <str>,
                                         grade: <str> }
                                        ]
        """
        if not student_list:
            return

        _report_summary = []
        
        for _student in student_list:
            _report_summary.append({"student_id": _student.get_student_id(),
                                   "grade": _student.get_preliminary_grade()})
        return _report_summary

    def generate_ilo_summary(self, student_list):
        """
        Calculates how it went per Intended Learning Outcome on the exam.
        :param student_list: List of StudentExamGrade objects
        :return: A list of dictionaries (one dict per ILO) in the form {"ILO": <string>,
                                                                        "SCORE": <float>,
                                                                        "TOTAL": <float>,
                                                                        "PERCENT": <float>}
        """
        if len(student_list) == 0:
            return

        _num_students = len(student_list)

        result = []
        for _exam in self.exam_list:
            for _ilo in _exam.get_ilo():
                _ilo_stat = {
                    "ILO": _ilo[0].replace(".", ""),
                    "ILO_DESC": _ilo[1],
                    "SCORE": 0.0,
                    "TOTAL": 0.0,
                    "PERCENT": 0.0
                }
                _earned = 0.0
                _total = 0.0
                for _s in student_list:
                    _earned += _s.get_score_by_ilo(_ilo[0])["earned_points"]
                    _total += _s.get_score_by_ilo(_ilo[0])["maximum_points"]

                _ilo_stat["SCORE"] = round((_earned / _num_students), 0)
                _ilo_stat["TOTAL"] = _total / _num_students
                _ilo_stat["PERCENT"] = round((_ilo_stat["SCORE"] /
                                              _ilo_stat["TOTAL"]) * 100, 0)

                result.append(_ilo_stat)
        return sorted(result, key=lambda k: k['ILO'][11:])

    def exam_analysis(self):
        # TODO: Make information parsable (just return the dict instead of text-string).

        """
        Calculates Total number of questions, what ILO's are included and what tags are included in an exam
        :return: A list in the form [['exam id', 'information']]
        """

        _return = []
        for _exam in self.exam_list:
            _exam_analysis = {
                "Number_of_questions": 0,
                "ILO": [],
                "Tags": set()
            }

            for _question in _exam.get_questions():
                _exam_analysis["Number_of_questions"] += 1
                for tag in _question.get_tags():
                    _exam_analysis["Tags"].add(tag)

                _question_ilos = _question.get_ilo()[2].copy()

                if not _exam_analysis["ILO"]:
                    for _ilo in _question_ilos:
                        _exam_analysis["ILO"].append([_ilo, 1])
                        _question_ilos.remove(_ilo)
                else:
                    for _ilo in _exam_analysis["ILO"]:
                        for question_ilo in _question_ilos:
                            if _ilo[0] == question_ilo:
                                _ilo[1] += 1
                                _question_ilos.remove(question_ilo)

                    if _question_ilos:
                        for _ilo in _question_ilos:
                            _exam_analysis["ILO"].append([_ilo, 1])
                            _question_ilos.remove(_ilo)

            _return_string = "Number of questions: %s \n" % _exam_analysis["Number_of_questions"]

            for _ilo in sorted(_exam_analysis["ILO"], key=lambda k: k[0]):
                _return_string = _return_string + _ilo[0] + ": " + str(_ilo[1]) + "\n"

            _return_string += "Tags: "
            for _tag in _exam_analysis["Tags"]:
                _return_string = _return_string + _tag + " "

            _return.append([_exam.get_exam_id(), _return_string])

        return _return
