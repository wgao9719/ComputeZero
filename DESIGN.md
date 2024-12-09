Our project was constructed in three components: input frontend, backend (API calls and SQL interfacing), output frontend

The overarching goal of the input frontend is to retrieve information and store it for a unique user. Hence, we implement login functionality, where the user can access register and login pages.
The user's input (username and hashed password) is stored in a SQL database called users.db under the users table, along with a user ID. Then, the unique user has access to the input form, which 
allows them to indirectly interface with the model. We include several possible datapoints, including: interested providers, industry, timeframe, estimated usage, technical details, and document
input. These are fed into users.db under the inputs table, along with the user ID.

The backend is meant to use the input to produce output for the dashboard. Using the input data stored in users.db, we can make API calls to an OpenAI assistant. We use a GPT-4o-mini assistant SScale we custom-designed for cloud compute queries. SScale uses a set of 10 additional documents in its vector database and provides all outputs in a rigid JSON schema.
When calling SScale, we retrieve the most recent unique user input and use a specific prompt (refer to app.py) to interface with the model through the OpenAI module. The JSON structured input 
(JSON structure shown in the prompt and model specs) is stored in users.db under the outputs table. 

The output frontend is an analytical dashboard that displays the model's structured outputs. Using the listed outputs, the output implementation retrieves the output info from users.db and converts it
from JSON structured text to a JSON file. The JSON file is then parsed with a custom parsing function and stored in a dictionary. Using the keys, the dictionary values are formatted into the index.html
template and displayed in the dashboard. The analytics also include a bar graph function that is implemented in helpers.py.
