from flask import Flask, render_template, redirect, url_for
from . import app
import subprocess

@app.route("/")
def home():
    return render_template("home.html")

# New functions
@app.route("/aggregate/")
def aggregate():
    return render_template("aggregate.html")

@app.route('/run-aggregator/', methods=['POST'])
def run_aggregator():
    subprocess.Popen(["python3", "aggregator.py"])
    return redirect(url_for('aggregatorsuccess'))

@app.route("/aggregator-success/")
def aggregatorsuccess():
    return render_template("aggregatorsuccess.html")

@app.route("/insights/")
def insights():
    #return render_template("insights.html")
    return app.send_static_file("sample_output.json")
