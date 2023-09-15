# from config import OPENAI_API_KEY, ASSEMBLYAI_API_KEY
import streamlit as st
import openai
import assemblyai as aai
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import plotly.express as px
import plotly.graph_objects as go
import hashlib
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
from wordcloud import STOPWORDS, ImageColorGenerator
import numpy as np
from PIL import Image
import seaborn as sns
import io
import os
import random
import PyPDF2
from io import BytesIO


st.set_page_config(page_title='TalkToMe', page_icon='🌍')


# Set the API keys 
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['ASSEMBLYAI_API_KEY'] = st.secrets['ASSEMBLYAI_API_KEY']

# Now, initialize the APIs
openai.api_key = os.environ['OPENAI_API_KEY']
aai.settings.api_key = os.environ['ASSEMBLYAI_API_KEY']

# # Initialize OpenAI and AssemblyAI APIs
# openai.api_key = OPENAI_API_KEY
# aai.settings.api_key = ASSEMBLYAI_API_KEY

languages_map = {
    "German": "de",
    "French": "fr",
    "Italian": "it",
    "Spanish": "es",
    "English": "en"
}
if 'word_counts' not in st.session_state:
    st.session_state['word_counts'] = []


def voice_to_text(audio_bytes, language_code):
    config = aai.TranscriptionConfig(language_code=language_code)
    transcriber = aai.Transcriber(config=config)
    file_name = 'temp_audio_file.wav'
    with open(file_name, 'wb') as f:
        f.write(audio_bytes)
    transcript = transcriber.transcribe(file_name)
    return transcript.text



# Integrate into the chat function
def chat_with_openai(prompt, language, register, content=None, vocab_list=None):
    messages = [{"role": "system", "content": f"Language: {language}, Register: {register}"}]
    
    if content:
        messages.append({"role": "user", "content": content})
    if vocab_list:
        vocab_str = ", ".join(vocab_list)
        messages.append({"role": "user", "content": f"I want to practice the following vocabulary: {vocab_str}"})
        
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content.strip()


def text_to_voice(text, lang):
    tts = gTTS(text=text, lang=lang)
    audio_path = "bot_response.mp3"
    tts.save(audio_path)
    return audio_path

st.title("TalkToMe Language Learning")

def tokenize(text):
    # Tokenize the text and return a list of words
    words = re.findall(r'\w+', text.lower())  # Convert to lowercase and tokenize
    return words


def display_wordcloud(word_counts, header="Word Cloud"):
    wordcloud = WordCloud(
        background_color='white',
        colormap='viridis',
        color_func=color_func, 
        mask=mask,
        random_state=42
    ).generate_from_frequencies(word_counts)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(header, fontsize=20)
    st.pyplot(plt)

def get_feedback(text, language, register, check_register, check_proficiency):
    prompt = f"Please correct the following {language} text for grammar: \"{text}\"."
    
    if check_register:
        prompt += f" Also, evaluate if the text is written in a {register} register. The response should be Yes or No"
    
    if check_proficiency:
        prompt += f" Lastly, assess the language proficiency level of the text using categories A1, A2, B1, B2, C1, C2 according to CEFR levels."
    
    response = chat_with_openai(prompt, language, register)
    return response

def extract_text_from_pdf(uploaded_pdf):
    pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
    text = ""
    for page in pdf_reader.pages:  # Iterating directly over pages
        text += page.extract_text()
    return text
    
# Welcome Message
st.write("""
### Welcome to TalkToMe! 🌍✨
This is your personal language learning assistant. Here, you can practice speaking, discussing articles, and get instant feedback in your chosen language! Currently, you can practice German, French, Italian, Spanish and English in real-time, without a partner.
""")
st.markdown("---") 

# Sidebar content
st.sidebar.title("Instructions & Tips")
st.sidebar.write("""
#### How to use:
1. **Select** your target language, proficiency level, and the kind of conversation you want (informal, formal, etc.).
2. If you have an **article or text** you want to discuss, simply paste it in the provided text box.
3. If you have **specific vocabulary** that you want to practice, add the words to the list of vocabulary. The tracker will keep count of how often you used the words in the conversation.
4. **Record** your voice by pressing the microphone button. You can ask questions about the text, practice sentences, or have a casual conversation.
5. Wait a moment for the transcription and get an **instant response** from your virtual language assistant. You can choose to have the feedback in text, voice, or both!
""")

# Tips & Tricks in the sidebar
st.sidebar.write("#### Tips for the best experience:")
tips = """
- Ensure you're in a **quiet environment**.
- Speak **clearly and at a moderate pace**.
- Paste **news articles, stories, or study materials** for context.
- **Experiment and practice** regularly!
"""
st.sidebar.markdown(tips)

def load_tips():
    with open('tipstalk.txt', 'r') as f:
        tipstalk = f.readlines()
    return [tip.strip() for tip in tipstalk]

tipstalk = load_tips()

