import csv

input_file = "/home/ludofw/Data/datasets/euroc_custom/oakd_lite/29052025_nanosec/mav0/imu0/data.csv"  # Replace with your input CSV file name
output_file = "microsec.csv" # 

with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        if row: # Ensure the row is not empty
            try:
                timestamp_ns = int(row[0])
                timestamp_micro_resolution_ns = (timestamp_ns // 1000) * 1000
                row[0] = str(timestamp_micro_resolution_ns) # Convert back to string for writing
                writer.writerow(row)
            except ValueError:
                # Handle cases where the first column might not be a valid integer
                print(f"Skipping row due to invalid timestamp: {row}")
                writer.writerow(row) # Write the original row if conversion fails
