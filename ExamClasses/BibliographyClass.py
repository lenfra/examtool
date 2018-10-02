# -*- coding: utf-8 -*-
import json
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


class Bibliography:
    def __init__(self):
        self.bibliography_id = None
        self.bibliography_id_modified = False

        self.bibliography_data = BibDatabase
        self.bibliography_data_modified = False

        self.bibliography_tags = None
        self.bibliography_tags_modified = False

        self._editable = True
        self._modified = False
        self._in_database = False
        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx
        return

    def get_editable(self):
        return self._editable

    def set_editable(self, editable):
        self._editable = editable

    def set_in_database(self, in_database):
        self._in_database = in_database

    def get_in_database(self):
        return self._in_database

    def get_modified(self):
        return self._modified

    def set_modified(self, modified):
        self._modified = modified

    def get_bibliography_id(self):
        return self.bibliography_id

    def set_bibliography_id(self, id_bibliography):
        self.bibliography_id = id_bibliography
        self.bibliography_id_modified = True
        return

    def get_raw_bibliography_data(self):
        return self.bibliography_data

    def get_bibliography_data(self):
        writer = BibTexWriter()
        # noinspection PyProtectedMember
        entry = writer._entry_to_bibtex(self.bibliography_data)
        return entry

    def set_bibliography_data(self, bibliography_data):
        self.bibliography_data = bibliography_data
        self.bibliography_data_modified = True
        return

    def set_bibliography_tags(self, bibliography_tags):
        self.bibliography_tags = bibliography_tags
        self.bibliography_tags_modified = True

    def get_bibliography_tags(self):
        return self.bibliography_tags

    def load_from_database(self, bibliography_id, data, tags):
        self.bibliography_data = json.loads(data)
        self.bibliography_id = bibliography_id
        self.bibliography_tags = tags

    def insert_into_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute('INSERT INTO Bibliography \
                                    (bibliography_id, data, tags) \
                                    VALUES (?, ?, ?)',
                       (self.bibliography_id,
                        json.dumps(self.bibliography_data),
                        self.bibliography_tags
                        )
                       )
        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if self.bibliography_data_modified:
            cursor.execute("UPDATE Bibliography\
                                SET data = ?\
                                WHERE bibliography_id = ?",
                           (json.dumps(self.bibliography_data),
                            self.bibliography_id)
                           )
        if self.bibliography_tags_modified:
            cursor.execute("UPDATE Bibliography\
                                SET tags = ?\
                                WHERE bibliography_id = ?",
                           (self.bibliography_tags,)
                           )

        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("DELETE FROM Question_has_Bibliography_Requirement \
                            WHERE bibliography_id = ?",
                       (self.bibliography_id,))

        cursor.execute("DELETE FROM Bibliography \
                      WHERE `bibliography_id`=?",
                       (self.bibliography_id,))

        self.cnx.commit()
        cursor.close()
        return
