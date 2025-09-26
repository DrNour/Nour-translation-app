import streamlit as st

# Make sure the correct package is installed
try:
    from comet import download_model, load_from_checkpoint
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call(["pip", "install", "unbabel-comet>=2.2.7"])
    from comet import download_model, load_from_checkpoint

@st.cache_resource(show_spinner=True)
def load_comet(model_name="wmt21-comet-qe-da"):
    """
    Load a COMET model for translation evaluation.
    
    Parameters:
        model_name (str): COMET model identifier.
        
    Returns:
        comet_model: The loaded COMET model object.
    """
    try:
        # Try to load from checkpoint if cached
        model = load_from_checkpoint(model_name)
    except Exception:
        # Download model if checkpoint not found
        download_model(model_name)
        model = load_from_checkpoint(model_name)
    return model
