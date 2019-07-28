#!/bin/bash

IMAGE=$(docker build -q ../) docker-compose up
