# -*- coding: utf-8 -*-
import sqlite3
import math
import re


class StudentExamGrade:
    def __init__(self, exam_id, student_id=None):
        self._exam_id_modified = True

        self._student_id_modified = True

        self._student_order_modified = True

        self._exam_result = list()
        self._exam_result_modified = False

        self.cnx = None

        self._summary = {
            "student_id": student_id,
            "student_order": 0,
            "exam_id": exam_id,
            "Number_of_Questions": 0,
            "Maximum_points": 0,
            "Earned_points": 0,
            "Percentage": '',
            "grade": None,
            "grade_after_fx": None,
            "ilo_result": [],
            "strong_tags": [],  # more than 66%
            "passed_tags": [],  # more than 33%
            "failed_tags": [],  # No points
            "recommended_reading": [],  # Reading instructions found in solutions.
            "result":[],
        }

        self.ilo_score_weight = {"A": 6,
                                 "B": 5,
                                 "C": 4,
                                 "D": 3,
                                 "E": 2,
                                 "Fx": 1,
                                 "F": 0,
                                 }

        self._grade_limits = None

        self._PF = False
        self._ilo_based_grading = False

        return

    def calculate_result(self, grade_limits):
        """

        :param grade_limits:{"PF": False,
                             "Percent": False,
                             "ILO_based_grading": False,
                             "Fx": int,
                             "Pass": int,
                             "D": int,
                             "C": int,
                             "B": int,
                             "A": int,
                              }
        :return:
        """

        self._grade_limits = self._clean_dictionary(grade_limits)
        self._calculate_total_score()
        self._calculate_score_by_ilo()
        self._calculate_preliminary_grade()

    def set_connector(self, cnx):
        self.cnx = cnx
        return

    def set_exam_id(self, exam_id):
        self._summary["exam_id"] = exam_id
        self._exam_id_modified = True
        return

    def get_exam_id(self):
        return self._summary["exam_id"]

    def set_student_id(self, student_id):
        self._summary["student_id"] = student_id
        self._student_id_modified = True
        return

    def get_student_id(self):
        return self._summary["student_id"]

    def set_student_order(self, order):
        self._summary["student_order"] = order
        self._student_order_modified = True
        return

    def get_student_order(self):
        return self._summary["student_order"]

    def get_grade_limit(self):
        return self._grade_limits

    def set_grade_limit(self, grade_limit):
        self._grade_limits = grade_limit

    def append_question_grade(self, question_id, earned_points, teacher_comment, question_number,
                              recommended_reading=None, ilo=None, max_point=None, tags=None,
                              solution=None):

        if max_point:
            if isinstance(max_point, str):
                max_point = float(max_point)

        if earned_points:
            if isinstance(earned_points, str):
                earned_points = float(earned_points)

        _question_result = {
            "question_id": question_id,
            "earned_points": earned_points,
            "teacher_comment": teacher_comment,
            "order": question_number + 1,
            "recommended_reading": recommended_reading,
            "ILO": ilo,
            "max_point": max_point,
            "tags": tags,
            "solution": solution,
        }
        self._exam_result.append(_question_result)
        self._exam_result_modified = True

    def get_question_grade(self, question_id):
        for _q in self._exam_result:
            if _q["question_id"] == question_id:
                return _q

    def get_result(self):
        for _q in self._exam_result:
            yield _q

    def _calculate_total_score(self):
        """
        Internal method that should be run at init. This will calculate the total results
        and save it to global parameters.
        :return:
        """
        for _q in self.get_result():
            self._summary["Number_of_Questions"] += 1
            self._summary["Maximum_points"] += _q["max_point"]
            self._summary["Earned_points"] += _q["earned_points"]

            self._summary["Percentage"] = round((self._summary["Earned_points"] /
                                                 self._summary["Maximum_points"]) * 100, 0)

            try:
                _question_result = (_q["earned_points"] / _q["max_point"]) * 100
            except ZeroDivisionError as err:
                print(err)
                return

            if _question_result == 0:  # If student got zero points.
                for _tag in _q["tags"]:
                    self._summary["failed_tags"].append([_tag, _q["order"]])
                if _q["recommended_reading"]:
                    for _reading in _q["recommended_reading"]:
                        if _reading not in self._summary["recommended_reading"]:
                            self._summary["recommended_reading"].append(_reading)

            elif _question_result < 100:
                for _tag in _q["tags"]:
                    self._summary["passed_tags"].append([_tag, _q["order"]])

            elif _question_result == 100:
                for _tag in _q["tags"]:
                    self._summary["strong_tags"].append([_tag, _q["order"]])

            self._summary["result"].append(
                {
                    'order': _q["order"],
                    'earned': _q["earned_points"],
                    'max_point': _q["max_point"],
                    'generated_feedback': self.get_generated_question_feedback(_q["solution"],
                                                                               _q["earned_points"],
                                                                               _q["max_point"]
                                                                               ),
                    'teacher_comment': _q["teacher_comment"],
                }
                )

    def get_generated_question_feedback(self, solution, earned_points, max_point):
        """
        Parse the solution to see if recommended solution format is used. If used, it place the grading criteria in a
        dict, and removes the criteria already met

        :param solution: The solution part of the question
        :return: dict in form:
        {
        'point': criteria
        ...
        }
        """
        _begin_description = re.compile(r'\\begin\{description\}')
        _end_description = re.compile(r'\\end\{description\}')
        _points = re.compile(r'\\item\[(?P<point>.+?)\](?P<solution>.*)')

        _desc_used = False
        feedback = {}
        _tmp_point = 0

        for line in solution.splitlines(True):
            if _begin_description.search(line):
                _desc_used = True

            elif _end_description.search(line):
                _desc_used = False

            if _desc_used:
                p = _points.search(line)
                if p:
                    _tmp_point = p.group('point')
                    _criteria = re.findall('[0-9]+', _tmp_point)
                    if _criteria:
                        _criteria = float(re.findall('[0-9]+', _tmp_point)[0])

                        if earned_points+1 == _criteria:
                            feedback[_tmp_point] = re.sub('\s\s+', " ", p.group('solution'))

                    elif _tmp_point == 'further study':
                        if earned_points == max_point:
                            feedback[_tmp_point] = re.sub('\s\s+', " ",p.group('solution'))

                elif _tmp_point in feedback:
                    feedback[_tmp_point] += re.sub('\s\s+', " ",line)

        return feedback

    def _calculate_score_by_ilo(self):
        """
        Calculates the Maximum point, earned points and which percentage earned point is out of maximum for
        each ILO that is covered on the exam.
        Generates dictionaries in format
                [{"ILO": str,
                  "Maximum_points": int,
                  "Earned_points": int,
                  "Percentage": int,
                 }
                ]
        That will be appended to self._summary["ilo_results"]
        """
        _used_ilo = set()

        for _q in self.get_result():
            _used_ilo.add(_q["ILO"])

        for _ilo in _used_ilo:
            _score_by_ilo = {"ILO": _ilo,
                             "maximum_points": 0,
                             "earned_points": 0,
                             "percentage": 0,
                             "grade": None,
                             }
            for _q in self.get_result():
                if _q["ILO"] == _ilo:
                    _score_by_ilo["maximum_points"] += _q["max_point"]
                    _score_by_ilo["earned_points"] += _q["earned_points"]

            _score_by_ilo["percentage"] = round(
                (_score_by_ilo["earned_points"] / _score_by_ilo["maximum_points"]) * 100, 0
            )

            self._summary["ilo_result"].append(_score_by_ilo)

        # Sorting the ILO's
        self._summary["ilo_result"] = sorted(self._summary["ilo_result"], key=lambda k: int(k['ILO'][0][11:]))

    def get_summary(self):

        return self._summary

    def get_score_by_ilo(self, ilo=None):
        if not ilo:
            return self._summary["ilo_result"]

        else:
            for _i in self._summary["ilo_result"]:
                if _i["ILO"][0] == ilo:
                    return _i

    def get_number_of_ilo(self):
        """
        Get number of ILO's used
        :return: int of len(used_ilo)
        """
        _used_ilo = set()
        for _q in self.get_result():
            _used_ilo.add(_q["ILO"])

        return len(_used_ilo)

    def _calculate_preliminary_grade_pass_fail(self):
        """
        Calculate preliminary grade based on pass of fail
        :return:
        """

        # Check if total score (sum of everything) is enough for a passing grade.
        if self._summary["Percentage"] >= self._grade_limits["E"]:
            self._summary["grade"] = 'Pass'
        else:
            self._summary["grade"] = 'F'

        # Check pass or fail for each ILO.
        for _ilo in self._summary["ilo_result"]:
            if _ilo["Percentage"] >= self._grade_limits["E"]:
                _ilo["grade"] = "Pass"
            else:
                # If one ILO has been failed, set final grade to F as well.
                _ilo["grade"] = "F"
                self._summary["grade"] = "F"
        return

    def _clean_dictionary(self, grade_limit):
        """
        Clean up the dictionary, so that it can be used for setting preliminary grade.
        :param grade_limit:{"PF": False,
                             "Percent": False,
                             "ILO_based_grading": False,
                             "Fx": int,
                             "Pass": int,
                             "D": int,
                             "C": int,
                             "B": int,
                             "A": int,
                            }

        :return:{"Fx": int, # If not used, it will be removed
                 "E": int,
                 "D": int,
                 "C": int,
                 "B": int,
                 "A": int,
                  }
        """
        self._PF = grade_limit["PF"]
        self._ilo_based_grading = grade_limit["ILO_based_grading"]
        _temp_dict = grade_limit.copy()
        _temp_dict.pop("Percent")
        _temp_dict.pop("PF")
        _temp_dict.pop("ILO_based_grading")

        # Rename Pass to E for use when setting the grade.
        _temp_dict["E"] = _temp_dict.pop("Pass")

        # If not Fx is used, pop it!
        if _temp_dict["Fx"] is None or _temp_dict["Fx"] <= 0:
            _temp_dict.pop("Fx")

        return _temp_dict

    def _calculate_preliminary_grade_scale(self):

        if self._summary["Percentage"] < self._grade_limits["E"]:
            self._summary["grade"] = "F"
        else:
            # Calculate grade based on the total score.
            for _grade, _limit in sorted(self._grade_limits.items(), reverse=True):
                if self._summary["Percentage"] >= _limit:
                    self._summary["grade"] = _grade

        # Calculate grade for each ILO
        for _ilo in self._summary["ilo_result"]:
            temp_grade = ""

            # If _ilo percantage is less than limit for E, set F
            if _ilo["percentage"] < self._grade_limits["E"]:
                temp_grade = "F"

            else:
                for _grade, _limit in sorted(self._grade_limits.items(), reverse=True):
                    if _ilo["percentage"] >= _limit:
                        temp_grade = _grade

            _ilo["grade"] = temp_grade

            # If one ILO has been failed, set grade to F
            # for _ilo in self._summary["ilo_result"]:
            #    if _ilo["grade"] == 'F':
            #        self._summary["grade"] = 'F'

    def _calculate_preliminary_grade_ilo(self):
        score = 0  # Each ILO has been given a weight, score holds the mean weight
        score_if_fx_passed = 0 # Used for calculating what score student will get after successfully pass the Fx assignment
        fail_count = 0  # Count number of F, ensure that if one ILO as been failed, student can't pass the exam.

        for _ilo in self._summary["ilo_result"]:
            if _ilo["grade"] == "F":
                fail_count += 1
                score_if_fx_passed += self.ilo_score_weight["E"]
            else:
                score += self.ilo_score_weight[_ilo["grade"]]  # Add the weight based on what grade each ILO got.
                score_if_fx_passed += self.ilo_score_weight[_ilo["grade"]]

        score = math.floor(score / self.get_number_of_ilo())  # Take mean score and round down
        score_if_fx_passed = math.floor(score_if_fx_passed / self.get_number_of_ilo())

        if fail_count:
            # If number of F's is one third or less out of the total ILO's, set grade to Fx.
            if (fail_count / self.get_number_of_ilo()) <= 0.34:
                self._summary["grade"] = "Fx"
            # If number of F's is more than one third, set grade to F.
            else:
                self._summary["grade"] = "F"

        if self._summary["grade"] != "F":
            for _grade, _value in self.ilo_score_weight.items():
                if score == _value:
                    self._summary["grade"] = _grade

                if score_if_fx_passed == _value:
                    self._summary["grade_after_fx"] = _grade

    def _calculate_preliminary_grade(self):
        """
        This method should be run after total score and ilo score has been calculated.
        Based on the exam grade limits, this method will generate a preliminary grade for the student.
        :return:
        """

        if not self._grade_limits:
            return

        if self._PF:
            self._calculate_preliminary_grade_pass_fail()

        else:
            # Find grade based on scale F - A
            self._calculate_preliminary_grade_scale()

            # If grade should be set based on result from the different ILO.
            if self._ilo_based_grading:
                self._calculate_preliminary_grade_ilo()

        return

    def get_preliminary_grade(self):
        return self._summary["grade"]

    def get_passed(self):
        if self._summary["grade"] == 'F':
            return 'Fail'
        if self._summary["grade"] == 'Fx':
            return 'Fx'
        else:
            return 'Pass'

    def insert_into_database(self):
        if not self.cnx:
            return None

        if not self._exam_result_modified:
            return False

        cursor = None

        for _r in self._exam_result:
            try:
                cursor = self.cnx.cursor()
                cursor.execute("SELECT `student_id`\
                                FROM Exam_Results \
                                WHERE exam_id = ? AND \
                                      student_id = ? AND \
                                      question_id = ?", (self._summary["exam_id"],
                                                         self._summary["student_id"],
                                                         _r["question_id"])
                               )

                _result_exist = cursor.fetchall()
            except sqlite3.Error as err:
                print(err)
                return False

            if _result_exist:
                try:
                    cursor.execute("UPDATE `Exam_Results` \
                                    SET `points` = ?, `custom_feedback` = ?, `order` = ? \
                                    WHERE `exam_id` = ? AND \
                                            `question_id` = ? AND\
                                            `student_id` = ?",
                                   (_r["earned_points"], _r["teacher_comment"], self._summary["student_order"],
                                    self._summary["exam_id"], _r["question_id"], self._summary["student_id"])
                                   )
                    self.cnx.commit()

                except sqlite3.Error as err:
                    print(err)
                    return False
            else:
                try:
                    cursor.execute("INSERT INTO Exam_Results "
                                   "(`exam_id`, `question_id`, `student_id`, `order`, `points`, `custom_feedback`) "
                                   "VALUES (?, ?, ?, ?, ?, ?)",
                                   (self._summary["exam_id"], _r["question_id"],
                                    self._summary["student_id"], self._summary["student_order"],
                                    _r["earned_points"], _r["teacher_comment"])
                                   )
                    self.cnx.commit()

                except sqlite3.Error:
                    return False

        cursor.close()
        return True

    def update_database(self):
        if not self.cnx:
            return None

        if not self._exam_result_modified:
            return

        if self.remove_from_database():
            if self.insert_into_database():
                return True

        return False

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        try:
            cursor.execute("DELETE FROM Exam_Results \
                        WHERE exam_id = ? AND\
                              student_id = ?",
                           (self._summary["exam_id"], self._summary["student_id"]))
        except sqlite3.Error:
            return False

        return True
