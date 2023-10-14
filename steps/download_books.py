from util import GeneratorContext
from rich import print
from rich.progress import (
    Progress,
    FileSizeColumn,
    SpinnerColumn,
    TextColumn,
    TotalFileSizeColumn,
    TaskProgressColumn,
    BarColumn,
    MofNCompleteColumn,
    TimeElapsedColumn
)
from rich.console import Console
import json
from typing_extensions import TypedDict
import string
import dateutil.parser
import os
import time

EDITION_REQUIRED_KEYS = [
    "edition_name",
    "title",
    "number_of_pages",
    "publish_date",
    "authors",
    "isbn_13",
]
EDITION_OPTIONAL_KEYS = [
    "publishers",
    "genres"
]

AUTHOR_REQUIRED_KEYS = ["name"]


class TrimmedEdition(TypedDict):
    edition_name: str
    title: str
    number_of_pages: int
    publish_date: str
    publishers: list[str]
    authors: list[dict[str, str]]
    genres: list[str]
    isbn_10: list[str]


class TrimmedAuthor(TypedDict):
    name: str


def download_books_main(context: GeneratorContext):
    print("[green][bold]STEP: [/bold] Processing books...[/green]")
    ls = int(time.time())
    with open(context.options["data_path"], "r") as data_stream:
        if context.options["data_limit"]:
            progress = Progress(
                TextColumn("\t"),
                SpinnerColumn(),
                TextColumn("{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn()
            )
        else:
            progress = Progress(
                TextColumn("\t"),
                SpinnerColumn(),
                TextColumn("{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                FileSizeColumn(),
                TextColumn("/"),
                TotalFileSizeColumn(),
                TimeElapsedColumn()
            )
        bytesize = 0
        count = 0
        if context.options["data_limit"]:
            task = progress.add_task(
                "[green]Processing data...", total=context.options["data_limit"]
            )
        else:
            task = progress.add_task(
                "[green]Processing data...",
                total=os.stat(context.options["data_path"]).st_size,
            )

        progress.start()

        for line in data_stream:
            bytesize += len(line)
            try:
                if process_line(context, line.strip(" \n"), progress.console):
                    count += 1
            except KeyboardInterrupt:
                exit(0)
            except:
                progress.console.print(
                    "\t[red][bold]Line Error:[/bold] {data}[/red]".format(
                        data=line.strip(" \n")
                    )
                )

            if int(time.time()) != ls:
                ls = int(time.time())
                if context.options["data_limit"]:
                    progress.update(task, completed=count)
                else:
                    progress.update(task, completed=bytesize)
                progress.refresh()

            if context.options["data_limit"] and count > context.options["data_limit"]:
                break
    progress.stop()
    context.clean_cache()


def store_author(
    id: str, data: dict, context: GeneratorContext, console: Console
) -> bool:
    if not all([k in data.keys() for k in AUTHOR_REQUIRED_KEYS]):
        return False

    trimmed: TrimmedAuthor = {
        k: v for k, v in data.items() if k in AUTHOR_REQUIRED_KEYS
    }

    if len(trimmed["name"].split(" ")) < 2:
        return False

    mapped_id = context.id("contributors")
    context.execute_cached(
        "INSERT OR IGNORE INTO "
        + context.table("contributors")
        + " (id, name_first, name_last_company) VALUES (:id, :first_name, :last_name)",
        dict(
            id=mapped_id,
            first_name=trimmed["name"].split(" ")[0].replace("'", "\\'"),
            last_name=trimmed["name"].split(" ")[-1].replace("'", "\\'"),
        ),
    )
    context.create_mapped("contributors", id, mapped_id)

    return True


def store_edition(
    id: str, data: dict, context: GeneratorContext, console: Console
) -> bool:
    if not all([k in data.keys() for k in EDITION_REQUIRED_KEYS]):
        return False

    trimmed: TrimmedEdition = {
        k: v for k, v in data.items() if k in EDITION_REQUIRED_KEYS or k in EDITION_OPTIONAL_KEYS
    }

    if len(trimmed["authors"]) == 0:
        return False

    if len(trimmed["isbn_13"]) == 0:
        return False

    if any([not i in string.digits for i in trimmed["isbn_13"][0]]):
        return False

    try:
        parsed_dt = int(dateutil.parser.parse(trimmed["publish_date"].replace("?", "")).timestamp())
    except SystemExit:
        exit(0)
    except:
        console.print(
            "\t[red][bold]Parse Error:[/bold] Parsing date string {dstring}[/red]".format(
                dstring=trimmed["publish_date"]
            )
        )
        return False

    mapped_id = context.id("editions")

    context.execute_cached(
        "INSERT OR IGNORE INTO "
        + context.table("books")
        + " (id, title, length, edition, release_dt, isbn) VALUES (:id, :title, :length, :edition, :release_dt, :isbn)",
        dict(
            id=mapped_id,
            title=trimmed["title"].replace("'", "\\'"),
            length=trimmed["number_of_pages"],
            edition=trimmed["edition_name"],
            release_dt=parsed_dt,
            isbn=int(trimmed["isbn_13"][0]),
        ),
    )
    context.create_mapped("editions", id, mapped_id)

    context.atomics["pages"][mapped_id] = trimmed["number_of_pages"]

    for g in trimmed.get("genres", []):
        normal = g.lower().replace("-", "").replace(".", "")
        if not normal in context.atomics["genre"].keys():
            genre_id = context.id("genres")
            context.execute_cached(
                "INSERT OR IGNORE INTO "
                + context.table("genres")
                + " (id, name) VALUES (:id, :name)",
                {"id": genre_id, "name": normal},
            )
            context.atomics["genre"][normal] = genre_id
        else:
            genre_id = context.atomics["genre"][normal]

        context.execute_cached(
            "INSERT OR IGNORE INTO "
            + context.table("books.genres")
            + " (book_id, genre_id) VALUES (:bid, :gid)",
            {"bid": mapped_id, "gid": genre_id},
        )

    for p in trimmed.get("publishers", []):
        normal = p.lower()
        if not normal in context.atomics["publisher"].keys():
            pub_id = context.id("contributors")
            context.execute_cached(
                "INSERT OR IGNORE INTO "
                + context.table("contributors")
                + " (id, name_first, name_last_company) VALUES (:id, NULL, :name)",
                {"id": pub_id, "name": normal},
            )
            context.atomics["publisher"][normal] = pub_id
        else:
            pub_id = context.atomics["publisher"][normal]

        context.execute_cached(
            "INSERT OR IGNORE INTO "
            + context.table("books.publishers")
            + " (book_id, contributor_id) VALUES (:bid, :pid)",
            {"bid": mapped_id, "pid": pub_id},
        )

    for a in trimmed["authors"]:
        if "key" in a.keys():
            context.stage_author(mapped_id, a["key"])

    return True


def process_line(context: GeneratorContext, line: str, console: Console) -> bool:
    parts = line.split("\t")
    record_type = parts[0]
    record_id = parts[1]
    record_data = json.loads(parts[4])

    if record_type == "/type/author":
        return store_author(record_id, record_data, context, console)
    if record_type == "/type/edition":
        return store_edition(record_id, record_data, context, console)

    return False
