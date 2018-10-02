# -*- coding: utf-8 -*-
class PreamblePackages:
    def __init__(self):
        self.preamble_package_id = None
        self.package_list = set()
        self.in_database = False
        self.cnx = None
        self.list_changed = False

    def set_connector(self, cnx):
        self.cnx = cnx
        return

    def set_id(self, default_package_id):
        self.preamble_package_id = default_package_id
        return

    def set_list_changed(self, status):
        self.list_changed = status

    def get_list_changed(self):
        return self.list_changed

    def get_id(self):
        return self.preamble_package_id

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def set_package_list(self, package_list):
        if isinstance(package_list, set):
            package_list = list(package_list)

        assert (isinstance(package_list, list))
        self.package_list = package_list

    def get_package_list(self):
        return self.package_list

    def contains_package_id(self, package_id):
        if package_id in self.package_list:
            return True
        else:
            return False

    def append_package_to_list(self, package_id):
        self.package_list.add(package_id)

    def remove_package_from_list(self, package_id):
        if package_id in self.package_list:
            self.package_list.remove(package_id)
        return

    def load_from_database(self, package_list):
        for item in package_list:
            self.package_list.add(item[0])

    def save_to_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("DELETE FROM Default_Packages "
                       "WHERE default_package_id = ?"
                       , (self.preamble_package_id,))
        self.cnx.commit()

        for _package in self.package_list:
            cursor.execute("INSERT INTO Default_Packages "
                           "(`default_package_id`, `package_id`) "
                           "VALUES (?, ?)",
                           (self.preamble_package_id, _package))

        self.cnx.commit()
        cursor.close()
