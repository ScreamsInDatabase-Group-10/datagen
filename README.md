# datagen
Data generation &amp; DB loading

## Configuration

Configure using a `.env` file with the following values specified:

```bash
# Steps (order doesn't matter)
# - staging : Build & fill staging tables
# - tables : Build tables & setup DB
# - download_books : Get book/contrib data and feed into tables
# - link_books : Link books to contributors & audiences, trim books without authors and authors without books
# - make_users : Generate users (without any linking)
# - supplemental : Link users to entities, generate ratings, generate follows, generate sessions, etc
# - clear_staging : Delete staging tables
STEPS = staging tables download_books link_books make_users supplemental clear_staging

# Database Options (currently with sqlite)

DB_FILE = main.db # DB File

# Database Setup
DB_CLEAR = true # Clear database before run (true/false)
DB_TABLES = spec/tables.json # Path to JSON file containing table creation commands (see next section)

# Data Source
DATA_PATH = ol_dump.dump # File to read raw data from
DATA_LIMIT = 10000 # Amount of records to load, omit to remove limit

# User Generation
USER_COUNT = 500 # Number of users to generate
MAX_PASSWORD = 50 # Max length of password
MAX_NAME = 25 # Max length of first and last names (individually)
NAMES_DICT = spec/names.dic # Dictionary file for markov chain

# Supplemental Data
WORDS_DICT = spec/words.dic # Dictionary file for markov chain
MAX_RATINGS = 100 # Max number of ratings that any book may have
MAX_COLLECTIONS = 10 # Max collections per user
MAX_COLLECTION_SIZE = 50 # Max books per collection
MAX_COLLECTION_NAME = 50 # Max length of collection name
MAX_SESSIONS = 50 # Max sessions/user
MAX_SESSION_TIME = 10 # Max session time in hours
MAX_FOLLOWING = 100 # Max amount of other users a user can follow
MAX_AUDIENCES = 3 # Max number of audiences/book
AUDIENCES = young adult, adult, children, education, government, reference # Comma-separated list of audience names
```

### Table Specification

Tables to generate are specified in a JSON document with the following structure:

```json
[
    {
        {
    "name": "table_name", // Table name in database
    "refer": "table.reference", // Reference for code
    "columns": [ // Column specifiers
      "<name> <type> <constraints...>",
      ...
    ],
    "primary": ["id", ...] // List of primary key columns
  },
    },
    ...
]
```

### Table References

Each table in the specification must contain a reference to the in-code name of the table (so we can change table names as needed without needing to hardcode). All defined references are listed below:

```
- books
- books.authors
- books.editors
- books.publishers
- books.genres
- books.audiences
- books.collections
- contributors
- genres
- audiences
- users
- users.ratings
- users.sessions
- users.collections
- users.following
- collections
```
