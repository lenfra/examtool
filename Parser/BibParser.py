# -*- coding: utf-8 -*-
import codecs
import logging

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

from ExamClasses.BibliographyClass import Bibliography

logging.getLogger('bibtexparser.bwriter').addHandler(logging.NullHandler())


class BibParser:
    def __init__(self):
        self.bib_database = BibDatabase()
        self.bibliographyList = []

    def load_bibtex_from_file(self, _file):
        with codecs.open(_file, 'r', 'utf8') as bibtex_file:
            bibtex_str = bibtex_file.read()

        self.bib_database = bibtexparser.loads(bibtex_str)
        self.save_bibliography_class()
        return self.bibliographyList

    def parse_data(self, data):
        self.bib_database = bibtexparser.loads(data)
        self.save_bibliography_class()

        return self.bibliographyList

    def save_bibliography_class(self):
        bibliography_entries = self.bib_database.get_entry_list()
        if bibliography_entries:
            for entry in bibliography_entries:
                bibliography = Bibliography()
                bibliography.set_bibliography_id(entry['ID'])
                bibliography.set_bibliography_data(entry)
                self.bibliographyList.append(bibliography)
        return
