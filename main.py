from flask import Flask, request, redirect, url_for, render_template, session
from flask import send_file
import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin import storage
import uuid
import datetime

app = Flask(__name__)

# Initialize Firestore
cred = credentials.Certificate("./lost-and-found-38a87-firebase-adminsdk-werec-2e2149d6fd.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'lost-and-found-38a87.firebasestorage.app'
})
db = firestore.client()

# Initialize Cloud Storage
bucket = storage.bucket()

# error handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_internal_error(error):
    return render_template('500.html'), 500


def get_listings():
    try:
        listings_ref = db.collection('listings')
        query = listings_ref.where('is_live', '==', True).order_by('created_at', direction=firestore.Query.DESCENDING)
        
        listings = []
        for doc in query.stream():
            listing_data = doc.to_dict()
            listing_data['id'] = doc.id
            listings.append(listing_data)
        
        print(f"Listings: {listings}")
        return listings
    except Exception as e:
        print(f"Error fetching listings: {e}")
        return []


@app.route('/', methods=['get'])
def index():
    if 'username' in session:
        return render_template("index.html", initial=session['username'][0].upper(), listings=get_listings(), login=True)
    else:
        return render_template("index.html", listings=get_listings())


@app.route('/my_listings')
def my_listings():
    if 'username' not in session:
        return render_template("my_listings.html", 
            messages="Login to see your listings")
    
    try:
        listings_ref = db.collection('listings')
        query = listings_ref.where('poster_id', '==', session['uid'])\
                          .where('is_live', '==', True)\
                          .order_by('created_at', direction=firestore.Query.DESCENDING)
        
        listings = []
        for doc in query.stream():
            listing_data = doc.to_dict()
            listing_data['id'] = doc.id
            listings.append(listing_data)
        print(f"Listings: {listings}")
        
        if listings:
            return render_template("my_listings.html", 
                initial=session['username'][0].upper(), 
                login=True, 
                listings=listings)
        else:
            return render_template("my_listings.html", 
                initial=session['username'][0].upper(), 
                login=True, 
                messages="You have no listings :)")

    except Exception as e:
        print(f"Error fetching listings: {e}")
        return render_template("my_listings.html", 
            initial=session['username'][0].upper(), 
            login=True, 
            messages="Error fetching listings")


@app.route('/archived')
def view_archived():
    if 'username' not in session:
        return render_template("archived.html", 
            messages="Login to see your archived listings")
    
    try:
        listings_ref = db.collection('listings')
        query = listings_ref.where('poster_id', '==', session['uid'])\
                          .where('is_live', '==', False)\
                          .order_by('created_at', direction=firestore.Query.DESCENDING)
        
        listings = []
        for doc in query.stream():
            listing_data = doc.to_dict()
            listing_data['id'] = doc.id
            listings.append(listing_data)

        if listings:
            return render_template("archived.html", 
                initial=session['username'][0].upper(), 
                login=True, 
                listings=listings)
        else:
            return render_template("archived.html", 
                initial=session['username'][0].upper(), 
                login=True, 
                messages="No archived listings here :)")

    except Exception as e:
        print(f"Error fetching archived listings: {e}")
        return render_template("archived.html", 
            initial=session['username'][0].upper(), 
            login=True, 
            messages="Error fetching archived listings")


@app.route('/edit-listing/<listing_id>', methods=['POST'])
def edit_listing(listing_id):
    if 'username' not in session:
        return redirect(url_for('login_page'))

    try:
        listing_ref = db.collection('listings').document(listing_id)
        listing_doc = listing_ref.get()

        if not listing_doc.exists:
            return redirect(url_for('my_listings'))

        listing_data = listing_doc.to_dict()

        if listing_data['poster_id'] != session['uid']:
            return redirect(url_for('my_listings', messages="You don't have permission to edit this listing"))

        item_name = request.form.get('item_name')
        item_location = request.form.get('item_location')
        additional_info = request.form.get('additional_info')
        f = request.files.get('file')

        update_data = {
            'item_name': item_name,
            'item_location': item_location,
            'additional_info': additional_info
        }

        if f and f.filename:
            try:
                if 'image_path' in listing_data:
                    old_blob = storage.bucket().blob(listing_data['image_path'])
                    old_blob.delete()

                file_extension = f.filename.split('.')[-1]
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                blob = storage.bucket().blob(f"listings/{unique_filename}")
                blob.upload_from_file(f, content_type=f.content_type)
                blob.make_public()

                update_data['image_url'] = blob.public_url
                update_data['image_path'] = f"listings/{unique_filename}"
            except Exception as e:
                print(f"Error handling image: {e}")
                return redirect(url_for('my_listings', messages="Error updating image"))

        listing_ref.update(update_data)

        return redirect(url_for('my_listings'))

    except Exception as e:
        print(f"Error updating listing: {e}")
        return redirect(url_for('my_listings', messages="Error updating listing"))


