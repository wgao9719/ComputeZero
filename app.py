import os

import openai
from openai import OpenAI

import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, create_stacked_bar_chart

# to get the the time for the history section
from datetime import datetime

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# SQLite3 database storing the following tables: users, inputs, outputs
db = SQL("sqlite:///users.db")
#CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, password TEXT NOT NULL);
#CREATE TABLE inputs (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, providers TEXT NOT NULL, industry TEXT NOT NULL, timeframe INT NOT NULL, usage INT NOT NULL, technicalDetails TEXT NOT NULL, attachments BLOB);
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
    '''Render index page'''

    # Extract info from the json response
    output = extract()
    if output == "No response":
        return render_template("index_nr.html", output=output)

    # Construct the barchart
    bar_chart_info = []
    # get names of providers and prices for plans from the output variable, then feed it to the bar chart
    bar_chart_info.append([output['name_1'], output['name_2'], output['name_3']])
    bar_chart_info.append([output['compute_1'][1:], output['compute_2'][1:], output['compute_3'][1:]])
    bar_chart_info.append([output['storage_1'][1:], output['storage_2'][1:], output['storage_3'][1:]])
    bar_chart_info.append([output['data_transfer_1'][1:], output['data_transfer_2'][1:], output['data_transfer_3'][1:]])
    for i in range(1, len(bar_chart_info)):
        for j in range(len(bar_chart_info[i])):
            bar_chart_info[i][j] = int(bar_chart_info[i][j].replace(",", ""))
    chart = create_stacked_bar_chart(bar_chart_info)

    return render_template("index.html", output=output, chart = chart)

@app.route("/demo")
@login_required
def demo():
    '''Render demo page'''
    return render_template("demo.html")

@app.route("/input", methods=["GET", "POST"])
@login_required
def input():
    '''Render input page, receive input'''

    if request.method == "POST":
        #Retrieve input from user
        providers = request.form.get("providers")
        industry = request.form.get("industry")
        timeframe = request.form.get("timeframe")
        usage = request.form.get("usage")
        technicalDetails = request.form.get("technicalDetails")
        attachments = request.form.get("attachments")

        # Store input into SQL database input table
        db.execute("INSERT INTO inputs (user_id, providers, industry, timeframe, usage, technicalDetails, attachments) VALUES (?, ?, ?, ?, ?, ?, ?);",
                       session["user_id"], providers, industry, timeframe, usage, technicalDetails, attachments)

        # API call to assistant
        answer = apicall()

        # Store response into SQL database output table
        db.execute("INSERT INTO outputs (user_id, response) VALUES (?, ?)", session["user_id"], answer)

        return redirect("/")

    else:
        return render_template("input.html")

def apicall():
    '''API call to custom LLM'''

    # Set up API key and environment
    openai.api_key = "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"
    api_key = "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"
    os.environ["OPENAI_API_KEY"] = api_key

    # Get user input
    input = db.execute("SELECT * FROM inputs WHERE user_id = %s ORDER BY id DESC LIMIT 1", session["user_id"])

    # Prompting values
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
Choose between vCPU and vGPU, and say why
Expected Compute needs with a probabilistic range
Recommended compute purchase factoring in a buffer for use case needs
Cost breakdown of cloud computing options:
Top 3 cloud computing providers we recommend (AWS, Azure, Voltage Park, smaller compute providers, etc. DO NOT just provide AWS, Azure, and Google Cloud; make sure to switch up the options and tailor it to the information regarding industry and size)
The service we think is best for each provider
The expected cost for each service based on our recommended compute purchase
The expected cost for each service over the total timeframe
At the end, explain how you arrived at your recommendations in a clear and concise manner. Cite your reasoning based on the provided information, such as industry, keywords in the project proposal, timelines, and goals of the client

Your response should be structured as follows in JSON format:
{{
    "Range": "Give the minimum to maximum range of compute required. Choose either vCPU or vGPU and explain." ,
    "Range With Buffer": "Z compute with a X% buffer",
    "Provider": [
        {{
            "name_1": "Provider 1",
            "recommended_service_1": "Service 1",
            "expected_cost_per_service_1": "$X per compute hour",
            "cost_breakdown_1": {{
                "compute_1": "$A",
                "storage_1": "$B",
                "data_transfer_1": "$C"
            }},
            "expected_total_cost_1": "$Y"
        }},
        {{
            "name_2": "Provider 2",
            "recommended_service_2": "Service 2",
            "expected_cost_per_service_2": "$X per compute hour",
            "cost_breakdown_2": {{
                "compute_2": "$A",
                "storage_2": "$B",
                "data_transfer_2": "$C"
            }},
            "expected_total_cost_2": "$Y"
        }},
        {{
            "name_3": "Provider 3",
            "recommended_service_3": "Service 3",
            "expected_cost_per_service_3": "$X per compute hour",
            "cost_breakdown_3": {{
                "compute_3": "$A",
                "storage_3": "$B",
                "data_transfer_3": "$C"
            }},
            "expected_total_cost_3": "$Y"
        }}
    ],
    "Explanation": "Provide a clear explanation based on the data points provided. Include how you arrived at your recommendation and any assumptions made."
}}
# Only use information about cloud service providers that is sourced from 2024.
# Replace all instances when you refer to yourself as “I” with “we”.
# Format response as a JSON file
'''.format(input[0]["providers"], input[0]["industry"], input[0]["timeframe"], input[0]["usage"], input[0]["technicalDetails"])

    client = OpenAI()

    # Set up threads
    thread = client.beta.threads.create()

    # Set up thread messages
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # Pretrained assistant, output in rigid JSON schema
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id="asst_ss6AB1S98ttDFE6TFEaV2YmU",
    )

    # Response messages
    response_message = None
    messages = client.beta.threads.messages.list(thread_id=thread.id).data
    for message in messages:
        if message.role == "assistant":
            response_message = message
            break

    return str(response_message.content[0].text.value)

def extract():
    '''Extract structured info from LLM JSON output text'''

    # get output response with SQL query
    output = db.execute("SELECT response FROM outputs WHERE user_id = %s ORDER BY id DESC LIMIT 1", session["user_id"])
    output = output[0]["response"] if output else "No response"

    # Check for valid output
    if output=="No response":
        #return [output]
        return output

    # Load string into JSON format
    try:
        output_json = json.loads(output[7:len(output)-3])
    except json.JSONDecodeError as e:
        return [f"Error decoding JSON: {str(e)}"]

    # Extract JSON info into dictionary info_dict
    info_dict = {}

    def extract_info(d, parent_key=''):
        '''extract info from given json schema'''
        # Check top layer dictionaries
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = f"{k}" if parent_key else k
                # Recursive call to next layer dictionary
                extract_info(v, new_key)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                new_key = f"{parent_key}[{i}]"
                # Recursive call to next layer dictionary
                extract_info(item, new_key)
        else:
            info_dict[parent_key] = d

    extract_info(output_json)

    return info_dict


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # check if username and password entered
        if not request.form.get("username"):
            return render_template("login.html")
        elif not request.form.get("password"):
            return render_template("login.html")

        # select for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # check if username and password match
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return render_template("login.html")

        # assign user_id
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")

        # check if username entered
        if not username:
            return render_template("register.html")

        # check if password entered
        password = request.form.get("password")
        if not password:
            return render_template("register.html")

        # check if confirmations match
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return render_template("register.html")

        # generate password hash
        hash = generate_password_hash(password)

        # insert into SQL database users table
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
