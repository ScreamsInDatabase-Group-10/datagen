# datagen
Data generation &amp; DB loading

## Configuration

Configure using a `.env` file with the following values specified:

```bash
# Database Spec (currently with sqlite)

DB_FILE = main.db # DB File

# Database Setup
DB_CLEAR = true | false # Clear database before run
DB_TABLES = spec/tables.json # Path to JSON file containing table creation commands (see next section)
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
    ]
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
