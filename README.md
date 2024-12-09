# Cloud Compute Recommendation Tool

## Purpose
This project is a cloud compute recommendation tool designed to help users select the best cloud provider for their needs based on specified input parameters.  
Implemented with Python, SQL, HTML, and CSS.
Youtube Demo: https://youtu.be/kvSZY3w0fZU

### Import Requirements
`cs50`, `flask`, `requests`, `plotly`, `sqlite3`, `openai`, `json`, `werkzeug`, `datetime`, `functools`

---

## Folder Contents

- **Static**: CSS styling document (`styles.css`)  
- **Templates**: HTML template documents and JavaScript file  
  - `demo.html`, `index.html`, `index_nr.html`, `layout.html`, `login.html`, `register.html`  
- **Main Folder**: Core files  
  - `app.py`, `helpers.py`, `users.db`

---

## Relevant File Contents

- **`styles.css`**: CSS styling document.  
- **`layout.html`**: Contains navigation and footer templates used in other HTML templates.  
- **`index.html`**: Homepage/dashboard analytics (if input is given).  
- **`index_nr.html`**: Homepage when no input is provided.  
- **`demo.html`**: Input form page.  
- **`login.html`**: Login page.  
- **`register.html`**: Register page.  
- **`script.js`**: JavaScript code for webpage functionality.  
- **`app.py`**: Main app file handling routing, logic, API calls, and interaction with the SQL database.  
- **`helpers.py`**: Contains helper functions, including `login_required` and graphing logic.  
- **`requirements.txt`**: Lists all dependencies and imports.  
- **`users.db`**: SQLite database containing `users`, `inputs`, and `outputs` tables.  

---

## SQL Database (`users.db`) Structure

### `users`
Stores user information for authentication.  
- `id`: Primary key  
- `username`: Unique username for each user  
- `password`: Hashed password for secure login  

### `inputs`
Stores input details submitted by users through the input form.  
- `id`: Primary key  
- `user_id`: Foreign key referencing the `users` table  
- `providers`: Selected cloud providers  
- `industry`: Industry information provided by user  
- `timeframe`: Timeframe  
- `usage`: Expected usage  
- `technicalDetails`: Additional technical details provided by user  
- `attachments`: Binary data for attachments  

### `outputs`
Stores results of recommendations generated for users.  
- `id`: Primary key  
- `user_id`: Foreign key referencing the `users` table  
- `response`: API response details  

### `sqlite_sequence`
Internal SQLite table used to track auto-incremented fields.  
- `name`: Name of the table with auto-increment  
- `seq`: Last sequence number used  

---

## How to Run the Project

1. Install dependencies.  
2. Navigate into the project folder and run `flask run` in the terminal.  
3. Access the app in your browser using the provided link.  
4. Register for an account through the registration page.  
5. Log in through the login page.  
6. Go to the input form and input details about your project.  
7. View the recommended plans and pricing.  

---

## How to Use the Input Form

1. Select providers you are interested in from the provided list. If none apply, select "Other."  
2. Input the industry you work in or the industry the project is for.  
3. Input the expected timeframe (in months) for the compute usage.  
4. Input the estimated hours of compute usage (hours/month) for the project.  
5. Input any additional relevant technical details about the project or a detailed project proposal.  
6. Upload any relevant attachments for the project.  
