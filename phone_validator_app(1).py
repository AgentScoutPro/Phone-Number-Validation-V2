
import streamlit as st
import pandas as pd
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from phonenumbers.phonenumberutil import PhoneNumberType

# Function to determine line type based on prefix patterns
def determine_line_type(number):
    line_type = phonenumbers.number_type(number)
    if line_type == PhoneNumberType.MOBILE:
        return 'Cell'
    elif line_type == PhoneNumberType.FIXED_LINE:
        return 'Landline'
    elif line_type == PhoneNumberType.VOIP:
        return 'VOIP'
    elif line_type == PhoneNumberType.TOLL_FREE:
        return 'Toll-Free'
    elif line_type == PhoneNumberType.UNKNOWN:
        return 'International'
    else:
        return 'Invalid/Fake'

# Function to calculate confidence score (mock implementation)
def calculate_confidence(number):
    # This is a placeholder for a real confidence score calculation
    # For demonstration, we return a random score between 0.8 and 1.0 for valid numbers
    import random
    return random.uniform(0.8, 1.0) if phonenumbers.is_valid_number(number) else 0.0

# Main validation function
def validate_phone(phone_number):
    try:
        number = phonenumbers.parse(phone_number)
        is_valid = phonenumbers.is_valid_number(number)
        if is_valid:
            line_type = determine_line_type(number)
            confidence = calculate_confidence(number)
            return {
                'valid': True,
                'carrier': carrier.name_for_number(number, "en"),
                'location': geocoder.description_for_number(number, "en"),
                'timezone': timezone.time_zones_for_number(number),
                'line_type': line_type,
                'confidence': confidence
            }
        return {'valid': False, 'line_type': 'Invalid/Fake', 'confidence': 0.0}
    except:
        return {'valid': False, 'line_type': 'Invalid/Fake', 'confidence': 0.0}

st.title('Phone Number Validator')

# File upload
uploaded_file = st.file_uploader("Upload Excel file with phone numbers", type=['xlsx', 'xls'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    phone_col = st.selectbox('Select phone number column', df.columns)
    
    if st.button('Validate Numbers'):
        results = []
        progress = st.progress(0)
        
        for i, number in enumerate(df[phone_col]):
            result = validate_phone(str(number))
            results.append(result)
            progress.progress((i + 1) / len(df))
        
        # Add results to dataframe
        df['Valid'] = [r['valid'] for r in results]
        df['Carrier'] = [r.get('carrier', '') for r in results]
        df['Location'] = [r.get('location', '') for r in results]
        df['Timezone'] = [','.join(r.get('timezone', [])) for r in results]
        df['Line Type'] = [r.get('line_type', '') for r in results]
        df['Confidence Score'] = [r.get('confidence', 0.0) for r in results]
        
        st.write(df)
        
        # Download validated results
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name="validated_numbers.csv",
            mime="text/csv"
        )
        
        # Show statistics
        st.subheader('Statistics')
        valid_count = df['Valid'].sum()
        st.write(f'Valid numbers: {valid_count} ({valid_count/len(df)*100:.1f}%)')
        st.write(f'Invalid numbers: {len(df)-valid_count} ({(len(df)-valid_count)/len(df)*100:.1f}%)')

else:
    st.write('Please upload an Excel file to begin validation')
