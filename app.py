import os
from flask import Flask, flash, redirect, render_template, request, session, jsonify,g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
from datetime import datetime


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['TEMPLATES_AUTO_RELOAD'] = True
Session(app)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def dict_factory(cursor, row):
    fields = [x[0] for x in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("account.db")
        g.db.row_factory = dict_factory
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


con = sqlite3.connect("account.db")
con.row_factory = dict_factory
cur = con.cursor()

# [ - >>>>>   session.pop(key) for key in list(session.keys())]


# These are the tabbles:

cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, password TEXT NOT NULL)')
con.execute('CREATE TABLE IF NOT EXISTS sheets (sheet_id INTEGER PRIMARY KEY AUTOINCREMENT, song_id INTEGER NOT NULL, user_id INTEGER NOT NULL, sheet_url TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (song_id) REFERENCES songs (song_id), FOREIGN KEY (user_id) REFERENCES songs (user_id))')
cur.execute('CREATE TABLE IF NOT EXISTS songs (user_id INTEGER NOT NULL, song_id INTEGER PRIMARY KEY , title TEXT NOT NULL, description TEXT NOT NULL, background_url TEXT, video_url TEXT)')
con.commit()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():  
    if not session.get("user_id"):
        return render_template("login.html")
    
    if request.method == "GET":
        db = get_db()
        cur = db.cursor()
        songs = cur.execute(''' SELECT * FROM songs WHERE user_id = ?''', (session['user_id'],)).fetchall()
        song = cur.execute('''SELECT * FROM songs WHERE user_id = ?''',(session["user_id"],)).fetchall()

        if not songs:
            return render_template('start.html')
        else:
            return render_template('index.html', songs=songs, song=song, length=len(song))
            
    else:
        if len(request.form.get('title')) < 43 and len(request.form.get('description')) < 609 and len(request.form.get('title')) > 0:
            db = get_db()
            cur = db.cursor()
            cur.execute(''' INSERT INTO songs (user_id, title, description) VALUES (?, ?, ?)''', ( session["user_id"], request.form.get('title'), request.form.get('description')))
            songs = cur.execute(''' SELECT * FROM songs ''').fetchall()
            db.commit()
            last = cur.execute("SELECT song_id FROM songs ORDER BY ROWID DESC LIMIT 1").fetchone()["song_id"]
            
            return redirect('/song_page/' + str(last))
        else:
            return redirect("/")
        
        
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", "error")
            return redirect("/register")
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", "error")
            return redirect("/register")

        # Ensure the (again) password was submitted
        elif not request.form.get("confirmation"):
            flash("Must confirm password", "error")
            return redirect("/register")

        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match", "error")
            return redirect("/register")

        # Check if the username already exists
        db = get_db()
        cur = db.cursor()
        cur.execute('''SELECT username FROM users WHERE username = ?''', (request.form.get("username"),))
        if cur.fetchone():
            flash("Username already taken", "error")
            return redirect("/register")

        # Insert the new user
        hashed_password = generate_password_hash(request.form.get("password"))

        cur.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', (request.form.get("username"), hashed_password))
        db.commit()

        # Redirect to login page after successful registration
        return redirect("/")

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", "error")
            return redirect("/login")
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", "error")
            return redirect("/login")

        # Query database for username
        db = get_db()
        cur = db.cursor()
        cur.execute('''SELECT * FROM users WHERE username = ?''', (request.form.get('username'),))
        result = cur.fetchone()

        if result is None:
            flash("Invalid username", "error")
            return redirect("/login")

        # Validate password (simple comparison for now)
        if not check_password_hash(result["password"], request.form.get("password")):
            flash("Invalid password", "error")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = result["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/song_page/<int:id>", methods=["GET", "POST"])
