#!/usr/bin/env python3

import csv
import argparse
import time
from tqdm import tqdm

def build_area_code_dict(csv_file_path):
    area_code_dict = {}
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            area_code = row['Phone Code'].strip()
            area_code_dict[area_code] = row['Area']
    return area_code_dict

def update_locations_with_area_codes(area_code_dict, phone_numbers_csv_path, output_csv_file_path):
    # Read the input CSV and determine the number of rows for the progress bar
    with open(phone_numbers_csv_path, 'r', newline='') as input_csvfile:
        reader = csv.reader(input_csvfile)
        next(reader, None)  # Skip header
        total_rows = sum(1 for row in reader)

    # Reset the read pointer and write to the output CSV
    with open(phone_numbers_csv_path, 'r', newline='') as input_csvfile, \
         open(output_csv_file_path, 'w', newline='') as output_csvfile:
        reader = csv.DictReader(input_csvfile)
        fieldnames = reader.fieldnames  # Use the fieldnames from the input CSV
        writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
        writer.writeheader()

        pbar = tqdm(total=total_rows, desc='Updating locations', unit='row')

        for row in reader:
            phone_number = ''.join(filter(str.isdigit, row['Phone Number']))
            # Attempt to match the area code starting from the longest (up to 6 digits)
            for length in range(6, 1, -1):
                area_code = phone_number[:length]
                if area_code in area_code_dict:
                    row['Area'] = area_code_dict[area_code]  # Update the 'Area' in the row
                    break
            else:
                row['Area'] = 'Unknown'  # If no match is found

            writer.writerow(row)  # Write the updated row
            pbar.update(1)

        pbar.close()

def csv_files_are_identical(file_path1, file_path2):
    with open(file_path1, 'r', newline='') as file1, open(file_path2, 'r', newline='') as file2:
        file1_reader = csv.reader(file1)
        file2_reader = csv.reader(file2)

        for row1, row2 in zip(file1_reader, file2_reader):
            if row1 != row2:
                return False

    # Check if both files have the same number of rows
    with open(file_path1, 'r', newline='') as file1:
        file1_rows = sum(1 for row in csv.reader(file1))
    with open(file_path2, 'r', newline='') as file2:
        file2_rows = sum(1 for row in csv.reader(file2))

    return file1_rows == file2_rows

def main():
    parser = argparse.ArgumentParser(description='Update locations in the phone number CSV using area codes.')
    parser.add_argument('original_csv', help='Original CSV file path with phone codes and locations.')
    parser.add_argument('generated_csv', help='Generated CSV file path with phone numbers.')
    parser.add_argument('output_csv', help='Output CSV file path for updated locations.')

    args = parser.parse_args()

    start_time = time.time()  # Start timing

    area_code_dict = build_area_code_dict(args.original_csv)
    update_locations_with_area_codes(area_code_dict, args.generated_csv, args.output_csv)

    end_time = time.time()  # End timing
    print(f"Execution time: {end_time - start_time:.2f} seconds")

    # Validate if the generated CSV and updated CSV are identical
    if csv_files_are_identical(args.generated_csv, args.output_csv):
        print("Validation passed: The files are identical.")
    else:
        print("Validation failed: The files are not identical.")

if __name__ == '__main__':
    main()
