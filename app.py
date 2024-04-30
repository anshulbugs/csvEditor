from flask import Flask, render_template, request, redirect, send_file ,make_response
import pandas as pd
import os
import tempfile
import numpy as np
import requests
app = Flask(__name__)

# Global variable to store the temporary file name
temp_csv_filename = None

def merge_csv(contact_file, company_file):
    # Read CSV files
    contacts_df = pd.read_csv(contact_file, skip_blank_lines=True)
    companies_df = pd.read_csv(company_file, skip_blank_lines=True)

    # Remove rows with all NaN values
    contacts_df.dropna(how='all', inplace=True)
    companies_df.dropna(how='all', inplace=True)

    
    
    # Merge based on the matching Company column
    merged_df = pd.merge(contacts_df, companies_df, on='Company Name')
    print("merged_df",merged_df.columns)
    # Check if all the columns exists
    # required_columns = ['First Name', 'Last Name', 'Job Title_x', 'Job Title_y', 'Personal Email','Email - Person', 'Company', 'LinkedIn Profile', 'LI Job Post URL']
    # for column in required_columns:
    #     if column not in merged_df.columns:
    #         return 'Error: The CSV file does not have a "{}" column.'.format(column), 400
    # Add a serial number column starting from 1 to the number of rows
    merged_df.insert(0, 'Serial Number', range(1, len(merged_df) + 1))
    #print columns of mergde_df
    # print(merged_df.columns)
    # print("merged_df['Personal Email']",merged_df['Personal Email'])
    merged_df['Work Email 2 new'] = merged_df['Work Email 2'].str.replace('❌ No Email Found', '')
    # print("merged_df['Personal Email new']",merged_df['Personal Email new'])
    merged_df['Work Email 2 new'] = merged_df['Work Email 2 new'].str.replace('✅ ', '')
    # print("merged_df['Personal Email new']",merged_df['Personal Email new'].head(40))
    # print("merged_df['Personal Email']",merged_df['Personal Email new'])
    # Create the final DataFrame with the specified column names and values
    
    final_df = pd.DataFrame({
        ' ': merged_df['Serial Number'],
        'recipient': merged_df['First Name'],
        'mobile_number': np.nan,  # Blank for now
        # 'email': merged_df['Email - Person'],       
        'email': merged_df['Work Email 1'].fillna(merged_df['Work Email 2 new']),
        'unique_id': np.random.randint(100000, 999999, size=len(merged_df)),  # Random number generator
        'name': merged_df['First Name'],
        'designation': merged_df['Designation'],
        # 'Name_2': merged_df['First Name'],
        'pow': merged_df['Company Name'],
        'jt': merged_df['Job Title'],
        'LinkedIn Profile ': merged_df['LinkedIn Profile'],
        'Job Posting': merged_df['LI Job Post URL'].str.slice(0, 45),
        # 'Landing Page': 'https://www.aptask.com/chat/eddie-bright-jr/',
        # 'YouTube Scroll': 'https://www.aptask.com/',
        'ApTask Scroll': 'https://www.aptask.com/'
    })

    return final_df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global temp_csv_filename
    
    # Check if the post request has the file part
    if 'contact_file' not in request.files or 'company_file' not in request.files:
        return redirect(request.url)
    
    contact_file = request.files['contact_file']
    company_file = request.files['company_file']

    # If user does not select file, browser also submits an empty part without filename
    if contact_file.filename == '' or company_file.filename == '':
        return redirect(request.url)
    
    # Save the uploaded files
    contact_filename = os.path.join(tempfile.mkdtemp(), contact_file.filename)
    company_filename = os.path.join(tempfile.mkdtemp(), company_file.filename)
    contact_file.save(contact_filename)
    company_file.save(company_filename)

    # Merge CSV files
    merged_df = merge_csv(contact_filename, company_filename)

    # Write the merged data to a temporary CSV file
    temp_csv_filename = os.path.join(tempfile.mkdtemp(), 'result.csv')
    merged_df.to_csv(temp_csv_filename, index=False)

    # No need to return anything on upload
    return redirect('/')

@app.route('/download')
def download():
    global temp_csv_filename
    
    # Return the merged CSV file as a response
    return send_file(temp_csv_filename, as_attachment=True)
