import streamlit as st
import json

# --- Config page ---
st.set_page_config(page_title="Machine d'action à haut rendement", layout="wide")
st.title("⚙️ Machine d'action à haut rendement")

# --- Initialisations sécurisées ---
if "items" not in st.session_state:
    st.session_state.items = []
if "seed_intent" not in st.session_state:
    st.session_state.seed_intent = ""
if "json_input" not in st.session_state:
    st.session_state.json_input = ""
if "kept_items" not in st.session_state:
    st.session_state.kept_items = set()

# --- Sidebar : JSON Input ---
st.sidebar.header("🧩 JSON Input")
json_input = st.sidebar.text_area(
    "Colle ici le JSON produit par le LLM",
    value=st.session_state.json_input,
    height=300,
    placeholder='{"seed_intent":"...","items":[{"id":"it-01",...}]}'
)

# --- Charger JSON ---
if st.sidebar.button("🚀 Charger le JSON"):
    try:
        data = json.loads(json_input)
        items = data.get("items", [])
        if not isinstance(items, list):
            items = []
        # Filtrer et valider les items
        valid_items = [it for it in items if isinstance(it, dict) and "id" in it]
        st.session_state.items = valid_items
        
        seed_intent = data.get("seed_intent", "")
        st.session_state.seed_intent = seed_intent if isinstance(seed_intent, str) else ""
        st.session_state.json_input = json_input
        
        # Initialiser tous les items comme "gardés" par défaut
        st.session_state.kept_items = {it["id"] for it in valid_items}
        
        st.sidebar.success("✅ JSON chargé avec succès !")
    except Exception as e:
        st.sidebar.error(f"Erreur de parsing JSON : {e}")

# --- Affichage des items ---
if st.session_state.items:
    st.subheader(f"🎯 Intention : {st.session_state.seed_intent}")
    st.write("---")

    for item in st.session_state.items:
        item_id = item.get("id", "no_id")
        
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

            cols = st.columns([0.15, 0.15, 0.7])
            
            with cols[0]:
                # Checkbox "Garder"
                is_kept = item_id in st.session_state.kept_items
                if st.checkbox("✅ Garder", value=is_kept, key=f"keep_{item_id}"):
                    st.session_state.kept_items.add(item_id)
                else:
                    st.session_state.kept_items.discard(item_id)
            
            with cols[1]:
                # Bouton "Supprimer"
                if st.button("🗑️ Supprimer", key=f"delete_{item_id}"):
                    st.session_state.items = [it for it in st.session_state.items if it.get("id") != item_id]
                    st.session_state.kept_items.discard(item_id)
                    st.rerun()

    # --- Export JSON filtré ---
    kept_items = [it for it in st.session_state.items if it.get("id") in st.session_state.kept_items]

    st.markdown("---")
    st.markdown("### 📦 JSON filtré des items gardés")
    
    if kept_items:
        st.json({"seed_intent": st.session_state.seed_intent, "items": kept_items})

        st.download_button(
            label="💾 Télécharger JSON filtré",
            data=json.dumps({"seed_intent": st.session_state.seed_intent, "items": kept_items}, indent=2, ensure_ascii=False),
            file_name="actions_filtrees.json",
            mime="application/json"
        )
    else:
        st.info("Aucun item sélectionné pour l'export.")

else:
    if not st.session_state.json_input.strip():
        st.info("👈 Colle ton JSON dans la sidebar et clique sur 'Charger le JSON'.")
    else:
        st.warning("⚠️ Aucun item valide dans le JSON chargé.")
