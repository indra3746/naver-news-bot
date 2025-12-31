import os
import requests
import time
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_news():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # 실제 브라우저처럼 보이게 하기 위한 설정
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # 랭킹 페이지로 직접 접속
        driver.get("https://m.entertain.naver.com/ranking")
        time.sleep(10) # 로딩 시간을 10초로 늘렸습니다.
        
        # 기사 제목 추출 (더 포괄적인 선택자 사용)
        elements = driver.find_elements(By.CSS_SELECTOR, ".title, .tit, a[class*='title']")
        titles = [el.text.strip() for el in elements if len(el.text.strip()) > 5]
        return list(dict.fromkeys(titles))[:10] # 중복 제거 후 상위 10개
    except Exception as e:
        print(f"❌ 크롤링 에러 발생: {e}")
        return []
    finally:
        driver.quit()

# 발송 로직 등 나머지는 동일...
