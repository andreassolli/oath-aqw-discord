import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db: Client = firestore.client()
