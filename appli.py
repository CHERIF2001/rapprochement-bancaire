import streamlit as st
import pandas as pd
import os
import tempfile
import shutil
from PIL import Image
import main

# Configuration
st.set_page_config(page_title="Bank Reconciliation System", layout="wide")
st.title("💼 Système de Rapprochement Bancaire")

# Session State
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'receipts_dir' not in st.session_state:
    st.session_state.receipts_dir = "project/images/receipts"
if 'selected_row' not in st.session_state:
    st.session_state.selected_row = None

# CSS personnalisé
st.markdown("""
<style>
    .stSelectbox div[data-baseweb="select"] {
        margin-bottom: 20px;
    }
    .stImage img {
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def safe_display_columns(df, default_columns):
    """Sélectionne uniquement les colonnes disponibles"""
    available_columns = [col for col in default_columns if col in df.columns]
    return df[available_columns]

# Interface principale
tab1, tab2 = st.tabs(["Rapprochement", "Recherche de Factures"])

with tab1:
    st.header("Rapprochement Bancaire")
    
    # Méthode d'import
    import_method = st.radio("Source des données", ["Dossier local", "Upload de fichiers"])
    
    if import_method == "Dossier local":
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.receipts_dir = st.text_input("Dossier des factures", st.session_state.receipts_dir)
        with col2:
            statements_dir = st.text_input("Dossier des relevés", "project/bank_statements")
    else:
        col1, col2 = st.columns(2)
        with col1:
            uploaded_receipts = st.file_uploader("Factures (images)", 
                                              type=["jpg", "jpeg", "png"], 
                                              accept_multiple_files=True)
        with col2:
            uploaded_statements = st.file_uploader("Relevés bancaires (CSV)", 
                                                type=["csv"], 
                                                accept_multiple_files=True)

    # Bouton d'exécution
    if st.button("Exécuter le rapprochement", type="primary"):
        temp_dir = None
        try:
            if import_method == "Upload de fichiers" and (uploaded_receipts or uploaded_statements):
                temp_dir = tempfile.mkdtemp()
                receipts_path = os.path.join(temp_dir, "receipts")
                statements_path = os.path.join(temp_dir, "statements")
                
                if uploaded_receipts:
                    receipts_path = save_uploaded_files(uploaded_receipts, receipts_path)
                if uploaded_statements:
                    statements_path = save_uploaded_files(uploaded_statements, statements_path)
            else:
                receipts_path = st.session_state.receipts_dir
                statements_path = statements_dir

            if not os.path.exists(receipts_path):
                st.error(f"Dossier introuvable: {receipts_path}")
            elif not os.path.exists(statements_path):
                st.error(f"Dossier introuvable: {statements_path}")
            else:
                with st.spinner("Analyse en cours..."):
                    output_csv = "rapprochement_results.csv"
                    main.main(receipts_path, statements_path, "project/doc_json", output_csv)
                    
                    if os.path.exists(output_csv):
                        st.session_state.results_df = pd.read_csv(output_csv)
                        st.success(f"Analyse terminée ({len(st.session_state.results_df)} transactions)")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    # Affichage des résultats
    if st.session_state.results_df is not None:
        st.subheader("Résultats du rapprochement")
        
        # Colonnes à afficher par défaut
        default_columns = ['vendor', 'amount', 'date', 'similarity_score']
        display_columns = [col for col in default_columns if col in st.session_state.results_df.columns]
        
        # Tableau compact
        st.dataframe(
            st.session_state.results_df[display_columns],
            height=300,
            use_container_width=True,
            hide_index=True
        )
        
        # Sélection de ligne
        if not st.session_state.results_df.empty:
            selected_idx = st.selectbox(
                "Sélectionnez une transaction pour voir les détails",
                range(len(st.session_state.results_df)),
                format_func=lambda x: (
                    f"{st.session_state.results_df.iloc[x].get('vendor', 'N/A')} | "
                    f"{st.session_state.results_df.iloc[x].get('amount', 'N/A')}€ | "
                    f"{st.session_state.results_df.iloc[x].get('date', 'N/A')}"
                )
            )
            
            # Détails de la transaction
            if selected_idx is not None:
                st.divider()
                row = st.session_state.results_df.iloc[selected_idx]
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    img_path = row.get('image_path', '')
                    if img_path and os.path.exists(img_path):
                        st.image(Image.open(img_path), width=350)
                    else:
                        st.warning("Image non disponible")
                
                with col2:
                    st.subheader("Détails de la transaction")
                    st.json({
                        "Fournisseur": row.get('vendor', 'N/A'),
                        "Montant": row.get('amount', 'N/A'),
                        "Date": row.get('date', 'N/A'),
                        "Score de similarité": row.get('similarity_score', 'N/A'),
                        "Fichier source": row.get('csv_file', 'N/A')
                    })

with tab2:
    st.header("Recherche de Factures")
    
    col1, col2 = st.columns(2)
    with col1:
        results_file = st.file_uploader("Fichier de résultats (.csv)", type=["csv"])
    with col2:
        search_image_dir = st.text_input("Dossier des images", st.session_state.receipts_dir)
    
    if st.button("Rechercher les factures"):
        if results_file and search_image_dir:
            with st.spinner("Recherche en cours..."):
                temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                try:
                    temp_csv.write(results_file.getvalue())
                    temp_csv.close()
                    
                    matches = main.search_receipts(temp_csv.name, search_image_dir)
                    
                    if matches:
                        st.session_state.results_df = pd.DataFrame(matches)
                        st.success(f"{len(matches)} factures trouvées")
                    else:
                        st.warning("Aucune correspondance trouvée")
                finally:
                    os.unlink(temp_csv.name)
        else:
            st.error("Veuillez sélectionner un fichier et un dossier d'images")
    
    if st.session_state.results_df is not None and not st.session_state.results_df.empty:
        st.subheader("Résultats de la recherche")
        
        selected_idx = st.selectbox(
            "Sélectionnez une facture",
            range(len(st.session_state.results_df)),
            key="search_select",
            format_func=lambda x: (
                f"{st.session_state.results_df.iloc[x].get('vendor', 'N/A')} | "
                f"{st.session_state.results_df.iloc[x].get('amount', 'N/A')}€"
            )
        )
        
        if selected_idx is not None:
            selected = st.session_state.results_df.iloc[selected_idx]
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if 'image_path' in selected and os.path.exists(selected['image_path']):
                    st.image(Image.open(selected['image_path']), width=350)
                    st.download_button(
                        "Télécharger l'image",
                        open(selected['image_path'], "rb").read(),
                        file_name=os.path.basename(selected['image_path']),
                        mime="image/jpeg"
                    )
                else:
                    st.warning("Image non trouvée")
            
            with col2:
                st.json({k: v for k, v in selected.items() if k != 'image_path'})