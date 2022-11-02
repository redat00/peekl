<div align=center>
<img src="./logo.png" height="100"/>

</br>

[![Python 3.10.6](https://img.shields.io/badge/python-3.10.6-blue.svg)](https://www.python.org/downloads/release/python-3106/)



</div>

## Table of contents

1. [Get started](#get-started)
2. [Installation](#installation)
    - [The Docker way](#the-docker-way)
    - [The manual installation way](#the-manual-installation-way)
4. [Configuration](#configuration)

## Get started

Peekl (pronounced like pickle) is a small and simple HTTP and certificate monitoring application developed in Python capable of sending alert to your preferred solution. It is developed using Python and RedisTimeSeries for storing data.

To get started with using Peekl, you can do it two ways : 

- Use the official Peekl docker image
- Or install it on a host and run it as service

The easiest way to get started is going the Docker way. Doing so will prevent you from having to manage a Python environment for the application. But if you're okay with the idea of using Python it is totally possible.

> :warning: In both case Peekl will require an accessible Redis database running with the RedisTimeSeries module in order to store timeseries data, as well as other data.
***

## Installation
### The Docker way

To spin up the application using Docker, we recommand you to create a docker-compose file. In this file you will need to declare two services : 

- A Redis service (with the RedisTimeSeries image)
- A Peekl service

> :warning: In this docker-compose.yaml file, we recommand you to set a link to the Redis container. In docker-compose syntax, a link looks like this : `redis:redis`. The first word correspond to the service name in the docker-compose. And the second one is the name that will be used inside the container to contact the first service.

```yaml
version: "3.9"
services:
  peekl:
    image: "redat00/peekl"
    links:
      - "redis:redis"
    volumes:
      - ./config.yaml:/usr/src/app/config.yaml

  redis:
    ports:
      - "6379:6379"
    image: "redislabs/redistimeseries"
```

> :warning: Exposing the Redis port is not an obligation, but can be useful when you're trying to debug the application, and see what is stored inside of it. If you're already using the 6379 port on your machine, you can remove the port exposition.

You can see for the Peekl service that we have a `config.yaml` file being passed to the container. This is a mandatory file. You can go to the Configuration section of this documentation to see how to configure Peekl.

Once this file is created, and you're ready, you can just spin up the app : 

```bash
docker-compose up -d
```

To make sure that the application is successfully running, you can check the logs of the Peekl container. You would have an output that look like this : 

```bash
2022-11-02 13:20:04.048 | INFO     | Starting Peekl worker...
2022-11-02 13:20:04.050 | INFO     | Successfully loaded configuration file : config.yaml
2022-11-02 13:20:04.067 | INFO     | Starting HTTP monitoring daemon for https://example.com ..
2022-11-02 13:20:04.068 | INFO     | Peekl worker successfully started.
```
***
### The manual installation way

The other to run Peekl is to install it from sources.

> :warning: This project uses Poetry. In order to build the packages from source you will need to have it installed as well. You can find information on how to install Poetry [here](https://python-poetry.org/docs/#installation).

The current version that this project uses is Python 3.10.6. We can't assure you that this will work under another Python version. And to make it easier, we will assume that it doesn't and we won't give support if your Python version is not one that we recommend.

Once the correct version of Python is installed, and Poetry is as well, you simply have to run the following command : 

```bash
poetry build
```

This command will create a `*.tar.gz` file as well as a `*.whl` file in `dist/` directory. You can install the package with any of those to file, simply using pip like this : 

```bash
pip install dist/peekl-*-.tar.gz
```

> :warning: You should replace the `*` character by the current version of the application.

To make sure that peekl is installed, you can run the `peekl --help` command, and you should have an output similar to this one:

```bash
~> peekl --help                             
Usage: peekl [OPTIONS]

  Main command entrypoint for Peekl.

  Args:     config_file: str representation of a file path

Options:
  -c, --config-file PATH  path of the configuration file of the application
                          [required]
  --help                  Show this message and exit.
```

We recommand creating systemd unit file in order for this application to be restarted and properly used as a service. 

First we will create a systemd unit file. (Make sure you have root access to create this file.) 

```bash
sudo vim /etc/systemd/system/peekl.service
```

Then in this file we will copy the following content.

```toml
[Unit]
Description=Peekl Service

[Service]
ExecStart=/usr/local/bin/peekl -c /path/to/config/config.yaml
Restart=always

[Install]
WantedBy=multi-user.target
```

Then just reload systemctl, start and enable your service.

```bash
sudo systemctl daemon-reload
sudo systemctl start peekl.service
sudo systemctl enable peekl.service
```

## Configuration

TODO