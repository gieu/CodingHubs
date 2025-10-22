
import streamlit as st

# Configuración de la página - debe ser lo primero
st.set_page_config(
    page_title="Colombia Programa - Análisis de Datos",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        "Análisis de Datos": [
            st.Page(
                page="app_pages/pares.py",
                title="Codinghub Masters",
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