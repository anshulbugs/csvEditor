from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import os
import tempfile
import numpy as np

app = Flask(__name__)

# Global variable to store the temporary file name
temp_csv_filename = None

def merge_csv(contact_file, company_file):
    # Read CSV files
    contacts_df = pd.read_csv(contact_file)
    companies_df = pd.read_csv(company_file)
    # # Remove the "Company" column from the companies DataFrame
    # if 'Company' in companies_df.columns:
    #     companies_df.rename(columns={'Company': 'Company Name'}, inplace=True)
    
    # # Rename columns for consistency
    # contacts_df.rename(columns={'Company Domain': 'Company'}, inplace=True)
    # companies_df.rename(columns={'Find Domain from Company Name': 'Company'}, inplace=True)
    
    # Merge based on the matching Company column
    merged_df = pd.merge(contacts_df, companies_df, on='Company')

    # Add a serial number column starting from 1 to the number of rows
    merged_df.insert(0, 'Serial Number', range(1, len(merged_df) + 1))

    # Create the final DataFrame with the specified column names and values
    final_df = pd.DataFrame({
        'Serial Number': merged_df['Serial Number'],
        'Recipient': merged_df['First Name'],
        'Mobile Number': np.nan,  # Blank for now
        'Email': merged_df['Email - Person'].fillna(merged_df['Personal Email']),
        'Unique ID': np.random.randint(100000, 999999, size=len(merged_df)),  # Random number generator
        'Name_1': merged_df['First Name'],
        'Designation': merged_df['Job Title_x'],
        'Name_2': merged_df['First Name'],
        'LinkedIn Profile': merged_df['LinkedIn Profile'],
        'PoW': merged_df['Company'],
        'Jt': merged_df['Job Title_y'],
        'Job Posting On LinkedIn': merged_df['LI Job Post URL'].str.slice(0, 45),
        'Landing Page': 'https://www.aptask.com/chat/eddie-bright-jr/',
        'YouTube Scroll': 'https://www.aptask.com/',
        'ApTask Scrolling': 'https://www.aptask.com/'
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

if __name__ == '__main__':
    app.run(debug=True)
