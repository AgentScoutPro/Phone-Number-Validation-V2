
import streamlit as st
import pandas as pd
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from phonenumbers.phonenumberutil import PhoneNumberType

def format_phone_number(phone):
    # Remove any non-numeric characters
    phone_str = ''.join(filter(str.isdigit, str(phone)))
    
    # Add US country code if not present
    if len(phone_str) == 10:
        phone_str = '1' + phone_str
    elif len(phone_str) == 7:
        phone_str = '1480' + phone_str  # Assuming 480 area code for 7-digit numbers
        
    # Add plus sign for phonenumbers library
    return '+' + phone_str

def determine_line_type(number):
    try:
        line_type = phonenumbers.number_type(number)
        if line_type == PhoneNumberType.MOBILE:
            return 'Cell'
        elif line_type == PhoneNumberType.FIXED_LINE:
            return 'Landline'
        elif line_type == PhoneNumberType.FIXED_LINE_OR_MOBILE:
            return 'Landline/Cell'
        elif line_type == PhoneNumberType.VOIP:
            return 'VOIP'
        elif line_type == PhoneNumberType.TOLL_FREE:
            return 'Toll-Free'
        elif line_type == PhoneNumberType.UNKNOWN:
            return 'Unknown'
        else:
            return 'Other'
    except:
        return 'Invalid'

def calculate_confidence(number, is_valid):
    if not is_valid:
        return 0.0
    try:
        # Base confidence score
        score = 0.8
        
        # Add confidence based on number properties
        if len(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)) >= 11:
            score += 0.1
        if phonenumbers.is_valid_number_for_region(number, "US"):
            score += 0.1
            
        return min(score, 1.0)
    except:
        return 0.0

def validate_phone(phone_number):
    try:
        # Format the phone number
        formatted_number = format_phone_number(phone_number)
        
        # Parse the number
        number = phonenumbers.parse(formatted_number)
        
        # Check validity
        is_valid = phonenumbers.is_valid_number(number)
        
        if is_valid:
            line_type = determine_line_type(number)
            confidence = calculate_confidence(number, is_valid)
            
            return {
                'valid': True,
                'formatted_number': phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'carrier': carrier.name_for_number(number, "en") or 'Unknown',
                'location': geocoder.description_for_number(number, "en") or 'USA',
                'timezone': timezone.time_zones_for_number(number),
                'line_type': line_type,
                'confidence': confidence
            }
        return {
            'valid': False,
            'formatted_number': str(phone_number),
            'carrier': '',
            'location': '',
            'timezone': [],
            'line_type': 'Invalid',
            'confidence': 0.0
        }
    except Exception as e:
        return {
            'valid': False,
            'formatted_number': str(phone_number),
            'carrier': '',
            'location': '',
            'timezone': [],
            'line_type': 'Invalid',
            'confidence': 0.0
        }

st.title('Phone Number Validator')

uploaded_file = st.file_uploader("Upload Excel file with phone numbers", type=['xlsx', 'xls'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        phone_col = st.selectbox('Select phone number column', df.columns)
        
        if st.button('Validate Numbers'):
            results = []
            progress = st.progress(0)
            status_text = st.empty()
            
            for i, number in enumerate(df[phone_col]):
                result = validate_phone(number)
                results.append(result)
                progress.progress((i + 1) / len(df))
                status_text.text(f'Processing... {i+1}/{len(df)} numbers')
            
            # Add results to dataframe
            df['Formatted Number'] = [r['formatted_number'] for r in results]
            df['Valid'] = [r['valid'] for r in results]
            df['Line Type'] = [r['line_type'] for r in results]
            df['Carrier'] = [r['carrier'] for r in results]
            df['Location'] = [r['location'] for r in results]
            df['Timezone'] = [','.join(r['timezone']) if r['timezone'] else '' for r in results]
            df['Confidence Score'] = [r['confidence'] for r in results]
            
            # Display results
            st.write(df)
            
            # Show statistics
            st.subheader('Validation Statistics')
            valid_count = df['Valid'].sum()
            total_count = len(df)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Numbers", total_count)
            with col2:
                st.metric("Valid Numbers", valid_count)
            with col3:
                st.metric("Invalid Numbers", total_count - valid_count)
            
            # Line type distribution
            st.subheader('Line Type Distribution')
            line_type_counts = df['Line Type'].value_counts()
            st.bar_chart(line_type_counts)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="validated_numbers.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
else:
    st.write("Please upload an Excel file to begin validation")
