# wellcome/fake-sns

Wraps https://github.com/elruwen/fake_sns in a container.

Exposes the service on port 9292.

## Usage

```
docker run wellcome/fake-sns
```

Then in your AWS config:

```ruby
AWS.config(
  use_ssl:       false,
  sns_endpoint:  "0.0.0.0",
  sns_port:      9292,
)
```