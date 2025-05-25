import streamlit as st
import cohere
import datetime
import pandas as pd
import plotly.express as px

# Load secrets
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
except KeyError as e:
    st.error(f"Missing secret: {e}")
    st.stop()

# Initialize Cohere client
co = cohere.Client(cohere_api_key)

# Reset state on first load
if "initialized" not in st.session_state:
    st.session_state.deadlines = []
    st.session_state.study_days = []
    st.session_state.study_times = []
    st.session_state.study_plan = None
    st.session_state.preferences = ""
    st.session_state.initialized = True

# Create columns for the layout
col1, col2 = st.columns([3, 1])

# Reset All button
with col2:
    if st.button("🔄 Reset All"):
        st.session_state.deadlines = []
        st.session_state.study_days = []
        st.session_state.study_times = []
        st.session_state.study_plan = None
        st.session_state.preferences = ""
        st.rerun()

# Function to generate study plan
def generate_study_plan(course_load, deadlines, preferences, study_days, study_times):
    prompt = (
        f"Generate a detailed weekly study plan for the following courses: {course_load}. "
        f"Deadlines: {deadlines}. Preferences: {preferences}. "
        f"Study Days: {study_days}. Study Times: {study_times}."
    )
    try:
        response = co.chat(model="command", message=prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating study plan: {e}")
        return None

# Function to parse deadlines for calendar
def parse_deadlines(deadlines):
    return [{'course': d['course'], 'date': d['date'].strftime('%Y-%m-%d')} for d in deadlines]

# Function for Time Allocation Visualization
def time_allocation_pie_chart(study_days, study_times, courses):
    if not study_days or not study_times or not courses:
        st.warning("Please select study days, time blocks, and add at least one course.")
        return

    slot_labels = []
    values = []
    i = 0

    for day in study_days:
        for time in study_times:
            course = courses[i % len(courses)]  # cycle through courses
            slot_labels.append(f"{day} {time} - {course}")
            values.append(1)
            i += 1

    fig = px.pie(
        names=slot_labels,
        values=values,
        title="🧠 Study Time Allocation by Subject",
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(clickmode='none')

    st.plotly_chart(fig, use_container_width=True)

# Dashboard display
def dashboard_view(study_plan, deadlines_data):
    st.subheader("📅 Weekly Calendar View")
    df = pd.DataFrame(deadlines_data)
    df['date'] = pd.to_datetime(df['date'])  # Ensure it's in datetime format
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')  # Format to display only the date part
    df = df.set_index('date')
    st.write(df)

    st.subheader("📝 Study Plan Summary")
    st.write(study_plan)

    st.subheader("📊 Time Allocation Visualization")
    course_list = [d['course'] for d in st.session_state.deadlines]
    time_allocation_pie_chart(st.session_state.study_days, st.session_state.study_times, course_list)

    st.download_button("💾 Export Plan (.txt)", study_plan, file_name="study_plan.txt")

# App Title
st.markdown('<h1 style="font-family: Times New Roman;">🎓 My AI Study Planner</h1>', unsafe_allow_html=True)
st.write("Let the AI help you organize your study sessions by considering your courses, deadlines, and personal study preferences. Stay efficient and organized!")

# Dynamic Course Inputs
st.markdown('<h2 style="font-family: Times New Roman;">🎯 Manage Your Courses & Deadlines</h2>', unsafe_allow_html=True)

if st.button("➕ Add Course"):
    st.session_state.deadlines.append({"course": "", "date": datetime.date.today()})

for idx, d in enumerate(st.session_state.deadlines):
    with st.expander(f"Course {idx+1}"):
        course = st.text_input(f"Course Name {idx+1}", key=f"course_{idx}", value=d['course'])
        date = st.date_input(f"Deadline {idx+1}", key=f"date_{idx}", value=d['date'])
        st.session_state.deadlines[idx] = {"course": course, "date": date}

# Preferences Section
st.markdown('<h2 style="font-family: Times New Roman;">🧠 Set Your Study Preferences</h2>', unsafe_allow_html=True)

preferences = st.text_area(
    "Personal Preferences (e.g., 45 min per session, Each day 2 hours)",
    value=st.session_state.get("preferences", ""),
    help="Type your study preferences here. e.g., 'study in the morning', '45 minutes per session'"
)
st.session_state.preferences = preferences

# Study Days Selection
st.session_state.study_days = st.multiselect(
    "📆 Select Study Days",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=st.session_state.study_days
)

# Study Time Blocks Selection
st.session_state.study_times = st.multiselect(
    "⏰ Select Study Time Blocks",
    ["Morning", "Afternoon", "Evening"],
    default=st.session_state.study_times
)

# Generate or Regenerate Study Plan
def create_and_display_plan():
    if st.session_state.deadlines and st.session_state.preferences and st.session_state.study_days and st.session_state.study_times:
        course_list = [d['course'] for d in st.session_state.deadlines]
        deadlines_text = "; ".join([f"{d['course']} by {d['date']}" for d in st.session_state.deadlines])
        plan = generate_study_plan(
            ", ".join(course_list),
            deadlines_text,
            st.session_state.preferences,
            ", ".join(st.session_state.study_days),
            ", ".join(st.session_state.study_times)
        )
        if plan:
            st.session_state.study_plan = plan
            dashboard_view(plan, parse_deadlines(st.session_state.deadlines))
    else:
        st.error("Please fill in all required fields.")

# Generate Study Plan Button
if st.button("🚀 Generate Study Plan"):
    create_and_display_plan()

# Regenerate Button
if st.session_state.get("study_plan"):
    if st.button("🔁 Regenerate Plan"):
        create_and_display_plan()

# Footer
st.markdown("---")
