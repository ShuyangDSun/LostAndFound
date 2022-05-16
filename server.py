from flask import Flask, request, redirect, url_for, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from flask import send_file
import mysql.connector

app = Flask(__name__)

# configurations
from config import Config
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']


# error handling
# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('404.html'), 404
#
#
# @app.errorhandler(500)
# def server_internal_error(error):
#     return render_template('500.html'), 500


def get_listings():
    # cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
    # cursor = cnx.cursor()
    #
    # query = "SELECT * FROM listings WHERE is_live=1"
    # cursor.execute(query)
    # listings = cursor.fetchall()
    #
    # cursor.close()
    # cnx.close()
    listings = ((123,234,345,456,567))
    return listings


@app.route('/')
def index():
    if 'username' in session:
        return render_template("index.html", initial=session['username'][0].upper(), listings=get_listings(), login=True)
    else:
        return render_template("index.html", listings=get_listings())


# @app.route('/my_listings')
# def my_listings():
#     if 'username' in session:
#         cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
#         cursor = cnx.cursor()
#
#         query = "SELECT * FROM listings WHERE is_live=1 AND posterid='" + session['username'] + "'"
#         cursor.execute(query)
#         listings = cursor.fetchall()
#
#         cursor.close()
#         cnx.close()
#         if listings:
#             return render_template("my_listings.html", initial=session['username'][0].upper(), login=True, listings=listings)
#         else:
#             return render_template("my_listings.html", initial=session['username'][0].upper(), login=True, messages="You have no listings :)")
#     else:
#         return render_template("my_listings.html", messages="Login to see your listings")
#
#
# @app.route('/archived')
# def view_archived():
#     if 'username' in session:
#         cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
#         cursor = cnx.cursor()
#
#         query = "SELECT * FROM listings WHERE is_live=0 AND posterid='" + session['username'] + "'"
#         cursor.execute(query)
#         listings = cursor.fetchall()
#
#         cursor.close()
#         cnx.close()
#         if listings:
#             return render_template("archived.html", initial=session['username'][0].upper(), login=True, listings=listings)
#         else:
#             return render_template("archived.html", initial=session['username'][0].upper(), login=True, messages="No archived listings here :)")
#     else:
#         return render_template("archived.html", messages="Login to see your archived listings")
#
#
# @app.route('/edit-listing/<postid>', methods=['post'])
# def edit_listing(postid):
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
#                                   database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#
#     query = "UPDATE listings SET item_name=%s, item_location=%s, additional_info=%s WHERE id=%s"
#
#     data = (request.form['item_name'], request.form['item_location'], request.form['additional_info'], postid)
#
#     f = request.files['file']
#     if f.filename != '':
#         query = "UPDATE listings SET item_name=%s, item_location=%s, additional_info=%s, image=%s WHERE id=%s"
#         new_image = f.read()
#         data = (request.form['item_name'], request.form['item_location'], request.form['additional_info'], new_image, postid)
#
#     cursor.execute(query, data)
#     cnx.commit()
#
#     cursor.close()
#     cnx.close()
#
#     return redirect(url_for('my_listings'))
#
#
# @app.route('/archive-listing/<postid>', methods=['get'])
# def archive_listing(postid):
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
#                                   database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#
#     query = "UPDATE listings SET is_live=%s WHERE id=%s"
#     data = (0, postid)
#     cursor.execute(query, data)
#     cnx.commit()
#
#     cursor.close()
#     cnx.close()
#     return redirect(url_for('my_listings'))
#
#
# @app.route('/relist-listing/<postid>', methods=['get'])
# def relist_listing(postid):
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
#                                   database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#
#     query = "UPDATE listings SET is_live=1 WHERE id=%s"
#     data = (postid,)
#     cursor.execute(query, data)
#     cnx.commit()
#
#     cursor.close()
#     cnx.close()
#     return redirect(url_for('view_archived'))
#
#
# @app.route('/register_user_page')
# def register_user_page():
#     username = request.args.get('username')
#     email = request.args.get('email')
#     if username is None:
#         username = ""
#     if email is None:
#         email = ""
#
#     if 'next_url' not in session:
#         session['next_url'] = request.referrer
#
#     return render_template("register_user.html", username=username, email=email, messages=request.args.get('messages'))
#
#
# @app.route('/register_user', methods=['post'])
# def register_user():
#     if not request.form['username'] or not request.form['email'] or not request.form['password']:
#         return redirect(url_for('register_user_page', messages="Please enter all fields"))
#
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#     insert_stmp = 'INSERT INTO users VALUES (%s, %s, %s, %s)'
#
#     hash = generate_password_hash(request.form['password'])
#
#     username = request.form['username']
#     email = request.form['email']
#
#     data = (None, username, email, hash)
#
#     try:
#         cursor.execute(insert_stmp, data)
#         cnx.commit()
#     except mysql.connector.IntegrityError as err:
#         cursor.close()
#         cnx.close()
#
#         message = "Integrity Error"
#
#         # if there are duplicate entries for primary keys
#         if err.msg.split()[-1] == "'users.username_UNIQUE'":
#             message = "Username has already been taken"
#         elif err.msg.split()[-1] == "'users.email_UNIQUE'":
#             message = "Email has already been taken"
#
#         return redirect(url_for("register_user_page", username=username, email=email, messages=message))
#
#     cursor.close()
#     cnx.close()
#     return redirect(url_for("login_page"))
#
#
# @app.route('/login_page')
# def login_page():
#
#     # redirect back to same page
#     if 'next_url' not in session:
#         session['next_url'] = request.referrer
#     if "username" in session:
#         return render_template("login.html", messages=request.args.get('messages'), login=True)
#     else:
#         email = request.args.get('email')
#         if email is None:
#             email = ""
#         return render_template("login.html", email=email, messages=request.args.get('messages'))
#
#
# @app.route('/login', methods=['post'])
# def login():
#     if 'username' in session:
#         return redirect(url_for('index'))
#     elif not request.form['email'] or not request.form['password']:
#         return redirect(url_for('login_page',
#                                 email=request.form['email'], messages="Please enter your password and email"))
#     else:
#         cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
#                                       database=app.config['DB_NAME'])
#         cursor = cnx.cursor()
#
#         cursor.execute("SELECT * FROM users WHERE email='" + request.form['email'] + "'")
#         users = cursor.fetchall()
#
#         if users:
#             user = users[0]
#
#             username = user[1]
#             hash = user[3]
#             if check_password_hash(hash, request.form['password']):
#                 session['username'] = username
#
#                 return redirect(session.pop('next_url', None))
#             else:
#                 # check for password
#                 return redirect(url_for('login_page',
#                                         email=request.form['email'], messages='Incorrect email or password entered'))
#         else:
#             return redirect(url_for('login_page',
#                                     email=request.form['email'], messages='Incorrect email or password entered'))
#
#
# @app.route('/logout')
# def logout():
#     if 'username' in session:
#         session.pop('username', None)
#     return redirect(url_for('index'))
#
#
# @app.route('/create_listing_page')
# def create_listing_page():
#     item_name = request.args.get('item_name')
#     item_location = request.args.get('item_location')
#     additional_info = request.args.get('additional_info')
#
#     if item_name is None:
#         item_name = ""
#     if item_location is None:
#         item_location = ""
#     if additional_info is None:
#         additional_info = ""
#
#     return render_template("create_listing.html",
#                            item_name=item_name, item_location=item_location, additional_info=additional_info,
#                            message=request.args.get('message'), login=('username' in session))
#
#
# @app.route('/create_listing', methods=['post'])
# def create_listing():
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#     insert_stmt = "INSERT INTO listings VALUES (%s, %s, %s, %s, %s, %s, %s)"
#
#     item_name = request.form['item_name']
#     item_location = request.form['item_location']
#     additional_info = request.form['additional_info']
#
#     f = request.files['file']
#     img_data = f.read()
#
#     if item_name is None or item_location is None or f.filename == '':
#         message = ""
#         if item_name == "":
#             message = "Please fill in the item name"
#         elif item_location == "":
#             message = "Please specify the item location"
#         elif f.filename == '':
#             message = "Please upload an image"
#
#         return redirect(url_for("create_listing_page", item_name=item_name, item_location=item_location,
#                                 additional_info=additional_info, message=message))
#
#     data = (None, item_name, item_location, session['username'], additional_info, img_data, 1)
#     cursor.execute(insert_stmt, data)
#     cnx.commit()
#     cursor.close()
#     cnx.close()
#
#     return redirect(url_for("index"))
#
#
# @app.route('/users/<postid>', methods=['get'])
# def get_image(postid):
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#
#     query = "SELECT * FROM listings WHERE id=%s"
#     data = (postid,)
#     cursor.execute(query, data)
#     listings = cursor.fetchall()
#
#     cursor.close()
#     cnx.close()
#
#     # send file
#     bytes_io = BytesIO(listings[0][5])
#
#     return send_file(bytes_io, mimetype='image/jpeg')
#
#
# @app.route('/contact/<postid>', methods=['get'])
# def get_listing(postid):
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
#                                   database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#
#     query = "SELECT * FROM listings WHERE id=%s"
#     data = (postid,)
#     cursor.execute(query, data)
#     listings = cursor.fetchall()[0]
#
#     cursor.close()
#     cnx.close()
#
#     if 'username' in session:
#         return render_template("listing.html", login=True, initial=session['username'][0].upper(), listing=listings)
#     else:
#         return render_template("listing.html", listing=listings)
#
#
# @app.route('/contact/send-messages/<postid>', methods=['post'])
# def send_messages(postid):
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#
#     query = "INSERT INTO messages VALUES (%s, %s, %s, %s)"
#     data = (None, postid, session['username'], request.form['message'])
#     cursor.execute(query, data)
#     cnx.commit()
#
#     cursor.close()
#     cnx.close()
#
#     d = {'message': "success"}
#     return d
#
#
# @app.route('/contact/get-messages/<postid>', methods=['get'])
# def get_messages(postid):
#     cnx = mysql.connector.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
#     cursor = cnx.cursor()
#
#     query = "SELECT senderid, message FROM messages WHERE postid=%s"
#     data = (postid,)
#     cursor.execute(query, data)
#     messages = cursor.fetchall()
#
#     cursor.close()
#     cnx.close()
#
#     d = {"messages": []}
#     for sender, message in messages:
#
#         if 'username' in session:
#             if sender != session["username"]:
#                 d["messages"].append({"sender": sender, "message": message, "is_sender": False})
#             else:
#                 d["messages"].append({"sender": sender, "message": message, "is_sender": True})
#         else:
#             d["messages"].append({"sender": sender, "message": message, "is_sender": False})
#     return d


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')  # use 0.0.0.0, allow access this app from my cell phone
