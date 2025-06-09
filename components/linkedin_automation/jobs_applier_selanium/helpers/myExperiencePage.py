from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from components.linkedin_automation.jobs_applier_selanium.helpers.LoginPage import click_apply_buttons
from components.linkedin_automation.jobs_applier_selanium.data.configurations import workexperience_field_mapping, certification_field_mapping, education_field_mapping, my_experience_data, language_field_mapping, resume_field_mapping

import time

# -------------------- Helper to delete files ---------------------------------
def delete_existing_files(driver, elem_name, log_base="logs/job_application_logs/logs_text/", echo=False):
    #---------------------{Find all delete buttons using the specified XPath}----------------------
    try: delete_buttons = driver.find_elements(By.XPATH, f"//div[contains(@data-fkit-id, '-{elem_name}')]//button[@type='button' and @data-automation-id='delete-file']")
    #---------------------{If finding delete buttons fails, exit the function}----------------------
    except: return

    #---------------------{Check if no delete buttons were found}----------------------
    if not delete_buttons:
        print(f"⚠️ No files found to delete in '{elem_name}'")
        return

    #---------------------{Iterate over all delete buttons found}----------------------
    for btn in delete_buttons:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
            WebDriverWait(driver, 2).until(EC.staleness_of(btn))
            print(f"✔ Deleted a file in '{elem_name}'")
        except TimeoutException: print(f"⚠️ Timeout while trying to delete file in '{elem_name}'")
        except Exception: print(f"⚠️ Could not delete file in '{elem_name}'")


# -------------------- Helper to delete selected pills in multiselect ---------------------------------
def delete_selected_pills(driver, elem_name, log_base="logs/job_application_logs/logs_text/", echo=False):
    #---------------------{Try to find all delete icons within the container for pills}----------------------
    try: delete_icons = driver.find_elements(By.XPATH, f"//div[contains(@data-automation-id, '-{elem_name}')]//div[@data-automation-id='DELETE_charm']")
    #---------------------{If the search for delete icons fails, exit the function}----------------------
    except: return

    #---------------------{Check if no selected pills were found}----------------------
    if not delete_icons:
        print(f"⚠️ No selected pills found in '{elem_name}'")
        return

    #---------------------{Iterate over each delete icon found}----------------------
    for icon in delete_icons:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
            #---------------------{Click the delete icon to remove the selected pill}----------------------
            driver.execute_script("arguments[0].click();", icon)
            print(f"✔ Cleared a selected value in '{elem_name}'")
        except Exception: print(f"⚠️ Could not delete pill in '{elem_name}'")


# -------------------- select multivalues ---------------------------------
def click_multiselect(driver, wait, element, elem_name, value):    
    try:
        #---------------------{Find the virtualized container for dropdown options}----------------------
        container = driver.find_element(By.CSS_SELECTOR, "div.ReactVirtualized__Grid")

        #---------------------{Build an XPath expression to find the dropdown option with the given value}----------------------
        dropdown_option_xpath = (
            f"//li[@role='option']//div[normalize-space()='{value}']"
            f" | //div[@role='option']//div[@data-automation-id='promptOption' and @data-automation-label='{value}']"
        )
        
        last_scroll_top = -1

        #---------------------{Loop to scroll and search until option is found or scrolling stops}----------------------
        while True:
            try:
                #---------------------{Try to find the dropdown option in the container}----------------------
                dropdown_option = container.find_element(By.XPATH, dropdown_option_xpath)
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_option)
                time.sleep(1)

                #---------------------{Check the selection state of the option}----------------------
                is_selected = dropdown_option.get_attribute("aria-selected") or dropdown_option.get_attribute("data-automation-selected")

                #---------------------{If selected, print success and exit loop}----------------------
                if is_selected.lower() == "true":                    
                    print(f"✔ Selected multiselect option '{value}' for element '{elem_name}'.")
                    break

                #---------------------{Otherwise, click the option to select it}----------------------
                driver.execute_script("arguments[0].click();", dropdown_option)
                time.sleep(1)
            #---------------------{If dropdown option is not found at this scroll position, continue scrolling}----------------------
            except Exception: pass

            #---------------------{Keep scrolling downwards to reveal more options}----------------------
            current_scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 50;", container)
            time.sleep(0.2)
            new_scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)

            #---------------------{If no new scroll position was reached, exit loop}----------------------
            if new_scroll_top == current_scroll_top or new_scroll_top == last_scroll_top:
                print(f"⚠️ Could not select option '{value}' for element '{elem_name}' after scrolling.")
                break

            last_scroll_top = new_scroll_top

    except Exception: print(f"⚠️ Could not select option '{value}' for element '{elem_name}'.")


