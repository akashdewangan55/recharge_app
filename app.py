from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERS_FILE = 'data/users.json'
RECHARGES_FILE = 'data/recharges.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_recharges():
    if not os.path.exists(RECHARGES_FILE):
        return []
    with open(RECHARGES_FILE, 'r') as f:
        return json.load(f)

def save_recharges(recharges):
    with open(RECHARGES_FILE, 'w') as f:
        json.dump(recharges, f, indent=4)

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('recharge'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users:
            flash('Email already registered!', 'danger')
        else:
            users[email] = {'password': password}
            save_users(users)
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users and users[email]['password'] == password:
            session['user'] = email
            return redirect(url_for('recharge'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/recharge', methods=['GET', 'POST'])
def recharge():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        number = request.form['number']
        operator = request.form['operator']
        amount = request.form['amount']
        recharge = {
            'email': session['user'],
            'number': number,
            'operator': operator,
            'amount': amount,
            'status': 'Success',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        recharges = load_recharges()
        recharges.append(recharge)
        save_recharges(recharges)
        flash('Recharge successful!', 'success')
    return render_template('recharge.html')

@app.route('/recharge', methods=['POST'])
def recharge():
    number = request.form['number']
    opid = request.form['opid']  # Hidden field or select operator
    amount = request.form['amount']
    order_id = str(int(time.time()))  # Unique order ID by timestamp

    result = do_recharge(number, opid, amount, order_id)

    status = result.get("status", "FAILED")
    txn_id = result.get("transaction_id")
    msg = result.get("message", "")

    recharge = {
        'email': session['user'],
        'number': number,
        'operator': opid,
        'amount': amount,
        'status': status,
        'txn_id': txn_id,
        'message': msg,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    recharges = load_recharges()
    recharges.append(recharge)
    save_recharges(recharges)

    flash(f"Recharge {status}: {msg}", 'success' if status == 'SUCCESS' else 'danger')
    return redirect(url_for('recharge'))
    
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
