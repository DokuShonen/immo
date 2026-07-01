import streamlit as st

def show_header():
    st.markdown("""
        <div style="background-color: #1a2a6c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; text-align: center;">
            <h2 style="margin: 0;">Plateforme de Gestion Immobilière</h2>
            <p style="margin: 5px 0 0; opacity: 0.8;">Votre partenaire de confiance</p>
        </div>
    """, unsafe_allow_html=True)

def show_footer():
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid #e0e0e0; color: #777;">
            <p>© 2026 Plateforme Immobilière - Tous droits réservés</p>
        </div>
    """, unsafe_allow_html=True)
