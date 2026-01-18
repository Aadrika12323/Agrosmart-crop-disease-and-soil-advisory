import os
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from groq import Groq

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

def retrieve_context(question):
    """Simple retrieval: find relevant text from Data files"""
    context = []
    for file in os.listdir("Data"):
        with open(os.path.join("Data", file), "r", encoding="utf-8") as f:
            text = f.read()
            if any(word.lower() in text.lower() for word in question.split()):
                context.append(text)
    return "\n".join(context[:2])  # limit context

def ask_llm(question):
    context = retrieve_context(question)

    prompt = f"""
You are an AI assistant for sustainable agriculture.

Context:
{context}

Question:
{question}

Answer clearly with crop disease info and soil requirements.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI for Sustainable Agriculture</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #e8f5e9;
            font-family: Arial, sans-serif;
        }

        .container {
            background: white;
            padding: 30px 40px;
            border-radius: 12px;
            width: 500px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
        }

        h2 {
            color: #2e7d32;
            margin-bottom: 20px;
        }

        input, select, button {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            font-size: 15px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }

        button {
            background-color: #43a047;
            color: white;
            border: none;
            cursor: pointer;
            margin-top: 15px;
        }

        button:hover {
            background-color: #388e3c;
        }

        .answer {
            margin-top: 20px;
            text-align: left;
            font-size: 15px;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>🌱 Crop Disease & Soil Advisor</h2>

    <form method="post">
        <input type="text" name="question"
               placeholder="Ask about crop disease or soil..."
               required>

        <input type="text" name="region"
               placeholder="Region (e.g., North India, Punjab)">

        <input type="number" name="temperature"
               placeholder="Temperature (°C)">

        <select name="climate">
            <option value="">Select Climate Type</option>
            <option value="Tropical">Tropical</option>
            <option value="Dry">Dry</option>
            <option value="Temperate">Temperate</option>
            <option value="Continental">Continental</option>
            <option value="Polar">Polar</option>
        </select>

        <button type="submit">Get Recommendation</button>
    </form>

    {% if answer %}
    <div class="answer">
        <h3>Answer:</h3>
        <p>{{ answer }}</p>
    </div>
    {% endif %}
</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    answer = None

    if request.method == "POST":
        question = request.form["question"]
        region = request.form.get("region", "")
        temperature = request.form.get("temperature", "")
        climate = request.form.get("climate", "")

        # Combine all inputs into one prompt
        final_query = f"""
        User Question: {question}
        Region: {region}
        Temperature: {temperature} °C
        Climate Type: {climate}
        """

        answer = ask_llm(final_query)

    return render_template_string(HTML, answer=answer)


if __name__ == "__main__":
    app.run(debug=True)
