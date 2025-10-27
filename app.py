import streamlit as st
import json

st.set_page_config(page_title="Machine d'action", layout="wide")
st.title("⚙️ Machine d'action à haut rendement")

# --- Sidebar ---
st.sidebar.header("🧩 Charger JSON")
json_text = st.sidebar.text_area("Colle ton JSON ici", height=400)

if st.sidebar.button("🚀 Charger"):
    try:
        data = json.loads(json_text)
        st.session_state["data"] = data
        st.session_state["kept"] = {item["id"]: True for item in data.get("items", [])}
        st.success("✅ Chargé !")
    except Exception as e:
        st.sidebar.error(f"Erreur : {e}")

# --- Affichage ---
if "data" not in st.session_state:
    st.info("👈 Colle ton JSON et clique sur Charger")
    st.stop()

data = st.session_state["data"]
kept = st.session_state.get("kept", {})

st.subheader(f"🎯 {data.get('seed_intent', 'Sans intention')}")
st.divider()

for item in data.get("items", []):
    item_id = item.get("id", "")
    
    # Couleur
    priorite = item.get("priorite", "").lower()
    colors = {"haute": "#ffcdd2", "moyenne": "#fff9c4", "basse": "#e1f5fe"}
    bg = colors.get(priorite, "#f5f5f5")
    
    # Card
    st.markdown(f"""
        <div style='background:{bg}; padding:20px; border-radius:8px; margin-bottom:15px; border-left:4px solid #666;'>
            <h3>{item.get('titre', 'Sans titre')}</h3>
            <p><b>Description:</b> {item.get('description', 'N/A')}</p>
            <p><b>Action:</b> {item.get('action', 'N/A')}</p>
            <p><b>Temps:</b> {item.get('temps_estime_min', '?')} min | <b>Effort:</b> {item.get('niveau_d_effort', '?')}/3</p>
            <p><b>Tags:</b> {', '.join(item.get('tags', []))}</p>
            <p><i>Suivant: {item.get('suggested_next', 'N/A')}</i></p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        kept[item_id] = st.checkbox("✅ Garder", value=kept.get(item_id, True), key=f"k_{item_id}")

st.divider()

# Export
filtered = [item for item in data.get("items", []) if kept.get(item.get("id"), False)]
export = {"seed_intent": data.get("seed_intent", ""), "items": filtered}

st.subheader(f"📦 Export ({len(filtered)} items)")
st.json(export)

st.download_button(
    "💾 Télécharger JSON",
    json.dumps(export, indent=2, ensure_ascii=False),
    "actions.json",
    "application/json"
)
