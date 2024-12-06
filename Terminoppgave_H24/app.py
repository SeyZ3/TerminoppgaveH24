from flask import Flask, render_template, redirect, url_for, flash, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Nødvendig for å bruke flash-meldinger

# Opprett database og tabell hvis de ikke eksisterer
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Hjemmeside
@app.route('/')
def home():
    return render_template('index.html')

# Registreringsside
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "" or password == "":
            flash("Vennligst fyll ut alle felt.")
            return redirect(url_for('register'))
        
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            flash("Registreringen var vellykket!")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Brukern avn eksisterer allerede. Vennligst velg et annet.")
            return redirect(url_for('register'))

    return render_template('register.html')

# Innloggingsside
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username  # Lagre brukernavnet i sesjonen
            flash("Innlogging vellykket!")
            return redirect(url_for('home'))
        else:
            flash("Feil brukernavn eller passord.")
            return redirect(url_for('login'))

    return render_template('login.html')

# Logg ut
@app.route('/logout')
def logout():
    session.pop('username', None)  # Fjern brukernavnet fra sesjonen
    flash("Du er nå logget ut.")
    return redirect(url_for('home'))

# Handlekurv
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart_items=cart_items)

@app.route('/add_to_cart/<product_name>')
def add_to_cart(product_name):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_name)
    flash(f"{product_name} har blitt lagt til i handlekurven.")
    return redirect(url_for('products'))

@app.route('/remove_from_cart/<product_name>')
def remove_from_cart(product_name):
    cart = session.get('cart', [])
    if product_name in cart:
        cart.remove(product_name)
        session['cart'] = cart
        flash(f"{product_name} har blitt fjernet fra handlekurven.")
    return redirect(url_for('cart'))

# Produktside
@app.route('/products')
def products():
    product_list = ['Produkt 1', 'Produkt 2', 'Produkt 3']  # Eksempelprodukter
    return render_template('products.html', products=product_list)

if __name__ == '__main__':
    app.run(debug=True)