@app.route('/archive-listing/<listing_id>', methods=['GET'])
def archive_listing(listing_id):
    if 'username' not in session:
        return redirect(url_for('login_page'))

    try:
        listing_ref = db.collection('listings').document(listing_id)
        listing_doc = listing_ref.get()

        if not listing_doc.exists:
            return redirect(url_for('my_listings', messages="Listing not found"))

        listing_data = listing_doc.to_dict()

        if listing_data['poster_id'] != session['uid']:
            return redirect(url_for('my_listings', messages="You don't have permission to archive this listing"))

        listing_ref.update({
            'is_live': False,
            'created_at': firestore.SERVER_TIMESTAMP
        })

        return redirect(url_for('my_listings'))

    except Exception as e:
        print(f"Error archiving listing: {e}")
        return redirect(url_for('my_listings', messages="Error archiving listing"))


@app.route('/relist-listing/<listing_id>', methods=['GET'])
def relist_listing(listing_id):
    if 'username' not in session:
        return redirect(url_for('login_page'))

    try:
        listing_ref = db.collection('listings').document(listing_id)
        listing_doc = listing_ref.get()

        if not listing_doc.exists:
            return redirect(url_for('view_archived', messages="Listing not found"))

        listing_data = listing_doc.to_dict()

        if listing_data['poster_id'] != session['uid']:
            return redirect(url_for('view_archived', messages="You don't have permission to relist this listing"))

        listing_ref.update({
            'is_live': True,
            'created_at': firestore.SERVER_TIMESTAMP
        })

        return redirect(url_for('my_listings'))

    except Exception as e:
        print(f"Error relisting listing: {e}")
        return redirect(url_for('view_archived', messages="Error relisting"))


@app.route('/register_user_page')
def register_user_page():
    username = request.args.get('username')
    email = request.args.get('email')
    if username is None:
        username = ""
    if email is None:
        email = ""

    if 'next_url' not in session:
        session['next_url'] = request.referrer

    return render_template("register_user.html", username=username, email=email, messages=request.args.get('messages'))


@app.route('/register_user', methods=['post'])
def register_user():
    if not request.form['username'] or not request.form['email'] or not request.form['password']:
        return redirect(url_for('register_user_page', messages="Please enter all fields"))

    try:
        user = auth.create_user(
            email=request.form['email'],
            password=request.form['password'],
            display_name=request.form['username']
        )
        
        db.collection('users').document(user.uid).set({
            'username': request.form['username'],
            'email': request.form['email']
        })
        
        return redirect(url_for("login_page"))
    except auth.EmailAlreadyExistsError:
        return redirect(url_for("register_user_page", 
            username=request.form['username'], 
            email=request.form['email'], 
            messages="Email already exists"))
    except auth.InvalidEmailError:
        return redirect(url_for("register_user_page", 
            username=request.form['username'], 
            email=request.form['email'], 
            messages="Invalid email format"))


@app.route('/login_page')
def login_page():
    if 'next_url' not in session:
        session['next_url'] = request.referrer
    if "username" in session:
        return render_template("login.html", messages=request.args.get('messages'), login=True)
    else:
        email = request.args.get('email')
        if email is None:
            email = ""
        return render_template("login.html", email=email, messages=request.args.get('messages'))


