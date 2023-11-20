from util import GeneratorContext
from dataclasses import dataclass
from typing import Literal, Union
from datetime import datetime, timedelta
from rich.progress import track, Progress
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
) -> tuple[list[int], list[int], list[int], list[int], list[int], list[int]]:
    print("[green][bold]Getting current IDs...[/bold][/green]")

    audiences = [i[0] for i in context.db.execute("SELECT id FROM audiences")]
    books = [i[0] for i in context.db.execute("SELECT id FROM books")]
    contributors = [i[0] for i in context.db.execute("SELECT id FROM contributors")]
    genres = [i[0] for i in context.db.execute("SELECT id FROM genres")]
    users = [i[0] for i in context.db.execute("SELECT id FROM users")]
    sessions = [
        i[0] for i in context.db.execute("SELECT session_id FROM users_sessions")
    ]
    return audiences, books, contributors, genres, users, sessions


def make_read_session(book: Book, user: int, id: int) -> list:
    start = book.release + timedelta(seconds=random.randint(100, 1000000))
    end = start + timedelta(seconds=random.randint(100, 3600))
    start_page = random.randint(0, book.length)
    end_page = random.randint(start_page + 1, book.length)
    return [id, book.id, user, start, end, start_page, end_page]


def main(context: GeneratorContext):
    (
        audiences_ids,
        books_ids,
        contributors_ids,
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

    # Upload data
    print("[green][bold]Pushing data...[/bold][/green]")
    sid = max(sessions_ids, default=-1) + 1
    with Progress() as progress:
        task = progress.add_task("Uploading...", total=len(books))
        for book in books:
            try:
                context.db.execute(
                    "INSERT INTO books (id, title, length, edition, release_dt, isbn) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    [
                        book.id,
                        book.title,
                        book.length,
                        book.edition,
                        book.release,
                        book.isbn,
                    ],
                )
                for author in book.authors:
                    context.db.execute(
                        "INSERT INTO contributors (id, name_first, name_last_company) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        [author.id, author.first, author.last],
                    )
                    context.db.execute(
                        "INSERT INTO books_authors (book_id, contributor_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        [book.id, author.id],
                    )

                for editor in book.editors:
                    context.db.execute(
                        "INSERT INTO contributors (id, name_first, name_last_company) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        [editor.id, editor.first, editor.last],
                    )
                    context.db.execute(
                        "INSERT INTO books_editors (book_id, contributor_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        [book.id, editor.id],
                    )

                for publisher in book.publishers:
                    context.db.execute(
                        "INSERT INTO contributors (id, name_first, name_last_company) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        [publisher.id, publisher.first, publisher.last],
                    )
                    context.db.execute(
                        "INSERT INTO books_publishers (book_id, contributor_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        [book.id, publisher.id],
                    )

                for audiences in book.audiences:
                    context.db.execute(
                        "INSERT INTO books_audiences (book_id, audience_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        [book.id, audiences],
                    )

                for genre in book.genres:
                    context.db.execute(
                        "INSERT INTO books_genres (book_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        [book.id, genre],
                    )

                user_read_ids = random.sample(users_ids, random.randint(2, 30))
                scr = context.db.cursor()
                scr.executemany(
                    "INSERT INTO users_sessions (session_id, book_id, user_id, start_datetime, end_datetime, start_page, end_page) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    [
                        make_read_session(book, i, sid + user_read_ids.index(i))
                        for i in user_read_ids
                    ],
                )
                sid += len(user_read_ids)

                user_rate_ids = random.sample(users_ids, random.randint(2, 30))
                rcr = context.db.cursor()
                rcr.executemany(
                    "INSERT INTO users_ratings (book_id, user_id, rating) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    [[book.id, i, random.randint(0, 5)] for i in user_rate_ids],
                )

                context.db.commit()
            except:
                context.db.rollback()
            progress.update(task, advance=1)


if __name__ == "__main__":
    main(GeneratorContext())
