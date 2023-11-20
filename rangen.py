from util import GeneratorContext
from dataclasses import dataclass
from typing import Literal, Union
from datetime import datetime, timedelta
from rich.progress import track
from rich import print
import random

MAX_AUTHORS = 3
MAX_LENGTH = 512


@dataclass
class Contributor:
    id: int
    first: Union[None, str]
    last: str


@dataclass
class Book:
    id: int
    title: str
    length: int
    edition: str
    release: datetime
    isbn: int
    authors: list[Contributor]
    editors: list[Contributor]
    publishers: list[Contributor]
    audiences: list[int]
    genres: list[int]


def generate_contributors(
    context: GeneratorContext, max_id: int
) -> tuple[list[Contributor], list[Contributor], list[Contributor]]:
    print("[green][bold]Generating contributors...[/bold][/green]")
    names_generator = context.get_markov("names", 4)
    words_generator = context.get_markov("words", 4)

    authors = []
    editors = []
    publishers = []

    cid = max_id

    for i in track(
        range(context.options["rand_count"] * MAX_AUTHORS),
        description="\tGenerating authors...",
    ):
        authors.append(
            Contributor(
                id=cid,
                first=names_generator.generate_word()[:25],
                last=names_generator.generate_word()[:25],
            )
        )
        cid += 1

    for i in track(
        range(context.options["rand_count"] * MAX_AUTHORS),
        description="\tGenerating editors...",
    ):
        editors.append(
            Contributor(
                id=cid,
                first=names_generator.generate_word()[:25],
                last=names_generator.generate_word()[:25],
            )
        )
        cid += 1

    for i in track(
        range(context.options["rand_count"] // 4),
        description="\tGenerating publishers...",
    ):
        publishers.append(
            Contributor(
                id=cid,
                first=None,
                last=words_generator.generate_word()[:25]
                + " "
                + random.choice(
                    [
                        "publishers",
                        "publishing",
                        "books",
                        "editing corp",
                        "literature group",
                        "publishing department",
                    ]
                ),
            )
        )
        cid += 1

    return authors, editors, publishers


def build_books(
    context: GeneratorContext,
    authors: list[Contributor],
    editors: list[Contributor],
    publishers: list[Contributor],
    genres: list[int],
    audiences: list[int],
    start_id: int,
) -> list[Book]:
    print("[green][bold]Generating books...[/bold][/green]")
    words_generator = context.get_markov("words", 4)
    bid = start_id
    results = []

    for i in track(range(context.options["rand_count"])):
        results.append(
            Book(
                id=bid,
                title=" ".join(
                    [
                        words_generator.generate_word()
                        for i in range(0, random.randint(1, 4))
                    ]
                ),
                length=random.randint(10, MAX_LENGTH),
                edition=random.choice(["1", "2", "3", "4", "5"]),
                release=datetime.now()
                - timedelta(seconds=context.options["rand_start"])
                + timedelta(seconds=random.randint(0, context.options["rand_end"])),
                isbn=random.randint(1000000000, 9999999999),
                authors=random.sample(authors, random.randint(1, MAX_AUTHORS)),
                editors=random.sample(editors, random.randint(1, MAX_AUTHORS)),
                publishers=random.sample(publishers, random.randint(1, MAX_AUTHORS)),
                genres=random.sample(genres, random.randint(1, 4)),
                audiences=[random.choice(audiences)],
            )
        )
        bid += 1

    return results


def current_data(
    context: GeneratorContext,
) -> tuple[list[int], list[int], list[int], list[int], list[int], list[int], list[int]]:
    print("[green][bold]Getting current IDs...[/bold][/green]")

    audiences = [i[0] for i in context.db.execute("SELECT id FROM audiences")]
    books = [i[0] for i in context.db.execute("SELECT id FROM books")]
    contributors = [i[0] for i in context.db.execute("SELECT id FROM contributors")]
    collections = [i[0] for i in context.db.execute("SELECT id FROM collections")]
    genres = [i[0] for i in context.db.execute("SELECT id FROM genres")]
    users = [i[0] for i in context.db.execute("SELECT id FROM users")]
    sessions = [
        i[0] for i in context.db.execute("SELECT session_id FROM users_sessions")
    ]
    return audiences, books, contributors, collections, genres, users, sessions


def main(context: GeneratorContext):
    (
        audiences_ids,
        books_ids,
        contributors_ids,
        collections_ids,
        genres_ids,
        users_ids,
        sessions_ids,
    ) = current_data(context)
    authors, editors, publishers = generate_contributors(
        context, max(contributors_ids, default=-1) + 1
    )
    books = build_books(
        context,
        authors,
        editors,
        publishers,
        genres_ids,
        audiences_ids,
        max(books_ids, default=-1) + 1,
    )
    print(books)


if __name__ == "__main__":
    main(GeneratorContext())
