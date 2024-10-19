from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash  
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)  # For development; for production, use a constant value

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lina'
app.config['MYSQL_DB'] = 'financeDB'

mysql = MySQL(app)

# Route for company registration form
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['company_name'] = request.form['company_name']
        session['industry_id'] = request.form['industry']
        session['country_id']  = request.form['country']
        session['address'] = request.form['company_address']
        session['company_size_id'] = request.form['company_size']
        return redirect(url_for('register_user'))

    # Fetching industries, countries, and sizes from the database
    cur = mysql.connection.cursor()

    # Fetch industries
    cur.execute("SELECT * FROM industries")
    industries = cur.fetchall()

    # Fetch countries
    cur.execute("SELECT * FROM countries")
    countries = cur.fetchall()

    # Fetch company sizes
    cur.execute("SELECT * FROM company_sizes")
    sizes = cur.fetchall()

    cur.close()

    # Pass fetched data to template
    return render_template('register.html', industries=industries, countries=countries, sizes=sizes)

# Route for admin user registration
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    company_id = session.get('company_id')  # Retrieve company_id from session
    company_name = session['company_name']
    industry_id = session['industry_id']
    country_id = session['country_id']
    address = session['address']
    company_size_id = session['company_size_id']

    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))  # Trailing comma to ensure it's a tuple
        user = cur.fetchall()
        print("user: ", user)
        cur.close()
        if user:
            return redirect(url_for('register'))

        try:
            with mysql.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO companies (company_name, industry_id, country_id, address, company_size_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (company_name, industry_id, country_id, address, company_size_id))
                mysql.connection.commit()
                print("company inserted")
                company_id = cur.lastrowid
                print("company_id:", company_id)

            with mysql.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (full_name, email, password_hash, role, company_id)
                    VALUES (%s, %s, %s, 'Admin', %s)
                """, (full_name, email, hashed_password, company_id))
                mysql.connection.commit()
                print("user inserted")
        except Exception as e:
            print("error", e)
            return redirect(url_for('register_user'))

        return redirect(url_for('login'))

    return render_template('register_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()  # Fetch one user
        print(user)
        print(check_password_hash(user[3], password))
        cur.close()

        if user and check_password_hash(user[3], password):  # Assuming password hash is in the 4th column (index 3)
            session['user_id'] = user[0]  # Assuming user ID is the first column
            session['email'] = user[2]  # Store email in session for reference
            session['company_id'] = user[4]  # Assuming company_id is in the 5th column (index 4)
            print('Login successful.')
            return redirect(url_for('dashboard'))  # Assuming a dashboard route
        else:
            print('Invalid email or password.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route for dashboard (once logged in)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        print('Please log in first.')
        return redirect(url_for('login'))

    # Dashboard logic goes here
    return render_template('dashboard.html')

# Route for logout
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    print('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)