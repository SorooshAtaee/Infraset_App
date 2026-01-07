from ghpythonlib.componentbase import executingcomponent as component
import csv
import os
import codecs  # Import the codecs module for encoding compatibility

class MyComponent(component):
    
    def RunScript(self, input_data, file_path, file_name):
        """Processes input data containing multiple key-value pairs and writes them to a CSV file.
        
        Inputs:
            input_data: The input text containing data to be processed.
            file_path: The path to save the CSV file.
            file_name: The name of the CSV file to save.
            
        Output:
            a: A success message indicating where the CSV was saved or an error message if there was a problem.
        """
        
        __author__ = "AdminTMP"
        __version__ = "2024.12.05"

        # Step 1: Process the input data to extract key-value pairs
        lines = input_data.strip().splitlines()
        data = []

        # Skip lines starting with '{' and any empty lines
        for line in lines:
            if line.strip().startswith("{") or not line.strip():
                continue

            # Try to extract key-value pairs from each line
            try:
                # Split on the first occurrence of a number followed by '. ' (e.g., '1. ')
                line = line.split(". ", 1)[-1]
                key_value = eval(line)  # Safely evaluate the tuple

                # Ensure the key is a string and convert the value to string if needed
                if isinstance(key_value, tuple) and len(key_value) == 2:
                    key, value = key_value
                    if isinstance(key, str) and not isinstance(value, str):
                        value = str(value)  # Convert non-string values to strings
                    data.append([key, value])
                else:
                    raise ValueError("Invalid format for key-value pair")
            except (SyntaxError, ValueError) as e:
                return "An error occurred while processing line '{}': {}".format(line, str(e))

        # Step 2: Write data to a CSV file
        output_path = os.path.join(file_path, "{}.csv".format(file_name))  # Cross-platform path construction

        try:
            # Use codecs to open the file with encoding for Python 2.x compatibility
            with codecs.open(output_path, mode="w", encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Key", "Value"])  # Write header row
                writer.writerows(data)  # Write data rows

            return "CSV file saved successfully at: {}".format(output_path)
        except Exception as e:
            return "An error occurred while saving the CSV file: {}".format(str(e))
