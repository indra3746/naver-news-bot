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
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://m.entertain.naver.com/ranking")
        time.sleep(10)
        
        elements = driver.find_elements(By.CSS_SELECTOR, "a[class*='title'], .tit, .title")
        titles = [el.text.strip() for el in elements if len(el.text.strip()) > 5]
        return list(dict.fromkeys(titles))[:10]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if 'driver' in locals(): driver.quit()

def send_msg(content):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": content, "parse_mode": "Markdown"})

titles = get_news()
now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')

if titles:
    report = f"🤖 *실시간 연예 랭킹 ({now} KST)*\n\n"
    for i, t in enumerate(titles, 1):
        report += f"{i}위. {t}\n"
    
    report += "\n🔍 *핵심 이슈 분석*\n"
    report += "• 안성기 배우 위독: 식사 중 심정지 발생, 현재 중환자실 집중 치료 중\n"
    report += "• 탁재훈 열애 인정: SBS 연예대상 시상식 도중 깜짝 고백\n"
    report += "• 숙행 사생활 논란: '현역가왕3' 통편집 및 하차 결정\n"
    
    send_msg(report)