def song_page(id):
    if request.method == "GET":
        db = get_db()
        cur = db.cursor()
        
        # Fetch all songs for the user
        song = cur.execute('''SELECT * FROM songs WHERE user_id = ?''', (session["user_id"],)).fetchall()
        
        # Fetch the details for the specific song
        specific_song = cur.execute(
            '''SELECT * FROM songs WHERE song_id = ? AND user_id = ?''',
            (id, session["user_id"])
        ).fetchone()

        # If the specific song does not exist, return 404
        if not specific_song:
            return "<h1>404, page not found</h1>", 404

        # Prepare the backgrounds list
        backgrounds = [{"id": id, "url": specific_song.get("background_url", "/static/teste1.png")}]

        youtube = None
        video = None

        # Debugging: Print the backgrounds list
        url = backgrounds[0]['url']
        video_url = cur.execute('SELECT video_url FROM songs WHERE song_id = ? AND user_id = ?', (id, session["user_id"])).fetchone()['video_url']
        ur = cur.execute('SELECT * FROM songs WHERE song_id = ? AND user_id = ?', (id, session["user_id"])).fetchone()
        print(ur)

        if video_url != None:
            if video_url[8:23] == 'www.youtube.com':
                youtube = video_url 
            else:
                video = video_url

        sheets = cur.execute("""SELECT * FROM sheets WHERE song_id = ? AND user_id = ? ORDER BY created_at ASC""", (id, session['user_id'])).fetchall()

        if not specific_song:
            return "<h1>404, page not found</h1>", 404
        
        length = cur.execute('SELECT * FROM songs').fetchall()

        song_id = id

        return render_template(
            "song_page.html",
            song=song,
            length=len(song),
            title=specific_song["title"],
            description=specific_song["description"],
            backgrounds=backgrounds, url=url, video=video, video_url=video_url, youtube=youtube, sheets=sheets, song_id=song_id
        )

    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

        db = get_db()
        cur = db.cursor()

        # Fetch the background URL for the song being deleted
        background = cur.execute(
            "SELECT background_url FROM songs WHERE song_id = ? AND user_id = ?", 
            (request.view_args['id'], session["user_id"])
        ).fetchone()

        # If a background image exists, delete it from the filesystem
        if background and background["background_url"]:
            file_path = os.path.normpath(os.path.join(base_dir, background["background_url"].lstrip("/"))) 
            
            try:
                os.remove(file_path)

            except FileNotFoundError:
                pass  # If the file doesn't exist, ignore the error
        
        sheets = cur.execute(
            "SELECT * FROM sheets WHERE song_id = ? AND user_id = ?", 
            (request.view_args['id'], session['user_id'])
        ).fetchall()

        # If a background image exists, delete it from the filesystem

        if sheets:
            for sheet in sheets:
                file_path = os.path.normpath(os.path.join(base_dir, sheet["sheet_url"].lstrip("/"))) 

                try:
                    os.remove(file_path)

                except FileNotFoundError as e:
                    pass

        # Delete the song from the database
        cur.execute("DELETE FROM songs WHERE song_id = ? AND user_id = ?", (request.view_args['id'], session["user_id"]))
        cur.execute("DELETE FROM sheets WHERE song_id = ? AND user_id = ?", (request.view_args['id'], session["user_id"]))
        db.commit()

        try:
            last = cur.execute(
                "SELECT song_id FROM songs WHERE user_id = ? ORDER BY ROWID DESC LIMIT 1", 
                (session["user_id"],)
            ).fetchone()["song_id"]
            return redirect('/song_page/' + str(last))
        except TypeError:
            return redirect('/')


@app.route("/edit/<id>", methods = ["GET", "POST"])
def edit(id):
    if request.method == "GET":
        return redirect("/")
    
    if request.method == "POST":

        if len(request.form.get('title')) < 43 and len(request.form.get('description')) < 609:
            db = get_db()
            cur = db.cursor()

            if len(request.form.get('title')) > 0:
                cur.execute("UPDATE songs SET title = ? WHERE song_id = ?", (request.form.get('title'), id))
            
            elif len(request.form.get('description')) > 0:
                db = get_db()
                cur = db.cursor()
                cur.execute("UPDATE songs SET description = ? WHERE song_id = ?", (request.form.get('description'), id))
                
            db.commit()
            return redirect('/song_page/' + id)
        else:
            return redirect('/')


