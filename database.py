import sqlite3


class Docs:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def set_dictionary(self, dict_name):
        with self.connection:
            return self.cursor.execute("INSERT INTO dictionaries (dict_name) VALUES (?)", (dict_name,))

    def delete_dictionary(self, dict_name):
        with self.connection:
            return self.cursor.execute("DELETE FROM dictionaries WHERE dict_name = ?", (dict_name,))

    def export_name_dictionaries(self):
        with self.connection:
            return [row[0] for row in self.cursor.execute("SELECT dict_name FROM dictionaries").fetchall()]

    def set_doc(self, filename, dictionary, file_description, time, mark, filepath):
        with self.connection:
            return self.cursor.execute("INSERT INTO docs "
                                       "(filename, docs_dictionary, file_description, time, mark, path_on_pc) "
                                       "VALUES (?, ?, ?, ?, ?, ?)",
                                       (filename, dictionary, file_description, time, mark, filepath,))

    def get_fileid(self, filename):
        with self.connection:
            return self.cursor.execute("SELECT doc_id FROM docs WHERE filename = ?",
                                       (filename,)).fetchone()[0]

    def find_by_fileid(self, file_id):
        with self.connection:
            return self.cursor.execute("SELECT "
                                       "doc_id, "
                                       "docs_dictionary, "
                                       "filename, "
                                       "file_description, "
                                       "time, "
                                       "mark, "
                                       "path_on_pc"
                                       " FROM docs WHERE doc_id = ?", (file_id,)).fetchall()

    def find_by_mark(self, mark):
        with self.connection:
            return self.cursor.execute("SELECT * FROM docs WHERE mark = ?", (mark,)).fetchall()

    def find_by_filename(self, filename):
        with self.connection:
            return self.cursor.execute("SELECT "
                                       "doc_id, docs_dictionary, filename, file_description, time, mark, path_on_pc"
                                       " FROM docs WHERE filename LIKE ?",
                                       (filename,)).fetchall()[0]

    def export_filenames(self):
        with self.connection:
            return [row[0] for row in self.cursor.execute("SELECT filename FROM docs").fetchall()]

    def get_all_files(self):
        with self.connection:
            return self.cursor.execute(
                "SELECT doc_id, docs_dictionary, filename, file_description, time, mark, path_on_pc FROM docs"
            ).fetchall()

    def delete_file_by_id(self, fileid):
        with self.connection:
            return self.cursor.execute("DELETE FROM docs WHERE doc_id = ?", (fileid,))

    def find_file_by_directory(self, directory):
        with self.connection:
            return self.cursor.execute("SELECT "
                                       "doc_id, "
                                       "docs_dictionary, "
                                       "filename, "
                                       "file_description, "
                                       "time, "
                                       "mark, "
                                       "path_on_pc "
                                       "FROM docs WHERE docs_dictionary = ?", (directory, )).fetchall()

    def commit_changes(self):
        with self.connection:
            return self.connection.commit()
