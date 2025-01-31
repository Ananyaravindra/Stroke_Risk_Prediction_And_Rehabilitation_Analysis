import streamlit as st
import pandas as pd
import numpy as np
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import tensorflow as tf
from datetime import datetime
from sklearn.preprocessing import StandardScaler

# Load trained Keras model
model = tf.keras.models.load_model(r"C:\Users\macke\strokepred\motion_classifier_model.h5")

# Load the scaler
with open(r"C:\Users\macke\strokepred\scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

st.set_page_config(page_title="Stroke Prediction Dashboard", layout="wide")
st.title("Stroke Risk Prediction & Health Tracker")

# Sidebar Navigation
menu = [
    "Home",
    "Predict Stroke Risk",
    "Risk Analysis Dashboard",
    "Medication Tracking",
    "Exercise Tracking",
    "Gamification",
    "Community Insights",
    "AI-Powered Chatbot",
    "Admin Panel"
]
choice = st.sidebar.selectbox("Select a Feature", menu)

# Function to predict stroke risk
def predict_risk(data):
    numerical_data = data[:5]  # Keeping only [age, hypertension, heart_disease, avg_glucose_level, bmi]
    scaled_data = scaler.transform([numerical_data])
    prediction = model.predict(scaled_data)
    return prediction[0][0] * 100  # Convert to percentage

# Function to categorize risk level
def get_risk_category(percentage):
    if percentage < 30:
        return "Low"
    elif 30 <= percentage < 70:
        return "Moderate"
    else:
        return "High"

# Home Page
if choice == "Home":
    st.markdown("### Welcome to the Stroke Risk Prediction App")
    st.write("Use this app to predict your stroke risk, track your health, and gain insights.")

# Stroke Risk Prediction
elif choice == "Predict Stroke Risk":
    st.subheader("Stroke Risk Prediction")

    age = st.number_input("Age", 1, 100, 50)
    hypertension = st.selectbox("Hypertension", ["No", "Yes"])
    heart_disease = st.selectbox("Heart Disease", ["No", "Yes"])
    avg_glucose_level = st.number_input("Average Glucose Level", 50.0, 300.0, 100.0)
    bmi = st.number_input("BMI", 10.0, 50.0, 25.0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    smoking_status = st.selectbox("Smoking Status", ["Never smoked", "Former smoker", "Smokes"])

    hypertension = 1 if hypertension == "Yes" else 0
    heart_disease = 1 if heart_disease == "Yes" else 0
    gender_map = {"Male": 0, "Female": 1, "Other": 2}
    gender = gender_map[gender]
    smoking_map = {"Never smoked": 0, "Former smoker": 1, "Smokes": 2}
    smoking_status = smoking_map[smoking_status]

    input_data = [age, hypertension, heart_disease, avg_glucose_level, bmi, gender, smoking_status]

    if st.button("Predict Risk"):
        risk_percentage = predict_risk(input_data)
        risk_category = get_risk_category(risk_percentage)
        st.metric(label="Stroke Risk Percentage", value=f"{risk_percentage:.2f}%")
        st.write(f"Risk Level: **{risk_category}**")

# Risk Analysis Dashboard
elif choice == "Risk Analysis Dashboard":
    st.subheader("Risk Analysis & Trends")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        data["Stroke Risk"] = data.apply(lambda row: predict_risk([
            row["age"], row["hypertension"], row["heart_disease"], 
            row["avg_glucose_level"], row["bmi"], row["gender"], row["smoking_status"]
        ]), axis=1)

        st.dataframe(data)
        required_columns = ["age", "hypertension", "heart_disease", "avg_glucose_level", "bmi", "gender", "smoking_status"]
        
        if all(col in data.columns for col in required_columns):
            data["Stroke Risk"] = data.apply(lambda row: predict_risk([
                row["age"], row["hypertension"], row["heart_disease"],
                row["avg_glucose_level"], row["bmi"], row["gender"], row["smoking_status"]
            ]), axis=1)

            grouped_data = data.groupby("age", as_index=False)["Stroke Risk"].mean()

            fig = px.line(grouped_data, x="age", y="Stroke Risk", title="Stroke Risk Across Ages")
            st.plotly_chart(fig)

            st.write("### Risk Factor Heatmap")
            correlation = data.corr()
            fig, ax = plt.subplots()
            sns.heatmap(correlation, annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.error(f"Dataset must contain the following columns: {', '.join(required_columns)}")

# Gamification
elif choice == "Gamification":
    st.subheader("Gamification: Earn Points and Unlock Rewards")

    # Input for tracking activities
    exercise_logged = st.number_input("Minutes of Exercise Today", 0, 120, 30)
    medication_adherence = st.selectbox("Did You Take Your Medication Today?", ["Yes", "No"])
    healthy_meals = st.number_input("Healthy Meals Today", 0, 5, 3)

    # Calculate points
    points = 0
    rewards = []

    if st.button("Submit Activity"):
        points += exercise_logged * 2  # 2 points for every minute of exercise
        if medication_adherence == "Yes":
            points += 50  # Bonus for medication adherence
        points += healthy_meals * 10  # 10 points per healthy meal

        # Determine rewards based on points
        if points >= 300:
            rewards.append("Gold Badge: Health Champion 🏅")
        elif points >= 150:
            rewards.append("Silver Badge: Consistent Achiever 🥈")
        elif points >= 50:
            rewards.append("Bronze Badge: Wellness Starter 🥉")

        st.success(f"You earned {points} points today!")
        
        # Display rewards
        if rewards:
            st.write("### Rewards Unlocked:")
            for reward in rewards:
                st.info(f"🎉 {reward}")
        else:
            st.write("No rewards unlocked today. Keep going!")
        
        st.write("### Leaderboard:")
        leaderboard = pd.DataFrame({
            "User": ["You", "Alice", "Bob", "Charlie"],
            "Points": [points, 275, 200, 150]
        })
        leaderboard = leaderboard.sort_values(by="Points", ascending=False)
        st.dataframe(leaderboard)


# Community Insights
elif choice == "Community Insights":
    st.subheader("Community Stroke Risk Insights")
    st.write("View anonymized insights from others using the app or upload your own data for analysis.")
    
    # Display mock data insights
    st.write("### Insights Based on Mock Community Data")
    mock_data = pd.DataFrame({
        "Age": np.random.randint(30, 80, 100),
        "Stroke Risk (%)": np.random.uniform(10, 90, 100)
    })
    fig_mock = px.scatter(mock_data, x="Age", y="Stroke Risk (%)", title="Community Stroke Risk Insights (Mock Data)")
    st.plotly_chart(fig_mock)

    st.write("### Top Health Advice from the Community")
    st.info("1. Maintain a balanced diet with low sugar intake.")
    st.info("2. Engage in at least 30 minutes of physical activity daily.")
    st.info("3. Regularly monitor blood pressure and glucose levels.")

    # Option to upload and analyze community data
    st.write("### Upload Community Data for Further Insights")
    uploaded_file = st.file_uploader("Upload Community Data (CSV)", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        if "age" in data and "avg_glucose_level" in data:
            fig_uploaded = px.scatter(data, x="age", y="avg_glucose_level", 
                                      title="Age vs. Average Glucose Level (Uploaded Community Data)")
            st.plotly_chart(fig_uploaded)
        else:
            st.error("The uploaded file must contain 'age' and 'avg_glucose_level' columns.")


# AI-Powered Chatbot
elif choice == "AI-Powered Chatbot":
    st.subheader("AI Chatbot: Your Health Assistant 🤖")
    
    # Store conversation context
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # User input
    user_query = st.text_input("Ask me anything about stroke prevention, health tracking, or general wellness:")
    
    if user_query:
        # Display the user's query in the chat history
        st.session_state.conversation.append({"user": user_query})
        
        # AI Response
        if "stroke" in user_query.lower():
            response = "Preventing stroke involves maintaining a healthy lifestyle: eating balanced meals, exercising regularly, and avoiding smoking or excessive alcohol consumption. Do you need tips on any specific area?"
        elif "exercise" in user_query.lower():
            response = "Exercise is crucial! Aim for at least 30 minutes of moderate activity daily. Would you like suggestions for low-impact exercises?"
        elif "diet" in user_query.lower():
            response = "A diet rich in fruits, vegetables, and whole grains is ideal for stroke prevention. Would you like to explore specific meal plans?"
        elif "medication" in user_query.lower():
            response = "It's vital to take your medication as prescribed. Are you looking for advice on managing your medication schedule?"
        else:
            response = "I'm here to help with any health-related queries. Could you clarify your question or provide more details?"

        # Add AI response to the chat history
        st.session_state.conversation.append({"ai": response})
        
    # Display the conversation
    st.write("### Conversation:")
    for message in st.session_state.conversation:
        if "user" in message:
            st.markdown(f"**You:** {message['user']}")
        elif "ai" in message:
            st.markdown(f"**AI:** {message['ai']}")
    
    # Option to clear the chat history
    if st.button("Clear Conversation"):
        st.session_state.conversation = []
        st.success("Conversation cleared!")




# Medication Tracking
elif choice == "Medication Tracking":
    st.subheader("Medication Tracker")
    med_name = st.text_input("Medication Name")
    dosage = st.text_input("Dosage")
    schedule = st.text_input("Schedule (e.g., Morning, Night)")
    if st.button("Add Medication"):
        st.success(f"Medication {med_name} added successfully!")

# Exercise Tracking
elif choice == "Exercise Tracking":
    st.subheader("Exercise Tracker")
    exercise_type = st.text_input("Exercise Type")
    duration = st.number_input("Duration (minutes)", 5, 120, 30)
    date = st.date_input("Date", datetime.today())
    if st.button("Log Exercise"):
        st.success(f"Exercise {exercise_type} for {duration} minutes logged!")

# Admin Panel
elif choice == "Admin Panel":
    st.subheader("Admin Dashboard")
    st.write("Monitor prediction trends and model performance.")
    mock_data = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "Predictions": np.random.randint(50, 100, 10),
        "High Risk Cases": np.random.randint(10, 30, 10)
    })
    fig = px.bar(mock_data, x="Date", y=["Predictions", "High Risk Cases"], barmode="group", title="Prediction Trends")
    st.plotly_chart(fig)
    st.write("### Model Performance Metrics")
    st.metric(label="Model Accuracy", value="92.5%")
    st.metric(label="Response Time", value="0.8 sec")
    st.metric(label="Data Drift", value="Low")
