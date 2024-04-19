from flask import Flask, render_template, request, redirect, send_file ,make_response
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
        ' ': merged_df['Serial Number'],
        'recipient': merged_df['First Name'],
        'mobile_number': np.nan,  # Blank for now
        'email': merged_df['Email - Person'].fillna(merged_df['Personal Email']),
        'unique_id': np.random.randint(100000, 999999, size=len(merged_df)),  # Random number generator
        'name': merged_df['First Name'],
        'designation': merged_df['Job Title_x'],
        # 'Name_2': merged_df['First Name'],
        'pow': merged_df['Company'],
        'jt': merged_df['Job Title_y'],
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
    # Read the CSV file
    df = pd.read_csv(data)
    if 'name' in df.columns:
        name_column = 'name'
    else:
        name_column = 'name_1'

    # Select the desired columns
    filtered_df = df[[ name_column, 'designation', 'pow', 'jt','thumbnail', 'url']]
    # print(filtered_df['url'])
    # print(filtered_df['url'].str.extract(r'video\.gan\.ai\/([a-zA-Z0-9_-]+)$', expand=False))
    # Create the 'landing page' column
    filtered_df['landing page'] = 'https://www.aptask.com/gan/?video_id=' + df['url'].apply(lambda x: x.split('/')[-1])

    filtered_df = filtered_df[[name_column, 'designation', 'pow', 'jt', 'landing page', 'thumbnail', 'url']]
    # Convert the filtered DataFrame to a CSV string
    csv_data = filtered_df.to_csv(index=False)

    # Create a response object with the CSV data
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=Gan.csv'

    return response
if __name__ == '__main__':
    app.run(debug=True)
