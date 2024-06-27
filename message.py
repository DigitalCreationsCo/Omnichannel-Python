from datetime import datetime
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expect
from dotenv import dotenv_values
import time
import random
from investor import Contact

env_vars = dotenv_values(".env")

random_delay = random.uniform(2, 5) + 2
long_random_delay = random.uniform(5, 8) + 1

linkedin_driver = None
gmail_driver = None
MAX_ATTEMPTS = 3

MAX_MESSAGE_TIME = 2 * 60 * 60 # 2 hours by default, feel free to modify it


did_send_message = False

def start_linkedin(attempt=1):
    
    global linkedin_driver
    global MAX_ATTEMPTS

    if attempt > MAX_ATTEMPTS:
        print("Max login attempts reached. Exiting.")
        return
    
    # Set up Selenium WebDriver for LinkedIn
    if not linkedin_driver:
        linkedin_driver = webdriver.Chrome()
        linkedin_driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        time.sleep(long_random_delay)  # Wait for LinkedIn to load
        
        try:
            user_field = WebDriverWait(linkedin_driver, 10).until(
                expect.visibility_of_element_located((By.ID, "username"))
            )
            pw_field = linkedin_driver.find_element("id","password")
            login_button = linkedin_driver.find_element(By.XPATH,
                        '//*[@id="organic-div"]/form/div[3]/button')
            user_field.send_keys(env_vars["LINKEDIN_EMAIL"])
            user_field.send_keys(Keys.TAB)
            time.sleep(random_delay)
            pw_field.send_keys(env_vars["LINKEDIN_PASSWORD"])
            time.sleep(random_delay)
            login_button.click()
            time.sleep(long_random_delay)

            # Check if login was successful, if not, retry
            if "feed" not in linkedin_driver.current_url:  # Assuming "feed" is in the URL after successful login

                # Pause for manual security check
                print("Please complete the security check manually and press Enter to continue...")
                input("Press Enter to continue...")

                time.sleep(long_random_delay)
                # After completing the security check manually, the script will resume here
                # Verify if the login was successful
                if "feed" in linkedin_driver.current_url:
                    print("Login successful.")
                else:
                    print("Login failed. Please try again.")
                    start_linkedin(attempt + 1)
                
            else:
                print("Login successful.")
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Exception occurred: {e}. Username/password field or login button not found")
            start_linkedin(attempt + 1)


