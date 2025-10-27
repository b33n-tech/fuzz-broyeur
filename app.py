import streamlit as st
import json

# --- Config page ---
st.set_page_config(page_title="Machine d’action à haut rendement", layout="wide")
st.title("⚙️ Machine d’action à haut rendement")

# --- Initialisations sécurisées ---
if "items" not in st.session_state or not isinstance(st.session_state.items, list):
    st.session_state.items = []

if "seed_intent" not in st.session_state or not isinstance(st.session_state.seed_intent, str):
    st.session_state.seed_intent = ""

# --- Sidebar : Input JSON ---
st.sidebar.header("🧩 JSON Input")
json_input = st.sidebar.text_area(
    "Colle ici le JSON produit par le LLM",
    height=300,
    placeholder='{"seed_intent":"...","items":[{"id":"it-01",...}]}'
)

# --- Charger JSON ---
if st.sidebar.button("🚀 Charger le JSON"):
    try:
        data = json.loads(json_input)
        # Items sécurisés
        items = data.get("items", [])
        if not isinstance(items, list):
            items = []
        st.session_state.items = items

        seed_intent = data.get("seed_intent", "")
        if not isinstance(seed_intent, str):
            seed_intent = ""
        st.session_state.seed_intent = seed_intent

        st.success("✅ JSON chargé avec succès !")
    except Exception as e:
        st.error(f"Erreur de parsing JSON : {e}")

# --- Affichage des items ---
if isinstance(st.session_state.items, list) and len(st.session_state.items) > 0:
    st.subheader(f"🎯 Intention : {st.session_state.seed_intent}")
    st.write("---")

    to_delete = []

    for item in st.session_state.items:
        # Couleur selon priorité
        color = (
            "#ff9999" if item.get("priorite") == "haute"
            else "#fff799" if item.get("priorite") == "moyenne"
            else "#cce5ff"
        )

        # Container card
        with st.container():
            st.markdown(
                f"""
                <div style='border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:10px; background-color:{color};'>
                <h4>{item.get('titre', item.get('intitule', 'Sans titre'))}</h4>
                <p><b>Description:</b> {item.get('description', 'N/A')}</p>
                <p><b>Action:</b> {item.get('action', 'N/A')}</p>
                <p><b>Durée estimée:</b> {item.get('temps_estime_min', 'N/A')} min | <b>Effort:</b> {item.get('niveau_d_effort', 'N/A')}/3</p>
                <p><b>Tags:</b> {', '.join(item.get('tags', []))}</p>
                <p><i>Prochaine micro-action:</i> {item.get('suggested_next', 'N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            cols = st.columns([0.1, 0.2])
            with cols[0]:
                st.checkbox("✅ Garder", key=f"keep_{item.get('id','no_id')}", value=True)
            with cols[1]:
                if st.button("🗑️ Supprimer", key=f"delete_{item.get('id','no_id')}"):
                    to_delete.append(item.get('id'))

    # --- Supprimer items sélectionnés ---
    if to_delete:
        st.session_state.items = [
            it for it in st.session_state.items if it.get("id") not in to_delete
        ]
        st.experimental_rerun()

    # --- Export JSON filtré ---
    kept_items = [
        it for it in st.session_state.items if st.session_state.get(f"keep_{it.get('id','no_id')}", False)
    ]

    st.markdown("### 📦 JSON filtré des items gardés")
    st.json({"seed_intent": st.session_state.seed_intent, "items": kept_items})

    st.download_button(
        label="💾 Télécharger JSON filtré",
        data=json.dumps({"seed_intent": st.session_state.seed_intent, "items": kept_items}, indent=2, ensure_ascii=False),
        file_name="actions_filtrees.json",
        mime="application/json"
    )

else:
    st.info("👈 Colle ton JSON dans la sidebar et clique sur 'Charger le JSON'.")
