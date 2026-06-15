import streamlit as st
import datetime
import calendar
import json
import os
import glob

# --- 설정 부분 ---
DATA_FILE = 'study_data.json'
COMMENTS_FILE = 'comments_data.json' 
IMAGE_DIR = 'images'

os.makedirs(IMAGE_DIR, exist_ok=True)

# 스터디원 이름과 고유 캐릭터 도장(이모지) 설정
USERS = {
    "희종": "🐶",
    "드림": "🐱",
    "승민": "🐰"
}

# --- 데이터 로드 및 저장 함수 ---
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

auth_records = load_data(DATA_FILE)
comments_records = load_data(COMMENTS_FILE)


# 네잎클로버가 쏟아지는 함수
def st_clovers():
    import random
    html = "<style>\n"
    html += "@keyframes clovers-fall { 0% { top: -10vh; opacity: 1; transform: rotate(0deg); } 100% { top: 110vh; opacity: 0; transform: rotate(360deg); } }\n"
    html += ".clover { position: fixed; z-index: 9999; user-select: none; animation: clovers-fall linear forwards; }\n"
    html += "</style>\n"
    
    # 50개의 네잎클로버를 화면 곳곳에 뿌립니다
    for _ in range(50):
        left = random.randint(0, 100)
        duration = random.uniform(2.5, 5.0) # 떨어지는 속도
        delay = random.uniform(0, 1.5)      # 떨어지기 시작하는 시간차
        size = random.uniform(1.5, 3.0)     # 클로버 크기
        html += f'<div class="clover" style="left: {left}vw; font-size: {size}rem; animation-duration: {duration}s; animation-delay: {delay}s;">🍀</div>\n'
        
    st.markdown(html, unsafe_allow_html=True)


# --- 웹 페이지 UI 시작 ---
st.set_page_config(page_title="만월 스터디 도장판", page_icon="🌕")
st.title("🌕 만월 스터디")

# 1. 인증하기 영역
st.subheader("일일 인증(전공 + 교과교재론)")
selected_user = st.selectbox("스터디원", list(USERS.keys()), key="auth_user")

