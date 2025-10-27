import streamlit as st
import json

st.set_page_config(page_title="Machine d’action à haut rendement", layout="wide")
st.title("⚙️ Machine d’action à haut rendement")

# Zone pour coller le JSON
json_input = st.text_area(
    "Colle ici le JSON produit par le LLM",
    height=300,
    placeholder='{"seed_intent":"...","items":[{"id":"it-01",...}]}'
)

# Stockage dans session_state
if "items" not in st.session_state:
    st.session_state.items = []

if st.button("🚀 Charger le JSON"):
    try:
        data = json.loads(json_input)
        st.session_state.items = data.get("items", [])
        st.session_state.seed_intent = data.get("seed_intent", "")
        st.success("✅ JSON chargé avec succès !")
    except Exception as e:
        st.error(f"Erreur de parsing JSON : {e}")

# Affichage des items
if st.session_state.items:
    st.subheader(f"🎯 Intention : {st.session_state.seed_intent}")
    st.write("---")
    items_to_keep = []

    for item in st.session_state.items:
        # Choix de la couleur selon priorité
        color = "#ff9999" if item.get("priorite") == "haute" else "#fff799" if item.get("priorite") == "moyenne" else "#cce5ff"

        with st.container():
            st.markdown(
                f"""
                <div style='border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:10px; background-color:{color};'>
                <h4>{item.get('titre')}</h4>
                <p><b>Description:</b> {item.get('description')}</p>
                <p><b>Action:</b> {item.get('action')}</p>
                <p><b>Durée estimée:</b> {item.get('temps_estime_min')} min | <b>Effort:</b> {item.get('niveau_d_effort')}/3</p>
                <p><b>Tags:</b> {', '.join(item.get('tags', []))}</p>
                <p><i>Prochaine micro-action:</i> {item.get('suggested_next')}</p>
                </div>
                """, unsafe_allow_html=True
            )

            cols = st.columns([0.1, 0.2])
            with cols[0]:
                keep = st.checkbox("✅ Garder", key=f"keep_{item['id']}", value=True)
            with cols[1]:
                if st.button("🗑️ Supprimer", key=f"delete_{item['id']}"):
                    st.session_state.items = [it for it in st.session_state.items if it["id"] != item["id"]]
                    st.experimental_rerun()

    # Export JSON filtré
    kept_items = [it for it in st.session_state.items if st.session_state.get(f"keep_{it['id']}", False)]
    st.markdown("### 📦 JSON filtré des items gardés")
    st.json({"seed_intent": st.session_state.seed_intent, "items": kept_items})

    if st.button("💾 Télécharger JSON filtré"):
        st.download_button(
            label="📥 Télécharger",
            data=json.dumps({"seed_intent": st.session_state.seed_intent, "items": kept_items}, indent=2, ensure_ascii=False),
            file_name="actions_filtrees.json",
            mime="application/json"
        )
