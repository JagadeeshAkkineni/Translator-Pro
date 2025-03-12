import streamlit as st
import pdfplumber
import docx
from deep_translator import GoogleTranslator
from fpdf import FPDF
from io import BytesIO
import zipfile
import base64
from gtts import gTTS
import time

# Set page config for a wider layout and customize theme
st.set_page_config(
    page_title="Document Translator Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📄"
)

# Custom CSS for better styling with dark theme
st.markdown("""
<style>
    /* Base dark theme */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Text styles */
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        color: #4F8BF9 !important;
    }
    .sub-header {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        margin-bottom: 1.5rem !important;
        color: #8F9BAF !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #4F8BF9;
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        min-width: 150px;
    }
    .stButton button:hover {
        background-color: #3a7bd5;
    }
    .download-all-btn {
        background-color: #28a745 !important;
    }
    .download-all-btn:hover {
        background-color: #218838 !important;
    }
    .translate-all-btn {
        background-color: #6c5ce7 !important;
        color: white !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    .translate-all-btn:hover {
        background-color: #5741d9 !important;
    }
    .tts-btn {
        background-color: #f39c12 !important;
        color: white !important;
    }
    .tts-btn:hover {
        background-color: #e67e22 !important;
    }
    
    /* File uploader */
    .file-uploader {
        border: 2px dashed #4F8BF9;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: rgba(79, 139, 249, 0.05);
    }
    
    /* Container styling */
    .dark-container {
        background-color: #191F2A;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styles */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #4F8BF9;
    }
    .file-item {
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        background-color: rgba(79, 139, 249, 0.1);
    }
    
    /* Override default white backgrounds */
    .stTextArea textarea {
        background-color: #121620;
        color: #CDD6E4;
        border: 1px solid #2D3748;
    }
    .stExpander {
        background-color: #191F2A !important;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stExpander > div {
        background-color: #191F2A !important;
        border: none !important;
    }
    
    /* Success/error messages */
    .success-message {
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        color: #CDD6E4;
        border-radius: 0 8px 8px 0;
    }
    .error-message {
        background-color: rgba(220, 53, 69, 0.1);
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        color: #CDD6E4;
        border-radius: 0 8px 8px 0;
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background-color: #2D3748;
        margin: 2rem 0;
    }
    
    /* Remove white background from different elements */
    div.stSelectbox > div[data-baseweb="select"] > div {
        background-color: #191F2A !important;
        border-color: #2D3748 !important;
    }
    div.stSelectbox > div[data-baseweb="select"] > div:hover {
        border-color: #4F8BF9 !important;
    }
    div.stRadio > div {
        background-color: transparent !important;
    }
    .streamlit-expanderHeader {
        background-color: #191F2A !important;
        color: #CDD6E4 !important;
    }
    .streamlit-expanderContent {
        background-color: #191F2A !important;
    }
    
    /* File cards */
    .file-card {
        background-color: #191F2A;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background-color: #4F8BF9 !important;
    }
    
    /* Hide the default streamlit decoration */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom footer */
    .custom-footer {
        text-align: center;
        color: #8F9BAF;
        padding: 1rem 0;
        margin-top: 2rem;
    }
    
    /* Download button styling */
    .download-btn {
        display: inline-block;
        background-color: #4F8BF9;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 1rem;
        font-weight: bold;
    }
    
    /* Button container */
    .button-container {
        display: flex;
        gap: 10px;
        margin-top: 1rem;
    }
    
    /* Section headers */
    .section-header {
        color: #4F8BF9;
        border-bottom: 1px solid #2D3748;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Remove white borders in all elements */
    .element-container, .stMarkdown, .stDownloadButton, .stRadio, .stCheckbox {
        border: none !important;
        background-color: transparent !important;
    }
    
    /* Audio player styling */
    .audio-player {
        width: 100%;
        margin: 1rem 0;
        border-radius: 8px;
        background-color: #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Function to extract text from Word file
def extract_text_from_word(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Function to translate text
def translate_text(text, target_lang):
    # Add progress info
    progress_text = "Translating document..."
    my_bar = st.progress(0)
    
    # For longer texts, we might need to chunk them
    if len(text) > 5000:
        chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            translated_chunk = GoogleTranslator(source='auto', target=target_lang).translate(chunk)
            translated_chunks.append(translated_chunk)
            my_bar.progress((i+1)/len(chunks))
            
        my_bar.empty()
        return " ".join(translated_chunks)
    else:
        # For shorter texts
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        my_bar.progress(1.0)
        my_bar.empty()
        return translated_text

# Function to create a PDF in memory
def create_pdf(text, title="Translated Document"):
    if not text.strip():
        return None

    pdf = FPDF()
    pdf.add_page()
    
    # Add a header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, 0, 1, 'C')
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # Add content
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, text)
    
    # Add footer with page numbers
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    
    # Output the PDF to a BytesIO stream
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Function to create Text-to-Speech audio
def text_to_speech(text, lang_code):
    try:
        # Limit text length for TTS to avoid issues
        if len(text) > 5000:
            text = text[:5000] + "... (Text truncated for audio)"
        
        tts = gTTS(text=text, lang=lang_code[:2], slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        # Return audio bytes
        return audio_bytes
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

# Helper function to create an HTML audio player with audio data
def get_audio_player_html(audio_bytes):
    audio_base64 = base64.b64encode(audio_bytes.read()).decode()
    return f"""
    <audio class="audio-player" controls>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """

# Language mapping for display and TTS
language_map = {
    "fr": "French 🇫🇷",
    "es": "Spanish 🇪🇸",
    "de": "German 🇩🇪",
    "it": "Italian 🇮🇹",
    "pt": "Portuguese 🇵🇹",
    "nl": "Dutch 🇳🇱",
    "hi": "Hindi 🇮🇳",
    "zh-CN": "Chinese (Simplified) 🇨🇳",
    "ja": "Japanese 🇯🇵",
    "ko": "Korean 🇰🇷",
    "ar": "Arabic 🇸🇦",
    "ru": "Russian 🇷🇺"
}

# Initialize session state for storing translated texts and file info
if 'translated_texts' not in st.session_state:
    st.session_state.translated_texts = {}
if 'file_info' not in st.session_state:
    st.session_state.file_info = {}
if 'all_translated_pdfs' not in st.session_state:
    st.session_state.all_translated_pdfs = []
if 'extracted_texts' not in st.session_state:
    st.session_state.extracted_texts = {}

# Hide Streamlit branding
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown('<div class="sidebar-header">Document Translator Pro</div>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2399/2399976.png", width=100)
    
    st.markdown('<div class="sidebar-header">Uploaded Files</div>', unsafe_allow_html=True)
    
    # This will be populated after files are uploaded
    file_placeholder = st.empty()
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">Translation Statistics</div>', unsafe_allow_html=True)
    stats_placeholder = st.empty()
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Add Translate All button in sidebar
    translate_all_placeholder = st.empty()
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">Need Help?</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="dark-container">
        📚 Accepted file formats: PDF and DOCX
    </div>
    <div class="dark-container">
        💡 Maximum file size: 200MB
    </div>
    <div class="dark-container">
        🔊 Text-to-Speech available separately after translation
    </div>
    """, unsafe_allow_html=True)

