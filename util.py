from dotenv import load_dotenv
from os import getenv, environ
from typing_extensions import TypedDict
from typing import Union, Literal
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


REFERENCE_NAMES = Literal[
    "books", 
    "books.authors", 
    "books.editors", 
    "books.publishers", 
    "books.genres", 
    "books.audiences", 
    "books.collections", 
    "contributors",
    "genres",
    "audiences",
    "users",
    "users.ratings",
    "users.sessions",
    "users.collections",
    "users.following",
    "collections"
]

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
            "max_following": int(getenv("MAX_FOLLOWING", "100")),
        }
        self.db = self._open_database()
        self.ids: dict[str, int] = {}

    def _open_database(self) -> Connection:
        conn = connect(self.options["db_file"])
        if "staging" in self.options["steps"]:
            conn.execute("DROP TABLE IF EXISTS staging_id_mapping;")
            conn.execute(
                "CREATE TABLE staging_id_mapping (original varchar(100) not null, mapped int not null, primary key (original, mapped));"
            )
            conn.commit()
        return conn

    def cleanup(self):
        if "staging" in self.options["steps"]:
            self.db.execute("DROP TABLE staging_id_mapping;")
        self.db.commit()
        self.db.close()

    def id(self, entity: str) -> int:
        if not entity in self.ids.keys():
            self.ids[entity] = 0
            return 0
        self.ids[entity] += 1
        return self.ids[entity]

    def create_mapped(self, entity_type: str, original_id: str, mapped_id: int):
        if not "staging" in self.options["steps"]:
            return
        self.db.execute(
            "INSERT INTO staging_id_mapping (original, mapped) VALUES ('{original}', {mapped})".format(
                original=original_id, mapped=mapped_id
            )
        )

    def table(self, ref: REFERENCE_NAMES) -> str:
        return self.tables[ref]
