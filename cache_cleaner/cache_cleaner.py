#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Purge cache based on age of files and the size of the cache.

Usage:
  cache_cleaner.py --path=<PATH> --max-age=<MAX_AGE> --max-size=<MAX_SIZE> [--force]
  cache_cleaner.py -h | --help

Options:
  -h --help                 Show this screen.
  --path=<PATH>             Path of the cache to clean.
  --max-age=<MAX_AGE>       Delete files that are older than MAX_AGE days.
  --max-size=<MAX_SIZE>     Delete files until the cache size is less than MAX_SIZE bytes.
                            Supports human-friendly options: 500M, 2G, 1T.
  --force                   Actually delete the files.  Otherwise runs in a "dry run" mode,
                            printing which files would be deleted without actually deleting.

"""
import os
import time

import daiquiri
import docopt
import humanize

from utils import (
    parse_max_cache_size_arg,
    delete_dir_if_empty,
    delete_file,
    get_file_stats,
    get_new_max_age,
)

daiquiri.setup(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = daiquiri.getLogger("cache_cleaner")


def main():
    args = docopt.docopt(__doc__)

    now = time.time()
    max_age = int(args["--max-age"]) * 24 * 60 * 60
    cache_path = args["--path"]
    max_cache_size = parse_max_cache_size_arg(args["--max-size"])

    force = bool(args["--force"])
    if force:
        os.environ["X-RUN-CACHE-CLEANER"] = "True"

    total_size = 0
    initial_pass = True

    while initial_pass or total_size > max_cache_size:
        logger.info(
            "Walking filesystem for %r, deleting files that have not been accessed in more than %s",
            cache_path,
            humanize.naturaldelta(max_age),
        )

        largest_access_age = 0
        n_deletions = 0
        # Start looking from the deepest subdirectories first (topdown=False)
        # so that we can delete their parent directories as we go
        for _, dirs, files, root_fd in os.fwalk(cache_path, topdown=False):
            for filename in files:
                file_size, age = get_file_stats(filename, root_fd, now)
                # Calculate the total size on the first path, only decrease
                # it thereafter
                if initial_pass:
                    total_size += file_size

                # Delete any file that hasn't been accessed in > max_age
                if age > max_age:
                    delete_file(filename, root_fd)
                    n_deletions += 1
                    total_size -= file_size
                elif age > largest_access_age:
                    # Store the least recently accessed file
                    largest_access_age = age

                # Stop deleting files if we've deleted enough
                if not initial_pass and total_size <= max_cache_size:
                    logger.info(
                        "Deleted %d files, cache reduced to %s, clearing complete",
                        n_deletions,
                        humanize.naturalsize(total_size, gnu=True),
                    )
                    return

            for dirname in dirs:
                delete_dir_if_empty(dirname, root_fd)

        logger.info("Deleted %d files.", n_deletions)
        initial_pass = False

        if total_size > max_cache_size:
            max_age = get_new_max_age(
                largest_age=largest_access_age,
                max_size=max_cache_size,
                current_size=total_size,
            )
            logger.info(
                "Cache size (%s) exceeds maximum size (%s), decreasing max age",
                humanize.naturalsize(total_size, gnu=True),
                humanize.naturalsize(max_cache_size, gnu=True),
            )

    logger.info(
        "Cache clearing complete. Current cache size: %s",
        humanize.naturalsize(total_size, gnu=True),
    )


if __name__ == "__main__":
    main()
