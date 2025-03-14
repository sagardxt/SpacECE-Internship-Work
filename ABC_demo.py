import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gtts import gTTS
import os
import speech_recognition as sr
import base64
import mysql.connector
import matplotlib.pyplot as plt
import random
from PIL import Image
import random
from time import time
from random import randint, shuffle 
from datetime import datetime 
import pickle
import bisect 
from groq import Groq
from num2words import num2words  # Convert numbers to words
import json


# Load data from Google Sheets (example URL)
# You should replace with your own Google Sheets URL
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1s8BLc8CNyWAN9u2gJPJZx9Zqs5mc7VR3RgfVM_yMHQk/export?format=csv&id=1s8BLc8CNyWAN9u2gJPJZx9Zqs5mc7VR3RgfVM_yMHQk&gid=0"
    return pd.read_csv(url)


# Load the dataset
df = load_data()

# Check the structure of the dataset to help with visualization
#st.write(df.head())  # Display first few rows to check the data




# List of letters, words, and image URLs from A to Z
letters = [
    ("A", "Apple", "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg"),
    ("B", "Ball", "https://upload.wikimedia.org/wikipedia/commons/7/7a/Basketball.png"),
    ("C", "Cat", "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg"),
    ("D", "Dog", "https://upload.wikimedia.org/wikipedia/commons/d/d9/Collage_of_Nine_Dogs.jpg"),
    ("E", "Elephant", "https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg"),
    ("F", "Fish", "https://upload.wikimedia.org/wikipedia/commons/2/24/Fish_icon.svg"),
    ("G", "Giraffe", "https://upload.wikimedia.org/wikipedia/commons/e/ec/Giraffe_picture.jpg"),
    ("H", "Hat", "https://upload.wikimedia.org/wikipedia/commons/c/cc/Red_hat.jpg"),
    ("I", "Ice Cream", "https://upload.wikimedia.org/wikipedia/commons/9/91/Ice_cream_cone.jpg"),
    ("J", "Jug", "https://upload.wikimedia.org/wikipedia/commons/2/2a/Jug_icon.png"),
    ("K", "Kite", "https://upload.wikimedia.org/wikipedia/commons/0/04/Kite_icon.svg"),
    ("L", "Lion", "https://upload.wikimedia.org/wikipedia/commons/a/a0/Lion_icon.png"),
    ("M", "Monkey", "https://upload.wikimedia.org/wikipedia/commons/5/56/Monkey_icon.png"),
    ("N", "Nest", "https://upload.wikimedia.org/wikipedia/commons/a/a7/Nest_icon.svg"),
    ("O", "Orange", "https://upload.wikimedia.org/wikipedia/commons/4/43/Orange_icon.svg"),
    ("P", "Pencil", "https://upload.wikimedia.org/wikipedia/commons/3/37/Pencil_icon.svg"),
    ("Q", "Queen", "https://upload.wikimedia.org/wikipedia/commons/d/d4/Queen_icon.svg"),
    ("R", "Rainbow", "https://upload.wikimedia.org/wikipedia/commons/7/7e/Rainbow_icon.png"),
    ("S", "Sun", "https://upload.wikimedia.org/wikipedia/commons/a/a3/Sun_icon.svg"),
    ("T", "Tree", "https://upload.wikimedia.org/wikipedia/commons/1/17/Tree_icon.png"),
    ("U", "Umbrella", "https://upload.wikimedia.org/wikipedia/commons/7/74/Umbrella_icon.png"),
    ("V", "Violin", "https://upload.wikimedia.org/wikipedia/commons/d/df/Violin_icon.svg"),
    ("W", "Whale", "https://upload.wikimedia.org/wikipedia/commons/2/2f/Whale_icon.png"),
    ("X", "Xylophone", "https://upload.wikimedia.org/wikipedia/commons/e/ef/Xylophone_icon.png"),
    ("Y", "Yarn", "https://upload.wikimedia.org/wikipedia/commons/0/04/Yarn_icon.svg"),
    ("Z", "Zebra", "https://upload.wikimedia.org/wikipedia/commons/c/c6/Zebra_icon.svg"),
]



# Initialize session state for current word index
if "current_index" not in st.session_state:
    st.session_state["current_index"] = 0




# Add Title
st.title("Child's Education Application")


# Function to add a persistent background image
def add_bg_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({image_url});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        button {{
            background-color: #4CAF50;
            border-radius: 10px;
            padding: 10px;
            font-size: 18px;
            color: white;
            border: none;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #45a049;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



# Function to generate text-to-speech audio dynamically
def generate_audio(text, filename):
    tts = gTTS(text)
    tts.save(filename)


MYSQL_CONFIG = {
        "host": '127.0.0.1',
        "user": 'root',
        "password": '9545883002@Sj',
        "database": 'child_learning'
    }



# Function to recognize speech in real-time
def recognize_live_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Speak now!")
        try:
            audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"Could not request results; {e}"
        except Exception as e:
            return f"Error: {e}"


def update_mysql_table_animal(alphabet_name, is_correct):
    """Insert a new entry into MySQL table with alphabet performance data."""
    try:
        # Establish MySQL connection
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alphabet_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                child_id INT,
                alphabet_name VARCHAR(255) NOT NULL,
                attempt INT DEFAULT 0,
                correct INT DEFAULT 0,
                incorrect INT DEFAULT 0,
                timestamps TEXT,
                dates TEXT
            )
        """)

        # Generate timestamp and date
        current_timestamp = datetime.now().timestamp()
        current_date = datetime.now().date()

        # Always insert a new record for the alphabet
        cursor.execute("""
    INSERT INTO alphabet_data (child_id, alphabet_name, attempt, correct, incorrect, timestamps, dates)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                st.session_state.child_id,  # child_id
                alphabet_name,              # alphabet_name
                1,                          # attempt (always 1 for a single entry)
                1 if is_correct else 0,     # correct (1 if correct, otherwise 0)
                0 if is_correct else 1,     # incorrect (1 if incorrect, otherwise 0)
                current_timestamp,          # timestamps (current timestamp)
                current_date                # dates (current date)
            ))

        # Commit the transaction
        conn.commit()
        print(f"Data inserted successfully for '{alphabet_name}'.")

    except mysql.connector.Error as e:
        raise e
        print(f"Error inserting data into MySQL table: {e}")




