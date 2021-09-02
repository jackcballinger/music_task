# Music Case Study - Jack Ballinger

## Contents
This repo contains three folders:
- inputs - this contains the inputs for the exercises, as sent in the initial email
- musicie - this contains the code for the exercises
- outputs - this contains the outputs for the exercises

## Musicie
Musicie (music-ie) is the name of the 'package' i've created in order to run the exercise code.
It comes with it's own cli, which makes running the code even easier

### **Installation**
To install, simply navigate to the parent folder (music_task) and use pip to install:
```
cd music_task
pip install -e .
```

### **Running exercises**
To run, use the cli:
```
musicie --exercise_number 1 --write_mode true
```

The arguments the cli takes are:
```
required_arguments: 
  --exercise_number {1,3}
                        Number of the exercise to run
optional_arguments:
  --input_folder_location INPUT_FOLDER_LOCATION
                        Location of the folder containing inputs
  --write_mode WRITE_MODE
                        Boolean flag that when true, will write output data to file
  --postgres_yaml POSTGRES_YAML
                        Location of a postgres_config.yaml file. If specified, code will alltempt to write to sql.
  --output_folder_location OUTPUT_FOLDER_LOCATION
                        Location of the folder to write outputs to
```

This will run exercise 1, and will write the corresponding files to the default download location, which is:
```{Home Directory}/Downloads/jack_ballinger_task_outputs/```

The code for musicie has been formatted using [black](https://black.readthedocs.io/en/stable/) - this does make some code look a little strange, but in my view, it's good to have all code following similar style guidelines.
The code has also been linted in order to ensure best practices.

## Exercise Code
### **Exercise 1**
The code for exercise 1 is essentially made up of three parts:
- obtaining data from the input pdfs
- formatting the data obtained from the pdf
- validating this input data

Each of these steps has a base class containing all of the functions that can be generalised between pdf schema types, which is then inherrited by a custom schema class containing all of the more bespoke functions related to that specific schema type

The pdf_reader classes output data to be formatted, the pdf_formatted classes output data to be validated, and the pdf_validator classes output a test report to the specified output location, running tests specified in the config

### **Exercise 3**
The code for exercise 3 is also essentially made up of three parts:
- matching artist and track_names to artist entities in the musicbrainz ecosystem
- taking those artists and extracting all recordings for each artist
- taking those records and extracting all related works for each record

The data is then formatted into the relevant Dimension and Mapping tables and written to csv/sql as required

The matching artist and track_names is the key part to this exercise, and is the part of the process where there is the most scope for errors to creep in. I've tried to make the process as robust as possible by following the steps shown in the [mapping flowchat](outputs/exercise_3_artist_recording_universe/artist_track_mapping_process.png).

## Outputs
### **Exercise 1**
The outputs for this exercise are as follows:
- A folder for each pdf processed (here only one) containing:
    - csv tables containing data from the pdf
    - pdf formatted quality report

### **Exercise 2**
The outputs for this exercise are as follows:
- A [few slides](outputs/exercise_2_standardise_royalty_statements/workflow_design.pptx) on the ideal workflow design
- An [image](outputs/exercise_2_standardise_royalty_statements/royalty_statement_workflow_process.jpeg) of the proposed royalty statement workflow design

### **Exercise 3**
The outputs for this exercise are as follows:
- The output Dimension and Mapping tables created in the process
- The [database_schema image](outputs/exercise_3_artist_recording_universe/database_schema.png) containing information regarding how the database is structured
- The [database_schema_code sql script](outputs/exercise_3_artist_recording_universe/database_schema_code.sql) containing the code used to create the tables in the database_schema
- The [mapping flowchat](outputs/exercise_3_artist_recording_universe/artist_track_mapping_process.png) containing the process used to map the billboard tracks

### **Exercise 4**
The outputs for this exercise are as follows:
- A [few slides](outputs/exercise_4_structure_database/database_schema.pptx) on the database structure
- The [database_schema image](outputs/exercise_4_structure_database/database_schema.png) containing information regarding how the database is structured
- The [database_schema_code sql script](outputs/exercise_4_structure_database/database_schema_code.sql) containing the code used to create the tables in the database_schema


## Improvements/Next Steps
There are a number of improvements I'd make to the code if it were to be productionalised:
- split the two exercises up into their own packages as they do vastly different things
- write unit tests for the code to ensure it's doing exactly what I want it to do
- potentially use classifiers (tree methods?) to classify pdfs into the correct schema