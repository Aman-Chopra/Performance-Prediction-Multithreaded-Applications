# Creating the dataset

Downloading and building PARSEC Benchmark:
- `wget http://parsec.cs.princeton.edu/download/3.0/parsec-3.0.tar.gz`
- `tar -xzf parsec-3.0.tar.gz`
- `source env.sh`

Running the python script to create the dataset:
- `python data_creator.py`
- python version 2 is already installed in CIMS and Crunchy machines.
- We have run the script multiple times to take the mean value of all the attributes for better modeling.
- The dataset will be created as dataset.csv

# Running the prediction model

Google collab:
- Open perf_prediction.ipynb file in Google Collab
- Upload the dataset.csv file in the sample_data folder
- Run all cells to run the model and see the results put in the report