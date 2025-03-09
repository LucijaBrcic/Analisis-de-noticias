import streamlit as st

st.title("Análisis de Datos")

# Subpage navigation
subpage = st.sidebar.selectbox("Selecciona un análisis:", ["Overview", "Scatter Plot", "Heatmap"])

if subpage == "Overview":
    st.write("📊 Resumen de los datos...")
elif subpage == "Scatter Plot":
    st.write("📈 Aquí está el scatter plot...")
    # Add scatter plot code here
elif subpage == "Heatmap":
    st.write("🔥 Aquí está el heatmap...")
    # Add heatmap code here
