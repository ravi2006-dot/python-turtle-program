# Complete Code: Code Snippet Organizer with AI
from flask import Flask, jsonify, request, send_from_directory
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import openai
import os
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__, static_folder="frontend/build", static_url_path="/")
CORS(app)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/snippetdb"
mongo = PyMongo(app)

# OpenAI API key (replace with your own)
openai.api_key = "your_openai_api_key"

# Routes
@app.route('/api/snippets', methods=['GET'])
def get_snippets():
    snippets = mongo.db.snippets.find()
    return dumps(snippets), 200

@app.route('/api/snippets', methods=['POST'])
def create_snippet():
    data = request.json
    mongo.db.snippets.insert_one(data)
    return jsonify({"message": "Snippet created!"}), 201

@app.route('/api/snippets/<id>', methods=['DELETE'])
def delete_snippet(id):
    mongo.db.snippets.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Snippet deleted!"}), 200

@app.route('/api/search', methods=['POST'])
def search_snippets():
    query = request.json.get("query", "")
    snippets = mongo.db.snippets.find()
    snippets_list = [s for s in snippets]

    # Use OpenAI to find relevant snippets
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Find relevant code snippets for: {query}\n\nSnippets: {snippets_list}",
        max_tokens=150
    )
    return jsonify({"results": response.choices[0].text.strip()}), 200

# Serve React frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

# Fallback for React routing
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)

# ================= FRONTEND (React) =================
# Place the following files in the "frontend/src" directory.

# File: frontend/src/App.js
import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [snippets, setSnippets] = useState([]);
  const [newSnippet, setNewSnippet] = useState("");
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState("");

  useEffect(() => {
    fetchSnippets();
  }, []);

  const fetchSnippets = async () => {
    const response = await axios.get("/api/snippets");
    setSnippets(response.data);
  };

  const addSnippet = async () => {
    await axios.post("/api/snippets", { snippet: newSnippet });
    setNewSnippet("");
    fetchSnippets();
  };

  const deleteSnippet = async (id) => {
    await axios.delete(`/api/snippets/${id}`);
    fetchSnippets();
  };

  const searchSnippets = async () => {
    const response = await axios.post("/api/search", {
      query,
    });
    setSearchResults(response.data.results);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Code Snippet Organizer</h1>
      <div>
        <input
          type="text"
          value={newSnippet}
          onChange={(e) => setNewSnippet(e.target.value)}
          placeholder="Add a new snippet"
        />
        <button onClick={addSnippet}>Add</button>
      </div>
      <hr />
      <div>
        <h2>All Snippets</h2>
        <ul>
          {snippets.map((snippet) => (
            <li key={snippet._id}>
              {snippet.snippet} <button onClick={() => deleteSnippet(snippet._id)}>Delete</button>
            </li>
          ))}
        </ul>
      </div>
      <hr />
      <div>
        <h2>Search Snippets</h2>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for snippets"
        />
        <button onClick={searchSnippets}>Search</button>
        <div>
          <h3>Results:</h3>
          <p>{searchResults}</p>
        </div>
      </div>
    </div>
  );
};

export default App;

# File: frontend/src/index.js
import React from "react";
import ReactDOM from "react-dom";
import App from "./App";

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
);

# ================== SETUP INSTRUCTIONS ==================
# 1. Backend:
#    - Install required Python libraries: flask, flask-pymongo, openai, flask-cors.
#    - Run the Flask app.

# 2. Frontend:
#    - Create a React app using "npx create-react-app frontend".
#    - Replace the "src" folder with the files above.
#    - Build the React app: "npm run build".
#    - Place the build folder in the same directory as the Flask app.

# 3. MongoDB:
#    - Start MongoDB locally or connect to a cloud instance.

# 4. Run the Flask app and access the organizer at "http://localhost:5000".
