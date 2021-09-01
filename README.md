# Music Case Study - Jack Ballinger

## Contents
This repo contains three folders:
- inputs - this contains the inputs for the exercises, as sent in the initial email
- musicie - this contains the code for the exercises
- outputs - this contains the outputs for the exercises

## Musicie
Musicie (music-ie) is the name of the 'package' i've created in order to run the exercise code.
It comes with it's own cli, which makes running the code even easier

### Installation
To install, simply navigate to the parent folder (music_task) and use pip to install:
```
cd music_task
pip install -e .
```

### Running exercises
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

## Outputs
### Exercise 1
The outputs for this exercise are as follows:
- A folder for each pdf processed (here only one) containing:
    - csv tables containing data from the pdf
    - pdf formatted quality report

### Exercise 2
The outputs for this exercise are as follows:
- A few slides on the ideal workflow design

### Exercise 3
The outputs for this exercise are as follows:
- The output Dimension and Mapping tables created in the process
- The database_schema jpg image containing information regarding how the database is structured
- The database_scheam_code sql script containing the code used to create the tables in the database_schema

### Exercise 4
The outputs for this exercise are as follows:
- A few slides on the database structure