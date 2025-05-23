
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
        "Marco de Consolidacion": [
            st.Page(
                page="app_pages/marco.py",
                title="Marco de Consolidacion",
                icon="📊",
                url_path="/marco"
            )
        ],
        "Graficador Pares": [
            st.Page(
                page="app_pages/pares.py",
                title="Graficador Pares",
                icon="📊",
                url_path="/pares"
            )
        ],
    }

    app = st.navigation(pages)
    
    # st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
    app.run()
    

if __name__ == '__main__': 
    main()