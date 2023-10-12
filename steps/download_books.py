import requests
from util import GeneratorContext
from rich import print
from rich.status import Status
from rich.console import Console
import json

def dl_string(context: GeneratorContext, count: int) -> str:
    return "Downloading {count}{suffix}...".format(
        count=str(count),
        suffix=(" / " + str(context.options["data_limit"])) if context.options["data_limit"] else ""
    )

def download_books_main(context: GeneratorContext):
    print("[green][bold]STEP: [/bold] Downloading books...[/green]")
    data_stream = requests.get(context.options["data_url"], stream=True)

    if data_stream.encoding is None:
        data_stream.encoding = "utf-8"

    with Status(dl_string(context, 0)) as status:
        count = 0
        for line in data_stream.iter_lines(decode_unicode=True):
            status.update(dl_string(context, count + 1))
            process_line(context, line, status.console)
            count += 1
            if context.options["data_limit"] and count > context.options["data_limit"]:
                break

def process_line(context: GeneratorContext, line: str, console: Console) -> bool:
    parts = line.split("\t")
    record_type = parts[0]
    record_id = parts[1]
    record_data = json.loads(parts[4])

    if record_type == "/type/author":
        pass
    if record_type == "/type/edition":
        pass

    return False    
