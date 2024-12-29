# _Music Mindspace_
####  Video demo: https://www.youtube.com/LINKDOVIDEO 

####  The project 
Music Mindspace is a web application That allows people to add songs that they want to learn or that you learned. Each song can have a background image, a video added by an Youtube URL or a file, sheet music, title and description for the songs. To enter in the site you need to register an username and a password and then log in the site. This site makes it easy to see all the songs that you want to play in one place.

# CS50
> Languages used:  `Python , JavaScript , HTML and CSS`.

# The database
The website has 3 databases:

## Table users
The table users is used to store all the users that register in the site, each having an unique id and username.
```
id INTEGER PRIMARY KEY
username TEXT NOT NULL
password TEXT NOT NULL
```

## Table songs
The table songs is used to store the songs that each user add in the site. Storing an unique song_id for each song, the user_id to identify the user, the title of the song, the description to write anythin about the song, a background_url for the background image for that song and a video_url for the video displayed at the page of that song.
```
user_id INTEGER NOT NULL
song_id INTEGER PRIMARY KEY 
title TEXT NOT NULL
description TEXT NOT NULL
background_url
video_url
```

## Table sheets
The table sheets is used to store the all the sheet music that the user adds for that song, storing the sheet_id to to uniquely identify that sheet, sheet_url to store the image of that sheet,created_at to store what moment that sheet was added, and other columns are to identify who is the user. 
```
sheet_id INTEGER PRIMARY KEY AUTOINCREMENT
song_id INTEGER NOT NULL
user_id INTEGER NOT NULL
sheet_url TEXT NOT NULL
sheet_position INTEGER NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
FOREIGN KEY (song_id) REFERENCES songs (song_id)
FOREIGN KEY (user_id) REFERENCES songs (user_id)
```

## Source Files
account.db - The database of the project
app.py - It contains the flask framework used to create the web application in Python

###Static
index.css - Is the main css, it styles the almost all of the pages of the site, with exception of the login and register pages.
login-register.css - It styles the login and register pages.
inde.js - It has the script of almost all the pages of the site.

###Templates
layout.html - The layout of the page, that is extended with other files for better organization
register.html - The register page, when you still don't have an account in the site
login.html - The login page, when you have an account to enter in the site
start.html - The page when you log in and has no song added 
index.html - The page when you log in and already ha a song added
song_page.html - The page of the song added















