import firebase_admin
from firebase_admin import credentials, db

import os

# Path to your credentials file
# Option A (recommended): raw string literal so backslashes are not treated as escapes
cred_path = r"C:\Users\LENOVO\OneDrive\Desktop\drublet\serviceAccountKey.json"
# Option B: use forward slashes (also works on Windows)
# cred_path = "C:/Users/LENOVO/OneDrive/Desktop/drublet/serviceAccountKey.json"
# Option C: build with os.path.join for portability
# cred_path = os.path.join("C:", "Users", "LENOVO", "OneDrive", "Desktop", "drublet", "serviceAccountKey.json")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://console.firebase.google.com/u/0/project/metaglasses-d660a/overview'  # Edit with your details
})

# Save data
ref = db.reference('/some/path')
ref.set({
    'message': 'Hello from Firebase!'
})

# Read data
data = ref.get()
print(data)
