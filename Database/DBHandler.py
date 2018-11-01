# -*- coding: utf-8 -*-
import sqlite3


class DBHandler:
    def __init__(self, database_path):
        self.cnx = sqlite3.connect(database_path)

        self.cursor = self.cnx.cursor()

    def query(self, query):
        try:

            self.cursor.execute(query)
            if 'SELECT' in query:
                answer = self.cursor.fetchall()
                if answer:
                    self.cursor.close()
                    return answer
                else:
                    self.cursor.close()
                    return None
            else:
                self.cnx.commit()
                self.cursor.close()
                return

        except AttributeError as err:
            print(err)
            return

    def get_connector(self):
        return self.cnx

    def escape_input(self, _input):
        # noinspection PyUnresolvedReferences
        return self.cnx.converter.escape(_input)

    def __del__(self):
        self.cursor.close()
        self.cnx.close()
