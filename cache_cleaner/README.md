# cache_cleaner

This service allows us to purge a filesystem cache based on the age and size of items.

Some of our ECS applications use local storage as a cache (for example, Loris).
Because ECS instances have very little disk space, we use an EBS mount rather than the host disk.
However, because EBS volumes are bounded in size, we need to delete files occasionally to prevent the volumes from filling up.

Our caches are bounded by two parameters:

*   **maximum age** -- if an item is in the cache but hasn't been accessed for more than 30 days, there isn't much value in keeping it in the cache.
    We can delete it, and re-fetch it the next time it's requested.

*   **maximum size** -- if the cache exceeds a given size, we can delete items from the cache until it comes back under the limit.
    Items are deleted in order of last access time -- items which haven't been accessed very recently are deleted first.

Both of these parameters are configurable.

Cache cleaner can optionally repeat executions at a timed interval if ```CLEAN_INTERVAL``` is set.

*   **CLEAN_INTERVAL** -- the time to wait between cleanups, argument is as for sleep (e.g., 1s, 1m, 1h). To run once only do not set, or set to 0.

## Usage

Build the Docker image containing the script:

```console
$ docker build -t cache_cleaner .
```

To run the script, share the cache directory with the container and pass parameters as environment variables:

```console
$ docker run -v /path/to/cache:/data -e MAX_AGE=30 -e MAX_SIZE=5000000 cache_cleaner
```

or to repeat every 10 minutes

```console
$ docker run -v /path/to/cache:/data -e MAX_AGE=30 -e MAX_SIZE=5000000 -e CLEAN_INTERVAL=10m cache_cleaner
```
