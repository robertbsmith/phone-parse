#!/usr/bin/env python3

import csv
import random
import argparse
from tqdm import tqdm

# Define the length of a standard UK phone number (excluding country code)
UK_PHONE_NUMBER_LENGTH = 10

def load_area_codes(csv_file_path):
    area_codes = {}
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            area_code = row['Phone Code'].strip()
            area_codes[area_code] = {
                'Area': row['Area'],
                'Extensions': set()
            }
    # Build extensions for each area code
    for code in area_codes.keys():
        for potential_extension in area_codes.keys():
            if potential_extension != code and potential_extension.startswith(code):
                area_codes[code]['Extensions'].add(potential_extension)
    return area_codes

def generate_phone_number(area_code, extensions, phone_number_length):
    while True:
        # Calculate the number of digits to pad
        padding_length = phone_number_length - len(area_code)
        # Generate the random padding
        random_padding = ''.join([str(random.randint(0, 9)) for _ in range(padding_length)])
        # Create the full phone number
        phone_number = f'{area_code}{random_padding}'
        # Check if the generated number matches any of the extensions
        if not any(phone_number.startswith(ext) for ext in extensions):
            return phone_number

def generate_random_phone_numbers(area_codes_csv_path, output_csv_file_path, total_numbers):
    area_codes = load_area_codes(area_codes_csv_path)

    with open(output_csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Phone Number', 'Area']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        pbar = tqdm(total=total_numbers, desc='Generating phone numbers', unit='num')

        generated_numbers = 0
        while generated_numbers < total_numbers:
            for area_code, data in area_codes.items():
                if generated_numbers >= total_numbers:
                    break
                phone_number = generate_phone_number(area_code, data['Extensions'], UK_PHONE_NUMBER_LENGTH)
                writer.writerow({'Phone Number': phone_number, 'Area': data['Area']})
                generated_numbers += 1
                pbar.update(1)

        pbar.close()

def main():
    parser = argparse.ArgumentParser(description='Generate UK phone numbers.')
    parser.add_argument('area_codes_csv', help='CSV file path with area codes and locations.')
    parser.add_argument('output_csv', help='Output CSV file path for generated phone numbers.')
    parser.add_argument('total_numbers', type=int, help='Total number of phone numbers to generate.')

    args = parser.parse_args()

    generate_random_phone_numbers(args.area_codes_csv, args.output_csv, args.total_numbers)

if __name__ == '__main__':
    main()
