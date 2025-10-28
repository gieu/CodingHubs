
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
        "Observaciones de Aula": [
            st.Page(
                page="app_pages/observaciones.py",
                title="Graficador de Instantaneas",
                icon="📊",
                url_path="/observaciones"
            )
        ],
    }

    app = st.navigation(pages)
    
    # st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
    app.run()
    

if __name__ == '__main__': 
    main()