@app.route('/process_csv', methods=['POST'])
def process_csv():
    data = request.files['file']
    
    # Read the CSV file, skipping empty lines
    df = pd.read_csv(data, skip_blank_lines=True)

    # Remove rows with all NaN values
    df.dropna(how='all', inplace=True)
    if 'name' in df.columns:
        name_column = 'name'
    else:
        name_column = 'name_1'
    # Check if all the columns exists
    required_columns = [name_column, 'designation', 'pow', 'jt', 'thumbnail', 'url', 'email']
    for column in required_columns:
        if column not in df.columns:
            return 'Error: The CSV file does not have a "{}" column.'.format(column), 400
        
    # Select the desired columns
    filtered_df = df[[ name_column, 'designation', 'pow', 'jt','thumbnail', 'url','email']]
    # print(filtered_df['url'])
    # print(filtered_df['url'].str.extract(r'video\.gan\.ai\/([a-zA-Z0-9_-]+)$', expand=False))
    # Create the 'landing page' column
    filtered_df['landing page'] = 'https://www.aptask.com/gan/?video_id=' + df['url'].apply(lambda x: x.split('/')[-1] if isinstance(x, str) else '')

    # filtered_df = filtered_df[[name_column,'email', 'designation', 'pow', 'jt', 'landing page', 'thumbnail', 'url']]

    filtered_df = filtered_df[[name_column,'email', 'designation', 'pow', 'jt', 'landing page', 'thumbnail']]
    # Convert the filtered DataFrame to a CSV string
    csv_data = filtered_df.to_csv(index=False)

    # Create a response object with the CSV data
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=Gan.csv'

    return response


@app.route('/process_csv_without_linkedin', methods=['POST'])
def process_csv_without_linkedin():
    # Check if the post request has the file part
    if 'contact_file1' not in request.files or 'company_file1' not in request.files:
        return redirect(request.url)
    
    contact_file = request.files['contact_file1']
    company_file = request.files['company_file1']

    # If user does not select file, browser also submits an empty part without filename
    if contact_file.filename == '' or company_file.filename == '':
        return redirect(request.url)
    
    # Save the uploaded files
    contact_filename = os.path.join(tempfile.mkdtemp(), contact_file.filename)
    company_filename = os.path.join(tempfile.mkdtemp(), company_file.filename)
    contact_file.save(contact_filename)
    company_file.save(company_filename)

    contacts_df = pd.read_csv(contact_filename, skip_blank_lines=True)
    companies_df = pd.read_csv(company_filename, skip_blank_lines=True)
    print("companies_df",companies_df.columns)
    # Remove rows with all NaN values
    contacts_df.dropna(how='all', inplace=True)
    companies_df.dropna(how='all', inplace=True)

    # Merge based on the matching Company column
    merged_df = pd.merge(contacts_df, companies_df, on='Company Name')
    print("merged_df",merged_df.columns)
    merged_df.insert(0, 'Serial Number', range(1, len(merged_df) + 1))
    merged_df['Work Email 2 new'] = merged_df['Work Email 2'].str.replace('❌ No Email Found', '')
    merged_df['Work Email 2 new'] = merged_df['Work Email 2 new'].str.replace('✅ ', '')
    
    final_df = pd.DataFrame({
        ' ': merged_df['Serial Number'],
        'recipient': merged_df['First Name'],
        'mobile_number': np.nan,  # Blank for now
        # 'email': merged_df['Email - Person'],       
        'email': merged_df['Work Email 1'].fillna(merged_df['Work Email 2 new']),
        'unique_id': np.random.randint(100000, 999999, size=len(merged_df)),  # Random number generator
        'name': merged_df['First Name'],
        'designation': merged_df['Designation'],
        'pow': merged_df['Company Name'],
        'jt': merged_df['Job Title'],
        'Company URL': merged_df['Company Domain'],
        'ApTask Scroll': 'https://www.aptask.com/'
    })

    # Create a response object with the CSV data
    csv_data = final_df.to_csv(index=False)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=ResultW/oLinkedin.csv'

    return response

if __name__ == '__main__':
    app.run(debug=True)
