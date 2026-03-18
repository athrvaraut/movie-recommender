import json
import os

def init_db():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)
    if not os.path.exists('history.json'):
        with open('history.json', 'w') as f:
            json.dump({}, f)

def register_user(username, password):
    import bcrypt
    with open('users.json', 'r') as f:
        users = json.load(f)
    if username in users:
        return False, "Username already exists!"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed
    with open('users.json', 'w') as f:
        json.dump(users, f)
    return True, "Registered successfully!"

def login_user(username, password):
    import bcrypt
    with open('users.json', 'r') as f:
        users = json.load(f)
    if username not in users:
        return False, "Username not found!"
    if bcrypt.checkpw(password.encode(), users[username].encode()):
        return True, "Login successful!"
    return False, "Wrong password!"

def save_history(username, movie, recs):
    with open('history.json', 'r') as f:
        history = json.load(f)
    if username not in history:
        history[username] = []
    history[username].insert(0, {"movie": movie, "recommendations": recs[:5]})
    history[username] = history[username][:20]
    with open('history.json', 'w') as f:
        json.dump(history, f)

def get_history(username):
    with open('history.json', 'r') as f:
        history = json.load(f)
    return history.get(username, [])

init_db()
print("Login system ready!")