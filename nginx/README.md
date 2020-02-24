# wellcome/nginx

This container image is intended to work with the services module.

See: https://github.com/wellcomecollection/terraform/tree/master/services

By default this container redirects HTTPS -> HTTP.

This container needs to be started with two environment variables:

- `HTTPS_DOMAIN`: The domain to redirect HTTPS requests to
- `APP_PORT`: The application port to redirect to.
- `NGINX_PORT`: The port nginx should listen on

## Usage

```sh
docker run \
  --env NGINX_PORT=9000 \
  --env HTTPS_DOMAIN=example.com \
  --env APP_PORT=80 \
  wellcome/nginx:latest
```
