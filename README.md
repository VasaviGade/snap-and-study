# 📚 Snap & Study

Snap & Study is an AI-powered study assistant that helps students understand questions, diagrams, and notes from images.

Users can:

- 📸 Upload a question, diagram, or study notes
- ✏️ Ask what they want to understand
- 🤖 Get a simple explanation from Gemini
- 💬 View their study conversation
- 📧 Send their study summary to their email

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Gmail SMTP

## 📁 Project Structure

```text
Snap & Study/
│
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    ├── secrets.toml
    └── secrets.toml.example
⚙️ Setup
1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER

2. Create a virtual environment

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure secrets

Create:
.streamlit/secrets.toml


Add your own credentials:
GEMINI_API_KEY = "your_gemini_api_key"

GMAIL_ADDRESS = "your_gmail@gmail.com"

GMAIL_APP_PASSWORD = "your_gmail_app_password"

Never share or commit your real secrets.

5. Run the application

streamlit run app.py

The application will open in your browser.

🔐 Security

Real API keys and Gmail App Passwords are stored in .streamlit/secrets.toml.

The real secrets.toml file is excluded from GitHub using .gitignore.

👩‍💻 Project

Built as part of an AI project submission