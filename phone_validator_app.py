
import streamlit as st
import pandas as pd
import phonenumbers
from phonenumbers import carrier, geocoder, timezone, number_type
from phonenumbers.phonenumberutil import NumberType

def determine_line_type(number):
    try:
        line_type = number_type(number)
        if line_type == NumberType.MOBILE:
            return 'Cell'
        elif line_type == NumberType.FIXED_LINE:
            return 'Landline'
        elif line_type == NumberType.VOIP:
            return 'VOIP'
        elif line_type == NumberType.TOLL_FREE:
            return 'Toll-Free'
        elif line_type == NumberType.UNKNOWN:
            return 'International'
        else:
            return 'Invalid/Fake'
    except:
        return 'Invalid/Fake'

def calculate_confidence(number, is_valid):
    if not is_valid:
        return 0.0
    try:
        # Base confidence score
        score = 0.8
        
        # Add confidence based on number properties
        if carrier.name_for_number(number, "en"):
            score += 0.1
        if geocoder.description_for_number(number, "en"):
            score += 0.1
            
        return min(score, 1.0)
    except:
        return 0.0

def validate_phone(phone_number):
    try:
        if not phone_number or pd.isna(phone_number):
            return {
                'valid': False,
                'carrier': '',
                'location': '',
                'timezone': [],
                'line_type': 'Invalid/Fake',
                'confidence': 0.0
            }
            
        number = phonenumbers.parse(str(phone_number))
        is_valid = phonenumbers.is_valid_number(number)
        
        if is_valid:
            line_type = determine_line_type(number)
            confidence = calculate_confidence(number, is_valid)
            
            return {
                'valid': True,
                'carrier': carrier.name_for_number(number, "en") or 'Unknown',
                'location': geocoder.description_for_number(number, "en") or 'Unknown',
                'timezone': timezone.time_zones_for_number(number),
                'line_type': line_type,
                'confidence': confidence
            }
        return {
            'valid': False,
            'carrier': '',
            'location': '',
            'timezone': [],
            'line_type': 'Invalid/Fake',
            'confidence': 0.0
        }
    except:
        return {
            'valid': False,
            'carrier': '',
            'location': '',
            'timezone': [],
            'line_type': 'Invalid/Fake',
            'confidence': 0.0
        }

def main():
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
                df['Valid'] = [r['valid'] for r in results]
                df['Line Type'] = [r['line_type'] for r in results]
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
                total_numbers = len(df)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Numbers", total_numbers)
                with col2:
                    st.metric("Valid Numbers", valid_numbers)
                with col3:
                    st.metric("Invalid Numbers", total_numbers - valid_numbers)
                
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
        st.write("Please upload an Excel file to begin validation.")

if __name__ == "__main__":
    main()