@app.route('/login', methods=['post'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    elif not request.form['email'] or not request.form['password']:
        return redirect(url_for('login_page',
                            email=request.form['email'], 
                            messages="Please enter your password and email"))
    
    try:
        user = auth.get_user_by_email(request.form['email'])
        session['username'] = user.display_name
        session['uid'] = user.uid
        
        return redirect(session.pop('next_url', None))
    except auth.UserNotFoundError:
        return redirect(url_for('login_page',
                            email=request.form['email'], 
                            messages='Incorrect email or password entered'))


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    if 'uid' in session:
        session.pop('uid', None)
    return redirect(url_for('index'))


@app.route('/create_listing_page')
def create_listing_page():
    item_name = request.args.get('item_name')
    item_location = request.args.get('item_location')
    additional_info = request.args.get('additional_info')

    if item_name is None:
        item_name = ""
    if item_location is None:
        item_location = ""
    if additional_info is None:
        additional_info = ""

    return render_template("create_listing.html",
                           item_name=item_name, item_location=item_location, additional_info=additional_info,
                           message=request.args.get('message'), login=('username' in session))


@app.route('/create_listing', methods=['post'])
def create_listing():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    item_name = request.form['item_name']
    item_location = request.form['item_location']
    additional_info = request.form['additional_info']
    f = request.files['file']

    if not item_name or not item_location or not f.filename:
        message = ""
        if not item_name:
            message = "Please fill in the item name"
        elif not item_location:
            message = "Please specify the item location"
        elif not f.filename:
            message = "Please upload an image"

        return redirect(url_for("create_listing_page", 
            item_name=item_name, 
            item_location=item_location,
            additional_info=additional_info, 
            message=message))

    try:
        file_extension = f.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        blob = bucket.blob(f"listings/{unique_filename}")
        blob.upload_from_file(f, content_type=f.content_type)
        
        blob.make_public()
        image_url = blob.public_url

        listing_data = {
            'item_name': item_name,
            'item_location': item_location,
            'poster_id': session['uid'],
            'poster_name': session['username'],
            'additional_info': additional_info,
            'image_url': image_url,
            'image_path': f"listings/{unique_filename}",
            'is_live': True,
            'created_at': firestore.SERVER_TIMESTAMP
        }

        db.collection('listings').add(listing_data)

        return redirect(url_for("index"))
        
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return redirect(url_for("create_listing_page", 
            item_name=item_name, 
            item_location=item_location,
            additional_info=additional_info, 
            message=f"Error uploading image: {str(e)}"))


@app.route('/users/<postid>', methods=['get'])
def get_image(postid):
    try:
        listing_doc = db.collection('listings').document(postid).get()
        if listing_doc.exists:
            return redirect(listing_doc.to_dict()['image_url'])
        else:
            return '', 404
    except Exception as e:
        return str(e), 500


@app.route('/contact/<listing_id>')
def get_listing(listing_id):
    try:
        listing_doc = db.collection('listings').document(listing_id).get()
        
        if not listing_doc.exists:
            return render_template('listing.html', 
                messages="Listing not found", 
                login='username' in session,
                initial=session['username'][0].upper() if 'username' in session else None,
                listing={"id": listing_id, "item_name": "Item not found", "item_location": "", "poster_name": "", "additional_info": "", "image_url": ""})

        listing = listing_doc.to_dict()
        listing['id'] = listing_doc.id

        is_owner = 'username' in session and listing['poster_id'] == session['uid']
        
        return render_template('listing.html',
            listing=listing,
            is_owner=is_owner,
            login='username' in session,
            initial=session['username'][0].upper() if 'username' in session else None)

    except Exception as e:
        print(f"Error getting listing: {e}")
        return render_template('listing.html', 
            messages="Error retrieving listing", 
            login='username' in session,
            initial=session['username'][0].upper() if 'username' in session else None,
            listing={id: listing_id, item_name: "Item not found", item_location: "", poster_name: "", additional_info: "", image_url: ""},
            is_owner=False)


@app.route('/contact/send-messages/<listing_id>', methods=['POST'])
def send_messages(listing_id):
    if 'username' not in session:
        return redirect(url_for('login_page'))

    try:
        listing_doc = db.collection('listings').document(listing_id).get()
        
        if not listing_doc.exists:
            return redirect(url_for('index', messages="Listing not found"))
        
        message_content = request.form.get('message')

        message_data = {
            'listing_id': listing_id,
            'sender_id': session['uid'],
            'sender_name': session['username'],
            'message': message_content,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        
        db.collection('messages').add(message_data)
        
        return {'message': 'success'}

    except Exception as e:
        print(f"Error sending message: {e}")
        return {'message': 'error'}


@app.route('/contact/get-messages/<listing_id>', methods=['GET'])
def get_messages(listing_id):
    try:
        messages = db.collection('messages').where('listing_id', '==', listing_id).order_by('timestamp', direction=firestore.Query.ASCENDING)

        d = {"messages": []}
        for message in messages.stream():
            data = message.to_dict()
            if 'uid' in session:
                d["messages"].append({"sender": data["sender_name"], "message": data["message"], "is_sender": data["sender_id"] == session["uid"]})
            else:
                d["messages"].append({"sender": data["sender_name"], "message": data["message"], "is_sender": False})

        return d
    except Exception as e:
        print(f"Error getting messages: {e}")
        return {'message': 'error'}


if __name__ == "__main__":
    app.run(port=8000, debug=False, host='0.0.0.0')
