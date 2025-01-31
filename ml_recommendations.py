import streamlit as st
import pandas as pd
import numpy as np
from textblob import TextBlob
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Run this in a Python console once
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class RehabMLAnalysis:
    def __init__(self):
        if 'exercise_history' not in st.session_state:
            st.session_state.exercise_history = []
        if 'emotional_scores' not in st.session_state:
            st.session_state.emotional_scores = []
            
    def analyze_sentiment(self, notes):
        """Analyze sentiment of progress notes"""
        if not notes:
            return 0
        
        analysis = TextBlob(notes)
        return analysis.sentiment.polarity
    
    def get_exercise_recommendations(self, progress_data):
        """Generate personalized exercise recommendations based on progress"""
        if not progress_data:
            return []
            
        df = pd.DataFrame(progress_data)
        
        # Calculate exercise frequency and performance
        exercise_stats = df.groupby('exercise').agg({
            'duration': ['mean', 'count'],
            'completion_rate': 'mean'
        }).reset_index()
        
        recommendations = []
        
        # Analyze each exercise
        for _, row in exercise_stats.iterrows():
            exercise = row['exercise']
            freq = row[('duration', 'count')]
            avg_duration = row[('duration', 'mean')]
            completion = row[('completion_rate', 'mean')]
            
            if freq < 3:
                recommendations.append(f"Try to do more {exercise} sessions")
            if completion < 0.7:
                recommendations.append(f"Focus on completing full sets of {exercise}")
            if avg_duration < 10:
                recommendations.append(f"Gradually increase duration of {exercise}")
                
        return recommendations
    
    def predict_milestones(self, progress_data):
        """Predict recovery milestones based on progress patterns"""
        if not progress_data:
            return []
            
        df = pd.DataFrame(progress_data)
        
        # Calculate improvement rates
        df['improvement_rate'] = df.groupby('exercise')['performance_score'].diff()
        
        milestones = []
        for exercise in df['exercise'].unique():
            exercise_data = df[df['exercise'] == exercise]
            
            if len(exercise_data) >= 5:  # Need minimum data points
                avg_improvement = exercise_data['improvement_rate'].mean()
                current_score = exercise_data['performance_score'].iloc[-1]
                
                # Predict time to reach next milestone
                if avg_improvement > 0:
                    days_to_milestone = (0.8 - current_score) / avg_improvement
                    milestone_date = datetime.now() + timedelta(days=days_to_milestone)
                    
                    milestones.append({
                        'exercise': exercise,
                        'predicted_date': milestone_date.strftime('%Y-%m-%d'),
                        'target_score': 0.8
                    })
                    
        return milestones

def ml_analysis_interface():
    """ML Analysis Interface"""
    st.subheader("🤖 AI Analysis & Recommendations")
    
    ml_analyzer = RehabMLAnalysis()
    
    # Progress Notes Analysis
    st.write("### Sentiment Analysis of Progress Notes")
    notes = st.text_area("Enter your progress notes")
    if notes:
        sentiment = ml_analyzer.analyze_sentiment(notes)
        st.session_state.emotional_scores.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'score': sentiment
        })
        
        # Display sentiment analysis
        st.write(f"Sentiment Score: {sentiment:.2f}")
        if sentiment > 0.3:
            st.success("You're showing positive progress!")
        elif sentiment < -0.3:
            st.warning("Consider talking to your healthcare provider about any concerns.")
            
        # Plot emotional trend
        if st.session_state.emotional_scores:
            df_emotions = pd.DataFrame(st.session_state.emotional_scores)
            fig = px.line(df_emotions, x='date', y='score', 
                         title='Emotional Wellbeing Trend')
            st.plotly_chart(fig)
    
    # Exercise Recommendations
    st.write("### Personalized Recommendations")
    if st.session_state.exercise_history:
        recommendations = ml_analyzer.get_exercise_recommendations(
            st.session_state.exercise_history
        )
        for rec in recommendations:
            st.info(rec)
            
        # Milestone Predictions
        st.write("### Predicted Milestones")
        milestones = ml_analyzer.predict_milestones(
            st.session_state.exercise_history
        )
        if milestones:
            for milestone in milestones:
                st.write(f"🎯 {milestone['exercise']}: Target score of {milestone['target_score']} "
                        f"predicted by {milestone['predicted_date']}")
                        
        # Progress Visualization
        st.write("### Progress Analysis")
        df_progress = pd.DataFrame(st.session_state.exercise_history)
        if not df_progress.empty:
            fig = px.scatter(df_progress, x='date', y='performance_score',
                           color='exercise', title='Exercise Performance Over Time')
            st.plotly_chart(fig)
    else:
        st.info("Start logging your exercises to get personalized recommendations!")