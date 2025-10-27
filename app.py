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
if "json_input" not in st.session_state or not isinstance(st.session_state.json_input, str):
    st.session_state.json_input = ""

# --- Sidebar : JSON Input ---
st.sidebar.header("🧩 JSON Input")
json_input = st.sidebar.text_area(
    "Colle ici le JSON produit par le LLM",
    value=st.session_state.json_input,
    height=300,
    placeholder='{"seed_intent":"...","items":[{"id":"it-01",...}]}'
)

# --- Charger JSON ---
def charger_json():
    try:
        data = json.loads(json_input)
        items = data.get("items", [])
        if not isinstance(items, list):
            items = []
        # Forcer chaque item à être dict
        st.session_state.items = [it for it in items if isinstance(it, dict)]
        seed_intent = data.get("seed_intent", "")
        st.session_state.seed_intent = seed_intent if isinstance(seed_intent, str) else ""
        st.session_state.json_input = json_input
        st.success("✅ JSON chargé avec succès !")
    except Exception as e:
        st.error(f"Erreur de parsing JSON : {e}")

st.sidebar.button("🚀 Charger le JSON", on_click=charger_json)

# --- Fonction de suppression ---
def supprimer_item(item_id):
    st.session_state.items = [it for it in st.session_state.items if it.get("id") != item_id]

# --- Préparer items à afficher ---
items_to_display = [it for it in st.session_state.get("items", []) if isinstance(it, dict)]

# --- Affichage des items ---
if items_to_display:
    st.subheader(f"🎯 Intention : {st.session_state.seed_intent}")
    st.write("---")

    for item in items_to_display:
        # Couleur selon priorité
        color = "#cce5ff"
        if item.get("priorite") == "haute":
            color = "#ff9999"
        elif item.get("priorite") == "moyenne":
            color = "#fff799"

        # Carte item
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
                # Checkbox "Garder" lié à session_state
                keep_key = f"keep_{item.get('id','no_id')}"
                if keep_key not in st.session_state:
                    st.session_state[keep_key] = True
                st.session_state[keep_key] = st.checkbox("✅ Garder", value=st.session_state[keep_key], key=keep_key)
            with cols[1]:
                # Bouton "Supprimer"
                if st.button("🗑️ Supprimer", key=f"delete_{item.get('id','no_id')}"):
                    supprimer_item(item.get('id'))
                    st.experimental_rerun = None  # Ne plus utiliser rerun, suppression gérée par session_state

    # --- Export JSON filtré ---
    kept_items = [it for it in st.session_state.items if st.session_state.get(f"keep_{it.get('id','no_id')}", True)]

    st.markdown("### 📦 JSON filtré des items gardés")
    st.json({"seed_intent": st.session_state.seed_intent, "items": kept_items})

    st.download_button(
        label="💾 Télécharger JSON filtré",
        data=json.dumps({"seed_intent": st.session_state.seed_intent, "items": kept_items}, indent=2, ensure_ascii=False),
        file_name="actions_filtrees.json",
        mime="application/json"
    )

else:
    if not st.session_state.json_input.strip():
        st.info("👈 Colle ton JSON dans la sidebar et clique sur 'Charger le JSON'.")
    else:
        st.warning("⚠️ Aucun item à afficher dans le JSON chargé.")

