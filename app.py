import streamlit as st

# Main entry point for the Career Recommendation System
st.set_page_config(page_title="Career Recommendation System", layout="wide")

st.title("Career Recommendation System")
st.write("Find careers that match your skills, interests, education and goals.")
st.write("Use the pages in the sidebar to start your assessment.")

st.subheader("How it works")
st.markdown(
    "1. Complete the career assessment\n"
    "2. Review your ranked career matches\n"
    "3. Check the skills you need for each career\n"
    "4. Explore all careers in the catalogue"
)
