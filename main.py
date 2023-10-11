from util import GeneratorContext
from steps.tables import tables_main

def main():
    context = GeneratorContext()
    tables_main(context)

    context.cleanup()

if __name__ == "__main__":
    main()
