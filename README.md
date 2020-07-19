# Open Trivia
## Consuming Transifex API for Open Trivia Database

This is a very simple Web application that has been created in order to consume the API of Open Trivia Database and the 
Transifex API.

This application is written in Python 3.7 using Django 3.0.8, using Postgres as the app's database.

In here  you will find the source code and a set of docker configuration files to run this application either locally, 
or in a docker container, both locally (again) or in Docker Swarm.

More technical details for packages used and installation details in the next sections of this document.

### Web application overview

As mentioned above, this simple application offers a way to fetch questions from the Open Trivia Database and upload 
them as resource strings to a Transifex project for translation. 

It has two main pages, one for questions and another for categories.
In order to query Trivia for questions, you need to visit and download all the available categories first. 
Then you can visit the questions' page and fetch questions. The questions that you can fetch can be either of a random 
or a specific category (by using the available categories' list).

After you download some questions from Trivia, you can then select the question to be uploaded to Transifex 
for translation.

**🙌** Of course, you should have an organization, a project and a token already available to do so.

Each question's category will be considered as a possible resource. Questions that belong to different categories will 
be uploaded to different resources.

In the questions page, next to each question there is a label that states if it has been already uploaded or is 
available to be upload.

If you click it, the system will check if the category of this question exists as resource in the Transifex project.

If it doesn't, then it first creates it and the question and its answers are considered as resource strings, and are 
uploaded there.

Since each resource and its resource strings are bind together, it has been asked that if a new source file is uploaded,
 for the same resource, not to remove the strings that are already there.

In order to achieve that, the easiest way was to tag each question that we have already have uploaded. So, when a new
question is to be uploaded we also upload the questions that belong to the same category.

This works only for this prototype application and for a limited amount of questions, until the size of the body is too
big to be handled. A positive thing here is that since there are more than 30 categories, 
and the questions are uniformly distributed, then this effect takes some time to happen.

### Django project

As mentioned above this application is based on Django. The main application is transifex, while there have been added 
one application (pages) for the URL pages (to hold the urls mainly) and another one (trivia) which holds the business
 and data access logic.

Also a template directory is holding the html files.

The requests to the different APIs are separated to two different files in the trivia app. 
Additionally the data access layer to the database is separated in another file.

### What for sure is missing

What is not there is tests. Although there could have been a design 
(i.e. use of the strategic design pattern) in order to create mock tests for the API requests,
I mainly focused on fast learning the Django ecosystem and deliver a concluded web application. 
I felt that at the current point, a test driven development would have
cost me in time, something that was already little.

Also, what is also missing is the complete users' management. 
Any who can access the app will be able to request and download questions from trivia. On the other hand, 
only with valid Transifex token/organization/project will be able to access the 
Transifex API and create resources or upload resource strings.

Btw, as mentioning below, I didn't take advantage of some special calls to the trivia API like retrieving 
a session token or setting special encoding for the language.

### APIs

The APIs and the endpoints that have been used are the following:

#### Trivia

In order to fetch the categories:

    GET https://opentdb.com/api_category.php


In order to fetch questions from random categories:

    GET https://opentdb.com/api.php?amount=10

and the following to get questions from a specific category:

    GET https://opentdb.com/api_count.php?category=CATEGORY_ID_HERE&amount=10

**🙌** Note that the amount of questions in each fetch is limited to 10 at all calls.

Also, no special calls to retrieve, use or reset a session token for avoiding getting the same questions 
(although a check in the models occurs if a question already exists).

Neither calls for other than the default encoding type took place.

#### Transifex

The endpoints that have been consumed from the Transifex API are the following:

In order to get the resources that exist in the current project:

    GET https://rest.api.transifex.com/resources

In order to create a new resource:

    POST https://rest.api.transifex.com/resources

In order to upload resource strings:

    POST https://rest.api.transifex.com/resource_strings_async_uploads

In order to retrieve the status of the resource strings' upload:

    GET https://rest.api.transifex.com/resource_strings_async_uploads/{resource_strings_async_upload_id}

### Provisioning and configuring

**Open Trivia** can be deployed as a [Docker Swarm Stack](https://docs.docker.com/get-started/part5/). 
To do this we need to prepare the ground with a Docker Swarm cluster first.

1. Install Python 3, pip and setuptools, if not already installed:

        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-setuptools

2. Install Docker 18.09, or newer ([docs](https://docs.docker.com/install/linux/docker-ce/ubuntu/))
3. [Enable Swarm mode](https://docs.docker.com/engine/reference/commandline/swarm_init/) on the Docker Engine
4. Install Docker Compose ([docs](https://docs.docker.com/compose/install/))
5. Finally, we need to setup the private (or public) docker registry where the Docker stack can reach 
the image and set the variables `DOCKER_REGISTRY` and `DOCKER_IMAGE_TAG` accordingly.

Lastly, we need to create all required [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/), 
as described below.

If all the above are a ton of work, no worries! Open Trivia can be deployed as a local container 
from the docker compose script. Still, we need to have Docker 18.09, or newer, and Docker Compose installed though.

If none of the above fits us, then we can ultimately install it from the directory as a plain Django application. 
The process to install the application locally is described below.

### Docker Secrets and/or Environmental variables

If we go with the Docker Swarm deployment then the following secrets should be created:

- `transifex-allowed-hosts-v1`: The host names from which you will be able to access Open Trivia (i.e. open-trivia.com)
- `transifex-postgres-user-v1`: The name of the user of Open Trivia's Postgres database (e.g. `postgres`).
- `transifex-postgres-password-v1`: The password of the user of Open Trivia's Postgres database (e.g. `postgres` 
but better if it is created randomly :D ).
- `transifex-postgres-db-v1`: The name of the Postgres database used by Open Trivia (e.g. `trivia`).
- `transifex-postgres-host-v1`: The name of the host where Open Trivia's Postgres is located. 
If it is accessed within the docker network it may be 'postgres' or else 'localhost'.
- `transifex-token-v1`: The API token retrieved for the Transifex project.
- `transifex-organization-v1`: The name of the Transifex organization.
- `transifex-project-v1`: The name of the Transifex project where the resources will be created.

To create each of these secrets, you need to run the following command in your terminal:

     printf "value-of-secret" | docker secret create name-of-your-secret -


Alternatively, if we want to run the application locally or with a local Docker container (that is not Swarm) 
the best approach is to create an env file with all the necessary environment variables. 
A sample `.env.sample` file will be included in this directory.

Copy this file as `.env` in order to run it:

    export $(cat .env | xargs)

and export all the necessary environmental variables.

If we are going to run the docker compose script (with `docker-compose up`) we don't need to change the environments 
that are set in the `docker-compose.override.yml` file (especially the postgres host - `postgres` is the address 
of the host internally the docker network).

### Deployment

In short, what ever is our choice of deployments, the basic steps are the following:

1. Deploy the application.
2. Migrate the database.
3. Enjoy it.


#### Docker Swarm deployment

If all the above requirements for Docker Swarm are fulfilled, then we can run:

    docker-compose build
    docker-compose push
    docker stack deploy -c docker-compose.yml open-trivia --with-registry-auth

This will create a stack with two services, open-trivia-trivia (the app) and open-trivia-postgres (the database).

#### Docker compose deployment

If we cannot deploy to a Docker Swarm environment but we do have docker-compose and we have already exported the 
environmental variables, then we can run:

    docker-compose up

In case we need to do changes and redeploy, run 

    docker-compose up --force-recreate --build

### Local deployment

Before we begin, we might want to setup a virtual environment. Personally I used virtualenv but others 
like pipenv can be used too (as long as we create a Pipfile with the packages). 
Install it with pip and then setup and use it as follows:

On macOS and Linux:

    python3 -m pip install --user virtualenv
    python3 -m venv env
    source env/bin/activate

On Windows (I haven't personally tested this, I just got them from the official docs):

    py -m pip install --user virtualenv
    py -m venv env
    .\env\Scripts\activate

Leave from the virtual environment with 

    deactivate

In the root directory a `requirements.txt` file contains all the necessary dependencies/packages. 
After we create our virtual environment we can install them with

    pip install -r requirements.txt

**🙌** Note that the file `requirements.txt` was produced in the end of the project by using the

    pip freeze

Other than the default dependencies that are added from running the django package I used a couple external ones:

* `sec` a very useful package that reads environmental variables or docker secrets and converts them 
into setting variables.
* `psycopg2` as the PostgreSQL database adapter for the Python 
* `requests` as a simple HTTP library for Python for the http calls to Trivia and Transfix

**Finally**, run the application with 

    python transifex/manage.py runserver

to run it on the default port 8000.


#### Migrate the database

If we have deployed the application with Docker (either Docker Swarm or with docker-compose) 
then we need to enter into the docker container. Let's say that the container's name is `open-trivia`. 
The `manage.py` file should be located into the `transifex` directory, so we run the following command:

    docker exec -it open-trivia python transifex/manage.py migrate

If we want to enable the Admin pages (they are not in use in this webapp) we still can do so:

    docker exec -it open-trivia python transifex/manage.py createsuperuser


If we are running the application locally, then we run correspondingly:

    python transifex/manage.py migrate
    python transifex/manage.py createsuperuser


### Final notes (finally...)

For the development of the Open Trivia application I used VS Code. In order to resolve `pylint` errors 
I had to install `pylint-django` and add a few arguments in the vscode settings. The `pylint` and `pylint-django` 
packages are included in the `requirements.txt` file.
