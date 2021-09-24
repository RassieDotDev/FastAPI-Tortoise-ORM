# Basic FastAPI with Tortoise-ORM implementation
## Intro details
This application is a basic CRUD and Login of a user with email token authentication.
We are using SendGrid as a mailer, Tortoise-ORM as the Object Relation Mapper and
Aerich to manage the migrations.

THe sweet part of it all is that Tortoise-ORM generates the schema's for you instead
of manually defining them when you use SqlAlchemy.

Bear in mind that the mail sent with the token is just a placeholder so that you can
include your frontend URL. You can use regex to extract the UUID and make a POST call to the
API with the UUID to Activate your user.


### Pre-flight Check:
Ensure that all you have completed the following

#### Add SendGrid API Key
Add your SendGrid API Key to the docker-compose file. Feel free to move it to a .env file
A .env file is a great way to stash all your keys

#### Add your FROM Email
Under `app > helpers > mail` Add your FROM email

### Build & Run Application
Run the following
`docker-compose up --build`

