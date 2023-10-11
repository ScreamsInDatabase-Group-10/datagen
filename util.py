from dotenv import load_dotenv
from os import getenv, environ
from typing_extensions import TypedDict
from typing import Union
from sqlite3 import Connection, connect


class OptionsDict(TypedDict):
    steps: list[str]
    db_file: str
    db_clear: bool
    db_tables: str
    data_url: str
    data_limit: Union[int, None]
    user_count: int
    max_password: int
    max_name: int
    names_dict: str
    words_dict: str
    max_ratings: int
    max_collections: int
    max_collection_size: int
    max_collection_name: int
    max_sessions: int
    max_session_time: int
    max_following: int


class GeneratorContext:
    def __init__(self):
        load_dotenv()
        self.tables: dict[str, str] = {}
        self.book_count: int = 0
        self.options: OptionsDict = {
            "steps": getenv(
                "STEPS", "tables download_books make_users supplemental"
            ).split(" "),
            "db_file": environ["DB_FILE"],
            "db_clear": getenv("DB_CLEAR", "true") == "true",
            "db_tables": environ["DB_TABLES"],
            "data_url": environ["DATA_URL"],
            "data_limit": int(environ["DATA_LIMIT"]) if getenv("DATA_LIMIT") else None,
            "user_count": int(getenv("USER_COUNT", "500")),
            "max_password": int(getenv("MAX_PASSWORD", "50")),
            "max_name": int(getenv("MAX_NAME", "25")),
            "names_dict": environ["NAMES_DICT"],
            "words_dict": environ["WORDS_DICT"],
            "max_ratings": int(getenv("MAX_RATINGS", "100")),
            "max_collections": int(getenv("MAX_COLLECTIONS", "10")),
            "max_collection_name": int(getenv("MAX_COLLECTION_NAME", "50")),
            "max_collection_size": int(getenv("MAX_COLLECTION_SIZE", "50")),
            "max_sessions": int(getenv("MAX_SESSIONS", "50")),
            "max_session_time": int(getenv("MAX_SESSION_TIME", "10")),
            "max_following": int(getenv("MAX_FOLLOWING", "100"))
        }
        self.db = self._open_database()

    def _open_database(self) -> Connection:
        return connect(self.options["db_file"])
    
    def cleanup(self):
        self.db.commit()
        self.db.close()