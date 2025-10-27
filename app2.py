import streamlit as st
import streamlit.components.v1 as components
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

# Template du prompt
PROMPT_TEMPLATE = """Tu es une MACHINE D'ACTION À HAUT RENDEMENT. 
Ta mission : à partir d'une **intention stratégique, même très vague ou symbolique**, générer **exclusivement** une liste d'items d'action concrets, granularisés et prêts à exécution. 
Ne génère **pas** de texte stratégique, pas de métaphores, pas d'analyse philosophique — produis uniquement des éléments opérationnels.
 
CONTRAINTES FORTE : 
1. Si l'intention est vide ou vague, considère qu'il faut *partir du néant* et produire matière opérationnelle.
2. **Ne crée pas** automatiquement de mails, réunions ou autres communications, sauf si l'entrée demande explicitement "préparer un mail", "fixer une réunion" ou équivalent. Dans ce cas, crée un item d'action spécifique pour l'envoi ou la planification (toujours comme item).
3. Chaque item doit être **exécutable immédiatement** (action claire, verbe d'exécution, résultat attendu).
4. Toutes les sorties doivent être en **JSON strict** selon le schéma ci-dessous.
5. Langage : français. Style : direct, impératif, sans verbes mous.
 
FORMAT DE SORTIE (strict JSON) :
{
  "seed_intent": "string (texte brut reçu)",
  "items": [
    {
      "id": "string court unique",
      "titre": "string (titre accrocheur et exécutif)",
      "description": "string (1-2 phrases décrivant l'action exacte à réaliser)",
      "action": "string (verbe direct + objet, ex: 'rédiger un mail de 5 lignes à...')",
      "priorite": "haute | moyenne | basse",
      "effet_attendu": "string (résultat concret attendu après exécution)",
      "temps_estime_min": integer,
      "niveau_d_effort": "1 | 2 | 3",
      "dependances": ["id1", "id2"] | [],
      "tags": ["string", ...],
      "statut_suggere": "à faire | en cours | bloqué | fait",
      "suggested_next": "string (prochaine micro-action si applicable)"
    }
  ],
  "summary": "string (2-3 phrases maximum, récapitulatif factuel du nombre d'items et des quick wins)"
}
 
RÈGLES OPÉRATIONNELLES :
- GÉNÈRE au moins **6 items** par intention (sauf si l'entrée demande explicitement moins), dont **2 quick-wins** exécutables en ≤ 15 minutes.
- Varie la granularité : mêle micro-actions (5–15 min) et petites tâches (30–90 min). Indique `temps_estime_min`.
- Pour chaque item, fournis une **prochaine petite étape** claire dans `suggested_next` (exécutée en ≤ 10 min).
- DON'T: n'écris jamais "voir", "penser", "réfléchir". Écris : "contacter X", "rédiger", "tester", "mettre en ligne", etc.
- Si l'intention contient un mot-clé explicite (ex: "client", "roadmap", "recrutement"), ajoute le tag correspondant.
- Génère des `id` courts (format `it-01`, `it-02`, ...).
 
ENTRÉE (insérée ici) :
"""

# --- Sidebar : Génération ---
st.sidebar.header("🚀 Générer des actions")
user_input = st.sidebar.text_area("Quelle est ton intention ?", height=150, placeholder="Ex: Lancer mon produit SaaS, préparer la réunion client...")

if st.sidebar.button("🤖 Push LLM", type="primary"):
    # Construire le prompt complet : template + input utilisateur
    full_prompt = PROMPT_TEMPLATE + user_input
    prompt_json = json.dumps(full_prompt)
    
    js_code = f"""
    <script>
        const promptText = {prompt_json};
        navigator.clipboard.writeText(promptText).then(function() {{
            console.log('Prompt copié !');
        }});
        window.open('https://chatgpt.com/', '_blank');
    </script>
    """
    components.html(js_code, height=0)
    st.sidebar.success("✅ Prompt copié ! ChatGPT s'ouvre...")

st.sidebar.divider()

# --- Sidebar : Chargement JSON ---
st.sidebar.header("🧩 Charger JSON")
json_text = st.sidebar.text_area("Colle le JSON de retour ici", height=300)

if st.sidebar.button("📥 Charger"):
    try:
        data = json.loads(json_text)
        st.session_state["data"] = data
        st.session_state["items"] = data.get("items", [])
        st.sidebar.success("✅ Chargé !")
    except Exception as e:
        st.sidebar.error(f"Erreur : {e}")

# --- Affichage ---
if "data" not in st.session_state:
    st.info("👆 Utilise la sidebar pour générer ou charger des actions")
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
        "haute": "#8b0000",
        "moyenne": "#b8860b",
        "basse": "#1e3a5f"
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
