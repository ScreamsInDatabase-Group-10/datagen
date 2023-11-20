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


def generate_contributors(
    context: GeneratorContext,
) -> tuple[list[Contributor], list[Contributor], list[Contributor]]:
    print("[green][bold]Generating contributors...[/bold][/green]")
    names_generator = context.get_markov("names", 4)
    words_generator = context.get_markov("words", 4)

    authors = []
    editors = []
    publishers = []

    for i in track(
        range(context.options["rand_count"] * MAX_AUTHORS),
        description="\tGenerating authors...",
    ):
        authors.append(
            Contributor(
                id=i,
                first=names_generator.generate_word(),
                last=names_generator.generate_word(),
            )
        )

    for i in track(
        range(context.options["rand_count"] * MAX_AUTHORS),
        description="\tGenerating editors...",
    ):
        editors.append(
            Contributor(
                id=i,
                first=names_generator.generate_word(),
                last=names_generator.generate_word(),
            )
        )

    for i in track(
        range(context.options["rand_count"] // 4),
        description="\tGenerating publishers...",
    ):
        publishers.append(
            Contributor(
                id=i,
                first=None,
                last=words_generator.generate_word()
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

    return authors, editors, publishers


def main(context: GeneratorContext):
    authors, editors, publishers = generate_contributors(context)
    print(authors, editors, publishers)


if __name__ == "__main__":
    main(GeneratorContext())