# Function to check if the user spoke the correct word for the image shown
def check_spoken_word(correct_word):
    st.write(f"Please speak the word that corresponds to the image shown.")
    spoken_text = recognize_live_speech()
    st.write(f"**You said:** {spoken_text}")
    if spoken_text.strip().lower() == correct_word.lower():
        st.success(f"Correct! 🎉 You correctly identified the word '{correct_word}'.")
        update_mysql_table_animal(word, 1)
    else:
        st.error(f"Incorrect! ❌ The correct word is '{correct_word}'.")
        update_mysql_table_animal(word, 0)


# Initialize session state for login if not already initialized
if 'log' not in st.session_state:
    st.session_state.log = 1

def login_page():
    st.title("Welcome to the Kids Learning App! 🎒")

    st.markdown("""
        Please log in to start using the app.
        Enter your username and password below.
    """)

    # Username and Password Section
    user = st.text_input("username", placeholder="Enter your username")
    p = st.text_input("password", placeholder="Enter your password", type="password")

    # Login Button
    if st.button("Log In"):
        if user and p:
            # Connect to the database
            conn = mysql.connector.connect(
                **MYSQL_CONFIG
            )
            cursor = conn.cursor(dictionary=True)
            
            # Query to check username and password
            query = """
                SELECT child_id, username, password 
                FROM child_details 
                WHERE username = %s AND password = %s
            """
            cursor.execute(query, (user, p))
            user = cursor.fetchone()  # Fetch one record that matches


            # Validate login
            if user:
                st.session_state.log = 2
                st.session_state.child_id = user["child_id"] 
                st.success(f"Welcome! You have successfully logged in.")
            else:
                st.error("Invalid username or password. Please try again.")
        else:
            st.error("Please fill in both username and password.")

    if st.button("Sign Up"):
        st.session_state.log = 3
        st.info("Redirecting to the Sign-Up page...")


if "dashboard_active" not in st.session_state:
    st.session_state["dashboard_active"] = False
