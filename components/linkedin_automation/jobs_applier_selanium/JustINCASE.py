#-------------------------------------------MY INFORMATION PAGE---------------------------------------------
#-------------------{Helper function to locate an element by trying multiple IDs}---------------------------
def interact_with(driver, wait, condition, by, xpath, id_option, log_base="logs/job_application_logs/logs_text/", echo=False):
    """
    Try to locate an element using the provided XPath and condition. Scrolls into view if found.
    Returns (element, True) if found, else (None, False).
    """
    try:
        print(f"🔍 Trying XPath: {xpath}")
        try:
            try:
                element = wait.until(condition((by, xpath)))
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.2)
                    return element, True
                except Exception:
                    print(f"⚠️ Could not scroll element or interact with element for ID '{id_option}'.")
                    return None, False
            except TimeoutException:
                print(f"⚠️ Timeout: Element with XPath '{xpath}' (ID option '{id_option}') not found.")
                return None, False
            except Exception:
                print(f"⚠️ Unexpected error while waiting for element with XPath '{xpath}' (ID option '{id_option}').")
                return None, False
        except Exception:
            print(f"⚠️ Unexpected error while creating short_wait for XPath '{xpath}' (ID option '{id_option}').")
            return None, False
    except Exception:
        print(f"❌ Unexpected error while locating element by XPath for ID '{id_option}'.")
        return None, False


#-------------------{Handler for text fields}---------------------------
def handle_text(driver, wait, all_ids, field_id, value, retry, needs_done=False, log_base="logs/job_application_logs/logs_text/", echo=False):
    """
    Handles filling text fields. Tries multiple IDs until one is found.
    If 'needs_done' is True, clears and resets the field.
    """
    used_id = cleared = None
    try:
        for id_option in all_ids:
            for tag in ["input", "div"]:
                if tag == "input":
                    xpath = f"//{tag}[contains(@data-automation-id, '{id_option}') or contains(@id, '{id_option}')]"
                else:
                    xpath = f"//{tag}[contains(@data-automation-id-prompt, '{id_option}')]"
                element, cleared = interact_with(driver, wait, EC.presence_of_element_located, By.XPATH, xpath, id_option, log_base, echo)
                if cleared:
                    used_id = id_option
                    break  # Element found, exit inner loop
            if cleared:
                break  # Element found, exit outer loop
        else:
            # No element found, skip this field
            print(f"⚠️ No matching element found for field_id '{field_id}'. Skipping.")
            return False

        try:
            if needs_done:
                # Clear value if needed
                element.clear()
                driver.execute_script("arguments[0].value = '';", element)

            element.send_keys(Keys.CONTROL + 'a')
            element.send_keys(Keys.DELETE)
            element.send_keys(value)

            # Handle special case for div-type elements
            if tag == "div":
                element.send_keys(Keys.ARROW_DOWN)
                element.send_keys(Keys.ENTER)
                time.sleep(1)

            element.send_keys(Keys.TAB)
            print(f"{'🔁 Retried' if retry else '✔'} Filled text '{used_id}' with '{value}'")

            if needs_done:
                try:
                    done_button = "//button[.//span[text()='Done']]"
                    if not click_apply_buttons(driver, wait, done_button):
                        print("Unable to find Done Button.")
                except:
                    pass

            return True
        except Exception:
            print(f"⚠️ Could not fill text field '{used_id}'.")
    except Exception:
        print("⚠️ Unexpected error in handle_text.")
    return False

#-------------------{Handler for listbox (dropdown) fields}---------------------------
def handle_listbox(driver, wait, all_ids, field_id, value, retry, needs_done=False, log_base="logs/job_application_logs/logs_text/", echo=False):
    """
    Handles selecting an option from a dropdown (listbox).
    """
    try:
        used_id = cleared = None
        for id_option in all_ids:
            xpath = f"//button[contains(@id, '{id_option}') or contains(@data-automation-id, '{id_option}')] | //input[contains(@id, '{id_option}') or contains(@data-automation-id, '{id_option}')]"
            element, cleared = interact_with(driver, wait, EC.presence_of_element_located, By.XPATH, xpath, id_option, log_base, echo)
            if cleared:
                used_id = id_option
                break  # Element found, exit loop
        else:
            print(f"⚠️ No matching element found for field_id '{field_id}'. Skipping.")
            return False

        try:
            if needs_done:
                element.clear()
                driver.execute_script("arguments[0].value = '';", element)

            driver.execute_script("arguments[0].click();", element)
            time.sleep(0.3)
            element.send_keys(value)
            time.sleep(1)
            element.send_keys(Keys.ENTER)
            print(f"{'🔁 Retried' if retry else '✔'} Selected '{value}' in listbox '{used_id}'")

            if needs_done:
                try:
                    done_button = "//button[.//span[text()='Done']]"
                    if not click_apply_buttons(driver, wait, done_button):
                        print("Unable to find Done Button.")
                except:
                    pass

            return True
        except Exception:
            print(f"⚠️ Could not interact with listbox '{used_id}'.")
    except Exception:
        print("⚠️ Unexpected error in handle_listbox.")
    return False

