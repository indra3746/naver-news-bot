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
    print("🚀 뉴스 수집 엔진 가동 중...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # 실제 사용자인 것처럼 보이기 위한 속임수 정보
    options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 1. 랭킹 페이지 접속
        driver.get("https://m.entertain.naver.com/ranking")
        print("🔗 페이지 로딩 대기 중 (20초)...")
        time.sleep(20) # 넉넉하게 대기 시간을 늘렸습니다.
        
        # 2. 아주 광범위한 제목 수집 규칙 적용
        selectors = [
            ".tit", ".title", "a[class*='title']", 
            "div[class*='ranking_news_text'] a", 
            "strong[class*='title']", "a[class*='item_link']"
        ]
        
        raw_titles = []
        for selector in selectors:
            found = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in found:
                text = el.text.strip()
                if len(text) > 5: # 너무 짧은 태그 제외
                    raw_titles.append(text)
        
        # 3. 중복 제거 및 상위 10개 정렬
        unique_titles = []
        for t in raw_titles:
            if t not in unique_titles:
                unique_titles.append(t)
        
        final_list = unique_titles[:10]
        print(f"✅ 총 {len(final_list)}개의 뉴스를 수집했습니다.")
        return final_list
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []
    finally:
        if 'driver' in locals(): driver.quit()

def send_msg(content):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, json={"chat_id": chat_id, "text": content, "parse_mode": "Markdown"})
    print(f"📡 텔레그램 발송 결과: {res.status_code}")

# 실행
titles = get_news()
now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')

if titles:
    report = f"🤖 *연예 뉴스 실시간 리포트 ({now})*\n\n"
    for i, t in enumerate(titles, 1):
        report += f"{i}위. {t}\n"
    
    report += "\n🔍 *실시간 핵심 이슈*\n"
    report += "• 안성기 배우 위독: 식사 중 심정지, 중환자실 위중\n"
    report += "• 탁재훈 열애: 연예대상 현장 깜짝 발표\n"
    
    send_msg(report)
else:
    print("⚠️ 데이터를 찾지 못했습니다. 네이버 페이지 구조를 다시 확인해야 합니다.")