st.subheader("Language Learning Tips for Speaking")
st.write("Learning a language is hard. Need some tips or motivation? Here are some tips for you that you can incorporate into your learning journey")

# Display tip in a pretty box
tip_to_display = st.session_state.get("current_tip", random.choice(tipstalk))
st.markdown(f"""
<div style="border:2px solid #F0F2F6; padding:20px; border-radius:5px; box-shadow: 2px 2px 12px #aaa;">
    {tip_to_display}
</div>
""", unsafe_allow_html=True)

st.write("###")
# Button to generate a new tip
if st.button("Get Another Tip"):
    new_tip = random.choice(tipstalk)
    while new_tip == tip_to_display:  # Ensure different tip is chosen
        new_tip = random.choice(tipstalk)
    st.session_state["current_tip"] = new_tip

st.write("##")
st.write("---")
st.write("##")

st.subheader("Choose your preferences for your practice today!")
# Select language, proficiency, and register
language = st.selectbox("Choose a language", ["German", "French", "Italian", "Spanish", "English"])
proficiency = st.selectbox("Select your proficiency level", ["A1", "A2", "B1", "B2", "C1", "C2"])
register = st.selectbox("Choose a register", ["Informal", "Formal", "Business", "Academic"])
output_preference = st.radio("Select output preference", ["Audio", "Transcript", "Both"])
# Add checkboxes
st.write("If you want some feedback on your language use, you can select any or all of these options. Please note that this is currently an experimental feature and might not provide accurate information")
correct_grammar_option = st.checkbox('Correct grammar (only works with option that includes a transcript)')
check_register_option = st.checkbox('Check register')
check_proficiency_option = st.checkbox('Check proficiency')

# Text area for pasting content
st.subheader("OPTIONAL: Text to talk about")

 # File uploader for PDF
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

content_text = ""

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        content_text = extract_text_from_pdf(uploaded_file)
    st.success("Text extracted!")
if not content_text:
    # Allow user to type in text, adding a unique key
    content_text = st.text_area("Paste the text you want to talk about:", key="unique_text_area")

if content_text:
    # Do whatever you need with content_text
    st.write("You provided a text to talk about")
   

# Vocabulary Input
st.subheader("OPTIONAL: Vocabulary Practice")
vocab_input = st.text_area("Enter vocabulary words you want to practice (separate by commas or line breaks):")
st.write("---")
st.write("#")

# Parse and listify the vocabulary
vocab_list = [word.strip() for word in vocab_input.split(",") if word] if "," in vocab_input else vocab_input.split("\n")

# Initialize counter
vocab_counter = {word: 0 for word in vocab_list}

# Check if 'vocab_counter' exists in the session state, and if not, initialize it
if 'vocab_counter' not in st.session_state:
    st.session_state['vocab_counter'] = {word: 0 for word in vocab_list}
else:
    # Update vocab_counter to match vocab_list, setting counts to 0 for new words
    st.session_state['vocab_counter'] = {word: st.session_state.vocab_counter.get(word, 0) for word in vocab_list}

## Update the counter with the student's input:
def update_vocab_counter(text):
    for word in vocab_list:  # Loop through the vocab words
        if word in st.session_state.vocab_counter:
            st.session_state.vocab_counter[word] += text.lower().count(word.lower())

# Define a function to get a hash of the audio bytes:
def get_audio_hash(audio_bytes):
    return hashlib.md5(audio_bytes).hexdigest()

# Initialize the last processed audio hash in session state:
if 'audio_processed' not in st.session_state:
    st.session_state.audio_processed = None

st.subheader("Let's start practising")
# Record audio directly in the app
st.write("Click the microphone to start recording. The recording will automatically stop after no sound has been detected for two seconds.")
audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=41_000)
st.write("---")
st.write("#")

# def generate_word_cloud(student_text):
#     tokens = tokenize(student_text)
#     word_counts = Counter(tokens)
    
#     # Generate the word cloud
#     wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)

#     # Use matplotlib to create the figure
#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis('off')
    
#     return fig

def generate_cumulative_word_cloud():
    # Generate the word cloud based on accumulated vocabulary
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)

    # Use matplotlib to create the figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')

    # Convert the Matplotlib figure to an image buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)
    
    return buffer


