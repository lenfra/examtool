# -*- coding: utf-8 -*-
class DocumentClass:
    def __init__(self):
        self.document_class_id = None
        self.document_class_id_modified = False

        self.document_class = None
        self.document_class_modified = False

        self.options = None
        self.options_modified = False

        self.in_database = False
        self.cnx = None

    def set_connector(self, connector):
        self.cnx = connector

    def load_from_database(self, document_class_id, document_class, options):
        self.document_class_id = document_class_id
        self.document_class_id_modified = True

        self.document_class = document_class
        self.document_class_modified = True

        self.options = options
        self.options_modified = True

        self.in_database = True

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def get_document_class_id(self):
        return self.document_class_id

    def set_document_class_id(self, document_class_id):
        self.document_class_id = document_class_id
        self.document_class_id_modified = True
        return

    def get_document_class(self):
        return self.document_class

    def set_document_class(self, document_class):
        self.document_class = document_class
        self.document_class_modified = True
        return

    def get_options(self):
        return self.options

    def set_options(self, options):
        self.options = options
        self.options_modified = True

    def generate_docclass_code(self):
        return "\documentclass[%s]{%s}\n" % (self.options, self.document_class)

    def insert_into_database(self):
        if not self.cnx:
            return

        cursor = self.cnx.cursor()

        cursor.execute("INSERT INTO Document_Classes \
                        (`document_class_id`, `class`, `options`)\
                        VALUES ('%s', '%s', '%s')"
                       % (self.document_class_id, self.document_class, self.options))

        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return

        cursor = self.cnx.cursor()

        if self.document_class_modified:
            cursor.execute("UPDATE Document_Classes\
                            SET class='%s'\
                            WHERE document_class_id = '%s'"
                           % (self.document_class, self.document_class_id)
                           )

        if self.options_modified:
            cursor.execute("UPDATE Document_Classes\
                            SET options='%s'\
                          WHERE document_class_id = '%s'"
                           % (self.options, self.document_class_id)
                           )
        self.cnx.commit()
        cursor.close()

        return

    def remove_from_database(self):
        if not self.cnx:
            return

        cursor = self.cnx.cursor()
        cursor.execute("DELETE FROM Document_Classes\
                        WHERE document_class_id = '%s'"
                       % (self.document_class_id,))
        self.cnx.commit()
        cursor.close()
        return


class Instructions:
    def __init__(self):
        self.instruction_id = None
        self.instruction_id_modified = False

        self.language = None
        self.language_modified = False

        self.instruction_data = None
        self.instruction_data_modified = False

        self.in_database = False
        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx

    def load_from_database(self, instruction_id, language, instruction_data):

        self.instruction_id = instruction_id
        self.instruction_id_modified = True

        self.language = language
        self.language_modified = True

        self.instruction_data = instruction_data
        self.instruction_data_modified = True

        self.in_database = True

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def get_instruction_id(self):
        return self.instruction_id

    def set_instruction_id(self, instruction_id):
        self.instruction_id = instruction_id
        self.instruction_id_modified = True
        return

    def get_language(self):
        return self.language

    def set_language(self, language):
        self.language = language
        self.language_modified = True
        return

    def get_instruction_data(self):
        return self.instruction_data

    def set_instruction_data(self, instruction_data):
        self.instruction_data = instruction_data
        self.instruction_data_modified = True

    def insert_into_database(self):
        if not self.cnx:
            return
        cursor = self.cnx.cursor()

        cursor.execute("DELETE FROM Instructions\
                        WHERE instruction_id = ?",
                       (self.instruction_id,))

        self.cnx.commit()

        cursor.execute("INSERT INTO Instructions \
                        (`instruction_id`, `language`, `data`)\
                        VALUES (?, ?, ?)",
                       (self.instruction_id, self.language,
                        self.instruction_data)
                       )
        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return
        cursor = self.cnx.cursor()

        if self.language_modified:
            cursor.execute("UPDATE Instructions\
                            SET language = ?\
                            WHERE instruction_id = ?",
                           (self.language, self.instruction_id)
                           )

        if self.instruction_data_modified:
            cursor.execute("UPDATE Instructions\
                            SET data = ?\
                            WHERE instruction_id = ?",
                           (self.instruction_data, self.instruction_id)
                           )

        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return
        cursor = self.cnx.cursor()
        cursor.execute("DELETE FROM Instructions\
                        WHERE instruction_id = ?",
                       (self.instruction_id,))

        self.cnx.commit()
        cursor.close()
        return
