import streamlit as st
import os


def about_us():
    st.title("👥 Acerca de Nosotros")
    st.write("Somos un grupo de estudiantes de Data Science en Hackaboss.")
    st.write("Este es nuestro proyecto final de la fase de formación en Data Science.")
    st.write("Esperamos que disfrutes de la aplicación que hemos creado. 🚀")

    # Get absolute path of the images directory
    images_dir = os.path.join("pages", "images")

    # Lista de integrantes (Nombre, Foto, LinkedIn, GitHub)
    integrantes = [
        ("Lucija Brcic", os.path.join(images_dir, "lucija.jpg"), 
         "www.linkedin.com/in/lucija-brcic-7479b31a4", 
         "https://github.com/LucijaBrcic"),
         
        ("Jordi Montseny", os.path.join(images_dir, "jordi.jpg"), 
         "https://linkedin.com/in/jordi", 
         "https://github.com/jmontseny"),
         
        ("Luis Serrano Borras", os.path.join(images_dir, "luis.jpg"), 
         "https://linkedin.com/in/luis", 
         "https://github.com/luis"),
    ]

    # Encabezado de la sección
    st.subheader("👨‍💻 Equipo de Desarrollo")

    # Sección con fotos y enlaces
    with st.container():
        for nombre, foto, linkedin, github in integrantes:
            col1, col2 = st.columns([1, 3])  # Column layout: 1 for image, 3 for text

            with col1:
                if os.path.exists(foto):
                    st.image(foto, width=100)  # Show profile picture
                else:
                    st.write("Imagen no encontrada")

            with col2:
                st.markdown(f"### {nombre}")  # Make name bold
                st.markdown(f"[🔗 LinkedIn]({linkedin}) | [💻 GitHub]({github})", unsafe_allow_html=True)


# Llamar a la función si el script se ejecuta directamente
if __name__ == "__main__":
    about_us()