#-------------------{Handler for radio button fields}---------------------------
def handle_radio(driver, wait, all_ids, field_id, value, retry, log_base="logs/job_application_logs/logs_text/", echo=False):
    """
    Handles selecting a radio button by label.
    """
    try:
        used_id = cleared = None
        for id_option in all_ids:
            for tag in ['div']:  # Radios are often in <div> wrappers
                xpath = f"//{tag}[contains(@data-automation-id, '{id_option}') or contains(@id, '{id_option}')]"
                element, cleared = interact_with(driver, wait, EC.presence_of_element_located, By.XPATH, xpath, id_option, log_base, echo)
                if cleared:
                    used_id = id_option
                    break  # Found element
            if cleared:
                break

        if not cleared:
            print(f"⚠️ No matching element found for field_id '{field_id}'. Skipping.")
            return False

        try:
            radios = element.find_elements(By.XPATH, ".//input[@type='radio']")
            for radio in radios:
                radio_id = radio.get_attribute("id")
                if not radio_id:
                    continue
                try:
                    label_elem = driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                    label_text = label_elem.text.strip().lower()
                    if value.lower() == label_text:
                        try:
                            is_checked = radio.get_attribute("aria-checked") == "true" or radio.is_selected()
                            if is_checked:
                                print(f"{'🔁 Retried' if retry else '✔'} Radio '{label_text}' already selected for '{field_id}'")
                                return True
                            driver.execute_script("arguments[0].scrollIntoView(true);", radio)
                            driver.execute_script("arguments[0].click();", radio)
                            time.sleep(0.5)
                            print(f"{'🔁 Retried' if retry else '✔'} Selected radio '{label_text}' for '{field_id}'")
                            return True
                        except Exception:
                            print(f"⚠️ Could not select radio button '{label_text}'.")
                except Exception:
                    print(f"⚠️ Could not find label for radio id '{radio_id}'.")
            print(f"{'⚠️ Retried' if retry else '❌'} No matching radio label for value '{value}' in '{field_id}'")
        except Exception:
            print(f"⚠️ Could not locate or interact with radios in '{used_id}'.")
    except Exception:
        print("⚠️ Unexpected error in handle_radio.")
    return False

#-------------------{Handler for checkbox fields}---------------------------
def handle_checkbox(driver, wait, all_ids, field_id, value, retry, log_base="logs/job_application_logs/logs_text/", echo=False):
    """
    Handles checking or unchecking a checkbox.
    """
    try:
        used_id = cleared = None
        for id_option in all_ids:
            for tag in ["input", "div"]:
                xpath = f"//{tag}[contains(@data-automation-id, '{id_option}') or contains(@id, '{id_option}')]"
                element, cleared = interact_with(driver, wait, EC.presence_of_element_located, By.XPATH, xpath, id_option, log_base, echo)
                if cleared:
                    used_id = id_option
                    break
            if cleared:
                break

        if not cleared:
            print(f"⚠️ No matching element found for field_id '{field_id}'. Skipping.")
            return False

        is_checked = element.is_selected()
        if value != is_checked:
            driver.execute_script("arguments[0].click();", element)
        print(f"{'🔁 Retried' if retry else '✔'} Checkbox '{used_id}' set to '{value}'")
        return True

    except Exception as e:
        print(f"⚠️ Unexpected error in handle_checkbox: {e}")
    return False

#-------------------{Dispatcher to call the correct handler based on field type}---------------------------
def try_field_all_ids(driver, wait, field_id, config, retry=False, log_base="logs/job_application_logs/logs_text/", echo=False):
    """
    Dispatch function that calls the appropriate handler based on the field type.
    """
    try:
        field_type = config.get("type")
        value = config.get("value")
        all_ids = [field_id] + config.get("alternate_ids", [])
        needs_done = config.get("needs_done_button", False)

        if field_type == "text":
            return handle_text(driver, wait, all_ids, field_id, value, retry, needs_done, log_base, echo)
        elif field_type == "listbox":
            return handle_listbox(driver, wait, all_ids, field_id, value, retry, needs_done, log_base, echo)
        elif field_type == "radio":
            return handle_radio(driver, wait, all_ids, field_id, value, retry, log_base, echo)
        elif field_type == "checkbox":
            return handle_checkbox(driver, wait, all_ids, field_id, value, retry, log_base, echo)
    except Exception:
        print(f"{'⚠️ Retried' if retry else '❌'} Failed to handle '{field_id}' ({field_type})")
    return False

