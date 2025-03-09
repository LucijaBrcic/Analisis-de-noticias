import streamlit as st

#---------------SETTINGS-----------------
page_title = "Análisis de noticias"
page_icon = ":newspaper:"
layout = "wide"
#----------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

st.write("Explora los datos y analiza tendencias en las noticias.")

st.sidebar.success("Selecciona una página en la barra lateral.")
