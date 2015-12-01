import sqlite3
import time
import os
from search import parse_search_entry
from flask import Flask, request, g, render_template, redirect
app = Flask(__name__)

@app.route("/")
def hello():
	return render_template('home.html')

@app.route("/api/", methods=["POST"])
def receive_search():
	form = request.form
	entry = form["search_entry"]
	begins_with = form["begins_with"]
	ends_with = form["ends_with"]

	try:
		num_results = int(form["how_many_words"])
	except:
		#Display that not a valid number
		placeholder = None
		num_results = None

	if num_results:
		results = parse_search_entry(entry, 'Synonym', begins_with, ends_with, num_results)
	else:
		results = parse_search_entry(entry, 'Synonym', begins_with, ends_with)

	data = [entry, results]
	return render_template('home.html', results = data)

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(debug=False, host='0.0.0.0', port=port)

