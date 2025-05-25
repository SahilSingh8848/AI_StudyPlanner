Personalized  Study Planner Using Genrative AI
This app generates a personalized study plan using AI. Based on the courses you provide, their deadlines, and your study preferences, it creates a smart schedule to help you stay organized and manage your time efficiently.

🔍 How It Works:

Add Your Courses and Deadlines: You can easily input your courses and their respective deadlines into the app.

Set Your Study Preferences: Enter your study preferences, such as preferred study times, session lengths, or any other habits.

AI-Generated Plan: The app uses Cohere’s AI model to generate a detailed study plan based on the information you provide.

Interactive View: The plan is displayed in a user-friendly format, with a weekly calendar view and a study plan summary.


🔧 How to Run

Installation

Clone the repository:
git clone https://github.com/SahilSingh8848/AI_StudyPlanner.git
cd AI_StudyPlanner

Create a virtual environment (recommended):
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install dependencies: pip install -r requirements.txt

Set Up API Key: Create a secrets.toml file in the .streamlit folder with your Cohere API key:
[cohere]

api_key = "YOUR_COHERE_API_KEY" 

Run the App: streamlit run app.py

Start Using: Open the app in your browser, add your courses, deadlines, and preferences to get a personalized study plan!

👨‍💻 Made by Sahil Singh 

GitHub: https://github.com/SahilSingh8848