uploaded_files = st.file_uploader(
    "오늘 푼 문제를 모두 올려주세요!", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if st.button("인증 완료하기"):
    if uploaded_files:
        today = str(datetime.date.today())
        
        if today not in auth_records:
            auth_records[today] = []
            
        # 💡 [핵심 변경] 파일 이름 겹침 방지를 위해 현재 시간(시분초)을 가져옵니다.
        now_time = datetime.datetime.now().strftime("%H%M%S")
        
        # 무조건 사진 파일은 저장합니다 (추가 업로드 허용)
        for idx, file in enumerate(uploaded_files):
            file_extension = file.name.split('.')[-1]
            # 파일명 예시: 2026-06-15_희종_143025_0.jpg (시간이 붙어 절대 겹치지 않음)
            save_filename = f"{today}_{selected_user}_{now_time}_{idx}.{file_extension}"
            save_path = os.path.join(IMAGE_DIR, save_filename)
            
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
        
        # 💡 [핵심 변경] 오늘 처음 올리는 건지, 추가로 올리는 건지에 따라 메시지를 다르게 줍니다.
        if selected_user not in auth_records[today]:
            auth_records[today].append(selected_user)
            save_data(auth_records, DATA_FILE)
            st.success(f"{USERS[selected_user]} {selected_user}님, 오늘 첫 인증과 함께 {len(uploaded_files)}장의 사진이 등록되었습니다! 🍀")
            st_clovers()
        else:
            st.success(f"{USERS[selected_user]} {selected_user}님, 열공하시네요! {len(uploaded_files)}장의 사진이 추가로 등록되었습니다! 👍")
            
    else:
        st.error("사진을 꼭 첨부해 주세요!")

st.divider()

# 2. 2026년 하반기 전체 누적 통계 영역
st.subheader("📊 2026년 하반기 누적 도장판")
total_stats = {user: 0 for user in USERS.keys()}

for date_str, users in auth_records.items():
    if date_str.startswith("2026-"):
        month_part = int(date_str.split("-")[1])
        if 6 <= month_part <= 11:
            for user in users:
                if user in total_stats:
                    total_stats[user] += 1

cols = st.columns(3)
for i, (user, count) in enumerate(total_stats.items()):
    with cols[i]:
        st.metric(label=f"{USERS[user]} {user}", value=f"{count}개 완료")

st.divider()

# 3. 월별 선택 캘린더 영역
st.subheader("📅 월별 도장판 확인")

target_month = st.selectbox(
    "확인하고 싶은 달을 선택하세요:",
    ["2026년 6월", "2026년 7월", "2026년 8월", "2026년 9월", "2026년 10월", "2026년 11월"]
)

year = 2026
month = int(target_month.split(" ")[1].replace("월", ""))
_, num_days = calendar.monthrange(year, month)

calendar_md = "| 날짜 | 인증 현황 (도장) |\n|---|---|\n"

for day in range(1, num_days + 1):
    date_str = f"{year}-{month:02d}-{day:02d}"
    daily_emojis = ""
    
    if date_str in auth_records:
        for user in USERS.keys():
            if user in auth_records[date_str]:
                daily_emojis += f"{USERS[user]} "
            else:
                daily_emojis += "▫️ "
    else:
        daily_emojis = "▫️ ▫️ ▫️ "

    calendar_md += f"| **{day}일** | {daily_emojis} |\n"

st.markdown(calendar_md)

st.divider()

# 4. 사진 구경하기 및 피드백(댓글) 영역
st.subheader("인증 문제 살펴보기")

available_dates = sorted(list(auth_records.keys()), reverse=True)

if available_dates:
    view_date = st.selectbox("사진과 피드백을 볼 날짜를 선택하세요:", available_dates)
    users_on_date = auth_records[view_date]
    
    if users_on_date:
        gallery_cols = st.columns(len(users_on_date))
        for i, user in enumerate(users_on_date):
            with gallery_cols[i]:
                st.write(f"**{USERS[user]} {user}의 인증샷**")
                
                # 추가로 올린 모든 사진들을 시간 상관없이 다 찾아서 보여줍니다.
                pattern = os.path.join(IMAGE_DIR, f"{view_date}_{user}*.*")
                matching_files = sorted(glob.glob(pattern)) # 올린 순서대로 정렬
                
                if matching_files:
                    st.image(matching_files, use_container_width=True)
                else:
                    st.warning("사진 파일을 찾을 수 없어요 😢")
                    
        st.write("---")
        
        # --- 피드백(댓글) 기능 시작 ---
        st.write(f"💬 **{view_date} 스터디 피드백**")
        
        if view_date in comments_records and len(comments_records[view_date]) > 0:
            for idx, comment in enumerate(comments_records[view_date]):
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.info(f"{USERS[comment['author']]} **{comment['author']}**: {comment['text']}")
                with col2:
                    if st.button("❌", key=f"del_{view_date}_{idx}", help="댓글 삭제"):
                        comments_records[view_date].pop(idx) 
                        save_data(comments_records, COMMENTS_FILE)
                        st.rerun() 
        else:
            st.write("아직 작성된 피드백이 없어요. 첫 번째 응원을 남겨주세요!")
            
        with st.form(key='comment_form', clear_on_submit=True):
            comment_col1, comment_col2 = st.columns([1, 4])
            with comment_col1:
                commenter = st.selectbox("작성자", list(USERS.keys()), key="commenter")
            with comment_col2:
                comment_text = st.text_input("피드백/응원 남기기", placeholder="수고했어! 3번 문제 풀이 대박이다!")
                
            submit_btn = st.form_submit_button("댓글 달기")
            
            if submit_btn:
                if comment_text.strip() == "":
                    st.error("댓글 내용을 입력해 주세요!")
                else:
                    if view_date not in comments_records:
                        comments_records[view_date] = []
                        
                    comments_records[view_date].append({
                        "author": commenter,
                        "text": comment_text
                    })
                    save_data(comments_records, COMMENTS_FILE)
                    st.rerun() 
else:
    st.info("아직 저장된 인증 사진이 없습니다. 첫 번째 인증을 남겨주세요!")