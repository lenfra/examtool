# -*- coding: utf-8 -*-
class Graphics:
    def __init__(self):
        self._id_graphic = None
        self._uri = None
        self._optional = ''
        self._uri_modified = False

        self.cnx = None

    def set_connector(self, cnx):
        self.cnx = cnx
        return

    def set_id(self, id_graphic):
        self._id_graphic = id_graphic
        return True

    def get_id(self):
        return self._id_graphic

    def set_uri(self, uri):
        self._uri = uri
        self._uri_modified = True
        return True

    def get_uri(self):
        return self._uri

    def get_optional(self):
        return self._optional

    def set_optional(self, optional):
        self._optional = optional
        return True

    def load_from_database(self, graphics_id, uri):
        self._id_graphic = graphics_id
        self._uri = uri

    def generate_include_code(self):
        if self._uri and self._id_graphic:
            _code = "\t\\includegraphics[%s]{%s}\n" % (self._optional, self._uri)
            return _code

    def insert_into_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        cursor.execute("INSERT INTO Graphics "
                       "(`graphics_id`, `uri`) "
                       "VALUES (?, ?)",
                       (self._id_graphic, self._uri))

        self.cnx.commit()
        cursor.close()
        return

    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()
        if self._uri_modified:
            cursor.execute("UPDATE Graphics "
                           "SET uri = ? ",
                           (self._uri,))

            self.cnx.commit()

        cursor.close()
        return
