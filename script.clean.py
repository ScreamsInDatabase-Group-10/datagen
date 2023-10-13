import dotenv
dotenv.load_dotenv()

import os
with open(os.getenv("DATA_EXT", "ol_dump.ext"), "r") as source:
    with open(os.getenv("DATA_PATH", "ol_dump.dump"), "w") as sink:
        for line in source:
            if line.split("\t")[0] in ["/type/author", "/type/edition"]:
                sink.write(line)