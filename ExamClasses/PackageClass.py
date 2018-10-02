# -*- coding: utf-8 -*-
class Package:
    def __init__(self):
        self.package_id = None
        self.id_package_modified = False

        self.package = None
        self.package__modified = False

        self.options = None
        self.options_modified = False

        self.in_database = False
        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx
        return

    def load_from_database(self, package_id, package, options):
        self.package_id = package_id

        self.package = package

        self.options = options

        self.in_database = True

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def get_id(self):
        return self.package_id

    def set_id(self, id_package):
        self.package_id = id_package
        self.id_package_modified = True
        return True

    def get_package_data(self):
        return self.package

    def set_package_data(self, package_data):
        self.package = package_data
        self.package__modified = True
        return True

    def get_options(self):
        return self.options

    def set_options(self, options):
        self.options = options
        self.options_modified = True
        return True

    def append_options(self, options):
        self.options = self.options + ',' + options

    def gen_package_code(self):
        if self.options is None or self.options == 'None':
            options = ''
        else:
            options = self.options
        return '\\usepackage[%s]{%s}\n' % (options, self.package)

    def insert_into_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("INSERT INTO Packages "
                       "(`package_id`, `package`, `options`) "
                       "VALUES (?, ?, ?)"
                       , (self.package_id, self.package, self.options))
        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        if self.package__modified:
            cursor.execute("UPDATE Packages "
                           "SET package = ? "
                           "WHERE package_id = ? ",
                           (self.package, self.package_id)
                           )
        if self.options_modified:
            cursor.execute("UPDATE Packages\
                            SET options = ?\
                            WHERE package_id = ?",
                           (self.options, self.package_id)
                           )
        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("DELETE FROM Packages\
                        WHERE package_id = ?",
                       (self.package_id,)
                       )

        self.cnx.commit()
        cursor.close()
        return
