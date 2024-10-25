import csv
from flask import Flask, jsonify, render_template, request, redirect, send_file, session, url_for
from flask_mysqldb import MySQL
import os
import re
from werkzeug.utils import secure_filename

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_groq import ChatGroq

from dotenv import load_dotenv

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)  # For development; for production, use a constant value
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
app.config['RESULT_FOLDER'] = 'results'  # Folder to store generated CSVs

# Ensure the upload and result directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lina'
app.config['MYSQL_DB'] = 'FinancialChatbotDB'
def connect_database(hostname: str, port: str, username: str, password: str, database: str) -> SQLDatabase:
    # uniform resource identifier
    db_uri = f"mysql+mysqlconnector://{username}:{password}@{hostname}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)
db = connect_database("localhost", 3306, "root","lina","FinancialChatbotDB")
if db:
    print("Connected to DB")
else:
    print("Not connected")

mysql = MySQL(app)

# Function to generate SQL Query
def get_sql_chain(db):
    prompt_template = """
        You are a senior data analyst. 
        Based on the table schema provided below, write a SQL query that answers the question. 
        Consider the conversation history.

        ```<SCHEMA> {schema} </SCHEMA>```
        each question is about one and only one table so make sure to keep the tables' name as they are
        note that when the user asks about the months or the days use the tables containing full dates not years only
        Conversation History: {conversation_history}

        Write only the SQL query without any additional text.

        For example:
        Question: Who are the top 3 artists with the most tracks?
        Answer: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;

        Response Format:
            Question: {question}
    """

    # Prompt
    prompt = ChatPromptTemplate.from_template(template=prompt_template)
    llm = ChatGroq(model="llama3-groq-70b-8192-tool-use-preview", temperature=0.2)

    # Function to return the details / schema of the database
    def get_schema(_):
        return db.get_table_info()
    output = (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm
            | StrOutputParser()
    )
    
    return output

def clean_sql_query(query: str) -> str:
    """Extracts only the SQL code from a string containing extra text."""
    sql_code = re.search(r"(SELECT .*?;)", query, re.DOTALL)
    print("sql_code : ",sql_code.group(1))
    return sql_code.group(1).strip() if sql_code else query

def get_response(user_query: str, db: SQLDatabase, conversation_history: list):
    sql_chain = get_sql_chain(db)
    prompt_template = """
        You are a senior data analyst. 
        Given the database schema details, question, SQL query, and SQL response, 
        write a natural language response for the SQL query. If the response does not contain the information required, 
        respond with "I'm unable to retrieve that information from the available data."

        <SCHEMA> {schema} </SCHEMA>
        
        Conversation History: {conversation_history}
        SQL Query: <SQL> {sql_query} </SQL>
        Question: {question}
        SQL Response: {response}
        
        Response Format:
            Natural Language Response:
    """

    prompt = ChatPromptTemplate.from_template(template=prompt_template)
    llm = ChatGroq(model="Mixtral-8x7b-32768", temperature=0.2)

    chain = (
            RunnablePassthrough.assign(sql_query=sql_chain).assign(
                schema=lambda _: db.get_table_info(),
                response=lambda vars: db.run(clean_sql_query(vars["sql_query"]))  # Apply clean_sql_query here
            )
            | prompt
            | llm
            | StrOutputParser()
    )

    output = chain.invoke({
        "question": user_query,
        "conversation_history": conversation_history
    })
    print("output : ", output)
    return output

class AIMessage:
    def __init__(self, content):
        self.content = content

class HumanMessage:
    def __init__(self, content):
        self.content = content

# Initialize conversation history
if "conversation_history" not in app.config:
    app.config['conversation_history'] = [
        AIMessage(content="Hello! I am a SQL assistant. Ask me questions about your MYSQL database.")
    ]
    
messages = []
@app.route('/chatbot', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_query = request.form.get('user_input', '').strip()
        if user_query:
            app.config['conversation_history'].append(HumanMessage(content=user_query))
            response = get_response(user_query,db, app.config['conversation_history'])
            app.config['conversation_history'].append(AIMessage(content=response))
        # Add bot response "Okay"
        messages.append(f"You: {user_query}")
        messages.append(f"Bot: {response}")  # Append the actual bot response
    
    
    # Render the template with the messages
    return render_template('chatbot.html', messages=messages)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.txt'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Parse questions from the .txt file
        questions = extract_questions(file_path)
        
        # Generate CSV with dummy answers
        csv_filename = 'answers.csv'
        csv_path = generate_csv_with_dummy_answers(questions)
        
        # Provide download link in the response
        download_link = request.host_url + 'download/' + csv_filename
        return jsonify({'download_link': download_link}), 200
    else:
        return jsonify({'error': 'Only .txt files are allowed'}), 400

def extract_questions(file_path):
    """Read questions from the .txt file."""
    with open(file_path, 'r') as file:
        questions = [line.strip() for line in file if line.strip()]  # Ignore empty lines
    return questions

def generate_csv_with_dummy_answers(questions):
    """Generate a CSV file with questions and dummy answers."""
    csv_filename = 'answers.csv'
    csv_path = os.path.join(app.config['RESULT_FOLDER'], csv_filename)
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Question', 'Answer'])  # Header row
        
        # Write each question with a dummy answer
        for question in questions:
            print(question)
            app.config['conversation_history'].append(HumanMessage(content=question))
            response = get_response(question,db, app.config['conversation_history'])
            app.config['conversation_history'].append(AIMessage(content=response))
            writer.writerow([question, response])
    
    return csv_filename  # Only the filename, used in the download route

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Endpoint to download the generated CSV file."""
    try:
        return send_file(os.path.join(app.config['RESULT_FOLDER'], filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)