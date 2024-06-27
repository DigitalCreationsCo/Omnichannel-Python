import csv

def write_contacts_to_csv(contacts, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=contacts[0].to_dict().keys())
        writer.writeheader()
        for contact in contacts:
            writer.writerow(contact.to_dict())

def append_contacts_to_csv(contacts, filename):
    print(f"Appending {len(contacts)} contacts to {filename}")
    if len(contacts) == 0:
        return
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=contacts[0].to_dict().keys())
        for contact in contacts:
            writer.writerow(contact.to_dict())
