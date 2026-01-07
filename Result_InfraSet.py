from ghpythonlib.componentbase import executingcomponent as component
import csv
import os
import codecs
import ast

class MyComponent(component):

    def RunScript(self, input_data, file_path, file_name):

        if not input_data:
            return "No input data provided."

        data = []

        # INPUT IS A LIST OF STRINGS (Grasshopper Panel)
        for line in input_data:
            if line is None:
                continue

            line = str(line).strip()

            # Skip GH path lines
            if not line:
                continue
            if line.startswith("{") and line.endswith("}"):
                continue

            # Extract tuple
            start = line.find("(")
            end = line.rfind(")")

            if start == -1 or end == -1:
                continue

            tuple_text = line[start:end + 1]

            try:
                key_value = ast.literal_eval(tuple_text)
            except:
                continue

            if isinstance(key_value, tuple) and len(key_value) == 2:
                key = key_value[0]
                value = key_value[1]

                if value is None:
                    value = "N/A"

                data.append([str(key), str(value)])

        if not data:
            return "No valid key-value pairs found."

        # Create folder if needed
        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except:
                return "Could not create directory: " + file_path

        output_path = os.path.join(file_path, file_name + ".csv")

        try:
            with codecs.open(output_path, "w", "utf-8") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(["Parameter", "Value"])

                for row in data:
                    writer.writerow(row)

            return "CSV saved with " + str(len(data)) + " rows at: " + output_path

        except Exception as e:
            return "CSV write error: " + str(e)
