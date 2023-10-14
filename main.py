from util import GeneratorContext
from steps.tables import tables_main
from steps.download_books import download_books_main
from steps.link_books import link_books_main
from steps.make_users import make_users_main

def main():
    context = GeneratorContext()
    tables_main(context)
    if "download_books" in context.options["steps"]:
        download_books_main(context)

    if "link_books" in context.options["steps"]:
        link_books_main(context)

    if "make_users" in context.options["steps"]:
        make_users_main(context)

    context.cleanup()

if __name__ == "__main__":
    main()
