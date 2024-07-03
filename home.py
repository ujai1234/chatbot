import streamlit as st

def main():
    # Custom CSS for styling the title
    st.markdown(
        """
        <style>
        .title {
            font-size: 100px;
            font-weight: bold;
            color: #FAFFAF;
            text-shadow: 2px 2px 4px #000000;
            padding: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Adding the title with custom styling
    st.markdown('<p class="title">Nutrimom</p>', unsafe_allow_html=True)
    
    st.title("Selamat Datang di Aplikasi Nutrimom")
    st.write("""
    ### Aplikasi Kesehatan untuk Ibu Hamil dan Balita
    Aplikasi ini untuk membantu mengatasi stunting dari masa kandungan sampai balita.
    """)

if __name__ == "__main__":
    main()
