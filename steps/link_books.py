from util import GeneratorContext
from rich import print


def store_audiences(context: GeneratorContext):
    print("[green]Storing audiences in DB...[/green]")
    context.db.executemany(
        "INSERT INTO " + context.table("audiences") + " (id, name) VALUES (:id, :name)",
        [
            {"id": context.options["audiences"].index(a), "name": a}
            for a in context.options["audiences"]
        ],
    )
    context.db.commit()


def link_books_main(context: GeneratorContext):
    print("[green][bold]STEP: [/bold] Linking books...[/green]")
    store_audiences(context)
