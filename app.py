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

col1, col2 = st.columns([3, 1])

# Reset All button
with col2:
    if st.button("🔄 Reset All"):
        st.session_state.deadlines = []
        st.session_state.study_days = []
        st.session_state.study_times = []
        st.session_state.study_plan = None
        st.session_state.preferences = ""
        st.experimental_rerun()

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

def parse_deadlines(deadlines):
    return [{'course': d['course'], 'date': d['date'].strftime('%Y-%m-%d')} for d in deadlines]

def time_allocation_pie_chart(study_days, study_times, courses):
    if not study_days or not study_times or not courses:
        st.warning("Please select study days, time blocks, and add at least one course.")
        return

    slot_labels = []
    values = []
    i = 0

    for day in study_days:
        for time in study_times:
            course = courses[i % len(courses)]
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

def dashboard_view(study_plan, deadlines_data):
    import datetime

    st.subheader("📅 Weekly Calendar View")

    time_block_map = {
        "Morning": ("08:00 AM", "10:00 AM"),
        "Afternoon": ("01:00 PM", "03:00 PM"),
        "Evening": ("06:00 PM", "08:00 PM"),
    }

    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    today = datetime.date.today()

    schedule = []
    courses = [d['course'] for d in st.session_state.deadlines]
    if not courses:
        st.warning("Add at least one course to see the weekly calendar.")
        return

    course_index = 0
    for day in st.session_state.study_days:
        day_idx = weekday_names.index(day)
        days_ahead = (day_idx - today.weekday() + 7) % 7
        target_date = today + datetime.timedelta(days=days_ahead)

        for time_block in st.session_state.study_times:
            start_time, end_time = time_block_map.get(time_block, ("N/A", "N/A"))
            course = courses[course_index % len(courses)]
            schedule.append({
                "Date": target_date.strftime("%Y-%m-%d"),
                "Course": course,
                "Start Time": start_time,
                "End Time": end_time,
                "Day": day,
                "Time Block": time_block
            })
            course_index += 1

    df_schedule = pd.DataFrame(schedule).reset_index(drop=True)
    st.dataframe(df_schedule, use_container_width=True, hide_index=True)

    st.subheader("📝 Study Plan Summary")
    st.write(study_plan)

    st.subheader("📊 Time Allocation Visualization")
    time_allocation_pie_chart(st.session_state.study_days, st.session_state.study_times, courses)

    st.download_button("💾 Export Plan (.txt)", study_plan, file_name="study_plan.txt")

st.markdown('<h1 style="font-family: Times New Roman;">🎓 My AI Study Planner</h1>', unsafe_allow_html=True)
st.write("Let the AI help you organize your study sessions by considering your courses, deadlines, and personal study preferences. Stay efficient and organized!")

st.markdown('<h2 style="font-family: Times New Roman;">🎯 Manage Your Courses & Deadlines</h2>', unsafe_allow_html=True)

if st.button("➕ Add Course"):
    st.session_state.deadlines.append({"course": "", "date": datetime.date.today()})

for idx, d in enumerate(st.session_state.deadlines):
    with st.expander(f"Course {idx+1}"):
        course = st.text_input(f"Course Name {idx+1}", key=f"course_{idx}", value=d['course'])
        date = st.date_input(f"Deadline {idx+1}", key=f"date_{idx}", value=d['date'])
        st.session_state.deadlines[idx] = {"course": course, "date": date}

st.markdown('<h2 style="font-family: Times New Roman;">🧠 Set Your Study Preferences</h2>', unsafe_allow_html=True)

preferences = st.text_area(
    "Personal Preferences (e.g., 45 min per session, Each day 2 hours)",
    value=st.session_state.get("preferences", ""),
    help="Type your study preferences here. e.g., 'study in the morning', '45 minutes per session'"
)
st.session_state.preferences = preferences

selected_days = st.multiselect(
    "📆 Select Study Days",
    options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    key="study_days"
)

selected_times = st.multiselect(
    "⏰ Select Study Time Blocks",
    options=["Morning", "Afternoon", "Evening"],
    key="study_times"
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

st.markdown("---")
