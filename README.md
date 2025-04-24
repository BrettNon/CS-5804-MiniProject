# CS-5804-MiniProject

## 🚀 How to Run This App on a New Computer

Follow these steps to get this app up and running on any machine.

### ✅ Prerequisites

- [Python 3.8–3.11](https://www.python.org/downloads/)
- [Ollama](https://ollama.com) (for running the local LLaMA 3 model)

---

### 🛠️ Setup Instructions

```bash
# 1. Clone the repository

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # For macOS/Linux
venv\Scripts\activate         # For Windows

# 3. Install required Python packages
pip install streamlit requests

# 4. Pull the LLaMA 3 model for offline chatbot support
ollama pull llama3 (I think you have to download it from their website https://ollama.com/download)

# 5. Run the model in a background terminal
ollama run llama3

# 6. In a new terminal window/tab, run the Streamlit app
streamlit run app.py
```

---

### 📦 Optional

To generate your own `requirements.txt` for sharing:
```bash
pip freeze > requirements.txt
```

---

### ✅ You're all set!

- Weather data is pulled from OpenWeather’s free API
- The chatbot runs completely offline using LLaMA 3 via Ollama
- Forecast and chatbot are displayed side-by-side in a VT-branded layout

Enjoy your weather assistant!
