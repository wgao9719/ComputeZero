import os

import openai
from openai import OpenAI

import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# to get the the time for the history section
from datetime import datetime

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///users.db")
#CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, password TEXT NOT NULL);
#CREATE TABLE inputs (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, providers TEXT NOT NULL, industry TEXT NOT NULL, timeframe INT NOT NULL, usage INT NOT NULL, technicalDetails TEXT NOT NULL, attachments BLOB);
#CREATE TABLE outputs (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, response TEXT NOT NULL);
#CREATE TABLE outputs (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, response TEXT NOT NULL);

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # output = db.execute("SELECT response FROM outputs WHERE user_id = %s ORDER BY id DESC LIMIT 1", session["user_id"])
    # output = (output[0]["response"]) if output else "No response found"
    output = extract()
    return render_template("index.html", output=output)

@app.route("/demo")
@login_required
def demo():
    return render_template("demo.html")

@app.route("/input", methods=["GET", "POST"])
@login_required
def input():
    if request.method == "POST":
        providers = request.form.get("providers")
        industry = request.form.get("industry")
        timeframe = request.form.get("timeframe")
        usage = request.form.get("usage")
        technicalDetails = request.form.get("technicalDetails")
        attachments = request.form.get("attachments")

        db.execute("INSERT INTO inputs (user_id, providers, industry, timeframe, usage, technicalDetails, attachments) VALUES (?, ?, ?, ?, ?, ?, ?);",
                       session["user_id"], providers, industry, timeframe, usage, technicalDetails, attachments)

        answer = apicall()

        db.execute("INSERT INTO outputs (user_id, response) VALUES (?, ?)", session["user_id"], answer)

        return redirect("/")

    else:
        return render_template("demo.html")

def apicall():
    '''API call to custom LLM'''

    openai.api_key = "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"
    api_key = "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"
    os.environ["OPENAI_API_KEY"] = api_key

    input = db.execute("SELECT * FROM inputs WHERE user_id = %s ORDER BY id DESC LIMIT 1", session["user_id"])

    #prompting
    prompt = '''You are a finops expert with extensive knowledge in cloud computing, finops, and data analytics. You have previously worked at Amazon AWS, Microsoft Azure, Voltage Park, and every single cloud provider,  where you have worked as a key member of the FinOps teams.
You also have access to up-to-date analytics and data of each cloud provider regarding their services, pricing, and performance.

A client organization approaches you for assistance in adopting cloud services. They are new to cloud computing and need your expert guidance on how to begin effectively.
You will receive relevant data points about the organization and should use this information to provide thorough, data-driven recommendations.

Example template of information that will be provided:
Interested cloud service providers: [Here you will find some cloud providers the client is currently considering]
Industry: [Here you will find what industry the client organization works in]
Projected timeframe: [Here you will find the expected timeframe of the compute usage]
Estimated usage: (optional), [Here you will find the expected amount the client expects]
Technical details: [Here you will find a detailed proposal describing a project. This could be an info page or grant proposal. Review the document for key technical information, and use it to inform your recommendations.]

This is the information provided. It is written in the format above:
Interested cloud service providers: {}
Industry: {}
Projected timeframe: {}
Estimated usage: {}
Technical details (formatted within the brackets): {}

This is your task
Using these data points, provide your best recommendations for how they should transition to the cloud. Give the outputs below, formatted exactly the same way:
Expected Compute needs with a probabilistic range
Recommended compute purchase factoring in a buffer for use case needs
Cost breakdown of cloud computing options:
Top 3 cloud computing providers we recommend (AWS, Azure, Voltage Park, smaller compute providers, etc. DO NOT just provide AWS, Azure, and Google Cloud; make sure to switch up the options and tailor it to the information regarding industry and size)
The service we think is best for each provider
The expected cost for each service based on our recommended compute purchase
The expected cost for each service over the total timeframe
At the end, explain how you arrived at your recommendations in a clear and concise manner. Cite your reasoning based on the provided information, such as industry, keywords in the project proposal, timelines, and goals of the client

Format the output with bullet points.
# Only use information about cloud service providers that is sourced from 2024.
# Replace all instances when you refer to yourself as “I” with “we”.
# Format response as a JSON file
'''.format(input[0]["providers"], input[0]["industry"], input[0]["timeframe"], input[0]["usage"], input[0]["technicalDetails"])

    client = OpenAI()

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    #pretrained assistant, output in JSON file
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id="asst_ss6AB1S98ttDFE6TFEaV2YmU",
    )

    response_message = None
    messages = client.beta.threads.messages.list(thread_id=thread.id).data
    for message in messages:
        if message.role == "assistant":
            response_message = message
            break

    return str(response_message.content[0].text.value)

def extract():
    '''Extract structured info from LLM JSON output text'''

    #get response with SQL query
    output = db.execute("SELECT response FROM outputs WHERE user_id = %s ORDER BY id DESC LIMIT 1", session["user_id"])

    output = output[0]["response"] if output else "No response"

    if output=="No response":
        return [output]

    try:
        output_json = json.loads(output[7:len(output)-3])
    except json.JSONDecodeError as e:
        return [f"Error decoding JSON: {str(e)}"]

    info_list = []

    def extract_info(d, parent_key=''):
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = f"{k}" if parent_key else k
                extract_info(v, new_key)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                new_key = f"{parent_key}[{i}]"
                extract_info(item, new_key)
        else:
            info_list.append(f"{parent_key}: {d}")

    extract_info(output_json)

    return info_list


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("login.html")
        elif not request.form.get("password"):
            return render_template("login.html")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return render_template("register.html")

        password = request.form.get("password")
        if not password:
            return render_template("register.html")

        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return render_template("register.html")

        hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, password) VALUES(?, ?)", username, hash)
        except:
            return render_template("register.html")

        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


