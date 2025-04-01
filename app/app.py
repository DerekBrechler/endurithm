import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shap
from datetime import datetime
import csv

from fueling_engine import goal_logic_run, recommend_macros

# Page config
st.set_page_config(page_title="Endurithm | Fueling Intelligence", layout="wide")

# Custom CSS styling
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        color: #333333;
    }
    .main-title {
        font-size: 2.5em;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 0.2em;
    }
    .subtitle {
        font-size: 1.1em;
        color: #5E6A75;
        margin-bottom: 2em;
    }
    </style>
""", unsafe_allow_html=True)

# Hero section
st.markdown('<div class="main-title">Endurithm</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Precision fueling and macronutrient recommendations for endurance athletes.</div>', unsafe_allow_html=True)

# Load model and encoders
BASE_DIR = os.path.dirname(__file__)
model = joblib.load(os.path.join(BASE_DIR, "..", "models", "lightgbm_calorie_model.pkl"))
encoder_sex = joblib.load(os.path.join(BASE_DIR, "..", "models", "encoder_sex.pkl"))
encoder_session = joblib.load(os.path.join(BASE_DIR, "..", "models", "encoder_session.pkl"))

# Sidebar for athlete input
with st.sidebar:
    st.markdown("### Athlete Profile")
    user_id = st.text_input("Athlete ID", "A001")
    age = st.slider("Age", 18, 50, 23)
    height = st.number_input("Height (cm)", value=180)
    weight = st.number_input("Weight (lbs)", value=160)
    goal = st.selectbox("Goal", ["cutting", "maintain", "bulking"])
    sport = st.selectbox("Sport", [
        "marathon_running", "track_and_field_distance", "track_and_field_mid", "track_and_field_power"
    ])

    st.markdown("---")
    st.markdown("### Workout Session")

    sex = st.selectbox("Sex", ["M", "F"])
    session_type = st.selectbox("Session Type", ["long_run", "tempo", "intervals"])
    age = st.number_input("Age", min_value=18, max_value=50, value=23, step=1)
    vo2_max = st.number_input("VO₂ Max", min_value=30, max_value=75, value=50)
    resting_hr = st.number_input("Resting HR", min_value=35, max_value=80, value=55)
    baseline_hrv = st.number_input("Baseline HRV", min_value=50, max_value=120, value=80)
    avg_hr = st.number_input("Average HR", min_value=100, max_value=190, value=160)
    max_hr = st.number_input("Max HR", min_value=avg_hr + 5, max_value=200, value=avg_hr + 15)
    distance_km = st.number_input("Distance (km)", min_value=1.0, max_value=42.0, value=10.0, step=0.1)
    duration_min = st.number_input("Duration (min)", min_value=20, max_value=240, value=60, step=1)
    elevation_gain_m = st.number_input("Elevation Gain (m)", min_value=0, max_value=1000, value=100)
    sleep_hrs_prior = st.number_input("Sleep (hrs prior)", min_value=0.0, max_value=12.0, value=7.5, step=0.1)
    hrv_today = st.number_input("HRV Today", min_value=30.0, max_value=120.0, value=75.0, step=0.1)
    temp_c = st.number_input("Temperature (°C)", min_value=-10, max_value=40, value=20)

    st.markdown("---")
    st.markdown("Help improve Endurithm: [Submit Feedback](https://forms.gle/your_form_link)")

# Encode categorical variables
encoded_sex = encoder_sex.transform([sex])[0]
encoded_session = encoder_session.transform([session_type])[0]

# Define features used in the model
features = [
    "age", "sex", "weight_kg", "vo2_max", "resting_hr", "baseline_hrv",
    "avg_hr", "max_hr", "distance_km", "duration_min", "elevation_gain_m",
    "sleep_hrs_prior", "hrv_today", "temp_c", "session_type",
    "hr_fluctuation", "fatigue_index", "depletion_score"
]

# Feature engineering UNIQUE ASPECTS
depletion_score = duration_min * avg_hr
hr_fluctuation = max_hr - avg_hr
fatigue_index = (baseline_hrv - hrv_today) if hrv_today < baseline_hrv else 0

# Build session input
session = pd.DataFrame([{
    "age": age,
    "sex": encoded_sex,
    "weight_kg": round(weight * 0.453592, 1),
    "vo2_max": vo2_max,
    "resting_hr": resting_hr,
    "baseline_hrv": baseline_hrv,
    "avg_hr": avg_hr,
    "max_hr": max_hr,
    "distance_km": distance_km,
    "duration_min": duration_min,
    "elevation_gain_m": elevation_gain_m,
    "sleep_hrs_prior": sleep_hrs_prior,
    "hrv_today": hrv_today,
    "temp_c": temp_c,
    "session_type": encoded_session,
    "hr_fluctuation": hr_fluctuation,
    "fatigue_index": fatigue_index,
    "depletion_score": depletion_score
}])

# Predict calories
calories_burned = model.predict(session[features])[0]
final_goal = goal_logic_run(user_id, age, height, weight, goal, sport)
macro_plan = recommend_macros(calories_burned, sport, final_goal)
clean_plan = {k: round(float(v), 2) if isinstance(v, (float, int)) else v for k, v in macro_plan.items()}

# Layout columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Fueling Summary")
    st.metric("Calories Burned", f"{calories_burned:.2f} kcal")
    st.metric("Goal", final_goal.capitalize())

with col2:
    st.subheader("🍽️ Macro Breakdown")
    st.json(clean_plan)

# Log button
if st.button("📥 Log This Session"):
    log_file = os.path.join(BASE_DIR, "fueling_log.csv")
    log_fields = [
        "timestamp", "athlete_id", "calories_burned", "goal", "replenish_kcal",
        "carbs_g", "protein_g", "fat_g", "carbs_kcal", "protein_kcal", "fat_kcal",
        "profile_type"
    ]
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "athlete_id": user_id,
        "calories_burned": round(calories_burned, 2),
        "goal": final_goal,
        "replenish_kcal": clean_plan["total_kcal_to_replenish"],
        "carbs_g": clean_plan["carbs_g"],
        "protein_g": clean_plan["protein_g"],
        "fat_g": clean_plan["fat_g"],
        "carbs_kcal": clean_plan["carbs_kcal"],
        "protein_kcal": clean_plan["protein_kcal"],
        "fat_kcal": clean_plan["fat_kcal"],
        "profile_type": clean_plan["profile_type"]
    }
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=log_fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)
    st.success("✅ Session logged to fueling_log.csv")

# Logged session history
log_file = os.path.join(BASE_DIR, "fueling_log.csv")
if os.path.exists(log_file):
    st.subheader("📈 Logged Session History")
    df_log = pd.read_csv(log_file)
    fig, ax = plt.subplots()
    sns.lineplot(data=df_log, y="calories_burned", x=range(len(df_log)), marker="o", ax=ax)
    ax.set_title("Calories Burned Over Sessions")
    ax.set_xlabel("Session Number")
    ax.set_ylabel("Calories Burned (kcal)")
    st.pyplot(fig)
else:
    st.info("No session log found. Run main.py or log a session to generate fueling_log.csv")

# SHAP explainer section
st.subheader("🔍 SHAP Feature Impact Explanation")
explainer = shap.Explainer(model)
shap_values = explainer(session[features])
st.write("### Session Inputs Used")
st.dataframe(session[features].T.rename(columns={session.index[0]: "value"}))
fig, ax = plt.subplots()
shap.plots.bar(shap_values[0], max_display=10, show=False)
plt.tight_layout()
st.pyplot(fig)
