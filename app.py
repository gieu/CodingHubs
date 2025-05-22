
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
        "Graficador Estudiantes": [
            st.Page(
                page="app_pages/estudiantes.py",
                title="Graficador Estudiantes",
                icon="📊",
                url_path="/estudiantes"
            )
        ],
        "Graficador Publico Pares": [
            st.Page(
                page="app_pages/public_pares.py",
                title="Graficador Publico Pares",
                icon="📊",
                url_path="/public_pares"
            )
        ],"Graficador Publico Estudiantes": [
            st.Page(
                page="app_pages/public_estudiantes.py",
                title="Graficador Publico Estudiantes",
                icon="📊",
                url_path="/public_estudiantes"
            )
        ], "Flourish": [
            st.Page(
                page="app_pages/flourish.py",
                title="Graficas de flourish",
                icon="📊",
                url_path="/flourish"
            )
        ],
        "Graficador de Instantaneas": [
            st.Page(
                page="app_pages/instantaneas.py",
                title="Graficador de Instantaneas",
                icon="📊",
                url_path="/instantaneas"
            )
        ],
        "Graficador de Preguntas Generales": [
            st.Page(
                page="app_pages/preguntas_generales.py",
                title="Graficador de Preguntas Generales",
                icon="📊",
                url_path="/preguntas_generales"
            )
        ],          
    }

    app = st.navigation(pages)
    
    # st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
    app.run()
    

if __name__ == '__main__': 
    main()