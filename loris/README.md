# loris

This is a Docker image for the [Loris IIIF image server][loris]. Unlike the existing [loris-docker][loris-docker] project, this is intended to be a production-ready image. It runs [Loris v2.1.0][v210], which implements [IIIF Image API 2.0][iiif].

[loris]: https://github.com/loris-imageserver/loris
[loris-docker]: https://github.com/loris-imageserver/loris-docker
[v210]: https://github.com/loris-imageserver/loris/releases
[iiif]: http://iiif.io/api/image/2.0/

## Using the image

The image is available on Docker Hub:

    $ docker run -d -p 8888:80 wellcome/loris
    ✨🐳✨

This starts the container, which is now running a IIIF Image server on port 8888. You can visit <http://localhost:8888/V0017059.jpg/full/full/0/default.jpg> in a browser to see an image being served via Loris!

Currently this serves images over HTTP from the root of this GitHub repo. To use your own Loris configuration file:

    $ docker run -d -p 8888:80 -v /path/to/loris2.conf:/opt/loris/etc/loris2.conf wellcome/loris

Instructions for writing a Loris configuration file [are in the Loris repo][config].

[config]: https://github.com/loris-imageserver/loris/blob/development/doc/configuration.md

## License

Code: MIT.
