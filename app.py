import streamlit as st
import json

st.set_page_config(page_title="Machine d’action à haut rendement", layout="wide")

st.title("⚙️ Machine d’action à haut rendement")

st.write("Colle ci-dessous la sortie JSON du LLM :")

# Champ texte pour coller le JSON
json_input = st.text_area("Entrée JSON", height=250, placeholder='Colle ici le JSON produit par le modèle...')

# Bouton pour traiter
if st.button("Traiter"):
    try:
        # Vérifie que le module json n’a pas été écrasé
        import json as json_lib
        data = json_lib.loads(json_input)

        st.success("✅ JSON valide et chargé avec succès !")

        # Conteneur pour les catégories (actions, livrables, etc.)
        for key, items in data.items():
            if not isinstance(items, list):
                continue

            st.subheader(f"📂 {key.capitalize()}")

            # Crée une colonne par 2 pour la lisibilité
            cols = st.columns(2)

            for i, item in enumerate(items):
                col = cols[i % 2]
                with col:
                    st.markdown("---")
                    with st.container():
                        # Checkbox pour marquer comme fait
                        checked = st.checkbox(f"✅ {item.get('intitule', item.get('titre', f'Item {i+1}'))}", key=f"{key}_{i}")

                        # Affichage des champs clés/valeurs
                        for k, v in item.items():
                            if k not in ["intitule", "titre"]:
                                st.markdown(f"**{k.capitalize()}** : {v}")

                        # Bouton pour supprimer
                        if st.button("🗑️ Supprimer", key=f"delete_{key}_{i}"):
                            data[key].pop(i)
                            st.rerun()

        # Affichage du JSON mis à jour (après suppression éventuelle)
        st.markdown("### 📤 JSON mis à jour")
        st.code(json.dumps(data, indent=2, ensure_ascii=False))

    except Exception as e:
        st.error(f"❌ Erreur de parsing JSON : {e}")

# Message d’aide
st.markdown("---")
st.info("💡 Conseil : vérifie que ton JSON commence par `{` et qu’il est bien formé.")
