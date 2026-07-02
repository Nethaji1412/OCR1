import streamlit as st
import sys
import importlib.util

st.write("Python:", sys.version)

st.write("cv2 installed:", importlib.util.find_spec("cv2"))

st.write("numpy installed:", importlib.util.find_spec("numpy"))

st.write("paddleocr installed:", importlib.util.find_spec("paddleocr"))
