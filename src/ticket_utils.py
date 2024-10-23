from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import re

def select_best_ticket(driver):
    try:
        print("開始選擇票種...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "zone.area-list")))
        available_tickets = driver.find_elements(By.CSS_SELECTOR, ".select_form_a a")
        print(f"找到 {len(available_tickets)} 個可選擇的票種")

        if not available_tickets:
            print("沒有找到可用的票種")
            return None

        ticket_info = []

        for ticket in available_tickets:
            ticket_text = ticket.text
            print(f"處理票種: {ticket_text}")
            try:
                # 使用正則表達式提取區域號碼和剩餘票數
                match = re.search(r'區(\d+)\s*剩餘\s*(\d+)', ticket_text)
                
                if match:
                    area_number = int(match.group(1))
                    remaining = int(match.group(2))
                    
                    print(f"  解析結果 - 區域: {area_number}, 剩餘: {remaining}")
                    
                    if 105 <= area_number <= 121 and remaining > 0:
                        ticket_info.append((ticket, area_number, remaining))
                else:
                    print(f"  無法從文本中提取區域號碼或剩餘票數")
            except Exception as e:
                print(f"處理票種信息時出錯: {e}")
                continue

        print(f"符合條件的票種數量: {len(ticket_info)}")

        if ticket_info:
            print("符合條件的票種:")
            for t, a, r in ticket_info:
                print(f"  票種: {t.text}, 區域: {a}, 剩餘: {r}")
            # 選擇剩餘票數最多的區域
            best_ticket = max(ticket_info, key=lambda x: x[2])
        else:
            print("沒有找到符合條件的票種")
            return None

        ticket, area_number, remaining = best_ticket
        print(f"選擇票種: {ticket.text} (區域: {area_number}, 剩餘票數: {remaining})")
        return ticket

    except Exception as e:
        print(f"選擇票種時發生錯誤: {e}")
        return None

def click_ticket(driver, ticket):
    driver.execute_script("arguments[0].scrollIntoView(true);", ticket)
    # time.sleep(5)

    click_methods = [
        ticket.click,
        lambda: driver.execute_script("arguments[0].click();", ticket),
        lambda: ActionChains(driver).move_to_element(ticket).click().perform()
    ]

    for click_method in click_methods:
        try:
            click_method()
            print("已點擊票種")
            # time.sleep(10)
            return True
        except Exception as e:
            print(f"點擊方法失敗: {e}")
    
    return False

def select_quantity(driver, desired_quantity=1, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"嘗試選擇 {desired_quantity} 張票... (嘗試次數: {attempt + 1})")
            
            # 等待選擇框出現，增加等待時間
            select_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice_']"))
            )
            print("找到票數選擇框")
            
            # 等待選擇框可交互
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice_']"))
            )
            
            # 獲取所有可選擇的選項
            select = Select(select_element)
            options = select.options
            print(f"可選擇的票數選項: {[option.text for option in options]}")
            
            # 選擇最接近所需數量的選項
            closest_option = min(options, key=lambda x: abs(int(x.get_attribute("value")) - desired_quantity))
            print(f"選擇最接近的選項: {closest_option.text}")
            
            # 選擇票數
            select.select_by_value(closest_option.get_attribute("value"))
            print(f"已選擇票數: {closest_option.text}")
            
            # 等待選擇生效
            time.sleep(5)
            
            # 驗證選擇是否成功
            selected_option = select.first_selected_option
            if selected_option.text == closest_option.text:
                print("票數選擇成功確認")
                return True
            else:
                print(f"票數選擇可能未生效，當前選中: {selected_option.text}")
                
        except (TimeoutException, StaleElementReferenceException) as e:
            print(f"選擇張數時發生錯誤: {e}")
            if attempt < max_retries - 1:
                print("重試中...")
                time.sleep(2)
                driver.refresh()
            else:
                print(f"當前頁面 URL: {driver.current_url}")
                print(f"頁面源碼: {driver.page_source}")
                return False

    print("選擇張數失敗，已達到最大重試次數")
    return False
