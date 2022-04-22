# literate-parakeet

## A simple django project intended to demonstrate Python and Django skills

This project is built upon Django, Django REST Framework and Django REST framework JSON:API

## Quickstart
The following assumes you have `docker` and `docker-compose` installed

```bash
# Start project
docker-compose up
# Create superuser to be able to access Django Admin interface
docker exec -it djangochallenge_web python manage.py createsuperuser
```

## Usage
When you are set up and running, you should have access the following urls:

http://localhost:8000/projects/ - A list of github projects

http://localhost:8000/projects/'id'/ - A detail endpoint for particular github project, where 'id' is the 'id' of the project

http://localhost:8000/webhooks/ - A list of configured webhooks for current authenticated user

http://localhost:8000/webhooks/'id'/ - A detail endpoint for particular webhook, where 'id' is the 'id' of the webhook

http://localhost:8000/admin/ - A simple Django Admin interface to navigate and manage Projects, Webhooks, Users and Tokens

## Description
The purpose of the system is to store interesting Github projects

- All users are able to list github projects. Listing
of the project entries are paginated so that there is 10 items on a page
- Query string parameters can be used to sort project entries
- Authenticated users are able to create, modify and delete project entries
- Authenticated users are able to configure (list, create, update and delete) webhooks that would get called when a new project entry is added to database by any user. Payload of that webhook is the same as the actual entry in JSON format
- Users are authenticated with a token in Authorization request header, eg. Authorization: Token foobar
- Django admin is able to create new users and tokens from Django Admin panel
- Webhooks are send outside of the request response cycle
