import argparse
import os
from os import path

from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO, TracedDataCodingCSVIO, TracedDataCSVIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges manually cleaned files back into a traced data file.")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata", nargs=1)
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to JSON input file, which contains a list of TracedData objects",
                        nargs=1)
    parser.add_argument("coding_mode", metavar="coding-mode",
                        help="How to interpret the files in the coding-input-directory. "
                             "Accepted values are 'coda' or 'coding-mode'", nargs=1, choices=["coda", "coding-csv"])
    parser.add_argument("coded_input_path", metavar="coded-input-path",
                        help="Directory to read coding files from", nargs=1)
    parser.add_argument("key_of_raw", metavar="key-of-raw",
                        help="Key in TracedData to import to Coda", nargs=1)
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write merged results to", nargs=1)
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to export coded data to", nargs=1)

    args = parser.parse_args()
    user = args.user[0]
    json_input_path = args.json_input_path[0]
    coding_mode = args.coding_mode[0]
    coded_input_path = args.coded_input_path[0]
    key_of_raw = args.key_of_raw[0]
    json_output_path = args.json_output_path[0]
    csv_output_path = args.csv_output_path[0]
    
    key_of_clean = "{}_clean".format(key_of_raw)

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Merge coded data into the loaded data file
    if coding_mode == "coda":
        # Merge manually coded Coda files into the cleaned dataset
        with open(path.join(coded_input_path, "{}.csv".format(key_of_raw)), "r") as f:
            data = list(TracedDataCodaIO.import_coda_to_traced_data_iterable(
                user, data, key_of_raw, key_of_clean, f, True))
    else:
        assert coding_mode == "coding-csv", "coding_mode was not one of 'coda' or 'coding-csv'"

        # Merge manually coded CSV files into the cleaned dataset
        with open(path.join(coded_input_path, "{}.csv".format(key_of_raw)), "r") as f:
            data = list(TracedDataCodingCSVIO.import_coding_csv_to_traced_data_iterable(
                user, data, key_of_raw, key_of_clean,
                key_of_raw, key_of_clean, f, True))

    # Write coded data back out to disk
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Export coded data to CSV for analysis
    if os.path.dirname(csv_output_path) is not "" and not os.path.exists(os.path.dirname(csv_output_path)):
        os.makedirs(os.path.dirname(csv_output_path))
    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=["avf_phone_id", key_of_raw, key_of_clean])