def send_linkedin_message(linkedin_url, name, subject, message_template: str):

    global linkedin_driver
    global did_send_message

    try: 
        name_parts = name.split(' ')
        first_name = name_parts[0] if len(name_parts) > 0 else name
        
        print("Sending Linkedin message to ", first_name)
        message = message_template.format(name=first_name)

        # Search for the recipient's profile
        # linkedin_driver.get("https://www.linkedin.com/search/results/people/?" + urlencode({"keywords": name}))
        
        # get the linkedin profile
        time.sleep(random_delay)
        linkedin_driver.get(linkedin_url)
        linkedin_driver.maximize_window()

        time.sleep(long_random_delay)
        # Click on the first search result (assuming it's the profile of the recipient)
        # search_result_list = linkedin_driver.find_element(By.XPATH, "//ul[@class='reusable-search__entity-result-list list-style-none']")
        # print("Class attribute of ul element:", search_result_list.get_attribute("class"))

        # first_profile_link = search_result_list.find_element(By.XPATH, "./li[1]")
        # first_profile_link.click()
        # time.sleep(long_random_delay*2)

        # Send a personalized message (optional)
        try:
            # message_button_xpath_expression = f"//button[contains(@aria-label, 'Message') and contains(@aria-label, '{first_name}')]"
            message_button_xpath_expression = "//button[contains(@aria-label, 'Message')]"
            
            print("XPath expression:", message_button_xpath_expression)
            elements = linkedin_driver.find_elements(By.XPATH, message_button_xpath_expression)
            print('message button elements found: ', elements)
            message_button  = elements[1] if len(elements) > 1 else elements[0] if len(elements) > 0 else None
            print('message button found', message_button)
            message_button.click()
            print('message button clicked')
            print('waiting delay')
            time.sleep(random_delay)

            # check if upsell modal is present
            try: 
                upsell_modal = linkedin_driver.find_element(By.XPATH, "//*[@data-test-modal-id='upsell-modal']")
                if upsell_modal:
                    print('upsell modal found')
                    # close upsell modal
                    close_button = upsell_modal.find_element(By.XPATH, ".//*[@aria-label='Dismiss']")
                    close_button.click()
                    print('upsell modal closed')
                    time.sleep(random_delay)
                    # raise exception to skipp messaging
                    raise Exception("Upsell modal found")
            except NoSuchElementException as e:
                print('upsell modal not found')
                print(e)
    
            # Get subjct input
            try:
                time.sleep(random_delay)

                subject_input = linkedin_driver.find_element(By.XPATH, "//input[@name='subject']")
                print('subject input found', subject_input)
                subject_input.send_keys(subject)
                print('subject input sent')
                print('waiting long delay')
                time.sleep(long_random_delay)
            except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
                print(f"Subject input not found for {name}. Error: {e.msg}")

            # Get message input
            try:
                time.sleep(random_delay)

                # elements = linkedin_driver.find_elements(By.XPATH, "//div[@class='msg-form__msg-content-container']")
                # print('message input elements found: ', elements)
                message_input = WebDriverWait(linkedin_driver, 30).until(expect.element_to_be_clickable((By.CSS_SELECTOR, ".msg-form__contenteditable")))
                print('message input found', message_input)
                message_input.click()
                print('message input clicked')

                # add message to selected element
                message_input.send_keys(message)
                print('set message input')
                time.sleep(random_delay)
                
                action_chains = ActionChains(linkedin_driver)
                action_chains.key_down(Keys.CONTROL).send_keys(Keys.RETURN).key_up(Keys.CONTROL).perform()
                # message_input.send_keys(Keys.ENTER)
                print('key down, ctrl + enter, key up performed')

                print("Sending message to", name)
                print("with the following subject:", subject)
                print("with the message content:", message)
                time.sleep(long_random_delay)

                did_send_message = True

            except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
                print(f"Message input not found for {name}. Error: {e.msg}")
                
            # close message dialog
            try:
                # gets 5 elements
                # elements = linkedin_driver.find_elements(By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control')]//svg[@data-test-icon='close-small']")
                
                
                elements = linkedin_driver.find_elements(By.XPATH, "//*[contains(@data-test-icon, 'close-small')]")
                print('message close button elements found: ', elements)

                # message_close_button = linkedin_driver.find_element(By.XPATH, "//svg[@data-test-icon='close-small']")
                message_close_button = elements[1] if len(elements) > 1 else elements[0] if len(elements) > 0 else None
                if not message_close_button:
                    raise NoSuchElementException("Message close button not found")
                print('message close button found', message_close_button)
                
                # DEBUG
                # highlight elements
                # highlight_elements(linkedin_driver, [message_close_button])

                message_close_button.click()
                print('message close button clicked')
                time.sleep(random_delay)
            except NoSuchElementException as e:
                print(f"Message close button not found for {name}. Skipping message.")
                print(e)
                raise e
            # except TimeoutException:
            #     raise Exception(f"Timeout waiting for message input for {name}.")
        # except NoSuchElementException(f"Message button not found for {name}. Skipping message."):
        #     print(f"Message button not found for {name}. Skipping message.")
        except (NoSuchElementException, Exception) as e:
            print(f"Messaging not available for {name}. Skipping message.")
            print(f"Reason: {e}")

        print(f"Send connection and follow request to {name}")
        # check for msg overlay list and close msg-overlay-list-bubble
        try:
            time.sleep(long_random_delay)
            msg_overlay_list_controls = linkedin_driver.find_element(By.XPATH, "//div[contains(@class, 'msg-overlay-bubble-header__controls')]")
            if msg_overlay_list_controls:
                print('msg overlay list found')
                # close list
                close_button = msg_overlay_list_controls.find_element(By.XPATH, "//*[contains(@data-test-icon, 'chevron-down-small')]")
                close_button.click()
                print('msg overlay list closed')
                time.sleep(random_delay)
        except Exception as e:
            print(e)

        # Send a connection request
        try:
            try: 
                # find standard connect button
                # elements = linkedin_driver.find_elements(By.XPATH,"//button[contains(@aria-label, 'More actions')]//span[contains(text(), 'connect')]")
                # connect_button = linkedin_driver.find_elements(By.XPATH,"//span[text()='Connect']")
                # print('connect button elements found: ', elements)
                # connect_button = WebDriverWait(linkedin_driver, 10+ random_delay).until(expect.element_to_be_clickable((By.XPATH,"//*[contains(@aria-label, 'connect')]")))
                connect_button = linkedin_driver.find_element(By.XPATH,"//li//*[contains(@aria-label, 'connect')]")
                WebDriverWait(linkedin_driver, 30).until(expect.visibility_of(connect_button))
                WebDriverWait(linkedin_driver, 30).until(expect.element_to_be_clickable(connect_button))
                connect_button.click()

                # handle connection dialog
                try:
                    connection_modal = linkedin_driver.find_element(By.XPATH, "//*[@data-test-modal-id='send-invite-modal']")
                    if connection_modal:
                        print('connection modal found')
                        time.sleep(2)

                        # send connection request
                        send_button = connection_modal.find_element(By.XPATH, ".//*[contains(@aria-label, 'Send')]")
                        send_button.click()
                        print('connection request sent')
                        print('connection modal closed')
                        time.sleep(random_delay)
                except NoSuchElementException as e:
                    print('connection_modal modal not found')
                    print(e)
                    raise Exception("Connection modal not found")
            except Exception as e:
                print(f"Connect button not found. Try to find the connect button in the more actions dropdown.")
                print(f"Reason: {e}")

                # get more actions dropdown menu
                elements = linkedin_driver.find_elements(By.XPATH,"//button[contains(@aria-label, 'More actions')]")
                print('more actions button elements found: ', elements)
                if len(elements) > 1:
                    more_actions_button = elements[1] if len(elements) > 1 else elements[0]
                else:
                    raise NoSuchElementException("More actions button not found")
                print('more actions button found', more_actions_button)
                        
                print('waiting delay')
                time.sleep(random_delay)

                more_actions_button.click()
                print('more actions button clicked')
                time.sleep(random_delay)

                # connect_button = WebDriverWait(linkedin_driver, 10+ random_delay).until(expect.element_to_be_clickable((By.XPATH,"//*[contains(@aria-label, 'connect')]")))
                connect_button = linkedin_driver.find_element(By.XPATH,"//li//*[contains(@aria-label, 'connect')]")
                print('connect button found', connect_button)
                
                # DEBUG
                # highlight_elements(linkedin_driver, [connect_button])

                WebDriverWait(linkedin_driver, 30).until(expect.visibility_of(connect_button))
                WebDriverWait(linkedin_driver, 30).until(expect.element_to_be_clickable(connect_button))
                time.sleep(2)

                connect_button.click()
                print('connect button clicked')

                # handle connection dialog
                try:
                    connection_modal = linkedin_driver.find_element(By.XPATH, "//*[@data-test-modal-id='send-invite-modal']")
                    if connection_modal:
                        print('connection modal found')
                        # send connection request
                        send_button = connection_modal.find_element(By.XPATH, ".//*[contains(@aria-label, 'Send')]")
                        time.sleep(random_delay)

                        send_button.click()
                        print('connection request sent')
                        print('connection modal closed')
                        time.sleep(random_delay)
                except Exception as e:
                    print('connection_modal modal not found')
                    print(e)

                print('waiting delay')
                time.sleep(random_delay)
        except Exception as e:
            print(f"Connect button not found for {name}. Skipping connection request.")
            print(e)
            time.sleep(2)

            more_actions_button.click()

        # Send a follow request
        try:
            try:
                # elements = linkedin_driver.find_elements(By.XPATH,"//button[contains(@aria-label, 'Follow {name}')]")
                # print('follow button elements found: ', elements)
                # follow_button = elements[1] if elements[1] else elements[0]
                # follow_button = WebDriverWait(linkedin_driver, 10+ random_delay).until(expect.element_to_be_clickable((By.XPATH,"//*[contains(@aria-label, 'Follow')]//svg[contains(@data-test-icon, 'add-small')]")))
                # follow_button = WebDriverWait(linkedin_driver, 10+ random_delay).until(expect.element_to_be_clickable((By.XPATH,"//*[contains(@aria-label, 'Follow')]")))
                follow_button = linkedin_driver.find_element(By.XPATH,"//li//*[contains(@aria-label, 'Follow')]")
                WebDriverWait(linkedin_driver, 30).until(expect.visibility_of(follow_button))
                WebDriverWait(linkedin_driver, 30).until(expect.element_to_be_clickable(follow_button))
                follow_button.click()

            except Exception as e:
                print(f"Follow button not found. Try to find the follow button in the more actions dropdown.")
                print(f"Reason: {e}")

                # get more actions dropdown menu
                elements = linkedin_driver.find_elements(By.XPATH,"//button[contains(@aria-label, 'More actions')]")
                print('more actions button elements found: ', elements)
                if len(elements) > 1:
                    more_actions_button = elements[1] if len(elements) > 1 else elements[0]
                else:
                    raise NoSuchElementException("More actions button not found")
                print('more actions button found', more_actions_button)
                
                print('waiting delay')
                time.sleep(random_delay)

                more_actions_button.click()
                print('more actions button clicked')
                time.sleep(random_delay)

                # follow_button = WebDriverWait(linkedin_driver, 10+ random_delay).until(expect.element_to_be_clickable((By.XPATH,"//*[contains(@aria-label, 'Follow')]//svg[contains(@data-test-icon, 'add-small')]")))
                # follow_button = WebDriverWait(linkedin_driver, 10+ random_delay).until(expect.element_to_be_clickable((By.XPATH,"//*[contains(@aria-label, 'Follow')]")))
                follow_button = linkedin_driver.find_element(By.XPATH,"//li//*[contains(@aria-label, 'Follow')]")
                print('follow button found', follow_button)

                # DEBUG
                # highlight_elements(linkedin_driver, [follow_button])
                WebDriverWait(linkedin_driver, 30).until(expect.visibility_of(follow_button))
                WebDriverWait(linkedin_driver, 30).until(expect.element_to_be_clickable(follow_button))
                follow_button.click()
                time.sleep(random_delay)

                print('follow button clicked')

                print('waiting delay')
                time.sleep(random_delay)
        except Exception as e:
            print(f"Follow button not found for {name}. Skipping follow action.")
            print(e)
            more_actions_button.click()
            time.sleep(random_delay)

        
        print('waiting delay')
        time.sleep(random_delay)
    except Exception as e:
        print(f"An error occurred sending a Linkedin message to {name}.")
        print(e)
    # Do not quit the driver to keep it open for the next task
    # linkedin_driver.quit()