if audio_bytes:
    current_audio_hash = get_audio_hash(audio_bytes)

    # Only process if the audio hasn't been processed before
    if st.session_state.audio_processed != current_audio_hash:
        st.write("Recording detected!")
        st.write("Transcribing your audio...")
        
        st.session_state.student_text = voice_to_text(audio_bytes, languages_map[language])
        feedback = ""  # Initialize feedback
    
        if correct_grammar_option or check_register_option or check_proficiency_option: 
            feedback = get_feedback(st.session_state.student_text, language, register, check_register_option, check_proficiency_option)

        # Split the feedback by newline or full stop to handle different pieces of information
        if feedback:
            feedback_parts = [part.strip() for part in feedback.split("\n") if part]

            # Display corrected text
            st.write(f"**Original**: {st.session_state.student_text}")
            st.write(f"**Suggested improvements (experimental)**: {feedback_parts[0]}")

            # check if any corrections occurred 
            if st.session_state.student_text.strip() == feedback_parts[0].strip():
                st.write("😊 Great job! No corrections or improvements needed.")
            
            # Check if the register matches
            if check_register_option:
                register_feedback = feedback_parts[1]
                if "Yes" in register_feedback:
                    st.write("👍 Register matches")
                else:
                    st.write("👎 Register doesn't match")
            
            # Check for language proficiency
            if check_proficiency_option:
                proficiency_feedback = feedback_parts[2]
                if "A1" in proficiency_feedback:
                    st.write("Proficiency Level: A1 - Beginner")
                elif "A2" in proficiency_feedback:
                    st.write("Proficiency Level: A2 - Elementary")
                
                elif "B1" in proficiency_feedback:
                    st.write("Proficiency Level: B1 - Intermediate")
                elif "B2" in proficiency_feedback:
                    st.write("Proficiency Level: B2 - Upper Intermediate")
                elif "C1" in proficiency_feedback:
                    st.write("Proficiency Level: C1 - Advanced")
                elif "C2" in proficiency_feedback:
                    st.write("Proficiency Level: C2 - Proficient")
                else:
                    st.write("Proficiency Level: Not Detected")


        update_vocab_counter(st.session_state.student_text)
        bot_response = chat_with_openai(st.session_state.student_text, language, proficiency, register, content_text)
        update_vocab_counter(st.session_state.student_text)
        tokens = tokenize(st.session_state.student_text)
        word_counts = Counter(tokens)
        # generate_word_cloud(st.session_state.student_text)


        # Check if 'messages' exists in the session state, and if not, initialize it
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if output_preference in ["Transcript", "Both"]:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": f" {st.session_state.student_text}"})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(f" {st.session_state.student_text}")

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": f" {bot_response}"})
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(f" {bot_response}")

        if output_preference in ["Audio", "Both"]:
            audio_path = text_to_voice(bot_response, languages_map[language])
            audio_file = open(audio_path, 'rb')
            audio_bytes_response = audio_file.read()
            st.audio(audio_bytes_response, format='audio/mp3')

        word_count_current_input = len(st.session_state.student_text.split())
        st.write(f"Word count for this input: {word_count_current_input}")

        # Add the current word count to the list
        st.session_state.word_counts.append(word_count_current_input)

        # Update the session state to mark this audio as processed
        st.session_state.audio_processed = current_audio_hash
    else:
        st.write("This recording has already been processed.")


# Compute the total word count of the text
total_word_count = sum(st.session_state.vocab_counter.values())


st.write("#")
# Display total word count
total_count = sum(st.session_state.word_counts)
# Use custom CSS to make this text stand out
st.markdown(f"<div style='border:2px solid #F0F0F0; padding:20px; border-radius:5px;'>"
            f"<h3 style='text-align:center;'>Total Word Count: {total_count}</h3>"
            "</div>", unsafe_allow_html=True)

st.write("#")
st.write("#")


st.subheader("Feedback Visualizations")
tab1,tab2,tab3, tab4 = st.tabs(["Bar Chart", "Donut Chart", "Graph", "Word Cloud"])


# For the Bar Chart
tab1.subheader("Vocabulary Usage")
if total_word_count > 0:
    vocab_data = {
        "Words": list(st.session_state.vocab_counter.keys()),
        "Counts": list(st.session_state.vocab_counter.values())
    }
    fig = px.bar(vocab_data, x="Words", y="Counts", title="Vocabulary Usage", labels={"Counts": "Number of Times Used", "Words": "Vocabulary Words"})
    tab1.plotly_chart(fig)
else:
    tab1.write("No vocabulary words used yet.")

# For the Donut Chart
tab2.subheader("Vocabulary Usage %")
if total_word_count > 0:
    labels = list(st.session_state.vocab_counter.keys())
    values = [count / total_word_count for count in st.session_state.vocab_counter.values()]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
    fig.update_layout(title_text="Proportion of Vocabulary Usage in Text")
    tab2.plotly_chart(fig)
else:
    tab2.write("No vocabulary words used yet.")

# For the Graph
tab3.subheader("Words Used")
if total_word_count > 0:
    fig = go.Figure(data=go.Scatter(y=st.session_state.word_counts, mode='lines+markers'))
    fig.update_layout(title="Word Count Over Time", xaxis_title="Recording Number", yaxis_title="Word Count")
    tab3.plotly_chart(fig)
else:
    tab3.write("No vocabulary words used yet.")
# For the Word Cloud
tab4.subheader("Word Cloud Visualisation")
if "student_text" in st.session_state:
    image_buffer = generate_cumulative_word_cloud()
    tab4.image(image_buffer, caption="Word Cloud Visualization")

else:
    tab4.write("No text available to generate a word cloud.")
