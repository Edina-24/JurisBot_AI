import os
import traceback
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.chains import LLMChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableSequence
import PyPDF2  # For reading PDFs

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/response": {"origins": "*"}})

# Get API key and model name from environment or use defaults
groq_api_key = os.getenv("GROQ_API_KEY")
model = "llama3-8b-8192"

# Initialize Groq client
client = ChatGroq(groq_api_key=groq_api_key, model_name=model)

# PDF folder path
pdf_folder = "data"  # Make sure the PDFs are stored in the 'data' folder

# Function to extract text from PDFs
def extract_pdf_text(pdf_folder):
    text = ""
    print(f"Accessing PDF files in {pdf_folder}...")
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
            print(f"Reading PDF: {filename}")
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()
    return text

# Function to truncate text to fit token limits
def truncate_text(text, max_tokens=3000):
    token_limit = max_tokens * 4  # Approximate number of characters per token
    if len(text) > token_limit:
        text = text[:token_limit]
    return text

# Set up memory for conversation history
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

# Build prompt chain
def build_prompt(pdf_text):
    truncated_text = truncate_text(pdf_text)
    system_prompt = (
        "You are a legal assistant who helps people with general legal inquiries. "
        "Your role is to provide general legal information, but not legal advice. "
        "You can help users with questions about contracts, criminal law, family law, intellectual property, and more. "
        "Avoid providing specific legal advice, as you're not a licensed attorney. "
        "Provide general information and suggest that the user consult with a licensed lawyer for legal advice.\n\n"
        f"Here is some additional legal information from the documents I have:\n"
        f"{truncated_text}\n\n"
    )
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}"),
        ]
    )

# Initialize Flask route for handling the responses
@app.route("/response", methods=["POST"])
def response():
    try:
        pdf_text = extract_pdf_text(pdf_folder)
        data = request.get_json()
        query = data.get("query", "").strip()
        print(f"Received query: {query}")

        if not query:
            return jsonify({"error": "Query is empty."}), 400

        prompt = build_prompt(pdf_text)

        llm_chain = LLMChain(
            llm=client,
            prompt=prompt,
            verbose=False,
            memory=memory,
        )

        bot_reply = llm_chain.run(query)
        print(f"Bot response: {bot_reply}")

        chat_history = memory.chat_memory.messages
        formatted_history = [
            {"role": "user" if m.type == "human" else "assistant", "content": m.content}
            for m in chat_history
        ]

        return jsonify({
            "response": bot_reply,
            "chat_history": formatted_history
        })

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return jsonify({"error": "Sorry, there was an error processing your request. Please try again."}), 500

# Serve frontend files (static hosting)
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

@app.route("/")
def index():
    return send_from_directory(frontend_path, "index.html")

@app.route("/<path:filename>")
def serve_file(filename):
    return send_from_directory(frontend_path, filename)

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
