import streamlit as st
import requests
import pandas as pd
import numpy as np
from PIL import Image
import uuid
from datetime import datetime, date
import json
import predict
import streamlit.components.v1 as components
from movement_detection import movement_analysis_interface
from ml_recommendations import ml_analysis_interface

# Configure page
st.set_page_config(
    page_title="Stroke Prediction & Rehabilitation System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:8000"

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'patient_id' not in st.session_state:
    st.session_state.patient_id = str(uuid.uuid4())
if 'risk_history' not in st.session_state:
    st.session_state.risk_history = []
if 'rehab_progress' not in st.session_state:
    st.session_state.rehab_progress = []

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp header {
        display: none;
    }

    .stMarkdown, .stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div>select, 
    .stNumberInput>div>div>input, .stSlider>div>div>div>div {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stNumberInput>div>div>input {
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #ddd;
    }

    .stSlider>div>div>div>div {
        border-radius: 8px;
    }

    .stMarkdown h1 {
        color: #4CAF50;
        font-size: 36px;
    }
    .stMarkdown h2 {
        color: #4CAF50;
        font-size: 28px;
    }
    .stMarkdown h3 {
        color: #4CAF50;
        font-size: 24px;
    }

    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }

    .chat-message.user {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }

    .chat-message.bot {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Stroke prediction styles
STROKE_STYLE = "padding: 20px; background-color: #f44336; color: white; margin-bottom: 15px; text-align: center; font-size: 24px; border-radius: 8px;"
STROKE_MESSAGE = "Stroke"
HEALTHY_STYLE = "padding: 20px; background-color: #4cbb17; color: white; margin-bottom: 15px; text-align: center; font-size: 24px; border-radius: 8px;"
HEALTHY_MESSAGE = "Healthy"
ERROR_STYLE = "padding: 20px; background-color: #ffc300; color: white; margin-bottom: 15px; text-align: center; font-size: 24px; border-radius: 8px;"

def print_outcome(outcome):
    """Outcome printing function"""
    if outcome:
        st.write(f'<div style="{STROKE_STYLE}">{STROKE_MESSAGE}</div>', unsafe_allow_html=True)
    else:
        st.write(f'<div style="{HEALTHY_STYLE}">{HEALTHY_MESSAGE}</div>', unsafe_allow_html=True)

def print_error(error):
    """Error print function"""
    st.write(f'<div style="{ERROR_STYLE}">Error: {error}</div>', unsafe_allow_html=True)

def create_feature_input():
    """Create input fields for features"""
    st.subheader("Patient Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=50)
        gender = st.selectbox("Gender", ["Male", "Female"])
        hypertension = st.checkbox("Hypertension")
        heart_disease = st.checkbox("Heart Disease")
    
    with col2:
        glucose = st.number_input("Average Glucose Level", min_value=0.0, value=90.0)
        bmi = st.number_input("BMI", min_value=0.0, value=25.0)
        smoking = st.selectbox("Smoking Status", ["Never Smoked", "Formerly Smoked", "Smokes"])
    
    gender_encoded = 1 if gender == "Female" else 0
    smoking_encoded = {"Never Smoked": 0, "Formerly Smoked": 1, "Smokes": 2}[smoking]
    
    return [age, gender_encoded, hypertension, heart_disease, glucose, bmi, smoking_encoded]

import streamlit as st
import streamlit.components.v1 as components

def chatbot_interface():
    """Medical and Rehabilitation Chatbot Interface"""
    st.subheader("🤖 Medical Assistant with Copilot")
    
    components.html(
        """
        <div style="height: 600px; border: 1px solid #eee; border-radius: 8px; padding: 1rem;">
            <div id="chat-container" style="height: 100%; display: flex; flex-direction: column;">
                <div id="chat-messages" style="flex: 1; overflow-y: auto; margin-bottom: 1rem;"></div>
                <div id="suggestions" style="margin-bottom: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;"></div>
                <div id="chat-input" style="display: flex; gap: 0.5rem;">
                    <input type="text" id="message-input" 
                        style="flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;"
                        placeholder="Type your question about stroke or rehabilitation...">
                    <button onclick="sendMessage()" 
                        style="padding: 0.5rem 1rem; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Send
                    </button>
                </div>
            </div>
        </div>

        <script>
            const qaDatabase = {
                // Stroke Information
                'what is stroke': `A stroke occurs when blood flow to the brain is interrupted, either by a blood clot (ischemic stroke) or burst blood vessel (hemorrhagic stroke). This interruption causes brain cells to die, leading to various symptoms and potential disabilities.`,

                'what to do if someone has stroke': `Immediate steps for stroke (FAST method):
1. Face - Check if one side is drooping
2. Arms - Can they raise both arms?
3. Speech - Is it slurred or strange?
4. Time - Call emergency services immediately

Additional steps:
- Note the time symptoms started
- Keep the person still and calm
- Monitor breathing
- Do not give food or drink
- Place them in recovery position if unconscious`,

                'early warning signs': `Early warning signs of stroke:
- Sudden severe headache
- Difficulty understanding speech
- Vision problems
- Loss of balance
- Facial drooping
- Arm weakness
- Numbness on one side
- Confusion or trouble speaking

Note: Even if symptoms go away, seek immediate medical attention.`,

                'symptoms in women': `Stroke symptoms specific to women:
- Sudden face and limb pain
- Sudden hiccups
- Sudden nausea
- Sudden chest pain
- Sudden shortness of breath
- General weakness
- Disorientation and confusion
- Fainting or loss of consciousness
- Sudden behavioral changes
- Agitation
- Hallucination`,

                'symptoms in men': `Common stroke symptoms in men:
- One-sided weakness or numbness
- Vision problems in one or both eyes
- Slurred speech or difficulty speaking
- Confusion or trouble understanding
- Severe headache with no known cause
- Balance problems or dizziness
- Difficulty walking
- Loss of coordination
- Sudden behavioral changes`,

                'treatment options': `Stroke treatment options:

Immediate Treatments:
- Clot-busting medications (for ischemic stroke)
- Blood pressure management
- Surgery to remove blood clots
- Surgery to repair broken blood vessels
- Medication to prevent blood clots

Long-term Treatments:
- Physical therapy
- Occupational therapy
- Speech therapy
- Cognitive rehabilitation
- Psychological support
- Medications to prevent future strokes

Prevention After Stroke:
- Blood pressure management
- Anticoagulation medication if needed
- Lifestyle modifications
- Regular medical check-ups`,

                'types of stroke': `There are three main types of stroke:

1. Ischemic Stroke:
   - Caused by blood clots blocking arteries
   - Most common type (87% of cases)
   - Requires clot-busting medications

2. Hemorrhagic Stroke:
   - Caused by bleeding in the brain
   - More severe but less common
   - May require surgery

3. Transient Ischemic Attack (TIA):
   - Also called "mini-stroke"
   - Temporary blockage
   - Warning sign for future strokes
   - Requires immediate medical attention`,

                'recovery after stroke': `Stroke recovery process:

Immediate Recovery (Hospital):
- Medical stabilization
- Initial rehabilitation assessment
- Basic movement exercises
- Swallowing evaluation

Early Recovery (First Months):
- Intensive rehabilitation
- Physical therapy sessions
- Speech therapy if needed
- Occupational therapy
- Learning adaptive techniques

Long-term Recovery:
- Continued therapy as needed
- Home exercise program
- Regular medical follow-up
- Support group participation
- Lifestyle modifications`,

                'stroke risk factors': `Common risk factors for stroke include:
1. Medical Conditions:
   - High blood pressure
   - Diabetes
   - Heart disease
   - High cholesterol
   - Previous stroke or TIA

2. Lifestyle Factors:
   - Smoking
   - Excessive alcohol use
   - Lack of exercise
   - Obesity
   - Poor diet

3. Other Factors:
   - Age (risk increases with age)
   - Family history
   - Gender (more common in men)
   - Race (higher risk in some ethnic groups)`,

                'stroke prevention': `Key steps for stroke prevention:
1. Medical Management:
   - Regular blood pressure monitoring
   - Control diabetes
   - Manage heart conditions
   - Take prescribed medications

2. Lifestyle Changes:
   - Quit smoking
   - Limit alcohol intake
   - Exercise regularly
   - Maintain healthy weight
   - Eat a balanced diet
   - Reduce salt intake
   - Control stress levels

3. Regular Check-ups:
   - Annual medical examinations
   - Monitor cholesterol levels
   - Check heart health
   - Discuss risk factors with doctor`,

                // Rehabilitation Content
                'rehabilitation exercises': `Common rehabilitation exercises include:
- Arm Raises: Lift arms slowly to shoulder height, 10 repetitions
- Leg Lifts: Lift legs while sitting/lying, 10 repetitions per leg
- Hand Squeezes: Squeeze soft ball/towel, 15 repetitions per hand
- Walking: Start with short distances, gradually increase
- Balance Exercises: Stand on one leg, 10 seconds each side`,

                'exercise recommendations': `Recommended rehabilitation exercises:
1. Motor Recovery:
   - Arm raises and stretches
   - Leg lifts and knee bends
   - Hand and finger exercises
   - Core strengthening
   - Balance training

2. Daily Living Skills:
   - Dressing practice
   - Eating and drinking exercises
   - Writing and drawing tasks
   - Object manipulation

3. Mobility Training:
   - Supported walking
   - Stair practice
   - Transfer training
   - Gait exercises`,

                'exercise safety': `Safety guidelines for stroke rehabilitation:
1. Before Exercise:
   - Get medical clearance
   - Start slowly
   - Have supervision
   - Set up a safe environment

2. During Exercise:
   - Stop if you feel pain
   - Take frequent breaks
   - Stay hydrated
   - Monitor your breathing
   - Don't overexert yourself

3. Important Precautions:
   - Use support when needed
   - Avoid unstable surfaces
   - Keep exercises simple initially
   - Report any problems to your healthcare team`,

                'help': `I can help you with information about:

Stroke Information:
- What is a stroke?
- Types of stroke
- Symptoms and warning signs
- Risk factors
- Prevention methods
- Emergency response (FAST)
- Treatment options
- Gender-specific symptoms

Rehabilitation & Recovery:
- Recovery process
- Recommended exercises
- Exercise safety guidelines
- Rehabilitation timeline
- Progress tracking

Type your question or click on suggestions below.`
            };

            function getResponse(question) {
                const lowercaseQuestion = question.toLowerCase().trim();
                
                const exactMatches = {
                    'what is stroke': 'stroke_info',
                    'what is a stroke': 'stroke_info',
                    'types of stroke': 'types',
                    'stroke types': 'types',
                    'what to do': 'emergency',
                    'emergency': 'emergency',
                    'fast': 'emergency',
                    'early signs': 'warning',
                    'warning signs': 'warning',
                    'women symptoms': 'women',
                    'symptoms women': 'women',
                    'men symptoms': 'men',
                    'symptoms men': 'men',
                    'treatment': 'treatment',
                    'treatments': 'treatment',
                    'recovery': 'recovery',
                    'risk factors': 'risk',
                    'prevention': 'prevention',
                    'prevent stroke': 'prevention',
                    'exercises': 'exercises',
                    'recommended exercises': 'exercises',
                    'exercise safety': 'safety',
                    'safe exercise': 'safety'
                };

                for (const [phrase, responseKey] of Object.entries(exactMatches)) {
                    if (lowercaseQuestion.includes(phrase)) {
                        switch(responseKey) {
                            case 'stroke_info':
                                return qaDatabase['what is stroke'];
                            case 'types':
                                return qaDatabase['types of stroke'];
                            case 'emergency':
                                return qaDatabase['what to do if someone has stroke'];
                            case 'warning':
                                return qaDatabase['early warning signs'];
                            case 'women':
                                return qaDatabase['symptoms in women'];
                            case 'men':
                                return qaDatabase['symptoms in men'];
                            case 'treatment':
                                return qaDatabase['treatment options'];
                            case 'recovery':
                                return qaDatabase['recovery after stroke'];
                            case 'risk':
                                return qaDatabase['stroke risk factors'];
                            case 'prevention':
                                return qaDatabase['stroke prevention'];
                            case 'exercises':
                                return qaDatabase['exercise recommendations'];
                            case 'safety':
                                return qaDatabase['exercise safety'];
                        }
                    }
                }

                // Keyword matching
                if (lowercaseQuestion.includes('stroke') && lowercaseQuestion.includes('symptom')) {
                    if (lowercaseQuestion.includes('woman') || lowercaseQuestion.includes('women')) {
                        return qaDatabase['symptoms in women'];
                    } else if (lowercaseQuestion.includes('man') || lowercaseQuestion.includes('men')) {
                        return qaDatabase['symptoms in men'];
                    } else {
                        return qaDatabase['early warning signs'];
                    }
                }
                
                if (lowercaseQuestion.includes('prevent')) {
                    return qaDatabase['stroke prevention'];
                }
                if (lowercaseQuestion.includes('risk')) {
                    return qaDatabase['stroke risk factors'];
                }
                if (lowercaseQuestion.includes('emergency') || lowercaseQuestion.includes('fast')) {
                    return qaDatabase['what to do if someone has stroke'];
                }
                if (lowercaseQuestion.includes('exercise') && lowercaseQuestion.includes('safe')) {
                    return qaDatabase['exercise safety'];
                }
                if (lowercaseQuestion.includes('help')) {
                    return qaDatabase['help'];
                }

                return "I don't understand that question. Type 'help' to see available topics, or try asking about stroke symptoms, types, prevention, or treatment options.";
            }

            function suggestFollowUp(message) {
                message = message.toLowerCase();
                
                const followUps = {
                    'general': [
                        'What is a stroke?',
                        'Types of stroke?',
                        'Stroke symptoms?'
                    ],
                    'symptoms': [
                        'Symptoms in women?',
                        'Symptoms in men?',
                        'Warning signs?'
                    ],
                    'emergency': [
                        'What is FAST method?',
                        'Treatment options?',
                        'Recovery process?'
                    ],
                    'treatment': [
                        'Recovery after stroke?',
                        'Rehabilitation exercises?',
                        'Exercise safety?'
                    ],
                    'prevention': [
                        'Risk factors?',
                        'Prevention methods?',
                        'Treatment options?'
                    ]
                };

                if (message.includes('symptom') || message.includes('sign')) {
                    return followUps.symptoms;
                } else if (message.includes('emergency') || message.includes('fast')) {
                    return followUps.emergency;
                } else if (message.includes('treat') || message.includes('recovery')) {
                    return followUps.treatment;
                } else if (message.includes('prevent') || message.includes('risk')) {
                    return followUps.prevention;
                }

                return followUps.general;
            }

            function addMessage(text, isUser) {
                const messagesDiv = document.getElementById('chat-messages');
                const messageDiv = document.createElement('div');
                messageDiv.style.marginBottom = '0.5rem';
                messageDiv.style.textAlign = isUser ? 'right' : 'left';
                
                const bubble = document.createElement('div');
                bubble.style.cssText = `
                    display: inline-block;
                    max-width: 80%;
                    padding: 0.5rem 1rem;
                    border-radius: 1rem;
                    background-color: ${isUser ? '#4CAF50' : '#f0f0f0'};
                    color: ${isUser ? 'white' : 'black'};
                    white-space: pre-wrap;
                    margin: ${isUser ? '0 0 0 20%' : '0 20% 0 0'};
                `;
                bubble.textContent = text;
                
                messageDiv.appendChild(bubble);
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                
                if (!isUser) {
                    showSuggestions(suggestFollowUp(text));
                }
            }

            function showSuggestions(suggestions) {
                const suggestionsDiv = document.getElementById('suggestions');
                suggestionsDiv.innerHTML = '';
                
                suggestions.forEach(suggestion => {
                    const button = document.createElement('button');
                    button.textContent = suggestion;
                    button.style.cssText = `
                        padding: 0.25rem 0.75rem;
                        background-color: #e0e0e0;
                        border: none;
                        border-radius: 15px;
                        margin: 0.25rem;
                        cursor: pointer;
                        font-size: 0.9rem;
                        transition: background-color 0.2s;
                    `;
                    button.onmouseover = () => button.style.backgroundColor = '#d0d0d0';
                    button.onmouseout = () => button.style.backgroundColor = '#e0e0e0';
                    button.onclick = () => {
                        document.getElementById('message-input').value = suggestion;
                        sendMessage();
                    };
                    suggestionsDiv.appendChild(button);
                });
            }

            function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                if (message) {
                    addMessage(message, true);
                    setTimeout(() => {
                        const response = getResponse(message);
                        addMessage(response, false);
                    }, 500);
                    input.value = '';
                }
            }

            // Add enter key listener
            document.getElementById('message-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            // Initialize with welcome message
            addMessage("Welcome! I'm here to help you with stroke-related questions and rehabilitation guidance. Type 'help' to see all topics, or click on the suggestions below.", false);
            
            // Show initial suggestions
            showSuggestions([
                'What exercises are recommended?',
                'How to exercise safely?',
                'How to track progress?'
            ]);
        </script>
        """,
        height=650,
    )

    # Initialize session state for chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def risk_analysis():
    """Risk Factor Analysis Interface"""
    st.subheader("🔍 Risk Factor Analysis")
    
    smoking = st.slider("Smoking (packs per day)", 0.0, 3.0, 0.5, 0.1)
    blood_pressure = st.slider("Systolic Blood Pressure", 90, 200, 120, 1)
    physical_activity = st.slider("Physical Activity (hours per week)", 0, 20, 5, 1)
    diet_quality = st.select_slider(
        "Diet Quality",
        options=["Poor", "Fair", "Good", "Excellent"],
        value="Good"
    )

    if st.button("Analyze Risk"):
        risk_score = (smoking / 3.0 * 25) + \
                    ((blood_pressure - 90) / 110 * 25) + \
                    ((20 - physical_activity) / 20 * 25) + \
                    {"Poor": 25, "Fair": 15, "Good": 5, "Excellent": 0}[diet_quality]
        
        risk_level = "High" if risk_score > 70 else "Medium" if risk_score > 30 else "Low"
        st.write(f"### Risk Score: {risk_score:.2f} (Risk Level: {risk_level})")

def mri_ct_prediction():
    """MRI/CT Stroke Prediction"""
    st.subheader("📸 Stroke Prediction with MRI/CT Scans")
    
    uploaded_file = st.file_uploader("Upload an MRI or CT image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Predict Stroke"):
            try:
                stroke = predict.predict(uploaded_file)
                print_outcome(stroke)
            except Exception as e:
                print_error(e)
import streamlit as st
import datetime

# Initialize session state
if 'rehab_progress' not in st.session_state:
    st.session_state.rehab_progress = []
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def chatbot_response(prompt):
    """
    Generate responses for the rehabilitation chatbot
    Args:
        prompt (str): User's input question
    Returns:
        str: Chatbot's response
    """
    responses = {
        "exercise": "Regular exercise is crucial for stroke recovery. Start with gentle exercises and gradually increase intensity.",
        "help": "I can help you track your exercises and provide general rehabilitation information.",
        "tired": "It's normal to feel tired. Make sure to rest between exercises and don't overexert yourself.",
    }
    
    for key in responses:
        if key in prompt.lower():
            return responses[key]
    return "I understand you have a question about stroke rehabilitation. Please be more specific or consult with your healthcare provider for medical advice."

def ai_features_page():
    """AI-Powered Rehabilitation Assistant"""
    st.title("🤖 AI-Powered Rehabilitation Assistant")
    
    # Navigation for AI features
    ai_feature = st.selectbox(
        "Choose AI Feature",
        ["Movement Analysis", "ML Recommendations & Analysis"]
    )
    
    if ai_feature == "Movement Analysis":
        movement_analysis_interface()
    else:
        ml_analysis_interface()

# Main app navigation
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Chatbot", "Risk Analysis", "MRI/CT Prediction", "Rehabilitation"]
)

if menu == "Home":
    st.title("🧠 Stroke Prediction & Rehabilitation System")
    st.write("Welcome to the Stroke Prediction & Rehabilitation System. Navigate through the menu to explore features.")
    
    st.markdown("""
    ### Available Features:
    1. **Medical Assistant Chatbot** - Get answers to your questions about stroke
    2. **Risk Analysis** - Analyze your stroke risk factors
    3. **MRI/CT Prediction** - Upload brain scans for stroke detection
    4. **Rehabilitation** - Exercise recommendations, progress tracking, and rehabilitation chatbot
    """)

elif menu == "Chatbot":
    chatbot_interface()
elif menu == "Risk Analysis":
    risk_analysis()
elif menu == "MRI/CT Prediction":
    mri_ct_prediction()
elif menu == "Rehabilitation":
    ai_features_page()