# -------------------- Helper Function interact_with ---------------------------------
def interact_with(driver, wait, by, elem_name, value, field_key, elem_type, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        element = None

        #---------------------{Handle text elements}----------------------
        if elem_type == "text":
            try: element = wait.until(EC.visibility_of_element_located((by, elem_name)))
            except TimeoutException: print(f"⚠️ Timeout: Text element '{elem_name}' not found.")
        #---------------------{Handle checkbox, listbox, multiselect elements}----------------------
        elif elem_type in ["checkbox", "listbox", "multiselect"]:
            try: element = wait.until(EC.presence_of_element_located((by, elem_name)))
            except TimeoutException: print(f"⚠️ Timeout: Element '{elem_name}' not found.")
        #---------------------{Handle file elements}----------------------
        elif elem_type == "file":
            try: element = wait.until(EC.presence_of_element_located((by, elem_name)))
            except TimeoutException: print(f"⚠️ Timeout: File input '{elem_name}' not found.")
        #---------------------{Handle date elements}----------------------
        elif elem_type == "date":
            try:
                display_xpath = f"{elem_name}//div[contains(@id,'{field_key}-display')]"
                input_xpath = f"{elem_name}//input[contains(@id,'{field_key}-input')]"
                try:
                    #---------------------{Wait until display element is clickable and click it}----------------------
                    display_element = wait.until(EC.element_to_be_clickable((By.XPATH, display_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", display_element)
                    driver.execute_script("arguments[0].click();", display_element)
                except TimeoutException: print(f"⚠️ Timeout: Display element '{elem_name}' not found or not clickable.")
                
                #---------------------{Wait until input element is visible}----------------------
                element = wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
            except TimeoutException: print(f"⚠️ Timeout: Date input '{elem_name}' not found.")
        #---------------------{Otherwise break the operation}----------------------
        else:
            print(f"⚠️ Unknown element type '{elem_type}' for {elem_name}. Skipped.")
            return None

        #---------------------{Scroll element into view}----------------------
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

        #---------------------{Handle different element type actions}----------------------
        #---------------------{Handle checkbox actions}----------------------
        if elem_type == "checkbox":
            return element        
        #---------------------{Handle file actions}----------------------
        elif elem_type == "file":
            #---------------------{Delete any existing files in field}----------------------
            delete_existing_files(driver, field_key, log_base, echo)
            try:
                #---------------------{Make the file input field visible and upload the file}----------------------
                driver.execute_script("""
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].style.opacity = '1';
                    arguments[0].style.position = 'static';
                """, element)
                element.send_keys(value)
                time.sleep(0.5)
                print(f"✔ Uploaded file: {value}")
            except Exception: print(f"⚠️ Could not upload file: {value}")
        #---------------------{Handle multiselect actions}----------------------
        elif elem_type == "multiselect":
            #---------------------{Delete any existing selected pills in multiselect}----------------------
            delete_selected_pills(driver, field_key, log_base, echo)
            try:
                if isinstance(value, list):
                    #---------------------{Loop through each value in the list}----------------------
                    for val in value:
                        driver.execute_script("arguments[0].click();", element)
                        #---------------------{Reset the input value using JS}----------------------
                        driver.execute_script("arguments[0].value = '';", element)
                        time.sleep(1)  # Let React register

                        #---------------------{Send the value and press ENTER to search}----------------------
                        element.send_keys(val)
                        element.send_keys(Keys.ENTER)
                        time.sleep(1)

                        #---------------------{Manually update value via JS}----------------------
                        driver.execute_script(f"arguments[0].value = '{val}';", element)
                        # click_multiselect(driver, wait, element, field_key, value)

                        time.sleep(1)
                        element.send_keys(Keys.TAB)
                else:
                    #---------------------{Single value case for multiselect}----------------------
                    element.send_keys(value)
                    time.sleep(0.1)
                    element.send_keys(Keys.ENTER)
                    click_multiselect(driver, wait, element, field_key, value)
                print(f"✔ Filled {field_key} with '{value}'")
            except Exception: print(f"⚠️ Could not interact with multiselect: {value}")
        #---------------------{Handle text, listbox, date actions}----------------------
        elif elem_type in ["text", "listbox", "date"]:
            try:
                if elem_type == "date": 
                    #---------------------{Clear existing value in date input}----------------------
                    element.clear()
                else:
                    #---------------------{Clear text input field}----------------------
                    driver.execute_script("arguments[0].click();", element)
                    element.send_keys(Keys.CONTROL + 'a')
                    element.send_keys(Keys.DELETE)
                time.sleep(1)
                #---------------------{Send the new value to the element}----------------------
                element.send_keys(value)

                #---------------------{Handle pressing ENTER or TAB as needed}----------------------
                if elem_type == "listbox": element.send_keys(Keys.ENTER)
                elif elem_type != "date": element.send_keys(Keys.TAB)

                print(f"✔ Filled {elem_name} with '{value}'")
            except Exception: print(f"⚠️ Could not fill element '{elem_name}' with value '{value}'.")
    except Exception:
        print(f"⚠️ Could not process interact_with for element '{elem_name}'.")


# -------------------- fill_experience_or_education_sections ---------------------------------
def fill_experience_or_education_sections(driver, wait, short_wait, data_list, section_name, field_mapping, heading="My Experience", log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        #---------------------{Check if heading includes skill or resume}----------------------
        check_headings = "skill" not in heading.lower() and "resume" not in heading.lower()

        #---------------------{Locate the heading element}----------------------
        xpath_base = f"//h3[contains(text(), '{heading}')]"
        if not click_apply_buttons(driver, wait, xpath_base):
            print(f"Unable to find {heading}. Continuing with the next part")
            return None

        #---------------------{If no skill or resume in headings, try clicking Add button}----------------------
        if check_headings:
            try:
                add_button_xpath = f"//div[@role='group' and @aria-labelledby='{section_name}section']//button[@data-automation-id='add-button' and (text()='Add')]"
                click_apply_buttons(driver, wait, add_button_xpath)
                print(f"✔ Clicked 'Add' for {section_name}.")
            except Exception:
                print(f"⚠️ Failed to click 'Add' button for {section_name}.")

        #---------------------{Iterate through the data list to fill each section}----------------------
        for index, entry in enumerate(data_list, start=1):
            try:
                #---------------------{Check if section exists or needs adding}----------------------
                if check_headings:
                    section_xpath = f"//div[@role='group' and @aria-labelledby='{section_name}{index}-panel']"
                    short_wait.until(lambda d: True)
                    try:
                        h4_elements = driver.find_elements(By.XPATH, f"//h4[@id='{section_name}{index}-panel']")
                        if h4_elements and h4_elements[0].is_displayed():
                            print(f"✔ {section_name}{index} section already exists. Skipping adding.")
                        else:
                            add_another_xpath = f"//div[@role='group' and @aria-labelledby='{section_name}section']//button[contains(@data-automation-id, 'add-button') and (text()='Add Another')]"
                            if click_apply_buttons(driver, wait, add_another_xpath):
                                print(f"✔ Clicked 'Add Another' for {section_name}{index}.")
                    except Exception:
                        print(f"⚠️ Error clicking 'Add Another' for {section_name}{index}.")
                else: 
                    section_xpath = f"//div[@role='group' and @aria-labelledby='{section_name}section']"

                #---------------------{Iterate through each field key in field mapping}----------------------
                for field_key, field_type in field_mapping.items():
                    try:
                        #---------------------{Handle date field separately}----------------------
                        if field_type == "date":
                            date_field_name = field_key.split('-')[0]
                            date_value = entry.get(date_field_name, "")
                            if not date_value: continue
                            day, month, year = date_value.split("/")
                            value = {"dateSectionDay": day, "dateSectionMonth": month, "dateSectionYear": year}.get(field_key.split('-')[-1], "")
                            if not value: continue

                            interact_with(driver=driver, wait=short_wait, by=By.XPATH, elem_name=section_xpath, value=value, field_key=field_key, elem_type="date", log_base=log_base, echo=echo)
                        #---------------------{Handle file field type}----------------------
                        elif field_type == "file":
                            element_xpath = f"{section_xpath}//input[@data-automation-id='file-upload-input-ref' and @type='file']"
                            interact_with(driver=driver, wait=wait, by=By.XPATH, elem_name=element_xpath, value=entry[field_key], field_key=field_key, elem_type="file", log_base=log_base, echo=echo)
                        #---------------------{Handle listbox field type}----------------------
                        elif field_type == "listbox":
                            element_xpath = f"{section_xpath}//button[contains(@id,'--{field_key}') and contains(@name,'{field_key}')]"
                            interact_with(driver=driver, wait=wait, by=By.XPATH, elem_name=element_xpath, value=entry[field_key], field_key=field_key, elem_type="listbox", log_base=log_base, echo=echo)
                        #---------------------{Handle multiselect field type}----------------------
                        elif field_type == "multiselect":
                            element_xpath = f"{section_xpath}//input[contains(@id,'--{field_key}')]"
                            interact_with(driver=driver, wait=wait, by=By.XPATH, elem_name=element_xpath, value=entry[field_key], field_key=field_key, elem_type="multiselect", log_base=log_base, echo=echo)
                        #---------------------{Handle checkbox field type and click if needed}----------------------
                        elif field_type == "checkbox":
                            element_xpath = f"{section_xpath}//input[@type='checkbox' and contains(@id,'--{field_key}') and contains(@name,'{field_key}')]"
                            checkbox = interact_with(driver=driver, wait=short_wait, by=By.XPATH, elem_name=element_xpath, value=entry[field_key], field_key=field_key, elem_type="checkbox", log_base=log_base, echo=echo)
                            if entry[field_key] != (checkbox.get_attribute("aria-checked") == "true"):
                                driver.execute_script("arguments[0].click();", checkbox)
                                print(f"✔ Set '{field_key}' checkbox for {section_name}{index}.")
                        #---------------------{Handle other text field types}----------------------
                        else:
                            # Not worked because it was school and not schoolName
                            element_xpath = f"{section_xpath}//textarea[contains(@id,'--{field_key}')] | {section_xpath}//input[contains(@id,'--{field_key}')]"
                            interact_with(driver=driver, wait=wait, by=By.XPATH, elem_name=element_xpath, value=entry[field_key], field_key=field_key, elem_type=field_type, log_base=log_base, echo=echo)
                        print(f"✔ Finished {section_name}{index}.")
                    except Exception:
                        print(f"⚠️ Could not fill field {field_key} for {section_name}{index}.")
            except Exception:
                print(f"⚠️ Error filling {section_name}{index}.")
    except Exception:
        print("⚠️ Unexpected error in fill_experience_or_education_sections.")


# -------------------- my_experience_form ---------------------------------
def my_experience_form(driver, wait, short_wait, my_experience_data, retry_count=0, max_retries=1, log_base="logs/job_application_logs/logs_text/", echo=False):
    try:
        #---------------------{Start the page 2 filling process}----------------------
        print("🌟 Starting Page 2 filling process...")
        time.sleep(5)

        #---------------------{Locate the 'My Experience' tab heading}----------------------
        xpath_base = f"//h2[contains(text(), 'My Experience')]"
        if not click_apply_buttons(driver=driver, wait=wait, xpath=xpath_base, log_base=log_base, echo=echo):
            print("❌ Unable to find my experience tab.")
            return None

        #---------------------{Fill the Work Experience section}----------------------
        fill_experience_or_education_sections(driver=driver, wait=wait, short_wait=short_wait, data_list=my_experience_data.get("workExperience", []), section_name="Work-Experience-", field_mapping=workexperience_field_mapping, heading="Work Experience", log_base=log_base, echo=echo)
        
        #---------------------{Fill the Education section}----------------------
        fill_experience_or_education_sections(driver=driver, wait=wait, short_wait=short_wait, data_list=my_experience_data.get("education", []), section_name="Education-", field_mapping=education_field_mapping, heading="Education", log_base=log_base, echo=echo)
        
        #---------------------{Fill the Certifications section}----------------------
        fill_experience_or_education_sections(driver=driver, wait=wait, short_wait=short_wait, data_list=my_experience_data.get("certifications", []), section_name="Certifications-", field_mapping=certification_field_mapping, heading="Certifications", log_base=log_base, echo=echo)
        
        #---------------------{Fill the Languages section}----------------------
        fill_experience_or_education_sections(driver=driver, wait=wait, short_wait=short_wait, data_list=my_experience_data.get("languages", []), section_name="Languages-", field_mapping=language_field_mapping, heading="Languages", log_base=log_base, echo=echo)
        
        #---------------------{Fill the Skills section}----------------------
        # fill_experience_or_education_sections(driver=driver, wait=wait, short_wait=short_wait, data_list=my_experience_data.get("skills-section", section_name=[]), "Skills-", field_mapping=skill_field_mapping, heading="Skills", log_base=log_base, echo=echo)

        #---------------------{Fill the Resume/CV section}----------------------
        fill_experience_or_education_sections(driver=driver, wait=wait, short_wait=short_wait, data_list=my_experience_data.get("resume", []), section_name="Resume/CV-", field_mapping=resume_field_mapping, heading="Resume/CV", log_base=log_base, echo=echo)

    except Exception:
        #---------------------{Handle errors during execution}----------------------
        print("⚠️ Error occurred during my_experience_form execution.")
        
        #---------------------{Check retry count and retry if allowed}----------------------
        if retry_count < max_retries:
            print(f"🔄 Retrying My Experience Form (attempt {retry_count + 1}/{max_retries})...")
            time.sleep(2)
            try:
                #---------------------{Navigate back to retry the form}----------------------
                if click_apply_buttons(driver=driver, wait=wait, xpath="//button[@data-automation-id='pageFooterNextButton' and contains(text(), 'Back')]", log_base=log_base, echo=echo):
                    print("🔄 Clicked Back button.")
                time.sleep(2)
                
                #---------------------{Try to click 'Save and Continue' to refresh the page}----------------------
                if click_apply_buttons(driver=driver, wait=wait, xpath="//button[@data-automation-id='pageFooterNextButton' and contains(text(), 'Save and Continue')]", log_base=log_base, echo=echo):
                    print("🔄 Clicked Save and Continue button.")
                time.sleep(2)
            except Exception:
                print(f"⚠️ Retry navigation error")
            
            #---------------------{Recursive call with incremented retry count}----------------------
            my_experience_form(driver=driver, wait=wait, short_wait=short_wait, my_experience_data=my_experience_data, log_base=log_base, echo=echo, retry_count=retry_count + 1, max_retries=max_retries)
        else:
            print("❌ Maximum retries reached for My Experience Form.")