def start_gmail():

    global gmail_driver

    if not gmail_driver:
        # Set up Selenium WebDriver for Gmail
        gmail_driver = webdriver.Chrome()

    # Log in to Gmail (replace EMAIL and PASSWORD with your Gmail credentials)
    gmail_driver.get("https://mail.google.com")
    time.sleep(long_random_delay)

    user_input = gmail_driver.find_element(By.ID, "identifierId")
    user_input.send_keys(env_vars["EMAIL_ADDRESS"])
    user_input.send_keys(Keys.ENTER)
    time.sleep(random_delay)

    password_input = gmail_driver.find_element(By.NAME, "Passwd")
    password_input.send_keys(env_vars["EMAIL_PASSWORD"])
    password_input.send_keys(Keys.ENTER)
    time.sleep(long_random_delay) # Wait for Gmail to load

def send_email(name, email, subject, message_template: str):

    global did_send_message
    global gmail_driver

    try: 
        gmail_driver.maximize_window()
        time.sleep(2)

        # close promo popups
        try: 
            popup = gmail_driver.find_element(By.XPATH, "//*[contains(@class, 'bjd anN ahP')]")
            popup.find_element(By.XPATH, ".//*[contains(@aria-label, 'Close')]").click()
            print('Promo popups closed')
            time.sleep(random_delay)
        except Exception as e:
            print('Promo popups not found')
            print(e)

        # close Notifications popup
        try: 
            popup = gmail_driver.find_element(By.XPATH, "//div[@class='ajR bnn']//*[contains(text(), 'Enable desktop notifications')]")
            popup.find_element(By.XPATH, ".//*[contains(@class, 'bBe')]").click()
            print('Notifications popup closed')
            time.sleep(random_delay)
        except Exception as e:
            print('Notifications popup not found')
            print(e)

        print(f"Sending email to {name}")
        message = message_template.format(name=name)

        # Compose and send email
        compose_button = WebDriverWait(gmail_driver, 10).until(expect.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'T-I') and contains(@class, 'T-I-KE') and contains(@class, 'L3')]")))
        compose_button.click()

        time.sleep(random_delay)
        print(f"with the following subject: {subject}")
        print(f"with the message content: {message}")

        # add recipient email
        gmail_driver.find_element(By.XPATH, "//input[contains(@aria-label, 'To recipients')]").send_keys(email)
        time.sleep(2)

        # add subject
        gmail_driver.find_element(By.NAME, "subjectbox").send_keys(subject)
        time.sleep(2)

        # prepend message, add new line, add existing message
        editable_message_div = WebDriverWait(gmail_driver, 10).until(expect.element_to_be_clickable((By.CSS_SELECTOR, "div.Am.Al.editable.LW-avf")))
        editable_message_div.click()

        # Highlight all the content (Ctrl+A or Command+A)
        editable_message_div.send_keys(Keys.COMMAND, 'a')
        time.sleep(1)

        # Copy the highlighted content to the clipboard (Ctrl+C or Command+C)
        editable_message_div.send_keys(Keys.COMMAND, 'c')
        time.sleep(1)

        # Clear content and formatting
        editable_message_div.send_keys(Keys.BACK_SPACE)
        editable_message_div.send_keys(Keys.BACK_SPACE)
        time.sleep(1)

        # Send your custom message
        editable_message_div.send_keys(message)
        
        # Paste the clipboard content back (Ctrl+V or Command+V)
        editable_message_div.send_keys(Keys.COMMAND, 'v')
        # THIS
        # Use JavaScript to prepend the text as the first child of the parent element
        # gmail_driver.execute_script("""
        #     var div = arguments[0];
        #     var prependText = arguments[1];
        #     div.innerText = prependText + div.innerText;
        # """, editable_message_div, message)

        # OR THIS
        # Use JavaScript to get existing content
        # existing_content = gmail_driver.execute_script("return arguments[0].innerHTML;", editable_message_div)

        # # Prepare the new content
        # new_content = message + existing_content
        # time.sleep(3)

        # # Clear existing content
        # editable_message_div.clear()  # This might not work for a contenteditable div, but try it
        # time.sleep(3)

        # Send the new content
        # editable_message_div.send_keys(message)
        time.sleep(3)

        # send
        gmail_driver.find_element(By.CSS_SELECTOR, "div.T-I.J-J5-Ji.aoO.T-I-atl.L3").click()
        time.sleep(long_random_delay)

        print(f"Successfully emailed {name} at {email}")
        
        did_send_message = True
        
        # Do not quit the driver to keep it open for the next task
        # gmail_driver.quit()
    except Exception as e:
        print(f"An occurred while emailing {name} at {email}.")
        print(e)


