#wellcome/flake8

Runs `scalafmt` over your code.

Greatly benefits from using your `.sbt` and `.ivy2` cache.

##Usage

```
docker run wellcome/scalafmt:latest \
    --volume=my_code:/repo \
    --volume=$HOME/.sbt:/root/.sbt \
    --volume=$HOME/.ivy2:/root/.ivy2
```