def load_data_from_mysql_alpha():
        try:
            # Establish the connection
            conn = mysql.connector.connect(
                **MYSQL_CONFIG
            )

            query = f"SELECT alphabet_name,attempt, correct, incorrect, timestamps, dates FROM alphabet_data where child_id={st.session_state.child_id};"
            df = pd.read_sql(query, conn)
            print(df)
            return df

        except mysql.connector.Error as e:
            st.error(f"Error fetching data from MySQL: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on error
 
def load_child_data():
    try:
        # Establish the connection
        conn = mysql.connector.connect(
            **MYSQL_CONFIG
        )

        query = f"SELECT child_name, username, age, phone, gmail, parent_name FROM child_details where child_id={st.session_state.child_id};"
        df = pd.read_sql(query, conn)

        # Convert the dataframe to JSON
        json_data = df.to_json(orient='records')
        
        return json.loads(json_data)  # Return the JSON object

    except mysql.connector.Error as e:
        st.error(f"Error fetching data from MySQL: {e}")
        return []  # Return an empty list on error
    

def update_signup_table(child_name, age, parent_name, password, phone, gmail, username):
    """Insert new entry into MySQL table with child details."""
    try:
        # Establish the connection
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS child_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                child_name VARCHAR(255) NOT NULL,
                age INT NOT NULL,
                parent_name VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                phone VARCHAR(15) NOT NULL,
                gmail VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert the record into the table
        cursor.execute("""
            INSERT INTO child_details (child_name, age, parent_name, password, phone, gmail, username)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (child_name, age, parent_name, password, phone, gmail, username))

        # Commit the changes to the database
        conn.commit()

    except mysql.connector.Error as e:
        print(f"Error inserting data into MySQL table: {e}")




def signup_page():
    # Initialize session state for login status if not already set
    # if "log" not in st.session_state:
    #     st.session_state.log = 0

    # Create input fields for signup
    st.title("Signup Page")

    child_name = st.text_input("Child's Name", placeholder="Enter child's name")
    age = st.number_input("Age", min_value=1, max_value=18, step=1, format="%d")
    parent_name = st.text_input("Parent's Name", placeholder="Enter parent's name")
    username = st.text_input("Username", placeholder="Choose a username")
    gmail = st.text_input("Gmail", placeholder="Enter Gmail address")
    phone = st.text_input("Phone Number", placeholder="Enter phone number")
    password = st.text_input("Password", type="password", placeholder="Enter a strong password")

    # Button to submit the form
    if st.button("Sign Up"):
        # Validation checks
        if not (child_name and age and parent_name and username and gmail and phone and password):
            st.error("All fields are required. Please fill in all the details.")
        elif "@" not in gmail or "." not in gmail:
            st.error("Please enter a valid Gmail address.")
        elif len(phone) != 10 or not phone.isdigit():
            st.error("Please enter a valid 10-digit phone number.")
        elif len(password) < 6:
            st.error("Password should be at least 6 characters long.")
        else:
            # Simulate saving data (could be a database or file system)
            
            st.success(f"Signup successful! Welcome, {child_name}!, Please log in to continue....")
            update_signup_table(child_name, age, parent_name, password, phone, gmail, username)
    if st.button("Log In"):
        st.session_state.log = 1


def alpha_dashboard_page():
    st.title("Learning Dashboard")

    # Load data from source
    df = load_data_from_mysql_alpha()

    if df.empty:
        st.warning("No data available.")
        return

    # Clean and preprocess data
    try:
        df['dates'] = pd.to_datetime(df['dates'], format="%Y-%m-%d", errors='coerce')
    except Exception as e:
        st.error(f"Error processing date column: {e}")
        return

    # Sidebar filters
    st.sidebar.header("Filters")
    time_filter = st.sidebar.radio("View Progress By", ["Daily", "Weekly", "Monthly"])

    alphabet_names = df['alphabet_name'].unique()
    selected_alphabet = st.sidebar.selectbox("Select Alphabet", ["All"] + list(alphabet_names))

    if selected_alphabet != "All":
        df = df[df['alphabet_name'] == selected_alphabet]

    # Process data for daily, weekly, or monthly trends
    if time_filter == "Daily":
        df['time_period'] = df['dates']
    elif time_filter == "Weekly":
        df['time_period'] = df['dates'].dt.to_period('W').apply(lambda r: r.start_time)
    else:  # Monthly
        df['time_period'] = df['dates'].dt.to_period('M').apply(lambda r: r.start_time)

    trend_data = df.groupby('time_period')[['attempt', 'correct', 'incorrect']].sum().reset_index()

    # Overall summary stats
    total_attempts = df['attempt'].sum()
    total_correct = df['correct'].sum()
    total_incorrect = df['incorrect'].sum()

    # Display overall statistics
    st.subheader("Overall Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Attempts", total_attempts)
    col2.metric("Total Correct", total_correct)
    col3.metric("Total Incorrect", total_incorrect)

    # Bar chart of attempts over alphabets
    st.subheader("Attempts Over Alphabet Names")
    bar_chart_data = df.groupby('alphabet_name')[['attempt', 'correct', 'incorrect']].sum().reset_index()
    fig = px.bar(bar_chart_data, x='alphabet_name', y=['correct', 'incorrect', 'attempt'], barmode='stack',
                labels={'value': 'Count', 'alphabet_name': 'Alphabet Name'}, title="Attempts per Alphabet")
    st.plotly_chart(fig)

    # Correct vs Incorrect pie chart
    st.subheader("Correct Vs Incorrect")
    pie_data = pd.DataFrame({
        "Metric": ["Correct", "Incorrect"],
        "Count": [total_correct, total_incorrect]
    })
    fig = px.pie(pie_data, values="Count", names="Metric", title="Correct vs Incorrect Distribution")
    st.plotly_chart(fig)

    # Trends over selected time period
    st.subheader(f"Trends in Attempts Over {time_filter.lower()}s")
    fig = px.line(trend_data, x='time_period', y=['attempt', 'correct', 'incorrect'],
                labels={'value': 'Count', 'time_period': f'{time_filter}'}, title=f"{time_filter}-Wise Trends")
    st.plotly_chart(fig)

# Conditional rendering based on login state
if st.session_state.log == 2:
    data = load_child_data()

    if data:
        # Create a DataFrame for better visualization
        df = pd.DataFrame(data)


        # Optionally, display the data in a more user-friendly format
        for index, row in df.iterrows():
            # Change the color of the child name (left side)
            st.markdown(f"<p style='color:white; display:inline-block'>Child Name : {row['child_name']}  </br> User Name : {row['username']}</p>", unsafe_allow_html=True)
            
            # Add space between the child name and username
            st.write("    ")
            
            # Change the color of the username (right side)

    option = st.selectbox("Choose an activity:", ["Select", "Learn ABC", "Play Counting Game","Maths for kids","Animal Learning","Freedom Fighters","Progress Report"])
    if option == "Learn ABC":
        if st.session_state["dashboard_active"]:
            
            st.subheader("Dashboard")
            st.write("Welcome to the dashboard!")
            alpha_dashboard_page()
            if st.button("Back to Learn ABC"):
                st.session_state["dashboard_active"] = False
        else:
            st.subheader("Learn ABC")
            current_index = st.session_state["current_index"]

            # Display current word and image
            letter, word, image_url = letters[current_index]
            st.image(image_url, caption=f"{letter} for {word}", width=300)
            st.write(f"### **{word}**")

            # Text-to-speech button (Listen to the word)
            audio_file = f"{word.lower()}_audio.mp3"
            if not os.path.exists(audio_file):
                generate_audio(word, audio_file)
            if st.button("🔊 Listen to the word", key=f"listen_word_{current_index}"):
                st.audio(audio_file)

            # Speech recognition button to check if the user spoke the word correctly
            if st.button("🎤 Speak the word", key=f"speak_word_{current_index}"):
                check_spoken_word(word)

            # Next button to move to the next letter
            if st.button("Next", key="next"):
                st.session_state["current_index"] = (current_index + 1) % len(letters)

            # Button to navigate to the dashboard
            if st.button("Go to Dashboard"):
                st.session_state["dashboard_active"] = True


  


# "Play Counting Game" Section
    elif option == "Play Counting Game":
        

        # Path to images directory for vegetables
        vegetable_images_path = 'vegetable_images'  

        # List of vegetable image filenames (ensure these images exist in the folder)
        vegetable_images = [
            'brinjal.jpg', 'cabbage.jpg', 'potato.jpg', 'tomato.jpg',
            'capsicum.jpg', 'onion.jpg', 'carrot.jpg', 'radish.jpg'
        ]

        # Function to display images and ask user to count the vegetables
        def count_vegetables(difficulty='easy'):
            if 'selected_images' not in st.session_state or 'options' not in st.session_state or 'correct_count' not in st.session_state:
                
                if difficulty == 'easy':
                    num_images = random.randint(1, 8)  
                elif difficulty == 'medium':
                    num_images = random.randint(9, 14)  
                else:  # Hard difficulty
                    num_images = random.randint(15, 20)  

               
                selected_images = random.choices(vegetable_images, k=num_images)  # Allow repetition of images

                # Store the selected images and their count in session state
                st.session_state.selected_images = selected_images
                st.session_state.correct_count = len(selected_images)

                # Generate 4 unique options (including the correct one)
                options = {st.session_state.correct_count}
                while len(options) < 4:
                    random_option = st.session_state.correct_count + random.randint(-1, 2)
                    options.add(random_option)

                st.session_state.options = list(options)

            
            st.subheader("Guess how many vegetables you see:")
            cols = st.columns(len(st.session_state.selected_images))  
            image_paths = [os.path.join(vegetable_images_path, img) for img in st.session_state.selected_images]
            
            for i, image_path in enumerate(image_paths):
                with cols[i]:
                    st.image(image_path, width=150)  # Resize each image to fit the columns

            correct_count = st.session_state.correct_count

            # Generate a unique key for the radio button based on the difficulty, selected images, and session ID
            radio_key = f"radio_button_{difficulty}_{len(st.session_state.selected_images)}_{str(st.session_state.selected_images)}"

            # Display options as radio buttons for user to select
            selected_option = st.radio(
                "How many vegetables do you see in the above images?", 
                st.session_state.options, 
                key=radio_key  # Unique key for the radio button
            )

            # Handle the user's response when they click 'Submit'
            submit_key = f"submit_button_{str(st.session_state.selected_images)}_{st.session_state.correct_count}"  # Unique key for Submit button
            if st.button('Submit', key=submit_key):
                if selected_option == correct_count:
                    st.success(f"Correct! There are {correct_count} vegetables! 🎉")
                    st.balloons()  # Add confetti for celebration
                else:
                    st.error(f"Incorrect. There are {correct_count} vegetables. Try again! 😢")

            # Continue button to generate a new question
            next_key = f"next_button_{str(st.session_state.selected_images)}_{st.session_state.correct_count}"  # Unique key for Next Question button
            if st.button('Next Question', key=next_key):
                # Clear the session state for a new question
                st.session_state.pop('selected_images', None)
                st.session_state.pop('options', None)
                st.session_state.pop('correct_count', None)

                # Regenerate new question
                count_vegetables(difficulty=difficulty)

        # Function for the "Guess the Number" Game
        def guess_the_number(): 
            DATASET_FOLDER = "no_images"  # Folder containing images named 1.png, 2.png, ..., 20.png
            IMAGE_SIZE = (100, 100)  
            OPTION_COUNT = 4  # Number of options to display
            # Helper Functions
            def get_image_path(value):
                """Returns the file path of the image corresponding to the given value."""
                return os.path.join(DATASET_FOLDER, f"{value}.png")

            def display_number_images(number, image_size=(100, 100)):
                """Displays the images corresponding to the digits of the number."""
                digits = list(str(number))  # Split the number into its digits
                images = []
                
                for d in digits:
                    img_path = get_image_path(int(d))
                    img = Image.open(img_path)
                    img = img.resize(image_size)  # Resize the image
                    images.append(img)
                
                cols = st.columns(len(images))  # Create a column for each digit
                for col, img in zip(cols, images):
                    col.image(img, use_container_width=True)  # Use resized image

            def generate_options(correct_number):
                """Generates unique word options including the correct answer."""
                options = {num2words(correct_number)}  # Start with the correct answer
                while len(options) < OPTION_COUNT:
                    random_number = random.randint(1, 999)
                    options.add(num2words(random_number))
                options = list(options)
                random.shuffle(options)  # Shuffle the options
                return options

            # Initialize Session State
            if "target_number" not in st.session_state or "options" not in st.session_state:
                st.session_state.target_number = random.randint(1, 999)  # Random number to guess
                st.session_state.message = ""
                st.session_state.selected_option = None
                st.session_state.options = generate_options(st.session_state.target_number)  # Generate options once

            # UI
            st.title("🔢 Guess the Number Game!")
            st.markdown(
                """Welcome to the **Number Guessing Game**!
                
                - **Rules**: Look at the images of the digits and guess the number they form.
                - Choose the correct number from the options below.
                """
            )

            # Display the number as images
            st.header("🖼️ Number Images")
            display_number_images(st.session_state.target_number, IMAGE_SIZE)

            # Display options in a single list (radio buttons)
            selected_option = st.radio(
                "Select the correct number from the options below:",
                st.session_state.options  # This will display the list of options
            )

            # Store the selected option in session state
            st.session_state.selected_option = selected_option

            # Submit Button
            if st.button("Check Answer"):
                if st.session_state.selected_option == num2words(st.session_state.target_number):
                    st.success("🎉 Correct! You guessed the number!")
                    st.session_state.message = "Great job! Try the next one."
                else:
                    st.error(f"❌ Incorrect! The correct answer was {num2words(st.session_state.target_number)}.")
                    st.session_state.message = "Try again with a new number!"

            # Display the message for feedback
            if st.session_state.message:
                st.write(st.session_state.message)

            # Next Question Button
            next_button = st.button("Next Question")
            if next_button:
                # Reset session state for the next question
                st.session_state.target_number = random.randint(1, 999)  # Generate a new random number
                st.session_state.options = generate_options(st.session_state.target_number)  # Generate new options
                st.session_state.selected_option = None  # Reset selected option
                st.session_state.message = ""  # Reset message

                # Redraw the page to show the new question
                st.rerun()

            # Quit Button
            if st.button("🚪 Quit"):
                st.write("🚪 Game has been quit. Refresh the page to restart.")



        # Main function to select difficulty level and start the game
        def select_game_type():
            st.markdown("""  
                Welcome to the Fun Game! 🎮
                Choose the game you want to play: 
            """)

            # Game Type Selection
            game_type = st.radio("Select Game Mode", ["Count Vegetables", "Guess the Number"], key="game_type_radio")
            
            if game_type == "Count Vegetables":
                difficulty = st.radio("Select Difficulty Level", ["Easy", "Medium", "Hard"], key="difficulty_radio")
                count_vegetables(difficulty=difficulty.lower())
            elif game_type == "Guess the Number":
                guess_the_number()

        # Streamlit app execution starts here
        st.title("Fun Educational Game")
        st.markdown("### Choose your game mode and have fun!")

        # Run the selected game
        select_game_type()

        

# "Maths for kids" Section
    elif option == "Maths for kids":
    
        # Constants
        LO = 1  # Lower range (avoiding zero for division)
        HI = 12  # Upper range for numbers

        # Helper Functions
        def generate_question(operations):
            a = randint(LO, HI)
            b = randint(LO, HI)
            operation = random.choice(operations)  # Randomly pick an operation from the selected ones

            if operation == "Addition":
                question = f"{a} + {b} = ?"
                correct_answer = a + b
            elif operation == "Subtraction":
                question = f"{a + b} - {b} = ?"
                correct_answer = a
            elif operation == "Multiplication":
                question = f"{a} × {b} = ?"
                correct_answer = a * b
            elif operation == "Division":
                product = a * b
                question = f"{product} ÷ {b} = ?"
                correct_answer = a

            # Generate options including the correct answer
            options = [correct_answer]
            while len(options) < 4:
                wrong_answer = randint(LO - 5, HI + 5)
                if wrong_answer != correct_answer and wrong_answer > 0:
                    options.append(wrong_answer)

            shuffle(options)
            return question, options, correct_answer

        # Initialize Session State
        if "start_time" not in st.session_state:
            st.session_state.update({
                "start_time": None,
                "message": "",
                "current_question": None,
                "answered": False,
                "operation_selected": [],
                "option_selected1": None,
                "option_selected2": None,
                "option_selected3": None,
                "option_selected4": None,
                "question_start_time": [None] * 4,  # Start times for each question
                "response_times": [None] * 4,  # Response times for each question
            })

        # Header and Theme
        st.title("🎉 Choose Your Math Game! 🎈")
        st.markdown(
            """Welcome to the **Maths Game**! Choose the operations you want to practice and solve the questions. 
            
            🧮 Select from addition, subtraction, multiplication, or division. Have fun!
            """
        )

        # Allow users to select operations
        st.sidebar.header("Choose Operations")
        operations = ["Addition", "Subtraction", "Multiplication", "Division"]
        selected_operations = st.sidebar.multiselect("Select operations to practice:", operations, default=["Addition"])

        # Ensure at least one operation is selected
        if not selected_operations:
            st.error("Please select at least one operation to start the game.")
        else:
            # Start the Game
            if st.session_state.start_time is None:
                st.session_state.start_time = time()

            # Generate new questions if necessary
            if st.session_state.current_question is None and not st.session_state.answered:
                st.session_state.current_question = [generate_question(selected_operations) for _ in range(4)]

            # If the player has already answered and submitted answers
            if st.session_state.answered:
                questions_data = st.session_state.current_question

                # Display the questions and answers
                answers = [
                    (st.session_state.option_selected1, questions_data[0][2], "Question 1", st.session_state.response_times[0]),
                    (st.session_state.option_selected2, questions_data[1][2], "Question 2", st.session_state.response_times[1]),
                    (st.session_state.option_selected3, questions_data[2][2], "Question 3", st.session_state.response_times[2]),
                    (st.session_state.option_selected4, questions_data[3][2], "Question 4", st.session_state.response_times[3]),
                ]

                correct_count = 0
                answer_details = []
                for idx, (selected, correct, question, response_time) in enumerate(answers):
                    if selected == correct:
                        correct_count += 1
                        result = "Correct"
                    else:
                        result = "Incorrect"
                    answer_details.append(f"{question}: You chose {selected}. Correct answer is {correct} ({result}). Response time: {response_time:.2f} seconds.")

                # Show the answers and results in a list
                st.write("### Answers Summary:")
                for detail in answer_details:
                    st.write(f"- {detail}")

                if correct_count == 4:
                    st.success("🎉 Hooray! All answers are correct! You're amazing! 🐻")
                    st.balloons()
                else:
                    st.error(f"❌ Oh no! {4 - correct_count} answers were incorrect. Keep going!")

                next_button = st.button("🔄 Next Questions", key="next_questions")
                if next_button:
                    # Reset for the next round
                    st.session_state.answered = False
                    st.session_state.current_question = None
                    st.session_state.current_question = [generate_question(selected_operations) for _ in range(4)]
                    st.session_state.response_times = [None] * 4

            else:
                # Generate Four Questions if not already generated
                questions_data = st.session_state.current_question
                row1_col1, row1_col2 = st.columns(2)
                row2_col1, row2_col2 = st.columns(2)

                # First row of questions (Question 1 and Question 2)
                with row1_col1:
                    question, options, correct_answer = questions_data[0]
                    st.header(f"🦄 Question 1:")
                    st.subheader(question)
                    option_selected1 = st.radio("Choose your answer:", options, key="q1")
                    if st.session_state.question_start_time[0] is None:
                        st.session_state.question_start_time[0] = time()

                with row1_col2:
                    question, options, correct_answer = questions_data[1]
                    st.header(f"🦄 Question 2:")
                    st.subheader(question)
                    option_selected2 = st.radio("Choose your answer:", options, key="q2")
                    if st.session_state.question_start_time[1] is None:
                        st.session_state.question_start_time[1] = time()

                # Second row of questions (Question 3 and Question 4)
                with row2_col1:
                    question, options, correct_answer = questions_data[2]
                    st.header(f"🦄 Question 3:")
                    st.subheader(question)
                    option_selected3 = st.radio("Choose your answer:", options, key="q3")
                    if st.session_state.question_start_time[2] is None:
                        st.session_state.question_start_time[2] = time()

                with row2_col2:
                    question, options, correct_answer = questions_data[3]
                    st.header(f"🦄 Question 4:")
                    st.subheader(question)
                    option_selected4 = st.radio("Choose your answer:", options, key="q4")
                    if st.session_state.question_start_time[3] is None:
                        st.session_state.question_start_time[3] = time()

                # Submit answers button
                submit_button = st.button("🐾 Submit Answers", key="submit_answers")

                if submit_button and not st.session_state.answered:
                    st.session_state.option_selected1 = option_selected1
                    st.session_state.option_selected2 = option_selected2
                    st.session_state.option_selected3 = option_selected3
                    st.session_state.option_selected4 = option_selected4

                    # Calculate the response times for each question
                    st.session_state.response_times[0] = time() - st.session_state.question_start_time[0]
                    st.session_state.response_times[1] = time() - st.session_state.question_start_time[1]
                    st.session_state.response_times[2] = time() - st.session_state.question_start_time[2]
                    st.session_state.response_times[3] = time() - st.session_state.question_start_time[3]

                    st.session_state.answered = True

            # Quit Button
            if st.button("🚪 Quit"):
                st.session_state.start_time = None
                st.session_state.current_question = None
                st.write("🚪 Game has been quit. Refresh the page to restart.")


# "Animal Learning" Section
    elif option == "Animal Learning":

        # Constants and Paths
        DATASET_PATH = "animal_dataset.csv"
        DATA_FILE_PATH = "animal_data.csv"
        

        # Load dataset
        animal_data = pd.read_csv(DATASET_PATH)

        # Utility Functions
        def get_animal_details(category):
            """Fetch animals and details based on category."""
            return animal_data[animal_data["animal_category"].str.lower() == category.lower()]

        def fetch_characteristics(animal, number_char):
            """Fetch animal characteristics using Groq API."""
            client = Groq(api_key="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")
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": f"""You are an expert teacher for children below age 5, to teach them characteristics for animal 
                        Please describe {number_char} of {animal} in a numbered list. each characteristics in 5-6 words."""
                    }],
                    model="llama-3.3-70b-versatile",
                )
                return chat_completion.choices[0].message.content.split("\n")
            except Exception as e:
                st.error(f"Error fetching characteristics: {e}")
                return []

        def generate_audio(text):
            """Generate audio from text and return base64 string."""
            try:
                tts = gTTS(text, lang="en")
                audio_file_path = "temp_audio.mp3"
                tts.save(audio_file_path)

                # Read and encode the audio file to base64
                with open(audio_file_path, "rb") as f:
                    audio_bytes = f.read()
                    b64_audio = base64.b64encode(audio_bytes).decode()

                os.remove(audio_file_path)
                return b64_audio
            except Exception as e:
                st.error(f"Error generating audio: {e}")
                return None

        def update_mysql_table(animal_name, is_correct, category):
            """Insert new entry into MySQL table with animal performance data."""
            try:
                conn = mysql.connector.connect(**MYSQL_CONFIG)
                cursor = conn.cursor()

                # Create table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS animal_data (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        child_id INT,
                        animal_name VARCHAR(255),
                        category VARCHAR(255),
                        attempt INT DEFAULT 0,
                        correct INT DEFAULT 0,
                        incorrect INT DEFAULT 0,
                        timestamps TEXT,
                        dates TEXT
                    )
                """)

                current_timestamp = datetime.now().timestamp()
                current_date = datetime.now().date()

                # Always insert a new record
                cursor.execute("""
                    INSERT INTO animal_data (child_id,animal_name, category, attempt, correct, incorrect, timestamps, dates)
                    VALUES (%s,%s, %s, 1, %s, %s, %s, %s)
                """, (st.session_state.child_id,animal_name, category, 1 if is_correct else 0, 0 if is_correct else 1, current_timestamp, current_date))

                conn.commit()
            except mysql.connector.Error as e:
                raise e
                st.error(f"Error inserting data into MySQL table: {e}")
            finally:
                cursor.close()
                conn.close()

        def recognize_speech():
            """Recognize speech using microphone input."""
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening... Please say the animal's name.")
                audio_data = recognizer.listen(source)
                try:
                    return recognizer.recognize_google(audio_data).lower()
                except (sr.UnknownValueError, sr.RequestError) as e:
                    st.error("Could not understand or request failed. Please try again.")
                    return None

        # Pages
        def home_page():
            st.title("Animal Sounds Learning Application")
            st.subheader("Choose a Category:")
            categories = ["🐄 Farm Animal", "🐠 Sea Creature", "🐦 Bird", "🦁 Wild Animal", "🐒 Jungle Animal"]
            for i, category in enumerate(categories):
                if st.button(category):
                    st.session_state.selected_category = category.lower()
                    st.session_state.page_index = i + 1
                    break

        def animal_page(category):
            """Display animal page with selected category."""
            st.title(f"{category} ")
            animals = get_animal_details(category)
            if animals.empty:
                st.error(f"No {category.lower()} found in the dataset.")
                return

            animal_names = animals["animal_name"].tolist()
            selected_animal_name = st.selectbox("Select an Animal:", animal_names)
            selected_animal = animals[animals["animal_name"] == selected_animal_name].iloc[0]

            try:
                st.image(selected_animal["url"], caption=selected_animal["animal_name"])
            except Exception:
                st.error(f"Failed to load image for {selected_animal_name}.")

            if st.button("Play Sound"):
                b64_audio = generate_audio(selected_animal_name)
                if b64_audio:
                    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>', unsafe_allow_html=True)

            if st.button(f"🎤 Try Saying Here"):
                recognized_text = recognize_speech()
                if recognized_text:
                    is_correct = recognized_text == selected_animal_name.lower()
                    st.session_state.test_attempts.append({"animal": selected_animal_name, "recognized_text": recognized_text, "is_correct": is_correct})

                    if is_correct:
                        st.success(f"Correct! You said '{selected_animal_name}'.")
                    else:
                        st.error(f"Incorrect. You said '{recognized_text}'. Try again.")

                    update_mysql_table(selected_animal_name, is_correct, category)
                    
            num_characteristics = st.selectbox("Select number of characteristics to display:", list(range(2, 21)))
            st.session_state.num_characteristics = num_characteristics

            st.subheader(f"{selected_animal_name} Characteristics:")
            characteristics = fetch_characteristics(selected_animal_name, num_characteristics)
            if characteristics:
                for char in characteristics:
                    st.write(char)
            else:
                st.error("Failed to fetch characteristics. Please try again.")

        def load_data_from_mysql():
            try:
                # Establish the connection
                conn = mysql.connector.connect(
                    **MYSQL_CONFIG
                )
                query = "SELECT animal_name, category, attempt, correct, incorrect, timestamps, dates FROM animal_data where child_id={st.session_state.child_id}"
                df = pd.read_sql(query, conn)

                return df

            except mysql.connector.Error as e:
                st.error(f"Error fetching data from MySQL: {e}")
                return pd.DataFrame()  # Return an empty DataFrame on error

            finally:
                if conn:
                    conn.close()
        def dashboard_page():
            st.title("Learning Dashboard")

            # Load data from MySQL
            df = load_data_from_mysql()
            print(df)
            if df.empty:
                st.warning("No data available.")
                return

            # Clean and preprocess data
            try:
                df['dates'] = df['dates'].str.strip(",")  # Remove leading/trailing commas if present
                df['dates'] = pd.to_datetime(df['dates'], format="%Y-%m-%d", errors='coerce')
            except Exception as e:
                st.error(f"Error processing date column: {e}")
                return

            # Sidebar filters
            st.sidebar.header("Filters")
            time_filter = st.sidebar.radio("View Progress By", ["Daily", "Weekly", "Monthly"])

            categories = df['category'].unique()
            selected_category = st.sidebar.selectbox("Select Category", ["All"] + list(categories))

            if selected_category != "All":
                df = df[df['category'] == selected_category]

            animal_names = df['animal_name'].unique()
            selected_animal = st.sidebar.selectbox("Select Animal", ["All"] + list(animal_names))

            if selected_animal != "All":
                df = df[df['animal_name'] == selected_animal]

            # Process data for daily, weekly, or monthly trends
            if time_filter == "Daily":
                df['time_period'] = df['dates']
            elif time_filter == "Weekly":
                df['time_period'] = df['dates'].dt.to_period('W').apply(lambda r: r.start_time)
            else:  # Monthly
                df['time_period'] = df['dates'].dt.to_period('M').apply(lambda r: r.start_time)

            trend_data = df.groupby('time_period')[['attempt', 'correct', 'incorrect']].sum().reset_index()

            # Overall summary stats
            total_attempts = df['attempt'].sum()
            total_correct = df['correct'].sum()
            total_incorrect = df['incorrect'].sum()

            # Display overall statistics
            st.subheader("Overall Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Attempts", total_attempts)
            col2.metric("Total Correct", total_correct)
            col3.metric("Total Incorrect", total_incorrect)

            # Bar chart of attempts over animals
            st.subheader("Attempts Over Animal Name")
            bar_chart_data = df.groupby('animal_name')[['attempt', 'correct', 'incorrect']].sum().reset_index()
            fig = px.bar(bar_chart_data, x='animal_name', y=['correct', 'incorrect', 'attempt'], barmode='stack',
                        labels={'value': 'Count', 'animal_name': 'Animal Name'}, title="Attempts per Animal")
            st.plotly_chart(fig)

            # Correct vs Incorrect pie chart
            st.subheader("Correct Vs Incorrect")
            pie_data = pd.DataFrame({
                "Metric": ["Correct", "Incorrect"],
                "Count": [total_correct, total_incorrect]
            })
            fig = px.pie(pie_data, values="Count", names="Metric", title="Correct vs Incorrect Distribution")
            st.plotly_chart(fig)

            # Trends over selected time period
            st.subheader(f"Trends in Attempts Over {time_filter.lower()}s")
            fig = px.line(trend_data, x='time_period', y=['attempt', 'correct', 'incorrect'],
                        labels={'value': 'Count', 'time_period': f'{time_filter}'}, title=f"{time_filter}-Wise Trends")
            st.plotly_chart(fig)

            # Animal distribution pie chart
            st.subheader("Animal Category Distribution")
            category_counts = df['category'].value_counts()
            fig = px.pie(names=category_counts.index, values=category_counts.values, title="Animal Categories")
            st.plotly_chart(fig)

            # Category-specific report
            st.subheader("Category Report")
            filtered_df = df[df['category'] == selected_category] if selected_category != "All" else df
            attempts = filtered_df['attempt'].sum()
            correct = filtered_df['correct'].sum()
            incorrect = filtered_df['incorrect'].sum()

            st.write(f"Category: {selected_category if selected_category != 'All' else 'All Categories'}")
            st.write(f"Total Attempts: {attempts}")
            st.write(f"Correct: {correct}")
            st.write(f"Incorrect: {incorrect}")

            # Bar chart for category-specific statistics
            report_data = {'Attempts': attempts, 'Correct': correct, 'Incorrect': incorrect}
            report_df = pd.DataFrame(list(report_data.items()), columns=["Metric", "Value"])
            st.bar_chart(report_df.set_index('Metric'))

        def load_data_from_mysql():
        # Connect to MySQL database
            connection = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='9545883002@Sj',
                database='child_learning'
            )

            query = f"SELECT animal_name, category, attempt, correct, incorrect, timestamps, dates FROM animal_data where child_id={st.session_state.child_id}"

            df = pd.read_sql(query, con=connection)
            connection.close()
            return df
        # Session State Initialization
        if "page_index" not in st.session_state:
            st.session_state.page_index = 0  # Home page
        if "test_attempts" not in st.session_state:
            st.session_state.test_attempts = []

        # Pages List
        pages = [
            home_page,  # Home Page
            lambda: animal_page("Farm Animals"),
            lambda: animal_page("Sea Creatures"),
            lambda: animal_page("Bird"),
            lambda: animal_page("Wild Animal"),
            lambda: animal_page("Jungle Animal"),
            dashboard_page
        ]

        # Display Page
        pages[st.session_state.page_index]()

        
        if st.session_state.page_index == 0 and st.button("Go to Dashboard"):
            st.session_state.page_index = 6
        elif st.session_state.page_index > 0 and st.button("Back to Home"):
            st.session_state.page_index = 0

                
   
    #freedom fighters
    elif option=="Freedom Fighters":

        ffighters = r"ff_images"
        question_json =r"questions.json"



        def load_quiz_questions(file_path):
            """Load quiz questions from a JSON file."""
            with open(file_path, 'r') as file:
                return json.load(file)

        def capture_speech():
            """Capture and process speech input."""
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening... Please speak your answer.")
                try:
                    audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
                    spoken_text = recognizer.recognize_google(audio)
                    return spoken_text
                except sr.UnknownValueError:
                    st.error("Sorry, I could not understand your speech. Please try again.")
                    return None
                except sr.RequestError as e:
                    st.error(f"Speech Recognition service is unavailable: {e}")
                    return None

        # List of Freedom Fighters
        freedom_fighters = [
            {"name": "Mahatma Gandhi", "image": "Mahatma Gandhi.jpg", "info": [
                "Born: 2 October 1869, Porbandar, India.",
                "Played a key role in the Indian independence movement through non-violent civil disobedience.",
                "Led several important movements like the Salt March and Quit India Movement.",
                "Known as the 'Father of the Nation'.",
                "Famous for his philosophy of 'Ahimsa' (non-violence).",
                "Assassinated on 30 January 1948."
            ]},
            {"name": "Jawaharlal Nehru", "image": "Jawaharlal Nehru.jpg", "info": [
                "Born: 14 November 1889, Allahabad, India.",
                "The first Prime Minister of India, serving from 1947 to 1964.",
                "A central figure in the Indian independence movement, closely working with Mahatma Gandhi.",
                "Known for his vision of a secular, socialist India, and played a key role in shaping India's policies post-independence.",
                "Author of several works, including his autobiography and 'Discovery of India'.",
                "Died on 27 May 1964."
            ]},
            {"name": "Bhagat Singh", "image": "Bhagat Singh.jpg", "info": [
                "Born: 28 September 1907, Banga, Punjab (now in Pakistan).",
                "One of the most influential revolutionaries in the Indian independence movement.",
                "Known for his acts of rebellion, including the assassination of John Saunders to avenge Lala Lajpat Rai’s death.",
                "Hanged at the age of 23 on 23 March 1931, along with Rajguru and Sukhdev.",
                "Famous for his courage and his slogan 'Inquilab Zindabad'."
            ]},
            {"name": "Sardar Vallabhbhai Patel", "image": "Sardar Vallabhbhai Patel.jpg", "info": [
                "Born: 31 October 1875, Nadiad, Gujarat, India.",
                "Known as the 'Iron Man of India' for his role in uniting the country post-independence.",
                "Served as the first Deputy Prime Minister and the first Minister of Home Affairs.",
                "Played a key role in integrating over 500 princely states into the Indian Union.",
                "Was a key figure in the freedom struggle and the success of the Salt Satyagraha.",
                "Died on 15 December 1950."
            ]},
            {"name": "Lal Bahadur Shastri", "image": "Lal Bahadur Shastri.jpg", "info": [
                "Born: 2 October 1904, Mughalsarai, India.",
                "Second Prime Minister of India, serving from 1964 to 1966.",
                "Known for promoting the White Revolution and the Green Revolution.",
                "Led India to victory in the 1965 war with Pakistan and advocated for peace with neighbors.",
                "Famous for the slogan 'Jai Jawan Jai Kisan'.",
                "Died suddenly in Tashkent, Uzbekistan, in January 1966, under mysterious circumstances."
            ]},
            {"name": "Rani Lakshmibai", "image": "Rani Lakshmibai.jpg", "info": [
                "Born: 19 November 1828, Varanasi, India.",
                "Queen of the princely state of Jhansi, known for her leadership during the 1857 Indian Rebellion.",
                "Led her army in battles against the British East India Company.",
                "Famous for her bravery and determination, she became a symbol of resistance.",
                "Died on 18 June 1858, in battle, while defending Jhansi."
            ]},
            {"name": "Chandra Sekhar Azad", "image": "Chandra Sekhar Azad.jpg", "info": [
                "Born: 23 July 1906, Bhavra, Madhya Pradesh, India.",
                "One of the most prominent revolutionaries in the Indian independence movement.",
                "Played a significant role in the Hindustan Socialist Republican Association (HSRA).",
                "Famous for his slogan 'Dilsay ki Azadi.'",
                "Committed suicide on 27 February 1931, after being surrounded by the police, maintaining his vow to never be captured alive."
            ]},
            {"name": "Dr. B.R. Ambedkar", "image": "Dr. B.R. Ambedkar.jpg", "info": [
                "Born: 14 April 1891, Mhow, Madhya Pradesh, India.",
                "Principal architect of the Constitution of India, advocating for social justice and equality.",
                "A leading figure in the fight against untouchability and caste-based discrimination.",
                "He converted to Buddhism in 1956 and inspired millions of Dalits to follow the path of Buddhism.",
                "First Law Minister of India, and a member of the first Cabinet of Independent India.",
                "Died on 6 December 1956."
            ]},
            {"name": "Mangal Pandey", "image": "Mangal Pandey.jpg", "info": [
                "Born: 19 July 1827, Nagwa, Ballia, India.",
                "Known for his role in the 1857 Indian Rebellion, also called the First War of Indian Independence.",
                "A sepoy in the British East India Company’s army, he sparked the rebellion by attacking his officers.",
                "Famous for his courage and is regarded as one of the first freedom fighters of India.",
                "Hanged on 21 April 1857, for his role in the rebellion."
            ]},
        

            
        ]

        folder_path = ffighters


        # Streamlit App
        st.title('Freedom Fighters of India')
        st.write('Click on any freedom fighter name to see their image and more information.')

        if os.path.isdir(folder_path):
            st.write(f"Folder found: {folder_path}")
            quiz_file_path = question_json  
            quiz_questions = load_quiz_questions(quiz_file_path)

            if 'current_fighter' not in st.session_state:
                st.session_state.current_fighter = None

            for fighter in freedom_fighters:
                image_path = os.path.join(folder_path, fighter['image'])

                if st.button(fighter['name']):
                    st.session_state.current_fighter = fighter['name']

                if st.session_state.current_fighter == fighter['name']:
                    if os.path.exists(image_path):
                        st.image(image_path, caption=fighter['name'], width=300)

                        if st.button(f"Show Info about {fighter['name']}"):
                            st.write(f"**Details about {fighter['name']}:**")
                            for point in fighter['info']:
                                st.markdown(f"- {point}")
                    else:
                        st.write("Image not available in the folder.")

                    st.write('---')

            # Quiz Section
            with st.expander("Start Quiz"):
                st.subheader("Freedom Fighters Quiz")

                if 'question_index' not in st.session_state:
                    st.session_state.question_index = 0

                current_question = quiz_questions[st.session_state.question_index]
                st.subheader(f"{st.session_state.question_index + 1}. {current_question['question']}")

                # Display options
                answer = st.radio(f"Choose your answer for Q{st.session_state.question_index + 1}", options=current_question["options"], key=f"q{st.session_state.question_index}")

                if 'answered' not in st.session_state:
                    st.session_state.answered = False
                
                if st.button(f"Submit Answer for Q{st.session_state.question_index + 1}", key=f"submit{st.session_state.question_index}"):
                    if answer == current_question["answer"]:
                        st.success("Correct!")
                    else:
                        st.error(f"Wrong! The correct answer is: {current_question['answer']}")
                    
                
                    st.session_state.answered = True
                
                if st.button(f"Speak Answer for Q{st.session_state.question_index + 1}", key=f"speak{st.session_state.question_index}"):
                    spoken_answer = capture_speech()
                    if spoken_answer:
                        st.write(f"You said: {spoken_answer}")
                        if spoken_answer.lower() == current_question["answer"].lower():
                            st.success("Correct!")
                        else:
                            st.error(f"Wrong! The correct answer is: {current_question['answer']}")
                        
                        st.session_state.answered = True
                
                if st.session_state.answered:
                    if st.session_state.question_index + 1 < len(quiz_questions):
                        next_question_button = st.button("Next Question")
                        if next_question_button:
                            st.session_state.question_index += 1  
                            st.session_state.answered = False  
                            st.rerun()  # Trigger a rerun to refresh the state
                    else:
                        st.success("Congratulations! You've completed the quiz.")



        
    else:
        st.write("Choose an activity from the dropdown above.")
elif st.session_state.log == 1:
    login_page()
elif st.session_state.log == 3:
    signup_page()



# Function to check the spelling of the word
#def check_spelling_word(correct_word):
#    st.write(f"Please spell the word '{correct_word}' by speaking each letter.")
#   spoken_text = recognize_live_speech()
#    st.write(f"**You said:** {spoken_text}")
#    if spoken_text.strip().lower() == correct_word.lower():
#        st.success(f"Correct spelling! 🎉 You spelled the word '{correct_word}' correctly.")
#    else:
#        st.error(f"Incorrect spelling. ❌ The correct spelling is '{correct_word}'.")

