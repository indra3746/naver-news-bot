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
    print("🚀 뉴스 수집을 시작합니다...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 1. 네이버 연예 랭킹 메인 페이지 접속
        driver.get("https://m.entertain.naver.com/ranking")
        time.sleep(15) # 페이지 로딩을 위해 15초 대기
        
        # 2. 다양한 기사 제목 패턴을 모두 시도합니다.
        selectors = [
            "a[class*='title']", 
            "div[class*='ranking_item_text'] a", 
            "span[class*='title']",
            "strong[class*='title']",
            ".tit",
            "a[class*='item_link']"
        ]
        
        titles = []
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                t = el.text.strip()
                if len(t) > 10: # 유효한 제목만 수집
                    titles.append(t)
        
        # 중복 제거 후 상위 10개만 추출
        unique_titles = []
        for t in titles:
            if t not in unique_titles:
                unique_titles.append(t)
        
        final_list = unique_titles[:10]
        print(f"✅ {len(final_list)}개의 뉴스를 찾았습니다.")
        return final_list
    except Exception as e:
        print(f"❌ 크롤링 에러: {e}")
        return []
    finally:
        if 'driver' in locals(): driver.quit()

def send_msg(content):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, json={"chat_id": chat_id, "text": content, "parse_mode": "Markdown"})
    print(f"📡 발송 결과: {res.status_code}")

# 실행부
news_list = get_news()
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.now(kst).strftime('%Y-%m-%d %H:%M')

if news_list:
    report = f"🤖 *실시간 연예 랭킹 리포트 ({now_kst})*\n"
    report += f"{'='*30}\n\n"
    for i, title in enumerate(news_list, 1):
        report += f"{i}위. {title}\n"
    
    report += "\n🔍 *2025년 12월 31일 주요 소식*\n"
    report += "• 안성기 배우 위독: 식사 중 심정지 발생, 현재 중환자실 집중 치료 중\n"
    report += "• 탁재훈 열애: 'SBS 연예대상' 현장에서 일반인과 열애 사실 전격 공개\n"
    report += "• 이상민 대상: '미운 우리 새끼'로 생애 첫 단독 연예대상 수상\n"
    
    send_msg(report)
else:
    print("⚠️ 뉴스를 찾지 못해 발송을 취소합니다.")
