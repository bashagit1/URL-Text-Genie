import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Initialize OpenAI client

# Function to extract text from YouTube video
def extract_youtube_transcript(video_url, language_code):
    video_id = video_url.split("v=")[-1]
    available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    
    try:
        transcript = available_transcripts.find_transcript([language_code])
        return ' '.join([entry['text'] for entry in transcript.fetch()])
    except NoTranscriptFound:
        return f"No transcripts found for the selected language '{language_code}'."
    except Exception as e:
        return str(e)

# Function to extract text from blog post URL
def extract_blog_text(blog_url):
    response = requests.get(blog_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    return ' '.join([para.get_text() for para in paragraphs])

# Function to query the AI agent
def query_ai_agent(prompt):
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo"  # Specify the model to use
    )
    
    # Correctly access the response content
    response_content = chat_completion.choices[0].message.content  # Access the response message
    return response_content

# Streamlit app interface
st.set_page_config(page_title="Text Extractor with AI Agent", layout="wide")

# Add title and description
st.title("🎤 Text Extractor with AI Agent 🌐")
st.write("Select an option below to extract text from a YouTube video or a blog post.")

# Sidebar for input and options
with st.sidebar:
    st.header("🤖 AI Agent")
    ai_query = st.text_input("Ask me about the extracted text:")
    if st.button("Ask Me"):
        if 'transcript_text' in st.session_state:
            ai_prompt = f"{ai_query}\n\nExtracted Text:\n{st.session_state.transcript_text}"
            ai_response = query_ai_agent(ai_prompt)
            st.subheader("AI Response:")
            st.write(ai_response)
        else:
            st.warning("Please extract text from a YouTube video or blog post first.")

# Main content area
source_type = st.selectbox("Select Source Type:", ["YouTube Video", "Blog Post"])
url = st.text_input("Enter URL:")
language_options = ["en", "hi", "ur", "fr", "es", "de"]
language = st.selectbox("Select Language:", language_options)

# Button to extract text
if st.button("Extract Text"):
    if url:
        try:
            if source_type == "YouTube Video":
                transcript_text = extract_youtube_transcript(url, language)
                st.subheader("Transcript:")
                st.write(transcript_text)

                # Store transcript text in session state for use in AI agent
                st.session_state.transcript_text = transcript_text

            else:
                blog_text = extract_blog_text(url)
                st.subheader("Blog Text:")
                st.write(blog_text)

                # Store blog text in session state for use in AI agent
                st.session_state.transcript_text = blog_text

        except Exception as e:
            st.error(f"Error extracting text: {e}")
    else:
        st.warning("Please enter a valid URL.")

# Add custom CSS for styling
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f0f8ff;
            color: #333;
            padding: 20px;  /* Add padding for aesthetics */
        }
        .stButton > button {
            background-color: #1e90ff;
            color: white;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            text-align: center;
        }
        h2 {
            color: #4682b4;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;  /* White background for sidebar */
            border-radius: 10px;  /* Rounded corners */
            padding: 15px;  /* Padding for the sidebar */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Add animations
st.balloons()
