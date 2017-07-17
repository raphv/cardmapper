# Cardmapper

Cardmapper is a tool to record and augment ideation card based workshops.

## How it works

### 1. Use ideation cards

Use printed ideation cards from one of the decks available here. Set up an ideation workshop and use the cards on a table, flipchart, or wall.

### 2. Turn your ideas into a “Card Map”

Take a photo of the table or wall you've put the cards on, upload it, and match the cards to the database.

### 3. Share your “Card Map”

Make your Card Map public: share the link to take away the outcome of the workshop, and add your Card Map to the database to share your insights with other ideation card users.

## How to try it online?

Go to [cardmapper.eu](http://www.cardmapper.eu/)

## How to install it?

### Requirements

This is an app created with the Python-based Django web framework for the back-end, Bootstrap (presentation), jQuery (effects), and Leaflet (maps) on the front-end.

Django 1.11 is the last version to be compatible with Python 2.7 and will be supported until 2020.
I have used Python 3 throughout development.
I have **not** done anything to make cardmapper compatible with Python 2.
If you need Python 2 compatibility, [check the Django documentation](https://docs.djangoproject.com/en/1.11/topics/python3/)

If running via Apache and ModWSGI, make sure you install the `libapache2-mod-wsgi-py3` module and **not** the (Python 2-compatible) `libapache2-mod-wsgi-py3`.
If you wish to run it on Windows 10, I strongly recommend using the "Ubuntu on Windows" subsystem.

### Install procedure

1. Clone the repository

```
git clone https://github.com/raphv/cardmapper
cd cardmapper
```

2. Create a virtual environment (you need to install python 3 and virtualenv first), run it and install requirements

```
cd cardmapper
virtualenv -p python3 env
source env/bin/activate
```

3. Copy and modify the settings to suit your requirements and database backend

```
cp src/cardmapper/settings.template.py src/cardmapper/settings.py
nano src/cardmapper/settings.py
```

4. Synchronize the database, create an admin user, create the demo deck and run Django's built-in development server

```
cd src
python manage.py migrate
python manage.py createsuperuser
python manage.py create_demo_deck
python manage.py runserver
```

Connect to `http://127.0.0.1:8000/` or whichever IP/port the server is running on.

Connect to `http://127.0.0.1:8000/admin/` to log in and create your own decks and cards.

## Examples of Ideation cards

  * From academic work:
	* [Mixed Reality Game Cards](https://www.pervasiveplayground.com/mixed-reality-game-cards/) by Richard Wetzel (Universities of Nottingham and Lincoln)
    * [Privacy Ideation Cards](https://lachlansresearch.wordpress.com/2015/10/30/privacy-ideation-card-progress/) by Lachlan Urquhart (University of Nottingham)
	* [PLEX Cards](http://www.funkydesignspaces.com/plex/) by Andrés Lucero (University of Southern Denmark and Aalto University)
	* [Envisioning Cards](http://www.envisioningcards.com/) by Batya Friedman (University of Washington) and her colleagues
	* [Design with Intent Cards](http://designwithintent.co.uk/) by Dan Lockton (Royal College of Arts, Carnegie-Mellon University)
	* [Exertion Cards](http://exertiongameslab.org/projects/design-tools-exertion-cards) by Floyd Mueller (RMIT University)
	* [UX Cards](https://uxmind.eu/2016/01/04/ux-cards/) by Carine Lallemand (University of Luxembourg)
	* [IoT Tiles Cards](http://tilestoolkit.io/) by Simone Mora (Norwegian University of Science and Technology)
	* [Security Cards](http://securitycards.cs.washington.edu/) by Tamara Denning and her colleagues (University of Washington)
	* [Growing Data Cards](https://www.horizon.ac.uk/project/growing-data/) by Sarah Martindale, Ben Bedwell (University of Nottingham), Robert Philips and Micaella Pedros (Royal College of Arts)
  * Commercial card sets:
    * [IDEO Method Cards](https://www.ideo.com/post/method-cards)
	* [MethodKit](https://methodkit.com/)

## Newest features

Annotations can be added to card maps.

Self-service account creation has been enabled.
At the moment, you can only use your self-service account to create card maps from existing decks.
If you want to create your own deck, contact me and I'll give your account additional privileges.
Alternatively, clone this repository and set up your own Cardmapper platform.

Deck import scripts have been added.
"Scrapers" to generate decks from existing ideation cards are in a [separate repository](https://github.com/raphv/cardmapper-scrapers/)

## Roadmap

Future work includes:

  * Simplifying tag input with jquery-tagit
  * Adding an authoring interface for decks and cards *(low priority as this is currently available through the admin interface)*
  * Making the database searchable
  * Adding a robust rights management interface *(sharing with a group, sharing through a private URL)*
  * Printing decks from the database
  * Automatic card detection from "card map" images *(using computer vision, with or without the need for printed markers)*