# Main content area
st.markdown('<h1 class="main-header">Document Translator Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Translate your documents with ease and precision</p>', unsafe_allow_html=True)

# Two-column layout for upload and language selection
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
    st.markdown("## Upload Documents")
    st.markdown("Drag and drop your PDF or Word files below")
    
    # File uploader with better styling
    uploaded_files = st.file_uploader(
        "",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="document_uploader"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="dark-container">', unsafe_allow_html=True)
    st.markdown("## Target Language")
    
    # Language selection with icons
    selected_language_name = st.selectbox(
        "Select the language you want to translate to:",
        options=list(language_map.keys()),
        format_func=lambda x: language_map[x]
    )
    
    # Option to detect source language or set it manually
    source_language_option = st.radio(
        "Source language:",
        ["Auto-detect", "Select manually"]
    )
    
    if source_language_option == "Select manually":
        source_language = st.selectbox(
            "Select source language:",
            options=["en"] + list(language_map.keys()),
            format_func=lambda x: "English 🇺🇸" if x == "en" else language_map.get(x, x)
        )
    else:
        source_language = "auto"
    
    st.markdown("</div>", unsafe_allow_html=True)

# Function to translate all documents at once
def translate_all_documents():
    # Display a progress bar for the overall process
    overall_progress = st.progress(0)
    status_text = st.empty()
    
    for i, (file_name, file_info) in enumerate(st.session_state.file_info.items()):
        status_text.text(f"Translating {file_name}... ({i+1}/{len(st.session_state.file_info)})")
        
        # Get the extracted text
        extracted_text = st.session_state.extracted_texts.get(file_name, "")
        
        if extracted_text:
            # Translate the text
            translated_text = translate_text(extracted_text, selected_language_name)
            
            if translated_text.strip():
                # Store translated text
                st.session_state.translated_texts[file_name] = translated_text
                
                # Generate PDF
                pdf_file = create_pdf(translated_text, f"Translated: {file_name}")
                
                if pdf_file:
                    # Store for download all option
                    st.session_state.all_translated_pdfs.append((file_name, pdf_file.getvalue()))
        
        # Update progress
        overall_progress.progress((i + 1) / len(st.session_state.file_info))
    
    # Mark as complete
    status_text.text("All translations complete!")
    time.sleep(1)  # Give user a moment to see the completion message
    status_text.empty()
    overall_progress.empty()
    
    # Force refresh
    st.rerun()

# Update sidebar file list and extract text from files
if uploaded_files:
    with file_placeholder.container():
        for f in uploaded_files:
            st.markdown(f'<div class="file-item">• {f.name}</div>', unsafe_allow_html=True)
            
            # Store file info and extract text if not already processed
            if f.name not in st.session_state.file_info:
                file_type = f.name.split(".")[-1].lower()
                st.session_state.file_info[f.name] = {
                    "type": file_type,
                    "translated": False
                }
                
                # Extract text
                if file_type == "pdf":
                    extracted_text = extract_text_from_pdf(f)
                elif file_type == "docx":
                    extracted_text = extract_text_from_word(f)
                else:
                    extracted_text = ""
                
                st.session_state.extracted_texts[f.name] = extracted_text
    
    # Update stats
    with stats_placeholder.container():
        st.markdown('<div class="dark-container">', unsafe_allow_html=True)
        st.metric("Files Uploaded", len(uploaded_files))
        translated_count = sum(1 for f in st.session_state.file_info.values() if f.get("translated", False))
        st.metric("Files Translated", f"{translated_count}/{len(uploaded_files)}")
        st.metric("Target Language", language_map.get(selected_language_name, selected_language_name))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show Translate All button if there are untranslated files
    if translated_count < len(uploaded_files):
        with translate_all_placeholder.container():
            st.markdown('<div class="dark-container">', unsafe_allow_html=True)
            st.markdown("### Batch Actions")
            
            # The button triggers the translate_all_documents function
            translate_all_button = st.button(
                "🔄 Translate All Documents", 
                key="translate_all_btn",
                help="Translate all uploaded documents at once",
                use_container_width=True
            )
            
            if translate_all_button:
                translate_all_documents()
                
            st.markdown('</div>', unsafe_allow_html=True)

# Process files if any are uploaded
if uploaded_files:
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">Translation Results</h2>', unsafe_allow_html=True)
    
    # Create a container for all file cards
    files_container = st.container()
    
    # Process each file and create a card for it
    for i, uploaded_file in enumerate(uploaded_files):
        file_name = uploaded_file.name
        
        with files_container:
            st.markdown(f'<div class="file-card">', unsafe_allow_html=True)
            
            # Display file info
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"File: {file_name}")
            with col2:
                file_type = st.session_state.file_info[file_name]["type"]
                file_icon = "📄" if file_type == "docx" else "📑"
                st.markdown(f"### {file_icon} {file_type.upper()}")
            
            # Get extracted text
            extracted_text = st.session_state.extracted_texts.get(file_name, "")
            
            if extracted_text:
                # Show text in expanders
                with st.expander(f"View Source Text", expanded=False):
                    st.text_area(
                        "",
                        extracted_text,
                        height=150
                    )
                
                # If already translated, show the translation
                if file_name in st.session_state.translated_texts:
                    translated_text = st.session_state.translated_texts[file_name]
                    
                    # Mark as translated in the file info
                    st.session_state.file_info[file_name]["translated"] = True
                    
                    # Show translated text
                    with st.expander(f"View Translated Text", expanded=True):
                        st.text_area(
                            "",
                            translated_text,
                            height=150
                        )
                    
                    # Create buttons row for downloading PDF and generating TTS
                    st.markdown('<div class="button-container">', unsafe_allow_html=True)
                    
                    # Find the PDF in already generated PDFs
                    pdf_data = None
                    for name, data in st.session_state.all_translated_pdfs:
                        if name == file_name:
                            pdf_data = data
                            break
                    
                    # If PDF exists, offer download
                    if pdf_data:
                        pdf_buffer = BytesIO(pdf_data)
                        pdf_buffer.seek(0)
                        
                        # Download PDF button
                        st.download_button(
                            label=f"📥 Download Translated PDF",
                            data=pdf_buffer,
                            file_name=f"translated_{file_name}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Add separate Text-to-Speech button
                    tts_button = st.button(
                        f"🔊 Generate Audio",
                        key=f"tts_{i}",
                        help="Generate audio from translated text",
                        type="primary",
                    )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # If TTS button is clicked, generate audio
                    if tts_button:
                        with st.spinner("Generating audio..."):
                            audio_bytes = text_to_speech(translated_text, selected_language_name)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")
                                st.markdown('<div class="success-message">Audio generated successfully!</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="error-message">Failed to generate audio.</div>', unsafe_allow_html=True)
                
                # If not yet translated, show translate button
                else:
                    # Translate button
                    if st.button(f"Translate Document", key=f"translate_{i}"):
                        with st.spinner(f"Translating {file_name}..."):
                            # Translate the text
                            translated_text = translate_text(extracted_text, selected_language_name)
                            
                            if not translated_text.strip():
                                st.markdown('<div class="error-message">Translation failed! No text returned.</div>', unsafe_allow_html=True)
                            else:
                                # Store translated text
                                st.session_state.translated_texts[file_name] = translated_text
                                st.session_state.file_info[file_name]["translated"] = True
                                
                                # Generate PDF
                                pdf_file = create_pdf(
                                    translated_text, 
                                    f"Translated: {file_name}"
                                )
                                
                                if pdf_file:
                                    # Store for download all option
                                    st.session_state.all_translated_pdfs.append((file_name, pdf_file.getvalue()))
                                
                                # Force refresh to show the translation
                                st.rerun()
            else:
                st.markdown('<div class="error-message">No text could be extracted from this file.</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # After processing all files, offer a "Download All" option
    if st.session_state.all_translated_pdfs:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Create an in-memory ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for original_name, pdf_bytes in st.session_state.all_translated_pdfs:
                # Use a filename that indicates it's the translated version
                zip_file.writestr(f"translated_{original_name}.pdf", pdf_bytes)
        
        # Important: move the pointer back to start so Streamlit can read it
        zip_buffer.seek(0)
        
        st.markdown("""
        <div class="file-card" style="text-align: center;">
            <h3>All Translations Complete!</h3>
            <p>Download all your translated documents in a single ZIP file.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📦 Download All Translated PDFs",
                data=zip_buffer,
                file_name="all_translated_documents.zip",
                mime="application/zip",
                use_container_width=True
            )
else:
    # Display instructions when no files are uploaded
    st.markdown('<div class="dark-container">👆 Upload one or more PDF or Word documents to get started!</div>', unsafe_allow_html=True)
    
    # Show example/demo section
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">How It Works</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="dark-container">', unsafe_allow_html=True)
        st.markdown("### 1. Upload")
        st.markdown("Upload one or more PDF or DOCX files")
        st.image("https://cdn-icons-png.flaticon.com/512/476/476863.png", width=80)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="dark-container">', unsafe_allow_html=True)
        st.markdown("### 2. Translate")
        st.markdown("Select your target language and translate")
        st.image("https://cdn-icons-png.flaticon.com/512/2329/2329086.png", width=80)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="dark-container">', unsafe_allow_html=True)
        st.markdown("### 3. Listen")
        st.markdown("Generate audio from translated content")
        st.image("https://cdn-icons-png.flaticon.com/512/727/727269.png", width=80)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="dark-container">', unsafe_allow_html=True)
        st.markdown("### 4. Download")
        st.markdown("Download individual files or as a ZIP package")
        st.image("https://cdn-icons-png.flaticon.com/512/2905/2905068.png", width=80)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="custom-footer">
    Document Translator Pro • Powered by Streamlit • Version 2.2
</div>
""", unsafe_allow_html=True)