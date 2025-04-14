import streamlit as st

# Inject custom CSS to hide Streamlit UI elements
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {visibility: hidden;}
            .stActionButton {visibility: hidden;}
            .css-eczf16 {visibility: hidden;} /* Top buttons */
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Hello, Production World!")
st.write("All Streamlit controls are now hidden.")

