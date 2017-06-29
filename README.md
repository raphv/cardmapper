# Cardmapper

Cardmapper is a tool to record and augment ideation card based workshops.

## How it works

### 1. Use ideation cards

Use printed ideation cards from one of the decks available here. Set up an ideation workshop and use the cards on a table, flipchart, or wall.

### 2. Turn your ideas into a �Card Map�

Take a photo of the table or wall you�ve put the cards on, upload it, and match the cards to the database.

### 3. Share your �Card Map�

Make your Card Map public: share the link to take away the outcome of the workshop, and add your Card Map to the database to share your insights with other ideation card users.

## Roadmap

Deck import scripts have been added.
"Scrapers" to generate decks from existing ideation cards are in a separate repository at [https://github.com/raphv/cardmapper-scrapers/]

Future work includes:

  * Adding user registration *(will be done using django-allauth)*
  * Simplifying tag input with jquery-tagit
  * Adding/editing annotations
  * Nicer markers on card maps
  * Adding an authoring interface for decks and cards *(low priority as this is currently available through the admin interface)*
  * Making the database searchable
  * Adding a robust rights management interface *(sharing with a group, sharing through a private URL)*
  * Printing decks from the database
  * Automatic card detection from "card map" images *(using computer vision, with or without the need for printed markers)*