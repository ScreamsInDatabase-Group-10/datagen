from util import GeneratorContext
import json
from typing_extensions import TypedDict

class TableSpec(TypedDict):
    name: str
    refer: str
    columns: list[str]
    primary: list[str]

def tables_main(context: GeneratorContext):
    with open(context.options["db_tables"], "r") as tablespec:
        spec: list[TableSpec] = json.load(tablespec)
    
    for t in spec:
        context.tables[t["refer"]] = t["name"]

    if "tables" in context.options["steps"]:
        for table in spec:
            create_table(context, table)
        
        context.db.commit()

def create_table(context: GeneratorContext, table: TableSpec):
    if context.options["db_clear"]:
        remove_table(context, table["name"])
    context.db.execute("CREATE TABLE {name} ({columns})".format(
        name=table["name"],
        columns=", ".join(table["columns"]),
        primary=", ".join(table["primary"])
    ))

def remove_table(context: GeneratorContext, table: str):
    context.db.execute(f"DROP TABLE IF EXISTS {table};")