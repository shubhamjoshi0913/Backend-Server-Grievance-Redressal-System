import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials from environment variable
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS')

if not firebase_credentials_json:
    raise Exception("FIREBASE_CREDENTIALS environment variable not set")

# Parse the credentials from the environment variable
cred_dict = json.loads(firebase_credentials_json)

# Initialize Firebase using the in-memory credentials
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
