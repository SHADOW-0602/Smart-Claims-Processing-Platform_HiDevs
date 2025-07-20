# AI-Powered Insurance Claims Automation

A Streamlit-based web application that automates the processing of insurance claim forms by analyzing uploaded images. The system extracts key information (e.g., policy number, claim value), classifies the claim type and priority, checks for policy compliance, and determines the optimal workflow routing path using configurable rules.

## Features
- **Document Processing**: Extracts text and entities (e.g., policy number, claim value, names, dates) from claim form images using Tesseract OCR and spaCy with image preprocessing.
- **Claim Classification**: Uses a Naive Bayes classifier with TF-IDF vectorization to predict claim type (e.g., auto, property, health) and assign priority.
- **Policy Compliance Check**: Validates claims against a configurable policy database in `config.json`.
- **Intelligent Routing**: Routes claims to workflows (e.g., manual review, auto-deny, senior adjuster, straight-through processing) based on rules in `config.json`.
- **Interactive UI**: Built with Streamlit, featuring image display, a detailed progress bar, and results in an expandable format.
- **Robustness**: Includes logging, error handling, file size validation (max 5MB), format validation, and caching of the pipeline and spaCy model.
- **Security**: Uses `python-magic` for file type validation and secure temporary file handling.
- **GitHub Codespaces Support**: Optimized for Codespaces with Tesseract OCR installation and port forwarding instructions.

## Prerequisites
- Python 3.8+
- Streamlit
- Pillow (PIL)
- pytesseract
- spaCy
- scikit-learn
- pandas
- numpy
- python-magic
- Tesseract OCR (installed in Codespaces via `apt`)

## Installation
### In GitHub Codespaces
1. Open your repository in GitHub Codespaces:
   - Click "Code" > "Create codespace on main" (or your branch).
2. Install Tesseract OCR:
   ```bash
   sudo apt update
   sudo apt install -y tesseract-ocr
   ```
3. Verify Tesseract:
   ```bash
   tesseract --version
   ```
4. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
5. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Install the spaCy model:
   ```bash
   python3 -m spacy download en_core_web_sm
   ```
7. Ensure `config.py` and `config.json` are in the project root with appropriate settings.

### On Local Machine
Follow steps 4–6 above, and install Tesseract OCR:
- **Linux/macOS**: `sudo apt install tesseract-ocr` (Ubuntu) or `brew install tesseract` (macOS).
- **Windows**: Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.

## Usage
1. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```
2. In GitHub Codespaces:
   - Open the "Ports" tab, locate port 8501, and set it to "Public" visibility.
   - Copy the URL (e.g., `https://<codespace-name>-8501.app.github.dev`) and open it in a browser.
3. On a local machine, access at `http://localhost:8501`.
4. Upload a claim form image (PNG, JPG, JPEG; max 5MB).
5. The app will process the image, showing progress for each stage (text extraction, classification, compliance, routing) and display:
   - The uploaded image.
   - A final routing decision (e.g., “Route to Senior Adjuster”) with reasoning.
   - Detailed results in an expander (extracted data, classification, compliance).
6. Use the `samples/` directory for example claim form images (e.g., `sample_claim.jpg`).

## Project Structure
- `streamlit_app.py`: Main application with Streamlit UI, file upload handling, and pipeline orchestration.
- `pipeline.py`: Orchestrates the claims processing pipeline.
- `document_processor.py`: Extracts text and entities from images using Tesseract OCR and a cached spaCy model.
- `claim_classifier.py`: Trains and applies a Naive Bayes classifier for claim type and priority.
- `compliance_checker.py`: Checks claim compliance against a configurable policy database.
- `workflow_router.py`: Determines the workflow path based on rules in `config.json`.
- `config.py`: Defines the spaCy model.
- `config.json`: Configures policy database, training data, and routing rules.
- `requirements.txt`: Lists Python dependencies.
- `temp/`: Temporary directory for uploaded files (created automatically). In Codespaces, uses `/workspaces/temp`.
- `samples/`: Directory for sample claim form images (create manually).

## Example
1. Upload a claim form image with text like “Policy No: PN-AUTO-12345, Claim Amount: $5,000, Description: Car accident on the highway”.
2. The app will:
   - Extract entities (e.g., `POLICY_NO: PN-AUTO-12345`, `CLAIM_VALUE: 5000.0`).
   - Classify the claim as `auto` with a confidence score (e.g., 0.85) and priority (e.g., Medium).
   - Check compliance (e.g., confirm “collision” is covered).
   - Route the claim (e.g., “Route to General Claims Queue”).
3. Results are displayed with a progress bar, final decision, and detailed breakdowns.

## Configuration
Modify `config.py` and `config.json`:
- `config.py`:
  - `SPACY_MODEL`: Specify the spaCy model (default: `en_core_web_sm`).
- `config.json`:
  - `policy_db`: Update policy database with coverage and exclusions.
  - `training_data`: Expand dataset for the classifier.
  - `routing_rules`: Define rules (e.g., `high_value_threshold`, `stp_threshold`).
  - `confidence_threshold`: Minimum confidence for automated routing (default: 0.75).

## Troubleshooting
If you encounter `ERROR - File handling error: argument 2: TypeError: wrong type`:
1. Check the terminal logs for details (e.g., file buffer type, file path).
2. Verify Streamlit version:
   ```bash
   pip show streamlit
   ```
   Ensure it’s 1.38.0; upgrade if needed:
   ```bash
   pip install streamlit==1.38.0
   ```
3. Verify `python-magic`:
   ```bash
   python -c "import magic; print(magic.__version__)"
   ```
   Reinstall if needed:
   ```bash
   pip install python-magic==0.4.27
   ```
4. Test with a sample image in `samples/` (e.g., `sample_claim.jpg` with text like “Policy No: PN-AUTO-12345, Claim Amount: $5,000”).
5. Ensure Tesseract is installed:
   ```bash
   tesseract --version
   ```
6. If the error persists, share the full log output in the Codespaces terminal.

## Limitations
- The classifier uses a simple Naive Bayes model with mock training data, which may not generalize well.
- OCR performance depends on image quality; preprocessing helps but may fail for blurry images.
- The mock `policy_db` in `config.json` is simplified; replace with a real database in production.
- Limited to PNG, JPG, JPEG images; consider adding PDF support.
- No malicious file scanning; add for production use.

## Future Improvements
- Add unit and integration tests with `pytest`.
- Implement malicious file scanning (e.g., using `clamav`).
- Use a more advanced NLP model (e.g., BERT) for classification.
- Integrate a real database (e.g., SQLite, PostgreSQL).
- Add PDF claim form support and batch processing.
- Enhance OCR with additional preprocessing techniques.
- Develop a FastAPI endpoint for programmatic access.
- Add a Streamlit UI for editing `config.json`.

## Testing
- Create a `samples/` directory with images like `sample_claim.jpg` containing text such as “Policy No: PN-AUTO-12345, Claim Amount: $5,000, Description: Car accident”.
- Test with diverse images (different lighting, formats) to ensure robustness.
- Implement `pytest` tests for each module (to be added).

## License
This project is licensed under the MIT License.