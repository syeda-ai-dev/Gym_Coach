import streamlit as st
import requests
import json
import io
from PIL import Image
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Gym Coach AI",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL - change this to your FastAPI server URL when deployed
API_URL = "http://localhost:8000"

# Define the pages
pages = {
    "Workout Planner": "workout_planner",
    "AI Coach": "ai_coach",
    "Food Scanner": "food_scanner",
    "Meal Planner": "meal_planner"
}

# Sidebar navigation
st.sidebar.title("Gym Coach AI")
st.sidebar.image("https://img.icons8.com/color/96/000000/personal-trainer.png", width=100)
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Helper function to display exercise details
def display_workout_segment(segment, title):
    st.subheader(title)
    st.write(f"**Motto:** {segment['motto']}")
    st.write(f"**Duration:** {segment['duration']}")
    
    if segment.get('video_url'):
        st.video(segment['video_url'])
    
    for i, exercise in enumerate(segment['exercises']):
        with st.expander(f"{i+1}. {exercise['name']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Sets:** {exercise['sets']}")
                st.write(f"**Reps:** {exercise['reps']}")
            with col2:
                st.write(f"**Rest:** {exercise['rest']}")
            st.write(f"**Instructions:** {exercise['instructions']}")

# Helper function to display meal details
def display_meal(meal, meal_type):
    st.subheader(meal_type)
    st.write(f"**{meal['name']}**")
    st.write(meal['description'])
    
    # Nutrition info
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{meal['calories']} kcal")
    col2.metric("Protein", f"{meal['protein']}g")
    col3.metric("Carbs", f"{meal['carbs']}g")
    col4.metric("Fat", f"{meal['fat']}g")
    
    st.write(f"**Why this meal:** {meal['rationale']}")
    
    # Preparation steps
    st.write("**Preparation:**")
    for i, step in enumerate(meal['preparation_steps']):
        st.write(f"{i+1}. {step}")

