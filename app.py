import streamlit as st
import json

st.set_page_config(page_title="Machine d'action", layout="wide")

# Style pour fond noir
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Machine d'action à haut rendement")

# --- Sidebar ---
st.sidebar.header("🧩 Charger JSON")
json_text = st.sidebar.text_area("Colle ton JSON ici", height=400)

if st.sidebar.button("🚀 Charger"):
    try:
        data = json.loads(json_text)
        st.session_state["data"] = data
        st.session_state["items"] = data.get("items", [])
        st.sidebar.success("✅ Chargé !")
    except Exception as e:
        st.sidebar.error(f"Erreur : {e}")

# --- Affichage ---
if "data" not in st.session_state:
    st.info("👈 Colle ton JSON et clique sur Charger")
    st.stop()

data = st.session_state["data"]
items = st.session_state.get("items", [])

st.subheader(f"🎯 {data.get('seed_intent', 'Sans intention')}")
st.divider()

for idx, item in enumerate(items):
    item_id = item.get("id", f"item_{idx}")
    
    # Couleurs adaptées au thème sombre
    priorite = item.get("priorite", "").lower()
    colors = {
        "haute": "#8b0000",      # Rouge foncé
        "moyenne": "#b8860b",    # Jaune foncé/or
        "basse": "#1e3a5f"       # Bleu foncé
    }
    bg = colors.get(priorite, "#1a1a2e")
    border_colors = {
        "haute": "#ff4444",
        "moyenne": "#ffaa00", 
        "basse": "#4488ff"
    }
    border = border_colors.get(priorite, "#666")
    
    # Card
    st.markdown(f"""
        <div style='
            background:{bg}; 
            padding:20px; 
            border-radius:8px; 
            margin-bottom:15px; 
            border-left:4px solid {border};
            color: #fafafa;
        '>
            <h3 style='color: #fafafa; margin-top:0;'>{item.get('titre', 'Sans titre')}</h3>
            <p><b>Description:</b> {item.get('description', 'N/A')}</p>
            <p><b>Action:</b> {item.get('action', 'N/A')}</p>
            <p><b>Temps:</b> {item.get('temps_estime_min', '?')} min | <b>Effort:</b> {item.get('niveau_d_effort', '?')}/3</p>
            <p><b>Tags:</b> {', '.join(item.get('tags', []))}</p>
            <p style='color: #aaa;'><i>Suivant: {item.get('suggested_next', 'N/A')}</i></p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Supprimer", key=f"del_{item_id}_{idx}"):
        st.session_state["items"] = [it for it in items if it.get("id") != item_id]
        st.rerun()

st.divider()
st.success(f"✅ {len(items)} items actifs")
