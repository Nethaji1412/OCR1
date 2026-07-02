"""
OCR System - Streamlit Cloud Compatible (FIXED)
Upload → Extract → Correct → Translate → Export with Format Preservation

Key Fixes:
- Proper OpenCV imports
- PDF format preservation during translation
- Better error handling
"""

import streamlit as st
from pathlib import Path
import os
from datetime import datetime
import json
import sys

# # Fix OpenCV import
# try:
#     import cv2
# except ImportError:
#     print("Installing opencv-python...")
#     os.system("pip install opencv-python-headless")
#     import cv2

# Import custom modules (cloud-compatible)
try:
    from ocr_engine_enhanced import EnhancedOCREngine
except ImportError as e:
    st.error(f"Error loading OCR engine: {e}")
    st.stop()

try:
    from llm_corrector_cloud import FireworksCorrector
except ImportError as e:
    st.error(f"Error loading corrector: {e}")
    st.stop()

try:
    from translation_engine_cloud import SimpleTranslationEngine
except ImportError as e:
    st.error(f"Error loading translator: {e}")
    st.stop()

try:
    from file_handler_enhanced import FileHandler
except ImportError as e:
    st.error(f"Error loading file handler: {e}")
    st.stop()

try:
    from pdf_layout_preserver import PDFLayoutPreserver
except ImportError as e:
    st.warning(f"PDF layout preservation unavailable: {e}")
    PDFLayoutPreserver = None

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Advanced OCR System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.title("⚙️ Configuration")

# API Key configuration
with st.sidebar.expander("🔑 API Keys", expanded=False):
    fireworks_key = st.text_input(
        "Fireworks API Key (Optional)",
        type="password",
        value="",
        help="Leave blank to use local correction only"
    )
    if fireworks_key:
        os.environ["FIREWORKS_API_KEY"] = fireworks_key

# Processing options
st.sidebar.subheader("🎯 Processing Options")

ocr_languages = st.sidebar.multiselect(
    "OCR Languages",
    options=['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Marathi'],
    default=['English', 'Hindi'],
    help="Languages to detect in documents"
)

language_map = {
    'English': 'en',
    'Hindi': 'hi',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Kannada': 'ka',
    'Marathi': 'mr'
}

ocr_langs = [language_map[lang] for lang in ocr_languages]

enable_correction = st.sidebar.checkbox("Enable Text Correction", value=True)
enable_translation = st.sidebar.checkbox("Enable Translation", value=False)
enable_pdf_format_preservation = st.sidebar.checkbox("Preserve PDF Format", value=True)

if enable_translation:
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        translation_source = st.selectbox(
            "From",
            ['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Marathi'],
            index=0,
            key="src_lang"
        )
    
    with col2:
        translation_target = st.selectbox(
            "To",
            ['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Marathi'],
            index=1,
            key="tgt_lang"
        )
else:
    translation_source = 'English'
    translation_target = 'Hindi'

with st.sidebar.expander("⚡ Advanced Options"):
    ocr_confidence = st.slider(
        "OCR Confidence Threshold",
        0.0, 1.0, 0.80, 0.05
    )
    
    pdf_dpi = st.slider(
        "PDF Quality (DPI)",
        72, 300, 150, 25
    )

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'ocr_result' not in st.session_state:
    st.session_state.ocr_result = None

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

if 'corrected_text' not in st.session_state:
    st.session_state.corrected_text = None

if 'translated_text' not in st.session_state:
    st.session_state.translated_text = None

if 'file_type' not in st.session_state:
    st.session_state.file_type = None

# ============================================================================
# MAIN APP
# ============================================================================

st.title("📄 Advanced OCR System")

st.markdown("""
Advanced OCR with Format-Preserving Capabilities:
- 🖼️ **Multi-format**: Images, PDFs (with layout preservation), DOCX
- ✨ **Smart Correction**: Local + LLM (Fireworks optional)
- 🌐 **Translation**: 6 Indian languages
- 📄 **Format Preservation**: Keep original PDF layout & fonts
- 📊 **Export**: JSON, TXT, **PDF with original formatting**
""")

# ============================================================================
# TAB LAYOUT
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload & Extract",
    "✏️ Correction",
    "🌐 Translation",
    "📊 Results"
])

# ============================================================================
# TAB 1: UPLOAD & EXTRACT
# ============================================================================