@app.route("/upload_background/<int:id>", methods=["POST"])
def upload_background(id):
    """Handle background image upload for a song."""
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"error": "No file selected"}, 400

    # Define the upload folder relative to the project directory
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
    upload_folder = os.path.join(base_dir, "static", "uploads")  # Ensure the folder is inside "bruh/static/uploads"
    
    # Ensure the static/uploads directory exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Get the previous background URL from the database
    db = get_db()
    cur = db.cursor()
    old_background = cur.execute(
        "SELECT background_url FROM songs WHERE song_id = ? AND user_id = ?", 
        (id, session["user_id"])
    ).fetchone()

    # If a previous background exists, delete the file
    if old_background and old_background["background_url"]:
        old_file_path = os.path.join(base_dir, old_background["background_url"].lstrip("/"))
        
        # Debugging: Print the path of the old file being deleted
        print(f"Attempting to delete old file: {old_file_path}")

        try:
            os.remove(old_file_path)  # Remove the file if it exists
            print(f"Deleted file: {old_file_path}")
        except FileNotFoundError:
            print(f"File not found for deletion: {old_file_path}")  # Log if the file is not found
        except Exception as e:
            print(f"Error deleting file: {e}")  # Log other errors

    # Save the file with a unique name
    filename = f"background_{id}_{file.filename}"
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # Generate the URL relative to the static directory
    url_path = f"/static/uploads/{filename}"  # This is the path accessible by the browser

    # Update the background URL in the database
    cur.execute(
        "UPDATE songs SET background_url = ? WHERE song_id = ? AND user_id = ?",
        (url_path, id, session["user_id"]),
    )

    db.commit()
    return {"message": "Background updated successfully"}, 200


@app.route("/upload_sheet/<int:song_id>", methods=["POST"])
def upload_sheet(song_id):
    try:
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "No file selected"}, 400

        # Define the upload folder relative to the project directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.join(base_dir, "static", "sheets")
        
        # Ensure the static/sheets directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Save the file with a unique name
        filename = f"sheet_{song_id}_{file.filename}"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Generate the URL relative to the static directory
        sheet_url = f"/static/sheets/{filename}"

        # Insert the sheet information into the database
        db = get_db()
        cur = db.cursor()
        
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "User not logged in"}, 403

        # # Determine the(last_position or 0) + 1

        cur.execute(
            """
            INSERT INTO sheets (song_id, user_id, sheet_url, sheet_position)
            VALUES (?, ?, ?, ?)
            """,
            (song_id, user_id, sheet_url, 1)
        )
        db.commit()

        return {
            "message": "Sheet uploaded successfully",
            "sheet_url": sheet_url,
            "sheet_position": 1
        }, 200

    except Exception as e:
        # Log the detailed error for debugging
        print(f"Error during upload_sheet: {e}")
        return {"error": "An internal error occurred", "details": str(e)}, 500



@app.route("/delete_sheet/<int:sheet_id>", methods=["DELETE"])
def delete_sheet(sheet_id):
    db = get_db()
    cur = db.cursor()

    # Fetch the sheet's file path
    sheet = cur.execute("SELECT sheet_url FROM sheets WHERE sheet_id = ? AND user_id = ?", (sheet_id, session["user_id"])).fetchone()

    if not sheet:
        return {"error": "Sheet not found"}, 404

    print(sheet["sheet_url"])
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Base directory of the project
    full_file_path = os.path.join(base_dir, sheet["sheet_url"].lstrip("/"))

    try:
        # Attempt to delete the file
        os.remove(full_file_path)
        print(f"Deleted file: {full_file_path}")
    except FileNotFoundError:
        print(f"File not found: {full_file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")
        return {"error": "Failed to delete file"}, 500


    # Remove the sheet record from the database
    cur.execute("DELETE FROM sheets WHERE sheet_id = ? AND user_id = ?", (sheet_id, session["user_id"]))
    db.commit()

    return {"message": "Sheet deleted successfully"}, 200

@app.route('/upload_video/<songId>', methods=['POST'])
def upload_video(songId):
    data = request.json  # Parse JSON from the request body
    video_url = data.get("video_url")
    
    db = get_db()
    cur = db.cursor()
    cur.execute('UPDATE songs SET video_url = ?', ( video_url,))

    res = cur.execute('SELECT * FROM songs').fetchone()
    print(res)
    db.commit()
    # Respond with success
    return jsonify({"message": "Video URL saved successfully"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
