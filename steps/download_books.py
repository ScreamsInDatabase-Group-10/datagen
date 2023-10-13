import requests
from util import GeneratorContext
from rich import print
from rich.status import Status
from rich.console import Console
import json
from typing_extensions import TypedDict
import string
import dateutil.parser

EDITION_REQUIRED_KEYS = [
    "revision",
    "title",
    "number_of_pages",
    "publish_date",
    "publishers",
    "authors",
    "genres",
    "subjects",
    "isbn_13",
]
AUTHOR_REQUIRED_KEYS = ["name"]


class TrimmedEdition(TypedDict):
    revision: int
    title: str
    number_of_pages: int
    publish_date: str
    publishers: list[str]
    authors: list[dict[str, str]]
    genres: list[str]
    subjects: list[str]
    isbn_10: list[str]


class TrimmedAuthor(TypedDict):
    name: str


def dl_string(context: GeneratorContext, count: int) -> str:
    return "Downloading {count}{suffix}...".format(
        count=str(count),
        suffix=(" / " + str(context.options["data_limit"]))
        if context.options["data_limit"]
        else "",
    )


def download_books_main(context: GeneratorContext):

    print("[green][bold]STEP: [/bold] Processing books...[/green]")
    with open(context.options["data_path"], "r") as data_stream:
        with Status(dl_string(context, 0)) as status:
            count = 0
            for line in data_stream:
                status.update(dl_string(context, count + 1))
                try:
                    if process_line(context, line.strip(" \n"), status.console):
                        count += 1
                except SystemExit:
                    exit(0)
                except:
                    status.console.print(
                        "[red][bold]Line Error:[/bold] {data}[/red]".format(data=line.strip(" \n"))
                    )
                if context.options["data_limit"] and count > context.options["data_limit"]:
                    break


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

    mapped_id = context.id("authors")
    try:
        context.execute_cached(
            "INSERT INTO "
            + context.table("contributors")
            + " (id, name_first, name_last_company) VALUES (:id, :first_name, :last_name)",
            dict(
                id=mapped_id,
                first_name=trimmed["name"].split(" ")[0].replace("'", "\\'"),
                last_name=trimmed["name"].split(" ")[-1].replace("'", "\\'"),
            ),
        )
        context.db.commit()
        context.create_mapped("authors", id, mapped_id)
    except SystemExit:
        exit(0)
    except:
        console.print(
            "[red][bold]Insertion Error:[/bold] {data}[/red]".format(data=trimmed)
        )
        return False

    return True


def store_edition(
    id: str, data: dict, context: GeneratorContext, console: Console
) -> bool:
    if not all([k in data.keys() for k in EDITION_REQUIRED_KEYS]):
        return False

    trimmed: TrimmedEdition = {
        k: v for k, v in data.items() if k in EDITION_REQUIRED_KEYS
    }

    if len(trimmed["authors"]) == 0:
        return False

    if len(trimmed["publishers"]) == 0:
        return False

    if len(trimmed["isbn_13"]) == 0:
        return False

    if any([not i in string.digits for i in trimmed["isbn_13"][0]]):
        return False

    try:
        parsed_dt = int(dateutil.parser.parse(trimmed["publish_date"]).timestamp())
    except SystemExit:
        exit(0)
    except:
        console.print(
            "[red][bold]Parse Error:[/bold] Parsing date string {dstring}[/red]".format(
                dstring=trimmed["publish_date"]
            )
        )
        return False

    mapped_id = context.id("editions")
    try:
        context.execute_cached(
            "INSERT INTO "
            + context.table("books")
            + " (id, title, length, edition, release_dt, isbn) VALUES (:id, :title, :length, :edition, :release_dt, :isbn)",
            dict(
                id=mapped_id,
                title=trimmed["title"].replace("'", "\\'"),
                length=trimmed["number_of_pages"],
                edition=trimmed["revision"],
                release_dt=parsed_dt,
                isbn=int(trimmed["isbn_13"][0]),
            ),
        )
        context.db.commit()
        context.create_mapped("editions", id, mapped_id)
    except SystemExit:
        exit(0)
    except:
        console.print(
            "[red][bold]Insertion Error:[/bold] {data}[/red]".format(data=trimmed)
        )
        return False
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
