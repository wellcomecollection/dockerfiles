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
  --max-size=<MAX_SIZE>     Delete files until the cache size is less than MAX_SIZE Kbytes.
                            Supports human-friendly options: 500M, 2G, 1T.
  --force                   Actually delete the files.  Otherwise runs in a "dry run" mode,
                            printing which files would be deleted without actually deleting.

"""
import os
import time

import daiquiri
import docopt

from utils import parse_max_cache_size_arg, delete_dir_if_empty, delete_file

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
            "Walking filesystem for %r, deleting files that have not been accessed in more than %d seconds",
            cache_path,
            max_age,
        )

        largest_access_age = 0
        n_deletions = 0
        # Start looking from the deepest subdirectories first (topdown=False)
        # so that we can delete their parent directories as we go
        for _, dirs, files, root_fd in os.fwalk(cache_path, topdown=False):
            for filename in files:
                stat = os.stat(filename, dir_fd=root_fd)
                file_size = stat.st_size
                last_access_time = stat.st_atime
                age = now - last_access_time

                # Delete any file that hasn't been accessed in > max_age
                if age > max_age:
                    delete_file(filename, root_fd)
                    n_deletions += 1
                    if not initial_pass:
                        total_size -= file_size
                    if not initial_pass and total_size <= max_cache_size:
                        logger.info(
                            "Cache reduced to %d bytes, clearing complete", total_size
                        )
                        return
                    continue

                # Store the least recently accessed file
                if age > largest_access_age:
                    largest_access_age = age

                if initial_pass:
                    total_size += file_size

            for dirname in dirs:
                delete_dir_if_empty(dirname, root_fd)

        logger.info("Deleted %d files.", n_deletions)
        initial_pass = False
        if total_size > max_cache_size:
            # Assuming that all files are the same size, how many would the
            # excess size require us to delete?
            estimated_fraction_files_to_keep = max_cache_size / total_size
            # Assume that access patterns follow a Pareto distribution
            # ie something like "80% of accesses are for 20% of documents"
            # Where the parameter alpha is 1.8, from
            # http://seelab.ucsd.edu/mobile/related_papers/Zipf-like.pdf
            # We can get the percentile we want by using the Lorenz curve
            # https://en.wikipedia.org/wiki/Pareto_distribution#Lorenz_curve_and_Gini_coefficient
            estimated_age_cutoff_percentile = 1 - pow(
                1 - estimated_fraction_files_to_keep, 1 - (1 / 1.8)
            )
            # Next pass, start deleting files that are in this age percentile
            max_age = largest_access_age * estimated_age_cutoff_percentile
            logger.info(
                "Cache size (%d bytes) exceeds maximum size (%d bytes), decreasing max age to %d seconds",
                total_size,
                max_cache_size,
                max_age,
            )

    logger.info("Cache clearing complete")


if __name__ == "__main__":
    main()
