
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
        phone_str = '1480' + phone_str  # Default area code for 7-digit numbers
        
    return '+' + phone_str

def determine_line_type(number):
    try:
        line_type = phonenumbers.number_type(number)
        
        # Explicit handling for mobile numbers
        if line_type == PhoneNumberType.MOBILE:
            return 'Mobile'
        elif line_type == PhoneNumberType.FIXED_LINE:
            return 'Landline'
        elif line_type == PhoneNumberType.FIXED_LINE_OR_MOBILE:
            # Additional logic for ambiguous numbers
            area_code = str(number.national_number)[:3]
            # List of area codes commonly used for mobile phones in the US
            mobile_area_codes = ['917', '347', '201', '551', '973', '862', '646', '332', 
                               '929', '718', '516', '631', '934', '914', '845', '838', 
                               '332', '917', '646', '347', '718']
            
            if area_code in mobile_area_codes:
                return 'Mobile'
            else:
                return 'Landline'  # Default to landline if uncertain
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
        score = 0.8
        if len(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)) >= 11:
            score += 0.1
        if phonenumbers.is_valid_number_for_region(number, "US"):
            score += 0.1
        return min(score, 1.0)
    except:
        return 0.0

def validate_phone(phone_number):
    try:
        formatted_number = format_phone_number(phone_number)
        number = phonenumbers.parse(formatted_number)
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
                'confidence': confidence,
                'is_mobile': line_type == 'Mobile'  # New field specifically for mobile detection
            }
        return {
            'valid': False,
            'formatted_number': str(phone_number),
            'carrier': '',
            'location': '',
            'timezone': [],
            'line_type': 'Invalid',
            'confidence': 0.0,
            'is_mobile': False
        }
    except Exception as e:
        return {
            'valid': False,
            'formatted_number': str(phone_number),
            'carrier': '',
            'location': '',
            'timezone': [],
            'line_type': 'Invalid',
            'confidence': 0.0,
            'is_mobile': False
        }

st.title('Phone Number Validator')
st.write('Upload an Excel file containing phone numbers for validation')

uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        phone_col = st.selectbox('Select the column containing phone numbers:', df.columns)
        
        if st.button('Validate Numbers'):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, number in enumerate(df[phone_col]):
                result = validate_phone(number)
                results.append(result)
                progress = (i + 1) / len(df)
                progress_bar.progress(progress)
                status_text.text(f'Processing... {int(progress * 100)}%')
            
            # Add results to dataframe
            df['Formatted Number'] = [r['formatted_number'] for r in results]
            df['Valid'] = [r['valid'] for r in results]
            df['Line Type'] = [r['line_type'] for r in results]
            df['Is Mobile'] = [r['is_mobile'] for r in results]  # New column specifically for mobile
            df['Carrier'] = [r['carrier'] for r in results]
            df['Location'] = [r['location'] for r in results]
            df['Timezone'] = [','.join(r['timezone']) if r['timezone'] else '' for r in results]
            df['Confidence Score'] = [r['confidence'] for r in results]
            
            # Display results
            st.subheader('Validation Results')
            st.dataframe(df)
            
            # Statistics
            st.subheader('Summary Statistics')
            valid_numbers = df['Valid'].sum()
            mobile_numbers = df['Is Mobile'].sum()
            total_numbers = len(df)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Numbers", total_numbers)
            with col2:
                st.metric("Valid Numbers", valid_numbers)
            with col3:
                st.metric("Mobile Numbers", mobile_numbers)
            with col4:
                st.metric("Other Types", total_numbers - mobile_numbers)
            
            # Line type distribution
            st.subheader('Line Type Distribution')
            line_type_counts = df['Line Type'].value_counts()
            st.bar_chart(line_type_counts)
            
            # Mobile vs Non-Mobile Distribution
            st.subheader('Mobile vs Non-Mobile Distribution')
            mobile_dist = df['Is Mobile'].value_counts()
            st.bar_chart(mobile_dist)
            
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
