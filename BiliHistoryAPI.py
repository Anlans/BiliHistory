import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
browser.get('https://www.bilibili.com/account/history')
submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#app > div > div.login > div > a')))
//tst
submit.click()
time.sleep(10)
browser.get('http://api.bilibili.com/x/v2/history')
content = browser.find_element_by_xpath('/html/body/pre').text
jsonContent = json.loads(content)
cnt = 0
for i in jsonContent['data']:
    cnt = cnt+1
    print('av号: %s--->%s'%(i['aid'], i['title']))

print('总计='+str(cnt))