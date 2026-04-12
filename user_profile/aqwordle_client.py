import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_key2.json")

if "aqwordle" not in firebase_admin._apps:
    app = firebase_admin.initialize_app(cred, name="aqwordle")
else:
    app = firebase_admin.get_app("aqwordle")

db = firestore.client(app=app)
