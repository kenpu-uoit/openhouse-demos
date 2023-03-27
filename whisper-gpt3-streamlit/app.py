import os
import whisper
import streamlit as st
from pydub import AudioSegment
import openai
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Whisper & GPT-3",
    page_icon="musical_note",
    layout="wide",
    initial_sidebar_state="auto",
)

upload_path = "uploads/"
download_path = "downloads/"
transcript_path = "transcripts/"

@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def to_mp3(audio_file, output_audio_file, upload_path, download_path):
    ## Converting Different Audio Formats To MP3 ##
    if audio_file.name.split('.')[-1].lower()=="wav":
        audio_data = AudioSegment.from_wav(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="mp3":
        audio_data = AudioSegment.from_mp3(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="ogg":
        audio_data = AudioSegment.from_ogg(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="wma":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"wma")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="aac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"aac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="flac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"flac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="flv":
        audio_data = AudioSegment.from_flv(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")

    elif audio_file.name.split('.')[-1].lower()=="mp4":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"mp4")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3")
    return output_audio_file

@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def process_audio(filename, model_type):
    model = whisper.load_model(model_type)
    result = model.transcribe(filename)
    return result["text"]

@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def save_transcript(transcript_data, txt_file):
    with open(os.path.join(transcript_path, txt_file),"w") as f:
        f.write(transcript_data)

st.title("Audio and Text Understanding with Whisper and GPT-3")
uploaded_file = st.file_uploader("Audio", type=["wav","mp3","ogg","wma","aac","flac","mp4","flv"])

audio_file = None

if uploaded_file is not None:
    audio_bytes = uploaded_file.read()
    with open(os.path.join(upload_path,uploaded_file.name),"wb") as f:
        f.write((uploaded_file).getbuffer())
    with st.spinner(f"Processing Audio ... 💫"):
        output_audio_file = uploaded_file.name.split('.')[0] + '.mp3'
        output_audio_file = to_mp3(uploaded_file, output_audio_file, upload_path, download_path)
        audio_file = open(os.path.join(download_path,output_audio_file), 'rb')
        audio_bytes = audio_file.read()
    print("Opening ",audio_file)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Feel free to play your uploaded audio file 🎼")
        st.audio(audio_bytes)
    with col2:
        whisper_model_type = st.radio("Please choose your model type", ('Tiny', 'Base', 'Small', 'Medium', 'Large'))

    if st.button("Generate Transcript and Classfification"):
        with st.spinner(f"Generating Transcript... 💫"):
            transcript = process_audio(str(os.path.abspath(os.path.join(download_path,output_audio_file))), whisper_model_type.lower())
            print(transcript)
            if transcript is not None:
                st.header("Transcript:")
                st.markdown("""
                </style>
                <div style='
                font-family: monospace;
                font-size: 14pt;
                background-color: #f5f5f5;
                max-width: 800px;
                padding: 30px;
                margin-left: auto;
                margin-right: auto;
                '>
                %s
                </div>
                """ % (transcript), unsafe_allow_html=True)

                openai.api_key = os.getenv("OPENAI_API_KEY")

                
                template1="""
                Where are you now? I'm sitting in my office. I doubt that. And why would you doubt that? If you were in your office right now, we'd be having this conversation face-to-face.

                sentiment analysis (very negativ, negativ, neutral, positive, very positive): negative
                
                {}
                
                sentiment analysis (very negativ, negativ, neutral, positive, very positive): """

                template2="""
                Summarize the following text in plain text in five senteneces or less. Remove all HTML tags.

                {}
                """

                response1 = openai.Completion.create(
                    model="text-davinci-002",
                    prompt=template1.format(transcript),
                    temperature=0.7,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )

                sentiment = response1.choices[0].text

                response2 = openai.Completion.create(
                    model="text-davinci-002",
                    prompt=template2.format(transcript),
                    temperature=0.7,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )

                summary = response2.choices[0].text

                st.header("Sentiment analysis:")
                st.caption("very negativ, negativ, neutral, positive, very positive")
                st.markdown("""
                <style>
                #x, #x p {
                    font-size: 16pt;
                }
                </style>
                <div id="x" style='
                font-family: monospace;
                text-align: left;
                background-color: #f5f5f5;
                padding: 30px;
                '>
                <p>%s</p>
                </div>
                <h1>%s</h1>
                """ % (summary, sentiment), unsafe_allow_html=True)

            st.balloons()
            st.success('✅ Successful !!')

else:
    st.warning('⚠ Please upload your audio file 😯')
