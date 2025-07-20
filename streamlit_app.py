import streamlit as st
from PIL import Image
import os
import logging
import magic
from pipeline import ClaimsPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AI Claims Automation",
    page_icon="📄",
    layout="wide"
)

# --- File Size and Format Limits ---
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FORMATS = {'image/png', 'image/jpeg', 'image/jpg'}

# --- Caching the Pipeline Initialization ---
@st.cache_resource
def load_pipeline():
    """Load and cache the claims processing pipeline."""
    try:
        return ClaimsPipeline()
    except Exception as e:
        st.error(f"Failed to initialize the processing pipeline: {e}")
        logging.error(f"Pipeline initialization failed: {e}")
        return None

# --- Main Application UI ---
st.title("📄 AI-Powered Insurance Claims Automation")
st.markdown("""
Upload an insurance claim form image (PNG, JPG, JPEG) to automatically process it. 
The system will extract key information, classify the claim, check for policy compliance, and determine the optimal routing path.
""")

# Load the processing pipeline
pipeline = load_pipeline()

if pipeline:
    # File uploader widget
    uploaded_file = st.file_uploader("Choose a claim form image...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        try:
            # Validate file size
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error(f"File exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB limit.")
                raise ValueError("File size too large")
            else:
                # Validate file type using python-magic
                file_buffer = uploaded_file.read()  # Read as bytes
                logging.info(f"Uploaded file: {uploaded_file.name}, type: {type(file_buffer)}, size: {len(file_buffer)}")
                file_type = magic.from_buffer(file_buffer, mime=True)
                if file_type not in ALLOWED_FORMATS:
                    st.error(f"Unsupported file format: {file_type}. Supported formats: PNG, JPG, JPEG.")
                    raise ValueError(f"Unsupported file format: {file_type}")
                
                # Adjust temp directory for Codespaces
                temp_dir = "/workspaces/temp" if os.getenv("CODESPACES") else "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir, mode=0o755)  # Ensure directory is writable
                    logging.info(f"Created temp directory: {temp_dir}")
                
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                # Save the uploaded file
                try:
                    with open(file_path, "wb") as f:
                        f.write(file_buffer)  # Write bytes directly
                    logging.info(f"File saved to {file_path}")
                except Exception as e:
                    st.error(f"Failed to save file: {e}")
                    logging.error(f"File saving error: {e}, file_path: {file_path}, buffer type: {type(file_buffer)}")
                    raise

                # --- Display Input and Output ---
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Uploaded Claim Form")
                    try:
                        image = Image.open(file_path)
                        st.image(image, caption="Scanned Claim Form", use_column_width=True)
                    except Exception as e:
                        st.error(f"Could not display the image: {e}")
                        logging.error(f"Image display failed: {e}")

                with col2:
                    st.subheader("Processing Results")
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Process the claim with progress updates
                        status_text.text("Extracting text from image...")
                        progress_bar.progress(25)
                        result = pipeline.run(file_path)

                        status_text.text("Classifying claim...")
                        progress_bar.progress(50)
                        status_text.text("Checking compliance...")
                        progress_bar.progress(75)
                        status_text.text("Determining routing...")
                        progress_bar.progress(100)

                        # Display the final routing decision prominently
                        if result.get("status") == "Success":
                            final_decision = result.get("final_routing", {})
                            st.success(f"**Final Decision:** {final_decision.get('decision', 'N/A')}")
                            st.caption(f"**Reason:** {final_decision.get('reason', 'N/A')}")

                            # Display the full result in an expander
                            with st.expander("View Processing Details"):
                                # Extracted Data Section
                                st.subheader("📝 Extracted Data")
                                entities = result.get("extracted_data", {})
                                claim_value = entities.get('CLAIM_VALUE')
                                if claim_value is not None:
                                    st.metric(label="Claim Value", value=f"${claim_value:,.2f}")
                                st.text(f"Policy Number: {entities.get('POLICY_NO', 'Not Found')}")
                                st.text(f"Names: {', '.join(entities.get('PERSON', ['None']))}")
                                st.text(f"Dates: {', '.join(entities.get('DATE', ['None']))}")

                                st.divider()

                                # Classification Section
                                st.subheader("📊 Classification")
                                classification = result.get("classification", {})
                                st.text(f"Predicted Type: {classification.get('type', 'N/A')}")
                                st.text(f"Assigned Priority: {classification.get('priority', 'N/A')}")
                                st.text(f"Confidence Score: {classification.get('confidence', 'N/A')}")

                                st.divider()

                                # Compliance Section
                                st.subheader("✅ Compliance Check")
                                compliance = result.get("compliance", {})
                                if compliance.get('compliant'):
                                    st.success(f"Status: {compliance.get('details', 'Compliant')}")
                                else:
                                    st.warning(f"Status: {compliance.get('details', 'Not Compliant')}")

                        else:
                            st.error(f"**Processing Failed:** {result.get('reason', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Processing failed: {e}")
                        logging.error(f"Processing error: {e}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            logging.error(f"File handling error: {e}, file: {uploaded_file.name if uploaded_file else 'None'}")
        finally:
            # Clean up the temporary file
            if 'file_path' in locals():
                try:
                    os.remove(file_path)
                    logging.info(f"Removed temporary file: {file_path}")
                except Exception as e:
                    logging.warning(f"Could not remove temporary file {file_path}: {e}")

else:
    st.error("The application could not be started. Please check the logs for more details.")

# Clean up temp directory if empty
try:
    temp_dir = "/workspaces/temp" if os.getenv("CODESPACES") else "temp"
    if os.path.exists(temp_dir) and not os.listdir(temp_dir):
        os.rmdir(temp_dir)
except Exception as e:
    logging.warning(f"Could not remove temp directory: {e}")