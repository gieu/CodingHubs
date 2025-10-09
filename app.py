
import streamlit as st
def main(): 
    pages = {
        "": [
            st.Page(
                page = "app_pages/home.py",
                title = "Inicio",
                icon = "🏠",
                url_path="/home"
            )
            ],       
        "¿Que es Colombia Programa?": [
            st.Page(
                page="app_pages/intro.py",
                title="¿Que es Colombia Programa?",
                icon="❓",
                url_path="/intro"
            )
        ],
        "Análisis de Datos": [
            st.Page(
                page="app_pages/pares.py",
                title="Pares Expertos",
                icon="👥",
                url_path="/pares"
            ),
            st.Page(
                page="app_pages/encuentros_colaborativos.py",
                title="Encuentros Colaborativos",
                icon="🤝",
                url_path="/encuentros_colaborativos"
            )
        ],
    }

    app = st.navigation(pages)
    
    # st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
    app.run()
    

if __name__ == '__main__': 
    main()