import errno
import os
import re


def parse_max_cache_size_arg(value):
    m = re.match(r"([0-9]+)([KMGT])", value)
    if m is not None:
        size = int(m.group(1))
        suffix = m.group(2)
        if suffix == "K":
            return size * 1024
        elif suffix == "M":
            return size * 1024 * 1024
        elif suffix == "G":
            return size * 1024 * 1024 * 1024
        elif suffix == "T":
            return size * 1024 * 1024 * 1024 * 1024
    return int(value)


def delete_file(name, dir_fd):
    if os.environ.get("X-RUN-CACHE-CLEANER"):
        try:
            os.unlink(name, dir_fd=dir_fd)
        except FileNotFoundError:
            pass


def delete_dir_if_empty(name, dir_fd):
    if os.environ.get("X-RUN-CACHE-CLEANER"):
        try:
            os.rmdir(name, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        except OSError as e:
            if e.errno == errno.ENOTEMPTY:
                pass
            else:
                raise


def get_file_stats(name, dir_fd, now):
    stat = os.stat(name, dir_fd=dir_fd)
    file_size = stat.st_size
    last_access_time = stat.st_atime
    age = now - last_access_time
    return file_size, age


def get_new_max_age(largest_age, max_size, current_size):
    # Assuming that all files are the same size, how many would the
    # excess size allow us to keep?
    estimated_fraction_files_to_keep = max_size / current_size
    # Assume that access patterns follow a Pareto distribution
    # ie something like "80% of accesses are for 20% of documents"
    #
    # We can approximate that the distribution of ages is similar
    # to the distribution of document requests, where the latter
    # is seen to be a Zipf distribution with a parameter of 0.8:
    # http://seelab.ucsd.edu/mobile/related_papers/Zipf-like.pdf
    #
    # Following the relation between the Zipf and Pareto distributions,
    # this makes our alpha for the Pareto distribution 1.8
    # https://en.wikipedia.org/wiki/Pareto_distribution#Relation_to_Zipf's_law
    #
    # Thus, we can get the cutoff percentile of ages using the Lorenz
    # curve for the Pareto distribution:
    # https://en.wikipedia.org/wiki/Pareto_distribution#Lorenz_curve_and_Gini_coefficient
    estimated_age_cutoff_percentile = 1 - pow(
        1 - estimated_fraction_files_to_keep, 1 - (1 / 1.8)
    )
    # Next pass, start deleting files that are in this age percentile
    return largest_age * estimated_age_cutoff_percentile
