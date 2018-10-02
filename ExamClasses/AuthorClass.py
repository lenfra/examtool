# -*- coding: utf-8 -*-
class Author:
    def __init__(self):
        self.cnx = None
        self.author_id = None
        self.id_author_modified = False

        self.name = None
        self.name_modified = False

        self.email = None
        self.email_modified = False

        self.phone = None
        self.phone_modified = False

        self.in_database = False

    def load_from_database(self, author, name, email, phone):
        self.author_id = author
        self.id_author_modified = True

        self.name = name
        self.name_modified = True

        self.email = email
        self.email_modified = True

        self.phone = phone
        self.phone_modified = True

        self.in_database = True

    def set_connector(self, cnx):
        self.cnx = cnx

    def get_id(self):
        return self.author_id

    def set_id_author(self, id_author):
        self.author_id = id_author
        self.id_author_modified = True
        return True

    def get_in_database(self):
        return self.in_database

    def set_in_database(self, in_database):
        self.in_database = in_database
        return

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name
        self.name_modified = True
        return True

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email
        self.email_modified = True
        return True

    def get_phone(self):
        return self.phone

    def set_phone(self, phone):
        self.phone = phone
        self.phone_modified = True
        return

    def gen_author_code(self):

        _authorTexCode = ('\t%s\\\\\n \
                 {\\small\\texttt{\\href{mailto:%s}{%s}}}\\\\\n \
                  {\\small\\textit{Phone:} %s}\n' % (self.name, self.email, self.email, self.phone))
        return _authorTexCode

    def insert_into_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("INSERT INTO Authors \
                    (author_id, name, email, phone)\
                    VALUES (?, ?, ?, ?)",
                       (self.author_id, self.name, self.email, self.phone))
        self.cnx.commit()
        cursor.close()
        return

    # noinspection PyStringFormat,PyStringFormat,PyStringFormat
    def update_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        if self.name_modified:
            cursor.execute("UPDATE Authors\
                        SET name = ?\
                      WHERE author_id = ?"
                           % (self.name, self.author_id)
                           )

        if self.email_modified:
            cursor.execute("UPDATE Authors\
                        SET email = ? \
                      WHERE author_id = ?"
                           % (self.email, self.author_id)
                           )

        if self.phone_modified:
            cursor.execute("UPDATE Authors \
                        SET phone = ? \
                        WHERE author_id = ?"
                           % (self.phone, self.author_id)
                           )

        self.cnx.commit()
        cursor.close()
        return

    def remove_from_database(self):
        if not self.cnx:
            return None

        cursor = self.cnx.cursor()

        cursor.execute("DELETE FROM Authors \
                 WHERE author_id = ?",
                       (self.author_id,))

        self.cnx.commit()
        cursor.close()
        return
