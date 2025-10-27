import streamlit as st
import json

# --- Config page ---
st.set_page_config(page_title="Machine d'action à haut rendement", layout="wide")

# --- Initialisation sécurisée du session_state ---
def init_state():
    defaults = {
        "items": [],
        "seed_intent": "",
        "json_input": "",
        "kept_items": set(),
        "loaded": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# --- Header ---
st.title("⚙️ Machine d'action à haut rendement")
st.markdown("*Transforme le JSON du LLM en interface actionnable*")

# --- Sidebar : JSON Input ---
with st.sidebar:
    st.header("🧩 Chargement JSON")
    
    json_input = st.text_area(
        "Colle le JSON produit par le LLM",
        value=st.session_state.json_input,
        height=400,
        placeholder='{"seed_intent":"...","items":[...],"summary":"..."}'
    )
    
    if st.button("🚀 Charger le JSON", type="primary", use_container_width=True):
        if not json_input.strip():
            st.error("❌ Le champ JSON est vide")
        else:
            try:
                data = json.loads(json_input)
                
                # Validation du format
                if "items" not in data or not isinstance(data["items"], list):
                    st.error("❌ Format invalide : 'items' manquant ou pas une liste")
                else:
                    # Filtrer items valides (avec ID)
                    valid_items = [
                        item for item in data["items"] 
                        if isinstance(item, dict) and "id" in item
                    ]
                    
                    if not valid_items:
                        st.warning("⚠️ Aucun item valide trouvé (vérifiez les 'id')")
                    else:
                        # Mise à jour du state
                        st.session_state.items = valid_items
                        st.session_state.seed_intent = data.get("seed_intent", "")
                        st.session_state.json_input = json_input
                        st.session_state.kept_items = {item["id"] for item in valid_items}
                        st.session_state.loaded = True
                        
                        st.success(f"✅ {len(valid_items)} items chargés")
                        st.rerun()
                        
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON invalide : {str(e)[:100]}")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)[:100]}")
    
    # Stats
    if st.session_state.loaded:
        st.divider()
        st.metric("Items chargés", len(st.session_state.items))
        st.metric("Items gardés", len(st.session_state.kept_items))

# --- Zone principale ---
if not st.session_state.loaded:
    st.info("👈 **Colle ton JSON dans la sidebar** et clique sur 'Charger le JSON'")
    
    with st.expander("📖 Format JSON attendu"):
        st.code('''
{
  "seed_intent": "Lancer le produit X",
  "items": [
    {
      "id": "it-01",
      "titre": "Rédiger pitch deck",
      "description": "Créer 10 slides...",
      "action": "Ouvrir Figma et...",
      "priorite": "haute",
      "effet_attendu": "Deck prêt",
      "temps_estime_min": 60,
      "niveau_d_effort": "2",
      "tags": ["quick-win"],
      "suggested_next": "Contacter designer"
    }
  ]
}
        ''', language="json")

else:
    # Affichage de l'intention
    st.subheader(f"🎯 {st.session_state.seed_intent}")
    st.divider()
    
    # Affichage des items
    for idx, item in enumerate(st.session_state.items):
        item_id = item["id"]
        
        # Définir la couleur selon priorité
        priorite = item.get("priorite", "basse").lower()
        color_map = {
            "haute": "#ffcdd2",    # Rouge clair
            "moyenne": "#fff9c4",   # Jaune clair
            "basse": "#e1f5fe"      # Bleu clair
        }
        bg_color = color_map.get(priorite, "#f5f5f5")
        
        # Container pour chaque item
        with st.container():
            # Card HTML
            st.markdown(f"""
                <div style='
                    background-color: {bg_color};
                    border-left: 4px solid {"#d32f2f" if priorite == "haute" else "#fbc02d" if priorite == "moyenne" else "#0288d1"};
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 15px;
                '>
                    <h3 style='margin:0 0 10px 0; color: #1a1a1a;'>{item.get('titre', 'Sans titre')}</h3>
                    <p style='margin: 5px 0;'><strong>📝 Description :</strong> {item.get('description', 'N/A')}</p>
                    <p style='margin: 5px 0;'><strong>⚡ Action :</strong> {item.get('action', 'N/A')}</p>
                    <p style='margin: 5px 0;'><strong>🎯 Effet attendu :</strong> {item.get('effet_attendu', 'N/A')}</p>
                    <p style='margin: 5px 0;'>
                        <strong>⏱️ Temps estimé :</strong> {item.get('temps_estime_min', 'N/A')} min | 
                        <strong>💪 Effort :</strong> {item.get('niveau_d_effort', 'N/A')}/3
                    </p>
                    <p style='margin: 5px 0;'><strong>🏷️ Tags :</strong> {', '.join(item.get('tags', [])) if item.get('tags') else 'Aucun'}</p>
                    <p style='margin: 5px 0; color: #666;'><em>➡️ Prochaine action : {item.get('suggested_next', 'N/A')}</em></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Contrôles
            col1, col2, col3 = st.columns([1, 1, 6])
            
            with col1:
                is_kept = item_id in st.session_state.kept_items
                keep = st.checkbox(
                    "✅ Garder",
                    value=is_kept,
                    key=f"keep_{item_id}_{idx}"
                )
                if keep and not is_kept:
                    st.session_state.kept_items.add(item_id)
                elif not keep and is_kept:
                    st.session_state.kept_items.discard(item_id)
            
            with col2:
                if st.button("🗑️ Supprimer", key=f"del_{item_id}_{idx}"):
                    st.session_state.items = [
                        it for it in st.session_state.items 
                        if it["id"] != item_id
                    ]
                    st.session_state.kept_items.discard(item_id)
                    st.rerun()
    
    # Export
    st.divider()
    st.subheader("📦 Export JSON filtré")
    
    kept_items = [
        item for item in st.session_state.items 
        if item["id"] in st.session_state.kept_items
    ]
    
    if kept_items:
        export_data = {
            "seed_intent": st.session_state.seed_intent,
            "items": kept_items
        }
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.json(export_data, expanded=False)
        with col2:
            st.download_button(
                label="💾 Télécharger",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name="actions_filtrees.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.warning("⚠️ Aucun item sélectionné pour l'export")
    
    # Bouton reset
    if st.button("🔄 Réinitialiser tout", type="secondary"):
        for key in ["items", "seed_intent", "json_input", "kept_items", "loaded"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