# Page content based on selection
if selection == "Workout Planner":
    st.title("Personalized Workout Planner")
    st.write("Generate a customized workout plan based on your profile and goals.")
    
    with st.form("workout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            primary_goal = st.selectbox(
                "Primary Goal",
                ["Build muscle", "Lose weight", "Eat healthier"]
            )
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=70.0, step=0.5)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
            is_meat_eater = st.checkbox("I eat meat", value=True)
            is_lactose_intolerant = st.checkbox("I am lactose intolerant")
        
        with col2:
            eating_style = st.selectbox(
                "Eating Style",
                ["Balanced", "Vegan", "Vegetarian", "Keto", "Paleo", "None"]
            )
            caffeine_consumption = st.selectbox(
                "Caffeine Consumption",
                ["None", "Occasionally", "Regularly", "Cravings"]
            )
            sugar_consumption = st.selectbox(
                "Sugar Consumption",
                ["None", "Occasionally", "Regularly", "Cravings"]
            )
            allergies = st.text_input("Allergies (comma separated)")
        
        submit_button = st.form_submit_button("Generate Workout Plan")
    
    if submit_button:
        with st.spinner("Generating your personalized workout plan..."):
            # Prepare the request payload
            payload = {
                "primary_goal": primary_goal,
                "weight_kg": weight,
                "height_cm": height,
                "is_meat_eater": is_meat_eater,
                "is_lactose_intolerant": is_lactose_intolerant,
                "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
                "eating_style": eating_style,
                "caffeine_consumption": caffeine_consumption,
                "sugar_consumption": sugar_consumption
            }
            
            try:
                response = requests.post(f"{API_URL}/workout-planner/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        st.success("Workout plan generated successfully!")
                        
                        # Display the workout plan
                        workout_plan = data.get("workout_plan", [])
                        
                        # Create tabs for each day
                        if workout_plan:
                            tabs = st.tabs([day["day"] for day in workout_plan])
                            
                            for i, day in enumerate(workout_plan):
                                with tabs[i]:
                                    st.header(f"{day['day']} - {day['focus']}")
                                    
                                    # Display workout segments
                                    display_workout_segment(day["warm_up"], "Warm Up")
                                    display_workout_segment(day["main_routine"], "Main Routine")
                                    display_workout_segment(day["cool_down"], "Cool Down")
                    else:
                        st.error(f"Error: {data.get('error', 'Unknown error')}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to the API: {str(e)}")

elif selection == "AI Coach":
    st.title("AI Gym Coach")
    st.write("Chat with your personal AI gym coach for fitness advice and motivation.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask your gym coach a question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                with st.spinner("Coach is thinking..."):
                    response = requests.post(
                        f"{API_URL}/coach/chat",
                        json={"message": prompt}
                    )
                    
                    if response.status_code == 200:
                        full_response = response.json().get("response", "Sorry, I couldn't process your request.")
                    else:
                        full_response = f"Error: {response.status_code} - {response.text}"
            except Exception as e:
                full_response = f"Error connecting to the API: {str(e)}"
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

elif selection == "Food Scanner":
    st.title("Food Scanner")
    st.write("Upload a photo of your food to get nutritional information and health insights.")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_column_width=True)
        
        # Analyze button
        if st.button("Analyze Food"):
            with st.spinner("Analyzing your food..."):
                try:
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)
                    
                    # Send the image to the API
                    files = {"image": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/food-scanner/analyze", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("success", False) and data.get("analysis"):
                            analysis = data["analysis"]
                            
                            # Display food items identified
                            st.subheader("Food Items Identified")
                            st.write(", ".join(analysis["food_items"]))
                            
                            # Display nutritional information
                            st.subheader("Nutritional Information")
                            nutrition = analysis["nutrition"]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Calories", f"{nutrition['calories']} kcal")
                            col2.metric("Protein", f"{nutrition['protein']}g")
                            col3.metric("Carbs", f"{nutrition['carbs']}g")
                            col4.metric("Fat", f"{nutrition['fat']}g")
                            
                            # Display health benefits
                            st.subheader("Health Benefits")
                            for benefit in analysis["health_benefits"]:
                                st.write(f"• {benefit}")
                            
                            # Display potential concerns
                            if analysis["concerns"]:
                                st.subheader("Potential Concerns")
                                for concern in analysis["concerns"]:
                                    st.write(f"• {concern}")
                        else:
                            st.error(f"Error: {data.get('error', 'Unknown error')}")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to the API: {str(e)}")

elif selection == "Meal Planner":
    st.title("Personalized Meal Planner")
    st.write("Generate a customized meal plan based on your profile and dietary preferences.")
    
    with st.form("meal_planner_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            primary_goal = st.selectbox(
                "Primary Goal",
                ["Build muscle", "Lose weight", "Eat healthier"]
            )
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=70.0, step=0.5)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
            is_meat_eater = st.checkbox("I eat meat", value=True)
            is_lactose_intolerant = st.checkbox("I am lactose intolerant")
        
        with col2:
            eating_style = st.selectbox(
                "Eating Style",
                ["Balanced", "Vegan", "Vegetarian", "Keto", "Paleo", "None"]
            )
            caffeine_consumption = st.selectbox(
                "Caffeine Consumption",
                ["None", "Occasionally", "Regularly"]
            )
            sugar_consumption = st.selectbox(
                "Sugar Consumption",
                ["None", "Occasionally", "Regularly"]
            )
            allergies = st.text_input("Allergies (comma separated)")
        
        submit_button = st.form_submit_button("Generate Meal Plan")
    
    if submit_button:
        with st.spinner("Generating your personalized meal plan..."):
            # Prepare the request payload
            payload = {
                "primary_goal": primary_goal,
                "weight_kg": weight,
                "height_cm": height,
                "is_meat_eater": is_meat_eater,
                "is_lactose_intolerant": is_lactose_intolerant,
                "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
                "eating_style": eating_style,
                "caffeine_consumption": caffeine_consumption,
                "sugar_consumption": sugar_consumption
            }
            
            try:
                response = requests.post(f"{API_URL}/meal-planner/generate", json=payload)
                
                if response.status_code == 200:
                    meal_plan = response.json()
                    
                    # Create tabs for each meal
                    tabs = st.tabs(["Breakfast", "Lunch", "Snack", "Dinner"])
                    
                    with tabs[0]:
                        display_meal(meal_plan["breakfast"], "Breakfast")
                    
                    with tabs[1]:
                        display_meal(meal_plan["lunch"], "Lunch")
                    
                    with tabs[2]:
                        display_meal(meal_plan["snack"], "Snack")
                    
                    with tabs[3]:
                        display_meal(meal_plan["dinner"], "Dinner")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to the API: {str(e)}")

# Add footer
st.markdown("---")
st.markdown("© 2023 Gym Coach AI - Your Personal Fitness Companion")