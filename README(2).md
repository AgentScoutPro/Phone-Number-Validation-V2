# Phone Number Validator App

A Streamlit application that validates phone numbers with enhanced mobile number detection.

## Installation

1. First, install the required dependencies:
```bash
pip install -r requirements.txt
```

OR

```bash
chmod +x install.sh
./install.sh
```

2. Run the Streamlit app:
```bash
streamlit run phone_validator_app.py
```

## Features
- Accurate mobile number identification
- Phone number validation with detailed analysis
- Line Type Detection (Mobile, Landline, VOIP, Toll-Free)
- Carrier Information
- Location Detection
- Confidence Scoring
- Excel file upload support
- CSV export functionality

## Troubleshooting

If you encounter ModuleNotFoundError:

1. Make sure you have Python 3.8 or higher installed:
```bash
python --version
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Try running the app again:
```bash
streamlit run phone_validator_app.py
```

## Required Files
- phone_validator_app.py (main application)
- requirements.txt (dependencies)
- setup.py (installation configuration)
- install.sh (installation script)

## Output Format
The validation results include:
- Formatted Number (International format)
- Valid (True/False)
- Line Type (Mobile, Landline, VOIP, etc.)
- Is Mobile (True/False)
- Carrier
- Location
- Timezone
- Confidence Score

## Requirements
Python 3.8 or higher
See requirements.txt for specific version dependencies.
