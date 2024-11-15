# Phone Number Validator App

A Streamlit application that validates phone numbers with enhanced mobile number detection.

## Features
- Accurate mobile number identification
- Phone number validation with detailed analysis
- Line Type Detection (Mobile, Landline, VOIP, Toll-Free)
- Carrier Information
- Location Detection
- Confidence Scoring
- Excel file upload support
- CSV export functionality

## Required Files
- phone_validator_app.py (main application)
- requirements.txt (dependencies)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
1. Upload an Excel file containing phone numbers
2. Select the column containing phone numbers
3. Click 'Validate Numbers'
4. View results and download validated data

## Mobile Number Detection
The app now includes enhanced mobile number detection:
- Explicit identification of mobile numbers
- Additional verification using area code analysis
- Clear separation between mobile and landline numbers
- New 'Is Mobile' column in results

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
See requirements.txt for specific version dependencies.
