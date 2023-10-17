from util import GeneratorContext
from rich import print
from rich.progress import track
import random


def store_audiences(context: GeneratorContext):
    print("\tStoring audiences in DB...")
    context.db.cursor().executemany(
        "INSERT INTO "
        + context.table("audiences")
        + " (id, name) VALUES (%(id)s, %(name)s)",
        [
            {"id": context.options["audiences"].index(a), "name": a}
            for a in context.options["audiences"]
        ],
    )
    context.db.commit()


def link_audiences(context: GeneratorContext):
    for book_id in track(
        range(context.ids["editions"]), description="\tAssigning audiences to books..."
    ):
        to_select = context.options["audiences"][:]
        random.shuffle(to_select)
        to_select = to_select[: random.randint(1, context.options["max_audiences"])]
        for audience in to_select:
            context.execute_cached(
                "INSERT INTO "
                + context.table("books.audiences")
                + " (book_id, audience_id) VALUES (:bid, :aid) ON CONFLICT DO NOTHING",
                {"bid": book_id, "aid": context.options["audiences"].index(audience)},
            )


def link_books_main(context: GeneratorContext):
    print("[green][bold]STEP: [/bold] Linking books...[/green]")
    store_audiences(context)
    link_audiences(context)

    print("\tLinking authors...")
    context.db.execute(
        "INSERT INTO {books_authors} (book_id, contributor_id) SELECT book_id, mapped from (SELECT * FROM staging_books_authors_mapping INNER JOIN staging_id_mapping ON author_raw=original) as superquery".format(
            books_authors=context.table("books.authors")
        )
    )
    context.db.commit()

    print("\tLinking editors...")
    context.db.execute(
        "INSERT INTO {books_editors} (book_id, contributor_id) SELECT book_id, mapped from (SELECT * FROM staging_books_authors_mapping INNER JOIN staging_id_mapping ON author_raw=original) as superquery WHERE MOD(mapped, 5) = 0".format(
            books_editors=context.table("books.editors")
        )
    )
    context.db.commit()
    """
    print("\tTrimming books...")
    context.db.execute(
        "DELETE FROM {books} WHERE id NOT IN (SELECT book_id FROM books_authors)".format(
            books=context.table("books")
        )
    )
    context.db.commit()

    print("\tTrimming contributors...")
    context.db.execute(
        "DELETE FROM {contributors} WHERE id NOT IN (SELECT contributor_id FROM books_authors) AND name_first IS NOT NULL".format(
            contributors=context.table("contributors")
        )
    )
    context.db.commit()"""