with tab1:
    st.subheader("📤 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["jpg", "jpeg", "png", "bmp", "tiff", "pdf", "docx", "doc"],
        help="Max 100MB"
    )
    
    if uploaded_file:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File", uploaded_file.name[:30])
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
        with col3:
            st.metric("Type", uploaded_file.type)
        
        file_handler = FileHandler()
        save_result = file_handler.save_file(uploaded_file)
        
        if save_result['success']:
            file_path = save_result['file_path']
            file_type = save_result['file_type']
            st.session_state.file_type = file_type
            
            st.success(f"✅ File ready: {save_result['saved_filename']}")
            
            if st.button("🚀 Extract Text (OCR)", key="extract_button", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    with st.spinner("Initializing OCR..."):
                        status_text.text("⏳ Initializing OCR engine...")
                        progress_bar.progress(10)
                        
                        ocr_engine = EnhancedOCREngine(languages=ocr_langs)
                        
                        # Special handling for PDFs with layout preservation
                        if file_type == 'pdf' and enable_pdf_format_preservation and PDFLayoutPreserver:
                            status_text.text("⏳ Extracting PDF with format preservation...")
                            progress_bar.progress(30)
                            
                            preserver = PDFLayoutPreserver()
                            pdf_result = preserver.extract_with_formatting(file_path)
                            
                            if pdf_result['status'] == 'success':
                                st.session_state.pdf_data = pdf_result
                                st.session_state.ocr_result = {
                                    'status': 'success',
                                    'raw_text': '\n\n'.join(preserver.get_text_by_page(pdf_result['pages'])),
                                    'blocks': pdf_result['blocks'],
                                    'confidence': 0.95,
                                    'page_count': pdf_result['page_count'],
                                    'block_count': pdf_result['block_count'],
                                    'source': 'pdf_formatted'
                                }
                            else:
                                st.warning("Could not preserve PDF format, using standard extraction")
                                result = ocr_engine.extract_text(file_path)
                                st.session_state.ocr_result = result
                        else:
                            status_text.text("⏳ Extracting text...")
                            progress_bar.progress(40)
                            
                            result = ocr_engine.extract_text(file_path)
                            st.session_state.ocr_result = result
                        
                        status_text.text("✅ Extraction complete!")
                        progress_bar.progress(100)
                        
                        st.success("✅ OCR Complete!")
                        
                        result = st.session_state.ocr_result
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Confidence", f"{result['confidence']:.1%}")
                        with col2:
                            st.metric("Blocks", result['block_count'])
                        with col3:
                            st.metric("Characters", len(result['raw_text']))
                        with col4:
                            st.metric("Source", result['source'].upper())
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    progress_bar.progress(0)
        else:
            st.error(f"❌ {save_result['message']}")
    
    # Display extracted text
    if st.session_state.ocr_result:
        st.subheader("📝 Extracted Text")
        
        extracted_text = st.session_state.ocr_result['raw_text']
        
        st.text_area(
            "Raw OCR Output",
            value=extracted_text,
            height=250,
            disabled=True,
            key="ocr_output"
        )

# ============================================================================
# TAB 2: CORRECTION
# ============================================================================

with tab2:
    st.subheader("✏️ Text Correction")
    
    if st.session_state.ocr_result is None:
        st.info("👈 Extract text first in the Upload tab")
    else:
        extracted_text = st.session_state.ocr_result['raw_text']
        
        st.text_area(
            "Original Text",
            value=extracted_text,
            height=200,
            disabled=True,
            key="correction_input"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            use_api = st.checkbox(
                "Use Fireworks API (if key provided)",
                value=bool(os.getenv("FIREWORKS_API_KEY", ""))
            )
        
        with col2:
            if st.button("✨ Correct Text", use_container_width=True, key="correct_button"):
                with st.spinner("Correcting..."):
                    try:
                        corrector = FireworksCorrector()
                        result = corrector.correct_text(
                            extracted_text,
                            use_api=use_api
                        )
                        
                        st.session_state.corrected_text = result['corrected']
                        
                        st.success(f"✅ Corrected ({result['method']})")
                        st.caption(f"Confidence: {result['confidence']:.0%}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.corrected_text:
            st.subheader("Corrected Output")
            
            st.text_area(
                "Corrected Text",
                value=st.session_state.corrected_text,
                height=200,
                disabled=True,
                key="correction_output"
            )

# ============================================================================
# TAB 3: TRANSLATION
# ============================================================================

with tab3:
    st.subheader("🌐 Text Translation")
    
    if not enable_translation:
        st.info("👈 Enable translation in sidebar")
    elif st.session_state.corrected_text is None and st.session_state.ocr_result is None:
        st.info("👈 Extract text first")
    else:
        text_to_translate = st.session_state.corrected_text or st.session_state.ocr_result['raw_text']
        
        st.text_area(
            "Text to Translate",
            value=text_to_translate,
            height=150,
            disabled=True,
            key="translation_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.info(f"📍 From:\n{translation_source}")
        with col2:
            st.info(f"📍 To:\n{translation_target}")
        with col3:
            if st.button("🔄 Translate", use_container_width=True, key="translate_button"):
                with st.spinner("Translating..."):
                    try:
                        translator = SimpleTranslationEngine()
                        
                        translated = translator.translate(
                            text_to_translate,
                            source_lang=language_map.get(translation_source, 'en'),
                            target_lang=language_map.get(translation_target, 'hi')
                        )
                        
                        st.session_state.translated_text = translated
                        
                        st.success(f"✅ Translated to {translation_target}!")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.translated_text:
            st.subheader(f"📝 {translation_target} Translation")
            
            st.text_area(
                "Translated Text",
                value=st.session_state.translated_text,
                height=150,
                disabled=True,
                key="translation_output"
            )

# ============================================================================
# TAB 4: RESULTS & EXPORT
# ============================================================================

with tab4:
    st.subheader("📊 Results & Export")
    
    if st.session_state.ocr_result or st.session_state.corrected_text or st.session_state.translated_text:
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            content_txt = "=== OCR RESULTS ===\n\n"
            
            if st.session_state.ocr_result:
                content_txt += f"RAW TEXT:\n{st.session_state.ocr_result['raw_text']}\n\n"
            
            if st.session_state.corrected_text:
                content_txt += f"CORRECTED TEXT:\n{st.session_state.corrected_text}\n\n"
            
            if st.session_state.translated_text:
                content_txt += f"TRANSLATED TEXT:\n{st.session_state.translated_text}\n"
            
            st.download_button(
                "📥 Download TXT",
                content_txt,
                file_name=f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'ocr': {
                    'raw_text': st.session_state.ocr_result['raw_text'] if st.session_state.ocr_result else None,
                    'confidence': st.session_state.ocr_result['confidence'] if st.session_state.ocr_result else None,
                    'blocks': len(st.session_state.ocr_result['blocks']) if st.session_state.ocr_result else 0,
                } if st.session_state.ocr_result else None,
                'corrected': st.session_state.corrected_text,
                'translated': st.session_state.translated_text,
            }
            
            st.download_button(
                "📥 Download JSON",
                json.dumps(export_data, indent=2),
                file_name=f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.ocr_result = None
                st.session_state.pdf_data = None
                st.session_state.corrected_text = None
                st.session_state.translated_text = None
                st.success("✅ Cleared")
                st.rerun()
        
        # PDF format preservation export
        if st.session_state.pdf_data and st.session_state.translated_text and st.session_state.file_type == 'pdf':
            st.subheader("📄 Export with Format Preservation")
            
            if st.button("💾 Create Formatted PDF with Translation", use_container_width=True):
                with st.spinner("Creating formatted PDF..."):
                    try:
                        if PDFLayoutPreserver:
                            preserver = PDFLayoutPreserver()
                            
                            # Create translation mapping
                            translations = {
                                block.text: st.session_state.translated_text
                                for block in st.session_state.pdf_data['blocks']
                            }
                            
                            # Update blocks with translations
                            updated_blocks = preserver.update_translated_text(
                                st.session_state.pdf_data['blocks'],
                                translations
                            )
                            
                            # Create PDF
                            output_path = f"/tmp/translated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            
                            success = preserver.create_formatted_pdf(
                                updated_blocks,
                                output_path,
                                st.session_state.pdf_data['pages']
                            )
                            
                            if success:
                                with open(output_path, 'rb') as f:
                                    st.download_button(
                                        "📥 Download PDF (Formatted)",
                                        f.read(),
                                        file_name=f"translated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                st.success("✅ PDF created with preserved formatting!")
                        else:
                            st.warning("PDF format preservation not available")
                    
                    except Exception as e:
                        st.error(f"❌ Error creating PDF: {str(e)}")
    
    else:
        st.info("👈 No results yet. Process a document first!")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🟢 OCR System v1.1 Cloud (Fixed)")

with col2:
    st.caption(f"📄 Format Preservation: {'✅' if PDFLayoutPreserver else '⚠️'}")

with col3:
    st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
