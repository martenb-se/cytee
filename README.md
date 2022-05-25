# cytee (Urangutest)

## Demo
![Image of the prototype](https://github.com/martenb-se/cytee/blob/main/docs/cytee.png)

## Requirements
### Software
* **Docker Compose**, [Installation instructions](https://docs.docker.com/compose/install/).

## Install
### Clone
Clone the repository
```
$ git clone git@github.com:martenb-se/cytee.git
```

### Preparation
In order to run Cytee using Docker the following must be prepared.

#### Host Project Folder
In [docker-compose.yml:19](https://github.com/martenb-se/cytee/blob/main/docker-compose.yml), 
change the `[EDIT-ME]` to the directory where projects you want to analyze are 
listed. For example, if your JavaScript projects are in 
`/home/Urangutest/Projects`, then change line 19 to:
```yaml
      - /home/Urangutest/Projects:/mnt/host-share
```
and Cytee will be able to analyze your projects.

#### Database Settings
There's no need to change the database settings when running inside the
Docker container. It is okay to keep `/docker/db.config.yml` as it is. 
Further, there's no need to change anything in `docker-compose.yml` on line
7 or 8.

## Run (and build if necessary)
Go to the main directory for Cytee and just type:
```
$ docker-compose up
```
If the container has not yet been built, it will then be built before running 
it. If you have already built it, and used it to create tests for projects, 
then the command will just run Cytee (and you can continue creating tests
for your projects).

Now open Cytee at: http://127.0.0.1:3000

## Stop
Just send an interrupt signal to the running container (CTRL+C) or 
tell Docker to stop the containers via the following command:
```
$ docker container stop cytee-api cytee-database cytee-client
```

## Uninstall
In order to remove Cytee completely, on Linux, perform the following.

Verify that the containers `cytee-api`, `cytee-database` and `cytee-client` 
are stopped:
```
$ docker container ls --all
```

..otherwise, stop the containers:
```
$ docker container stop cytee-api cytee-database cytee-client
```

Remove the containers:
```
$ docker container rm cytee-api cytee-database cytee-client
```

Remove the built images:
```
$ docker image rm cytee-client cytee-api
```

Remove any dangling image left from the build process:
```
$ docker rmi $(docker images -f "dangling=true" -q)
```