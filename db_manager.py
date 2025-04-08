import csv
import os
from datetime import datetime

class DBManager:
    def __init__(self, filename):
        self.filename = filename
        self.headers = ["clientID", "timestamp", "receiver", "transmitter", "topic", "subscriber", "message"]
        
        # Check if file exists, otherwise create it with headers
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def add_record(self, clientID, receiver, transmitter, topic, subscriber, message):
        """Add a record to the CSV file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([clientID, timestamp, receiver, transmitter, topic, subscriber, message])

    def get_all_records(self):
        """Retrieve all records from the CSV file."""
        with open(self.filename, mode='r') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def filter_records(self, **kwargs):
        """Filter records based on provided keyword arguments."""
        with open(self.filename, mode='r') as file:
            reader = csv.DictReader(file)
            return [row for row in reader if all(row[key] == str(value) for key, value in kwargs.items())]

# Example Usage
if __name__ == "__main__":
    db = DBManager("iot_data.csv")
    
    # Add sample records
    db.add_record(clientID="IOT_client-Id-1234567", receiver="Button", transmitter="Heater", 
                  topic="pr/home/1234567/sts", subscriber="HomeSystem", message="ON")
    db.add_record(clientID="IOT_client-Id-7654321", receiver="Heater", transmitter="Sensor", 
                  topic="pr/home/7654321/temp", subscriber="HomeSystem", message="Temperature: 23C")

    # Retrieve and print all records
    records = db.get_all_records()
    print("All Records:", records)

    # Filter and print specific records
    filtered = db.filter_records(receiver="Button")
    print("Filtered Records:", filtered)
