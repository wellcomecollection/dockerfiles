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
