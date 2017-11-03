from audit.digilib.db import DigilibDatabase


def load(db_file_path):
    return DigilibDatabase(db_file_path)
