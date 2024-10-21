from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import time

def select_best_ticket(driver):
    try:
        print("開始選擇票種...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "zone.area-list")))
        available_tickets = driver.find_elements(By.CSS_SELECTOR, ".select_form_a a")
        print(f"找到 {len(available_tickets)} 個可選擇的票種")

        ticket_info = [(ticket, int(''.join(filter(str.isdigit, ticket.text.split('剩餘')[-1]))))
                       for ticket in available_tickets if int(''.join(filter(str.isdigit, ticket.text.split('剩餘')[-1]))) > 0]

        if ticket_info:
            best_ticket, max_remaining = max(ticket_info, key=lambda x: x[1])
            print(f"選擇票種: {best_ticket.text}，剩餘票數: {max_remaining}")
            return best_ticket
        else:
            print("沒有找到可用的票種")
            return None
    except Exception as e:
        print(f"選擇票種時發生錯誤: {e}")
        return None

def click_ticket(driver, ticket):
    driver.execute_script("arguments[0].scrollIntoView(true);", ticket)
    time.sleep(5)

    click_methods = [
        ticket.click,
        lambda: driver.execute_script("arguments[0].click();", ticket),
        lambda: ActionChains(driver).move_to_element(ticket).click().perform()
    ]

    for click_method in click_methods:
        try:
            click_method()
            print("已點擊票種")
            time.sleep(10)
            return True
        except Exception as e:
            print(f"點擊方法失敗: {e}")
    
    return False

def select_quantity(driver, desired_quantity=1):
    try:
        select_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice_']"))
        )
        select = Select(select_element)
        options = select.options
        closest_option = min(options, key=lambda x: abs(int(x.get_attribute("value")) - desired_quantity))
        select.select_by_value(closest_option.get_attribute("value"))
        print(f"選擇張數: {closest_option.text}")
        time.sleep(5)  # 等待選擇生效
        return True
    except Exception as e:
        print(f"選擇張數時發生錯誤: {e}")
        return False
