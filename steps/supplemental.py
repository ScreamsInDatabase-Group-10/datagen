from util import GeneratorContext
from rich import print
from rich.progress import track
import random
from markov_word_generator import MarkovWordGenerator


def build_collections(context: GeneratorContext):
    markov = MarkovWordGenerator(
        markov_length=4, dictionary_filename=context.options["words_dict"]
    )
    for user_id in track(
        range(context.options["user_count"]), "\tCreating user collections..."
    ):
        for collection_count in range(
            random.randint(0, context.options["max_collections"])
        ):
            collection_name = " ".join(
                [markov.generate_word() for l in range(2)]
            ).title()[: context.options["max_collection_name"]]
            collection_id = context.id("collections")
            context.execute_cached(
                "INSERT INTO "
                + context.table("collections")
                + " (id, name) VALUES (:id, :name)",
                {"id": collection_id, "name": collection_name},
            )
            context.execute_cached(
                "INSERT INTO "
                + context.table("users.collections")
                + " (user_id, collection_id) VALUES (:uid, :cid)",
                {"uid": user_id, "cid": collection_id},
            )

            book_ids = list(
                set(
                    [
                        random.randint(0, context.ids["editions"])
                        for i in range(
                            random.randint(1, context.options["max_collection_size"])
                        )
                    ]
                )
            )

            for bid in book_ids:
                context.execute_cached(
                    "INSERT INTO "
                    + context.table("books.collections")
                    + " (book_id, collection_id) VALUES (:bid, :cid)",
                    {"bid": bid, "cid": collection_id},
                )

    context.clean_cache()


def make_friends(context: GeneratorContext):
    for follower in track(range(context.ids["users"]), "\tMaking friends..."):
        to_follow = list(
            set(
                [
                    random.randint(0, context.ids["users"])
                    for _ in range(random.randint(1, context.options["max_following"]))
                ]
            )
        )
        for followee in to_follow:
            if followee != follower:
                context.execute_cached(
                    "INSERT INTO "
                    + context.table("users.following")
                    + " (user_id, following_id) VALUES (:uid, :fid)",
                    {"uid": follower, "fid": followee},
                )
    context.clean_cache()


def rate_books(context: GeneratorContext):
    for book in track(range(context.ids["editions"]), "\tRating books..."):
        users = list(
            set(
                [
                    random.randint(0, context.ids["users"])
                    for i in range(random.randint(0, context.options["max_ratings"]))
                ]
            )
        )
        for user_id in users:
            context.execute_cached(
                "INSERT INTO "
                + context.table("users.ratings")
                + " (book_id, user_id, rating) VALUES (:bid, :uid, :rating)",
                {
                    "bid": book,
                    "uid": user_id,
                    "rating": random.randint(0, 5)
                },
            )
    context.clean_cache()


def supplemental_main(context: GeneratorContext):
    print("[green][bold]STEP: [/bold] Performing supplemental tasks...[/green]")
    build_collections(context)
    make_friends(context)
    rate_books(context)
