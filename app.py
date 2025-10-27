import streamlit as st
import json
from datetime import datetime
import uuid

st.set_page_config(page_title="Machine d’action à haut rendement", layout="wide")

st.title("⚙️ Machine d’action à haut rendement")
st.caption("Transforme des intentions floues en actions concrètes, exécutables immédiatement.")

# --- Sidebar : Input JSON ------------------------------------------------
st.sidebar.header("🧩 Charger les items")
json_input = st.sidebar.text_area(
    "Colle ici le JSON produit par le LLM",
    height=250,
    placeholder='{"seed_intent":"...","items":[{"id":"it-01",...}]}'
)

# État persistant
if "items" not in st.session_state:
    st.session_state.items = []
if "filtered_items" not in st.session_state:
    st.session_state.filtered_items = []

# --- Charger le JSON -----------------------------------------------------
if st.sidebar.button("🚀 Charger les actions"):
    try:
        data = json.loads(json_input)
        st.session_state.items = data.get("items", [])
        st.session_state.seed_intent = data.get("seed_intent", "")
        st.session_state.filtered_items = st.session_state.items.copy()
        st.sidebar.success("✅ Actions chargées avec succès !")
    except Exception as e:
        st.sidebar.error(f"Erreur de parsing JSON : {e}")

# --- Zone principale -----------------------------------------------------
if len(st.session_state.filtered_items) == 0:
    st.info("👈 Colle ton JSON à gauche et clique sur *Charger les actions*.")
else:
    st.subheader(f"🎯 Intention : {st.session_state.seed_intent}")
    st.write("---")

    items = st.session_state.filtered_items
    to_delete = []

    # --- Affichage des cartes ------------------------------------------------
    for i, item in enumerate(items):
        with st.container():
            cols = st.columns([0.05, 0.75, 0.2])
            with cols[0]:
                keep = st.checkbox("✅", key=f"keep_{item['id']}", value=True)
            with cols[1]:
                st.markdown(f"### {item['titre']}")
                st.markdown(f"**Description :** {item['description']}")
                st.markdown(f"**Action :** {item['action']}")
                st.markdown(
                    f"**Durée estimée :** {item['temps_estime_min']} min | "
                    f"**Priorité :** {item['priorite'].capitalize()} | "
                    f"**Effort :** {item['niveau_d_effort']}/3"
                )
                if item.get("tags"):
                    st.markdown(f"**Tags :** {' , '.join(item['tags'])}")
                if item.get("suggested_next"):
                    st.caption(f"➡️ *Prochaine micro-action :* {item['suggested_next']}")
            with cols[2]:
                if st.button("🗑️ Supprimer", key=f"delete_{item['id']}"):
                    to_delete.append(item['id'])
            st.divider()

    # --- Traitement suppression --------------------------------------------
    if to_delete:
        st.session_state.filtered_items = [
            it for it in st.session_state.filtered_items if it["id"] not in to_delete
        ]
        st.rerun()

    # --- Résumé ------------------------------------------------------------
    kept_items = [
        it for it in st.session_state.filtered_items
        if st.session_state.get(f"keep_{it['id']}", False)
    ]
    st.markdown("### 📦 Résumé des actions sélectionnées")
    st.write(f"- Total : {len(items)} items")
    st.write(f"- Sélectionnés : {len(kept_items)} items")

    if st.button("💾 Exporter les actions gardées en JSON"):
        output = {
            "seed_intent": st.session_state.seed_intent,
            "exported_at": datetime.now().isoformat(),
            "items": kept_items
        }
        st.download_button(
            label="📥 Télécharger le JSON filtré",
            data=json.dumps(output, indent=2, ensure_ascii=False),
            file_name=f"actions_filtrees_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
