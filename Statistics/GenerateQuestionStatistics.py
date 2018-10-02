import statistics


class GenerateQuestionStatistics:
    def __init__(self, question_id, question_max_point, question_data):
        self._question_id = question_id
        self._question_max_point = question_max_point
        self._question_data = question_data

    def set_question_id(self, question_id):
        self._question_id = question_id

    def get_question_id(self):
        return self._question_id

    def set_question_max_point(self, max_point):
        self._question_max_point = max_point

    def get_question_max_point(self):
        return self._question_max_point

    def set_question_data(self, question_data):
        self._question_data = question_data

    def get_question_data(self):
        return self._question_data

    def get_question_mean(self):
        if len(self._question_data) > 0:
            return round(statistics.mean(self._question_data), 2)
        return 0

    def get_question_stdev(self):
        if len(self._question_data) > 1:
            return round(statistics.stdev(self._question_data), 2)
        else:
            return 'N/A'

    def get_cardinality(self):
        return len(self._question_data)

    def get_stat_str(self):
        return str(self.get_question_mean()) + "/" + str(self.get_question_max_point()) + " \u03C3: " \
               + str(self.get_question_stdev())

    def __str__(self):
        if self.get_cardinality() > 0:
            return str(self.get_question_mean()) + "/" + str(self.get_question_max_point()) + " \u03C3: " \
                   + str(self.get_question_stdev())
