import streamlit as st
from movement_detection import movement_analysis_interface
from ml_recommendations import ml_analysis_interface

def ai_features_page():
    st.title("🤖 AI-Powered Rehabilitation Assistant")
    
    # Navigation for AI features
    ai_feature = st.sidebar.selectbox(
        "Choose AI Feature",
        ["Movement Analysis", "ML Recommendations & Analysis"]
    )
    
    if ai_feature == "Movement Analysis":
        movement_analysis_interface()
    else:
        ml_analysis_interface()

if __name__ == "__main__":
    ai_features_page()

# Requirements (requirements.txt):
"""
streamlit
tensorflow
opencv-python
pandas
numpy
textblob
plotly
scikit-learn
"""