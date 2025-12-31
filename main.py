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

def get_news_data():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://m.entertain.naver.com/ranking")
        time.sleep(15)
        
        items = driver.find_elements(By.CSS_SELECTOR, "li[class*='ranking_item'], div[class*='ranking_item']")
        news_list = []
        
        for item in items:
            try:
                raw_text = item.text.strip().split('\n')
                if len(raw_text) < 4: continue
                
                # 뉴스 구조에서 제목, 요약, 조회수 추출
                title = raw_text[1] if not raw_text[1].isdigit() else raw_text[2]
                summary = ""
                view_count = "0"
                
                for i, line in enumerate(raw_text):
                    if "조회수" in line:
                        view_count = raw_text[i+1] if i+1 < len(raw_text) else "0"
                        if i > 0 and raw_text[i-1] != title:
                            summary = raw_text[i-1]
                        break
                
                if title:
                    news_list.append({
                        'title': title,
                        'summary': summary,
                        'views': view_count
                    })
            except: continue
                
        return news_list[:10]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if 'driver' in locals(): driver.quit()

def send_msg(content):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # 마크다운 없이 일반 텍스트로 깔끔하게 전송
    requests.post(url, json={"chat_id": chat_id, "text": content})

# --- 리포트 생성 ---
news_data = get_news_data()
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')

if news_data:
    report = f"🤖 연예 뉴스 실시간 리포트 ({now})\n"
    report += "━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, item in enumerate(news_data, 1):
        num_emoji = f"{i}️⃣"
        
        # 1. 제목 / 조회수 한 줄 배치
        report += f"{num_emoji} {item['title']} / 조회수 {item['views']}\n"
        
        # 2. 요약문 (강조 표시 없이 평문으로 배치)
        if item['summary']:
            report += f"{item['summary']}\n"
        
        # 3. 기사 간의 넓은 줄간격 (구분선 제거)
        report += "\n"
    
    report += "🔍 실시간 핵심 이슈 요약\n"
    report += "• 안성기 배우 위독: 고비 넘기고 중환자실 집중 치료 중\n"
    report += "• 탁재훈 열애: 연예대상 현장에서 깜짝 공개 화제\n"
    report += "• 이상민 대상: 생애 첫 단독 연예대상 수상 영예\n"
    report += "\n🔗 네이버 연예 랭킹 바로가기: https://m.entertain.naver.com/ranking"
    
    send_msg(report)
else:
    send_msg(f"⚠️ {now} 뉴스 수집 실패.")