#--------------------my_information_page---------------------------------
def my_information_page(driver, wait, form_data=my_information_data, log_base="logs/job_application_logs/logs_text/", echo=False):
    """
    Main function to fill out the 'My Information' page.
    """
    try:
        driver.refresh()
        time.sleep(5)
        xpath_base = "//h2[contains(text(), 'My Information')]"
        if not click_apply_buttons(driver, wait, xpath_base):
            print("Unable to find my information. Continuing with the next job")
            return None

        failed_fields = {}
        for field_id, config in form_data.items():
            try:
                if not try_field_all_ids(driver, wait, field_id, config, retry=False, log_base=log_base, echo=echo):
                    failed_fields[field_id] = config
            except Exception:
                print(f"⚠️ Error processing field '{field_id}'.")

        return failed_fields
    except Exception:
        print("⚠️ Unexpected error in my_information_page.")
    return {}

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

import time
import pyautogui
import pygame


# === Setup ===
profile = {
    "email": "ramu@gmail.com",
    "password": "SweepEnd4091##",
    "mobie": "+44 7459146448"
}

#------------------ Define dummy data for each field ----------------
my_information_data = {
    "source--source": {
        "type": "listbox",
        "value": "Direct Mail",
        "alternate_ids": [
            "sourceSection_source",
        ],
        "needs_done_button": True 
    },
    "candidateIsPreviousWorker": {
        "type": "radio",
        "value": "No",
        "alternate_ids": [
            "previousWorker_candidateIsPreviousWorker"
        ],
        "needs_done_button": False,
    },
    "country--country": {
        "type": "listbox",
        "value": "United Kingdom",
        "alternate_ids": [
            "countryDropdown",
        ],
        "needs_done_button": True,
    },
    "name--legalName--title": {
        "type": "listbox",
        "value": "Mr",
        "alternate_ids": [
            "legalNameSection_title",
        ],
        "needs_done_button": False,
    },
    "name--legalName--firstName": {
        "type": "text",
        "value": "Don",
        "alternate_ids": [
            "legalNameSection_firstName",
        ],
        "needs_done_button": False,
    },
    "name--legalName--lastName": {
        "type": "text",
        "value": "Aaja",
        "alternate_ids": [
            "legalNameSection_lastName",
        ],
        "needs_done_button": False,
    },
    "name--preferredCheck": {
        "type": "checkbox",
        "value": True,
        "alternate_ids": [
            "preferredNameCheckbox",
        ],
        "needs_done_button": False,
    },
    "name--preferredName--title": {
        "type": "listbox",
        "value": "Dr",
        "alternate_ids": [
            "preferredNameSection_title",
        ],
        "needs_done_button": False,
    },
    "name--preferredName--firstName": {
        "type": "text",
        "value": "Ramu",
        "alternate_ids": [
            "preferredNameSection_firstName",
        ],
        "needs_done_button": False,
    },
    "name--preferredName--lastName": {
        "type": "text",
        "value": "Kaka",
        "alternate_ids": [
            "preferredNameSection_lastName",
        ],
        "needs_done_button": False,
    },
    "address--addressLine1": {
        "type": "text",
        "value": "1423 Main St",
        "alternate_ids": [
            "addressSection_addressLine1",
        ],
        "needs_done_button": False,
    },
    "address--addressLine2": {
        "type": "text",
        "value": "Sui5te 456",
        "alternate_ids": [
            "addressSection_addressLine2",
        ],
        "needs_done_button": False,
    },
    "address--addressLine3": {
        "type": "text",
        "value": "Bu8ilding A",
        "alternate_ids": [
            "addressSection_addressLine3",
        ],
        "needs_done_button": False,
    },
    "address--city": {
        "type": "text",
        "value": "Notting8ham",
        "alternate_ids": [
            "addressSection_city",
        ],
        "needs_done_button": False,
    },
    "address--countryRegion": {
        "type": "listbox",
        "value": "Nottinghamshire",
        "alternate_ids": [
            "addressSection_countryRegion",
        ],
        "needs_done_button": False,
    },
    "address--postalCode": {
        "type": "text",
        "value": "NG1 2DB",
        "alternate_ids": [
            "addressSection_postalCode",
        ],
        "needs_done_button": False,
    },
    "phoneNumber--phoneType": {
        "type": "listbox",
        "value": "Mobile",
        "alternate_ids": [
            "phone-device-type",
        ],
        "needs_done_button": False,
    },
    "phoneNumber--countryPhoneCode": {
        "type": "text",
        "value": "+44",
        "alternate_ids": [
            "country-phone-code",
        ],
        "needs_done_button": True,
    },
    "phoneNumber--phoneNumber": {
        "type": "text",
        "value": "7469137449",
        "alternate_ids": [
            "phone-number",
        ],
        "needs_done_button": False,
    }
}