def send_messages(data, messaged_contacts, subject, message_template, isLinkedInMode=False):
    
    global did_send_message
    global MAX_MESSAGE_TIME
    
    start_time: float = time.time()

    while time.time() - start_time < MAX_MESSAGE_TIME:
        try:
            print(f"{(MAX_MESSAGE_TIME - (time.time() - start_time)) // 60} minutes left in this message session")
            for record in data:
                did_send_message = False

                recipient_name = get_full_name(record)

                recipient_linkedin = None
                recipient_email = None

                for key, value in record.items():
                    if 'linkedin' in key.lower():
                        recipient_linkedin = value
                    if key.lower() == 'email':
                        recipient_email = value
                

                print("Next contact: ", recipient_name)

                if recipient_name and recipient_linkedin:
                    print("Linkedin url: ", recipient_linkedin)
                    if isLinkedInMode:
                        start_linkedin()
                        send_linkedin_message(recipient_linkedin, recipient_name, subject, message_template)
                    if not isLinkedInMode:
                        print("LinkedIn mode is disabled. Skipping LinkedIn message.")

                if recipient_email:
                    print("Email address: ", recipient_email)
                    if not gmail_driver:
                        start_gmail()
                    send_email(recipient_name, recipient_email, subject, message_template)
                    
                if not recipient_linkedin and not recipient_email:
                    print("No linked or email contact information for this record.")

                if did_send_message:
                    # add to messaged contacts
                    messaged_contacts.append(Contact(name=recipient_name, email=recipient_email, linkedin=recipient_linkedin, organization=record.get('Company'), date_contacted = datetime.now().strftime('%m/%d/%Y'), website=record.get('Website'), location=record.get('City')))
        except Exception as e:
            print(f"An error occurred while messaging contact: {recipient_name}")
            print(e)
            raise e

def get_full_name(record):
    # List of possible keys for first name and last name
    first_name_keys = ["name", "first name", "First Name", "first_name", "firstname", "firstName"]
    last_name_keys = ["last name", "last name", "Last Name", "last_name", "lastname", "lastName"]

    # Initialize first name and last name
    first_name = None
    last_name = None

    # Check for first name
    for key in first_name_keys:
        if key in record:
            first_name = record[key]
            if key == "name":
                return first_name
            break

    # Check for last name
    for key in last_name_keys:
        if key in record:
            last_name = record[key]
            break

    # Concatenate first name and last name
    full_name = f"{first_name} {last_name}" if first_name and last_name else None
    return full_name

def highlight_elements(driver, elements):

    print('highlighting elements')
    highlight_style = "border: 2px solid red;"

    for element in elements:
        # Apply the highlight style
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, highlight_style)
        time.sleep(2)  # Wait for a second to see the highlight effect
        # Remove the highlight style
        driver.execute_script("arguments[0].setAttribute('style', '');", element)