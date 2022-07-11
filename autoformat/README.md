# Autoformat

A Docker image containing the absolute minimal tooling to autoformat common Wellcome languages.

## Usage

Run the container providing the environment variable `FORMATTERS`: space-separated list of: `terraform`, `scalafmt`, `black`, `prettier`. By default, the container will run all of them.