my_experience_data = {
    "workExperience": [
        {
            "jobTitle": "Software Engineer",
            "companyName": "ABC Corp",
            "location": "Bangalore",
            "currentlyWorkHere": True,
            "startDate": "28/01/2020",
            "endDate": "31/12/2022",
            "roleDescription": "Developed web applications and maintained software systems."
        },
        {
            "jobTitle": "Senior Developer",
            "companyName": "XYZ Ltd",
            "location": "London",
            "currentlyWorkHere": False,
            "startDate": "28/02/2017",
            "endDate": "31/12/2019",
            "roleDescription": "Led a team of developers and implemented enterprise solutions."
        },
        {
            "jobTitle": "Full Stack Developer",
            "companyName": "Tech Solutions",
            "location": "Remote",
            "currentlyWorkHere": False,
            "startDate": "01/03/2015",
            "endDate": "01/01/2017",
            "roleDescription": "Built web and mobile applications for clients worldwide."
        },
        {
            "jobTitle": "Software Intern",
            "companyName": "Startup Inc.",
            "location": "Berlin",
            "currentlyWorkHere": False,
            "startDate": "01/06/2014",
            "endDate": "01/02/2015",
            "roleDescription": "Assisted with developing internal tools and automations."
        },
        {
            "jobTitle": "Junior Developer",
            "companyName": "Innovatech",
            "location": "New York",
            "currentlyWorkHere": False,
            "startDate": "01/01/2013",
            "endDate": "01/05/2014",
            "roleDescription": "Worked on backend systems and contributed to product launches."
        }
    ],
    "education": [
        {
            "schoolName": "University of Nottingham",
            "degree": "Bachelor of Engineering",
            "fieldOfStudy": "Computer Science",
            "gradeAverage": "Merit",
            "startDate": "01/09/2016",
            "endDate": "01/06/2020"
        },
        {
            "schoolName": "University of Brighsa",
            "degree": "Masters",
            "fieldOfStudy": "Mathematics",
            "gradeAverage": "Merit",
            "startDate": "01/09/2016",
            "endDate": "01/06/2020"
        }
    ],
    "certifications": [
        {
            "certification": "AWS Certified Solutions Architect",
            "certificationNumber": "AWS-12345",
            "issuedDate": "15/06/2022",
            "expirationDate": "15/06/2025",
            "attachments": r"C:\Users\ajayc\Downloads\Ajay Hiremath  Resume.pdf"
        },
        {
            "certification": "Google Cloud Certified",
            "certificationNumber": "GCP-67890",
            "issuedDate": "20/03/2021",
            "expirationDate": "20/03/2024",
            "attachments": r"C:\Users\ajayc\Downloads\Ajay Hiremath Other Work Experience.docx"
        }
    ],    
    "languages": ["English"],
    "skills": ["Python","AWS","PySpark"],
    "resume": "/path/to/test_resume.pdf"  # Replace with an actual path.
}

workexperience_field_mapping = {"jobTitle": "text",
                               "companyName": "text",
                               "location": "text",
                               "currentlyWorkHere": "checkbox",
                               "startDate-dateSectionDay": "date",
                               "startDate-dateSectionMonth": "date",
                               "startDate-dateSectionYear": "date",
                               "endDate-dateSectionDay": "date",
                               "endDate-dateSectionMonth": "date",
                               "endDate-dateSectionYear": "date",
                               "roleDescription": "text"
                               }

certification_field_mapping = {"certification": "multiselect",
                        "certificationNumber": "text",
                        "issuedDate-dateSectionDay": "date",
                        "issuedDate-dateSectionMonth": "date",
                        "issuedDate-dateSectionYear": "date",
                        "expirationDate-dateSectionDay": "date",
                        "expirationDate-dateSectionMonth": "date",
                        "expirationDate-dateSectionYear": "date",
                        "attachments": "file"
                        }

education_field_mapping = {"schoolName": "text",
                           "degree": "listbox",
                           "fieldOfStudy": "multiselect",
                           "gradeAverage": "text",
                           "startDate-firstYearAttended-dateSectionDay": "date",
                           "startDate-firstYearAttended-dateSectionMonth": "date",
                           "startDate-firstYearAttended-dateSectionYear": "date",
                           "endDate-lastYearAttended-dateSectionDay": "date",
                           "endDate-lastYearAttended-dateSectionMonth": "date",
                           "endDate-lastYearAttended-dateSectionYear": "date"
                           }
