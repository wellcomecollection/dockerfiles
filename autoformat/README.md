# Autoformat

A Docker image containing the absolute minimal tooling to autoformat common Wellcome languages.

## Usage

Run the container providing the environment variable `FORMAT_LANGUAGES`: space-separated list of: `hcl`, `scala`, `python` , `js`. When these are present, the container will run `terraform fmt`, `scalafmt`, `black` and `prettier`, respectively.
