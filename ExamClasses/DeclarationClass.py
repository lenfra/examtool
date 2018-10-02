# -*- coding: utf-8 -*-
class Declaration:
    def __init__(self):
        self.declaration_id = None
        self.declaration_id_modified = False

        self.package = None
        self.package_modified = False

        self.tags = None
        self.tags_modified = False

        self.in_database = False
        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx

    def load_from_database(self, declaration_id, declaration_data, tags):
        self.declaration_id = declaration_id
        self.declaration_id_modified = True

        self.package = declaration_data
        self.package_modified = True

        self.tags = tags
        self.tags_modified = True

        self.in_database = True

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def get_id(self):
        return self.declaration_id

    def set_id(self, declaration_id):
        self.declaration_id = declaration_id
        self.declaration_id_modified = True
        return True

    def get_declaration_data(self):
        return self.package

    def set_declaration_data(self, declaration_data):
        self.package = declaration_data
        self.package_modified = True
        return True

    def get_tags(self):
        return self.tags

    def set_tags(self, tags):
        self.tags = tags
        self.tags_modified = True
        return True

    def gen_declaration_code(self):
        return '%s\n' % self.package

    def insert_into_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("INSERT INTO Declarations \
                        (`declaration_id`, `data`, `tags`)\
                        VALUES (?, ?, ?)",
                       (self.declaration_id, self.package, self.tags))
        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        if self.package_modified:
            cursor.execute("UPDATE Declarations\
                        SET data = ?\
                      WHERE declaration_id = ?",
                           (self.package, self.declaration_id)
                           )
        if self.tags_modified:
            cursor.execute("UPDATE Declarations\
                            SET tags = ?\
                            WHERE declaration_id = ?",
                           (self.tags, self.declaration_id)
                           )

        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("DELETE FROM Declarations\
                        WHERE declaration_id = ?",
                       self.declaration_id)

        self.cnx.commit()
        cursor.close()
        return
