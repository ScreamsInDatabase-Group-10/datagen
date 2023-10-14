from markov_word_generator import MarkovWordGenerator
from util import GeneratorContext
from rich import print
from rich.progress import track
from rich.console import Console
import time
import random
import datetime


def make_users_main(context: GeneratorContext):
    console = Console()
    print("[green][bold]STEP: [/bold] Generating user data...[/green]")
    markov_names = MarkovWordGenerator(
        markov_length=4, dictionary_filename=context.options["names_dict"]
    )
    markov_passwords = MarkovWordGenerator(
        markov_length=2, dictionary_filename=context.options["words_dict"]
    )

    for _ in track(
        range(context.options["user_count"]), description="\tCreating users...", console=console
    ):
        first_name = markov_names.generate_word()[: context.options["max_name"]]
        last_name = markov_names.generate_word()[: context.options["max_name"]]
        email = (first_name + "_" + last_name)[
            : context.options["max_email"] - 10
        ] + "@gmail.com"
        password = (
            "-".join([markov_passwords.generate_word() for _ in range(3)])
            .title()
            .swapcase()
            .replace("S", "$")
            .casefold()[: context.options["max_password"]]
        )
        creation_time = random.randint(0, int(time.time()) - 100000)
        access_time = random.randint(creation_time, int(time.time()))
        internal_id = context.id("users")
        context.execute_cached(
            "INSERT INTO "
            + context.table("users")
            + " (id, creation_dt, access_dt, name_first, name_last, email, password) VALUES (:id, :creation, :access, :first, :last, :email, :password) ON CONFLICT DO NOTHING",
            {
                "id": internal_id,
                "creation": datetime.datetime.fromtimestamp(creation_time).isoformat(),
                "access": datetime.datetime.fromtimestamp(access_time).isoformat(),
                "first": first_name,
                "last": last_name,
                "email": email,
                "password": password,
            },
        )

    context.clean_cache()
