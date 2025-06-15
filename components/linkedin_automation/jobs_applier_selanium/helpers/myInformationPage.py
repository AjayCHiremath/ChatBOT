from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time

from components.linkedin_automation.jobs_applier_selanium.data.configurations import my_information_data
from components.linkedin_automation.jobs_applier_selanium.helpers.LoginPage import click_apply_buttons
from components.linkedin_automation.web_scrapper_selanium.helpers.TerminateProcess import exit_if_stopped


#-------------------------------------------MY INFORMATION PAGE---------------------------------------------
#-------------------{Helper function to locate an element by trying multiple IDs}---------------------------
def interact_with(driver, wait, condition, by, xpath, id_option, log_base="logs/job_application_logs/logs_text/", echo=False):
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


# -------------------- Helper to delete selected pills in multiselect ---------------------------------
def delete_selected_pills(driver, used_id, echo=False):
    container = None

    # Try finding container by data-automation-id-prompt
    try:
        container = driver.find_element(By.XPATH, f"//div[@data-automation-id='multiSelectContainer'][@data-automation-id-prompt='{used_id}']")
        print(f"✔ Found container by data-automation-id-prompt='{used_id}'")
    except:
        print(f"⚠️ Could not find by data-automation-id-prompt='{used_id}'")

    # Fallback: try data-fkit-id
    if not container:
        try:
            container = driver.find_element(By.XPATH, f"//div[@data-fkit-id='{used_id}']//div[@data-automation-id='multiSelectContainer']")
            print(f"✔ Found container by data-fkit-id='{used_id}'")
        except:
            print(f"⚠️ Could not find by data-fkit-id='{used_id}'")

    # Fallback: try formField id
    if not container:
        try:
            container = driver.find_element(By.XPATH, f"//div[@data-automation-id='formField-{used_id.split('--')[-1] if '--' in used_id else used_id}']//div[@data-automation-id='multiSelectContainer']")
            print(f"✔ Found container by formField id='{used_id}'")
        except:
            print(f"❌ Could not find container for '{used_id}'. Skipping.")

    # Now find all delete icons within that container
    delete_icons = container.find_elements(By.XPATH, ".//div[@data-automation-id='DELETE_charm']")
    if not delete_icons:
        if echo:
            print(f"⚠️ No selected pills found in '{used_id}'")
        return

    for icon in delete_icons:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
            driver.execute_script("arguments[0].click();", icon)
            if echo:
                print(f"✔ Cleared a selected value in '{used_id}'")
        except Exception as e:
            if echo:
                print(f"⚠️ Could not delete pill in '{used_id}': {e}")

#-------------------{Handler for text fields}---------------------------
def handle_text(driver, wait, all_ids, field_id, value, retry, needs_done=False, log_base="logs/job_application_logs/logs_text/", echo=False):
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
                # Clear value
                element.clear()
                delete_selected_pills(driver, used_id)

            element.send_keys(Keys.CONTROL + 'a')
            element.send_keys(Keys.DELETE)
            element.send_keys(value)

            # Handle special case for div-type elements
            element.send_keys(Keys.ENTER)
            time.sleep(0.5)

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
                # Clear value
                element.clear()
                delete_selected_pills(driver, used_id)

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
                used_id = id_option
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
                used_id = id_option
                break

        if not cleared:
            print(f"⚠️ No matching element found for field_id '{field_id}'. Skipping.")
            return False

        is_checked = element.is_selected()
        if value != is_checked:
            driver.execute_script("arguments[0].click();", element)
        print(f"{'🔁 Retried' if retry else '✔'} Checkbox '{used_id}' set to '{value}'")
        return True

    except Exception:
        print(f"⚠️ Unexpected error in handle_checkbox")
    return False

#-------------------{Dispatcher to call the correct handler based on field type}---------------------------
def try_field_all_ids(driver, wait, field_id, config, retry=False, log_base="logs/job_application_logs/logs_text/", echo=False):
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
        
        # if failed_fields:
        #     print("\n🔁 Retrying failed fields...\n")
        #     for field_id, config in failed_fields.items():
        #         if not try_field_all_ids(driver, wait, field_id, config, True, log_base, echo):
        #             print(f"⚠️ Field '{field_id}' still failed after retry.")

        return failed_fields
    except Exception:
        print("⚠️ Unexpected error in my_information_page.")
    return {}