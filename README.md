To run :
    1. Create python environment :python -m venv venv
    2. Run the environment : venv\Scripts\activate
    3. Download and install requirements.txt : pip install -r requirements.txt
    4. Run the program : python DataExtractor.py
    5. Choose the source 
    5. Provide it the folder address and filename, it will automatically download the csv file.
    6. If source is apollo,Select the files type based on columns in the file.
        Check if firstName is present in C column and lastName in D column then keep it as default Type 1 else if firstName is present in B column and lastName in C column then change the files type to Type 2.

