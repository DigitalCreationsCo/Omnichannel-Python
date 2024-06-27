import logging
import importlib.util
from dotenv import dotenv_values, set_key
from append_csv import append_contacts_to_csv
from parse_csv import parse_csv
from _input.google_sheets_parser_public import parse_google_sheet
from _input.airtable_parser_public import parse_airtable
from message import send_messages
import time

def log_data(data):
    logging.basicConfig(level=logging.INFO)
    for record in data:
        logging.info(record)

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    runLinkedIn = False

    env_vars = dotenv_values(".env")
    
    print("")
    print("Welcome to Omnichannel app!")
    time.sleep(2)
    print('This app will help you to send messages to your contacts via LinkedIn and Gmail.')
    print('You can provide your contacts data in Google Sheets, Airtable, or .csv file.')

    # use Linkedin mode
    # 1 for yes 2 for no
    choice = input("Do you want to run in Linkedin mode? (Enter '1' for Yes or '2' for No)").strip().upper()
    if choice == '1':
        runLinkedIn = True
        print("Linkedin mode is enabled.")
    else:
        print("Linkedin mode is disabled.")


    # get email and password
    if not env_vars.get("EMAIL_ADDRESS"):
        email_address = input("Enter your gmail username: ").strip()
        set_key(".env", "EMAIL_ADDRESS", email_address)

    if not env_vars.get("EMAIL_PASSWORD"):
        email_password = input("Enter your gmail password: ").strip()
        set_key(".env", "EMAIL_PASSWORD", email_password)

    if not env_vars.get("LINKEDIN_EMAIL"):
        linkedin_email = input("Enter your LinkedIn email: ").strip()
        set_key(".env", "LINKEDIN_EMAIL", linkedin_email)
    if not env_vars.get("LINKEDIN_PASSWORD"):
        linkedin_password = input("Enter your LinkedIn password: ").strip()
        set_key(".env", "LINKEDIN_PASSWORD", linkedin_password)


    # select data source
    choice = input("Enter '1' for Google Sheets or '2' for Airtable or '3' for .csv file: ").strip().upper()
    
    # google sheet
    if choice == '1':
        sheet_url = input("Enter the Google Sheet URL: ").strip()
        data = parse_google_sheet(sheet_url)

    # airtable
    elif choice == '2':
        # Check if the required variables are available
        if not env_vars.get("AIRTABLE_BASE_ID") or not env_vars.get("AIRTABLE_TABLE_NAME") or not env_vars.get("AIRTABLE_API_KEY"):
            print("Some or all of AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY are not available in the .env file.")
            # Get user input for base ID, table name, and API key
            base_id = input("Enter the Airtable Base ID: ").strip()
            table_name = input("Enter the Airtable Table Name: ").strip()
            api_key = input("Enter your Airtable API Key: ").strip()
            # Save the values in the .env file
            set_key(".env", "AIRTABLE_BASE_ID", base_id)
            set_key(".env", "AIRTABLE_TABLE_NAME", table_name)
            set_key(".env", "AIRTABLE_API_KEY", api_key)
        else:
            base_id = env_vars["AIRTABLE_BASE_ID"]
            table_name = env_vars["AIRTABLE_TABLE_NAME"]
            api_key = env_vars["AIRTABLE_API_KEY"]
        data = parse_airtable(base_id, table_name, api_key)

    # csv file
    elif choice == '3':
        if not env_vars.get("DATA_CSV_FILE"):
            csv_file_path = input("Enter the path to csv file: ").strip()
            set_key(".env", "DATA_CSV_FILE", csv_file_path)
        else:
            csv_file_path = env_vars["DATA_CSV_FILE"]
        
        data = parse_csv(csv_file_path).to_dict(orient='records')

    else:
        print("Invalid choice. Exiting.")
        return
    
    # log_data(data)
    print(f"Found {len(data)} records in the data source.")
    time.sleep(2)

    subject = "Cannabis Distribution B2B NY"
    message_template = """Hi {name}!

I'm Bryant, founder of Gras. We drive distribution for cannabis businesses via online and offline services. You can browse our consumer site at grascannabis.org

We're raising $250,000 to become a leading distributor in New York. 

I'm building trusted relationships with retail business owners, cannabis media company owners, and a New York transportation company owner. 
The funds will be used to establish a lucrative long term distribution deal.

If B2B is a fit for you, let's have a chat about partnership.
"""

    messaged_contacts = []
    try:
        send_messages(data, messaged_contacts, subject, message_template, runLinkedIn)
        print('')
        print("Messaged contacts completed successfully")
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Throwing a custom exception.")
        raise Exception("Program interrupted by user.")
    except Exception:
        pass
    finally:
        print(f"{len(messaged_contacts)} contacts received a message.")
        append_contacts_to_csv(messaged_contacts, env_vars["WRITE_CSV_FILE"])
        print("DONE")
        pass

if __name__ == "__main__":
    main()


# # Write to CSV in case of a fatal error
#         with open('error_contacts.csv', mode='w', newline='') as error_file:
#             error_writer = csv.DictWriter(error_file, fieldnames=contacts[0].to_dict().keys())
#             error_writer.writeheader()
#             for contact in contacts:
#                 error_writer.writerow(contact.to_dict())
#         # Re-raise the exception