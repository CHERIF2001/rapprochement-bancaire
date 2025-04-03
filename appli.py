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
if 'clicked_row' not in st.session_state:
    st.session_state.clicked_row = None

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
    .stDataFrame tr:hover {
        background-color: #f5f5f5;
        cursor: pointer;
    }
    .selected-row {
        background-color: #e6f7ff !important;
    }
</style>
""", unsafe_allow_html=True)

def safe_display_columns(df, columns):
    """Sélectionne uniquement les colonnes disponibles"""
    return df[[col for col in columns if col in df.columns]]

def save_uploaded_files(uploaded_files, save_dir):
    """Sauvegarde les fichiers uploadés dans un dossier"""
    os.makedirs(save_dir, exist_ok=True)
    for uploaded_file in uploaded_files:
        with open(os.path.join(save_dir, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
    return save_dir

def load_image(image_path):
    """Charge une image avec vérification du chemin"""
    try:
        if image_path and os.path.exists(image_path):
            return Image.open(image_path)
        return None
    except Exception as e:
        st.error(f"Erreur de chargement de l'image: {str(e)}")
        return None

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
                        st.session_state.clicked_row = None
                        st.success(f"Analyse terminée ({len(st.session_state.results_df)} transactions)")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    # Affichage des résultats
    if st.session_state.results_df is not None:
        st.subheader("Résultats du rapprochement")
        
        # Colonnes spécifiques à afficher
        columns_to_display = ['vendor', 'amount', 'currency', 'date']
        display_df = safe_display_columns(st.session_state.results_df, columns_to_display)
        
        # Afficher le tableau avec sélection de ligne
        selected_rows = st.dataframe(
            display_df,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="dataframe_tab1"
        )
        
        # Gérer la sélection de ligne
        if hasattr(selected_rows, 'selection') and selected_rows.selection:
            selected_indices = selected_rows.selection.rows
            if selected_indices:
                st.session_state.clicked_row = selected_indices[0]
        
        # Afficher l'image sélectionnée
        if st.session_state.clicked_row is not None and st.session_state.clicked_row < len(st.session_state.results_df):
            row = st.session_state.results_df.iloc[st.session_state.clicked_row]
            img_path = row.get('image_path', '')
            img = load_image(img_path)
            
            if img:
                st.divider()
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(img, width=350, caption=os.path.basename(img_path))
                with col2:
                    st.subheader("Détails de la transaction")
                    st.json({
                        "Fournisseur": row.get('vendor', 'N/A'),
                        "Montant": row.get('amount', 'N/A'),
                        "Devise": row.get('currency', 'N/A'),
                        "Date": row.get('date', 'N/A'),
                        "Chemin de l'image": img_path
                    })
            else:
                st.warning(f"Image non disponible ou chemin invalide: {img_path}")

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
                        st.session_state.clicked_row = None
                        st.success(f"{len(matches)} factures trouvées")
                    else:
                        st.warning("Aucune correspondance trouvée")
                finally:
                    os.unlink(temp_csv.name)
        else:
            st.error("Veuillez sélectionner un fichier et un dossier d'images")
    
    if st.session_state.results_df is not None and not st.session_state.results_df.empty:
        st.subheader("Résultats de la recherche")
        
        # Colonnes spécifiques à afficher
        columns_to_display = ['vendor', 'amount', 'currency', 'date']
        display_df = safe_display_columns(st.session_state.results_df, columns_to_display)
        
        # Afficher le tableau avec sélection de ligne
        selected_rows = st.dataframe(
            display_df,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="dataframe_tab2"
        )
        
        # Gérer la sélection de ligne
        if hasattr(selected_rows, 'selection') and selected_rows.selection:
            selected_indices = selected_rows.selection.rows
            if selected_indices:
                st.session_state.clicked_row = selected_indices[0]
        
        # Afficher l'image sélectionnée
        if st.session_state.clicked_row is not None and st.session_state.clicked_row < len(st.session_state.results_df):
            selected = st.session_state.results_df.iloc[st.session_state.clicked_row]
            img_path = selected.get('image_path', '')
            img = load_image(img_path)
            
            if img:
                st.divider()
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(img, width=350, caption=os.path.basename(img_path))
                with col2:
                    st.subheader("Détails de la facture")
                    st.json({k: v for k, v in selected.items() if k != 'image_path'})
            else:
                st.warning(f"Image non disponible ou chemin invalide: {img_path}")