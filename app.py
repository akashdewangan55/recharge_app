from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
import json
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 's3cr3t_@k45h_R3ch@rg3_2025!'  # Set a secure random string in production

# Load API details from .env
API_KEY = os.getenv("KWIKAPI_KEY")
BASE_URL = os.getenv("KWIKAPI_BASE", "https://www.kwikapi.com/api/v2")
RECHARGE_FILE = 'recharge_history.json'


def load_recharges():
    if os.path.exists(RECHARGE_FILE):
        with open(RECHARGE_FILE, 'r') as f:
            return json.load(f)
    return []


def save_recharges(data):
    with open(RECHARGE_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def do_recharge(number, opid, amount, order_id):
    url = f"{BASE_URL}/recharge.php"
    params = {
        "api_key": API_KEY,
        "number": number,
        "amount": amount,
        "opid": opid,
        "state_code": 0,
        "order_id": order_id
    }
    response = requests.get(url, params=params, timeout=20)
    return response.json()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/recharge', methods=['GET', 'POST'])
def recharge():
    if request.method == 'POST':
        number = request.form['number']
        opid = request.form['opid']
        amount = request.form['amount']
        order_id = str(int(time.time()))

        result = do_recharge(number, opid, amount, order_id)

        status = result.get("status", "FAILED")
        message = result.get("message", "No message")
        txn_id = result.get("transaction_id", "-")

        history = load_recharges()
        history.append({
            "number": number,
            "operator": opid,
            "amount": amount,
            "status": status,
            "message": message,
            "txn_id": txn_id,
            "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_recharges(history)

        flash(f"Recharge {status}: {message}", 'success' if status == 'SUCCESS' else 'danger')
        return redirect(url_for('recharge'))

    history = load_recharges()[::-1]  # show latest first
    return render_template('index.html', history=history)

from flask import session  # make sure this is imported at the top

# Sample user dictionary
users = {
    "user@example.com": {"password": "123456"}
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)

        if user and user['password'] == password:
            session['user'] = email  # ✅ Correctly indented inside this 'if'
            flash("Login successful!", "success")
            return redirect(url_for('recharge'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users:
            flash("Email already registered.", "danger")
            return redirect(url_for('register'))

        users[email] = {"password": password}
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/history')
def history():
    if not session.get('user'):
        return redirect(url_for('login'))
    user_email = session['user']
    user_history = history_data.get(user_email, [])
    return render_template('history.html', history=user_history)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
