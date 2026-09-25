"""
firebase_config.py
-------------------
Initializes the Firebase Admin SDK and exposes a Firestore client
that the rest of the app can import.

SETUP
1. In the Firebase console, go to Project Settings > Service Accounts
   and click "Generate new private key". This downloads a JSON file.
2. Save that file in this "backend" folder as: serviceAccountKey.json
   (never commit this file to a public repo - it is already listed
   in .gitignore).
3. Alternatively, set the GOOGLE_APPLICATION_CREDENTIALS environment
   variable to the path of that JSON file instead of step 2.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_PATH = os.path.join(
    os.path.dirname(__file__), "serviceAccountKey.json"
)


def init_firestore():
    """Initialize Firebase Admin (once) and return a Firestore client."""
    if not firebase_admin._apps:
        if os.path.exists(SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        else:
            # Falls back to GOOGLE_APPLICATION_CREDENTIALS env var,
            # or Application Default Credentials if running on
            # Google infrastructure (e.g. Cloud Run).
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

    return firestore.client()


db = init_firestore()
