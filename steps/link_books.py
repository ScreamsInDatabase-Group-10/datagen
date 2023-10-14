from util import GeneratorContext
from rich import print
from rich.progress import track
import random


def store_audiences(context: GeneratorContext):
    print("\tStoring audiences in DB...")
    context.db.executemany(
        "INSERT INTO " + context.table("audiences") + " (id, name) VALUES (:id, :name)",
        [
            {"id": context.options["audiences"].index(a), "name": a}
            for a in context.options["audiences"]
        ],
    )
    context.db.commit()

def link_audiences(context: GeneratorContext):
    for book_id in track(range(context.ids["editions"]), description="\tAssigning audiences to books..."):
        to_select = context.options["audiences"][:]
        random.shuffle(to_select)
        to_select = to_select[:random.randint(1, context.options["max_audiences"])]
        for audience in to_select:
            context.execute_cached("INSERT OR IGNORE INTO " + context.table("books.audiences") + " (book_id, audience_id) VALUES (:bid, :aid)", {
                "bid": book_id,
                "aid": context.options["audiences"].index(audience)
            })


def link_books_main(context: GeneratorContext):
    print("[green][bold]STEP: [/bold] Linking books...[/green]")
    store_audiences(context)
    link_audiences(context)
