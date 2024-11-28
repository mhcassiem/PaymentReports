# Project overview
Since the use case was so narrow I decided to implement the task using pure Python.
Ideally this would form part of a large web application or something similar, instead of running in the command line
and expecting user input from there.

With this assumption in mind I created "model" classes intending them to be easily transferred over into a Django project
from which it would be able to generate the required migrations.

From there it would straightforward to refactor the business logic portion of the data parsing, to query the database
instead of using data structures.

Speaking of data structures, I elected to use a dictionary to load and store data from the input CSV file for the various reports
For the initial loading the project uses pandas to load CSV data into a dictionary of ID -> payment data
From there we iterate through the dictionary and build up report data for each report simultaneously.
This prevents the need to iterate multiple times over the data for each report.
I chose a dictionary primarily for its ability to do O(1) lookups.
Once the reports are compiled we sort the reports based on each report requirements and then write the data to file.
# How to
Project has a make file to simplify set up.
# Build
Simply run
```makefile
make build
```
This will build the image and install dependencies
# Run
Run 
```makefile
make up
```
to compile a CSV file defined in docker-compose.yaml FILE_PATH
Alternatively you can run
```makefile
docker compose run -e FILE_PATH=p.csv 
```
to point the container to a different file
The output reports will always be written to OUTPUT_PATH, which you can also override like so:
```makefile
docker compose run -e FILE_PATH=p.csv OUTPUT_PATH=outp
```
# Clean up
This will remove any containers and associated networks 
```makefile
make clean
```
# Tests
To run tests:
```makefile
make test
```
This builds the project image and runs the tests in the container
Overrides for FILE_PATH and OUTPUT_PATH are the same as above
Additionally once tests complete, the containers and deleted.
