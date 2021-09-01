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
This will run exercise 1, and will write the corresponding files to the default download location, which is:
```C:/Downloads/jack_ballinger_task_outputs/```

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