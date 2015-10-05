import sqlite3
import time
from search import *
from flask import Flask, request, g, render_template, redirect
app = Flask(__name__)
DATABASE = 'hakks.db'

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
	return db

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

def db_read_hakks():
	cur = get_db().cursor()
	cur.execute("SELECT * FROM hakks")
	return cur.fetchall()

def db_add_hakk(search, results):
	cur = get_db().cursor()
	hakk_info = (search, results)
	cur.execute("INSERT INTO hakks VALUES (?, ?)", hakk_info)
	get_db().commit()

@app.route("/")
def hello():
	hakks = db_read_hakks()
	return render_template('home.html')

@app.route("/api/", methods=["POST"])
def receive_hakk():
	form = request.form
	entry = form["search_entry"]
	begins_with = form["begins_with"]
	ends_with = form["ends_with"]

	results_list = parse_search_entry(entry, 'Synonym', begins_with, ends_with)
	results_string = ' '.join(results_list)

	show = [entry, results]
	return render_template('home.html', results = show)

if __name__ == "__main__":
	app.run()