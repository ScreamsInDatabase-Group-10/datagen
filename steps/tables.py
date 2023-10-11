from util import GeneratorContext
import json
from typing_extensions import TypedDict
from rich.progress import Progress

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
        with Progress() as progress:
            progress.console.print("[green][bold]STEP: [/bold] Generating tables...[/green]")
            tables_task = progress.add_task("Creating tables...", total=len(spec))
            for table in spec:
                create_table(context, table)
                progress.update(tables_task, advance=1)
                progress.console.print(f"[grey70 italic]Generated {table['refer']} ({table['name']})[/grey70 italic]")
            
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