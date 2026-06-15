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

# --- 웹 페이지 UI 시작 ---
st.set_page_config(page_title="만월 스터디 도장판", page_icon="🌕")
st.title("🌕 만월 스터디")

# 1. 인증하기 영역
st.subheader("매일 인증하기")
selected_user = st.selectbox("이름 설정", list(USERS.keys()), key="auth_user")

uploaded_files = st.file_uploader(
    "오늘 푼 문제 사진을 모두 올려주세요! (여러 장 선택 가능)", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if st.button("인증 완료하기"):
    if uploaded_files:
        today = str(datetime.date.today())
        
        if today not in auth_records:
            auth_records[today] = []
            
        if selected_user not in auth_records[today]:
            for idx, file in enumerate(uploaded_files):
                file_extension = file.name.split('.')[-1]
                save_filename = f"{today}_{selected_user}_{idx}.{file_extension}"
                save_path = os.path.join(IMAGE_DIR, save_filename)
                
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
            
            auth_records[today].append(selected_user)
            save_data(auth_records, DATA_FILE)
            
            st.success(f"{USERS[selected_user]} {selected_user}님, 총 {len(uploaded_files)}장의 사진으로 오늘 인증 완료! 🍀")
            st.balloons()
        else:
            st.warning("오늘은 이미 인증하셨습니다! 내일 또 만나요🍀.")
    else:
        st.error("사진을 꼭 첨부해 주세요!")

st.divider()

# 2. 2026년 하반기 전체 누적 통계 영역
st.subheader("📊 2026년 하반기 누적 도장판 (6월 ~ 11월)")
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
st.subheader("🖼️ 만월 스터디 사진관 & 피드백")

available_dates = sorted(list(auth_records.keys()), reverse=True)

if available_dates:
    view_date = st.selectbox("사진과 피드백을 볼 날짜를 선택하세요:", available_dates)
    users_on_date = auth_records[view_date]
    
    if users_on_date:
        gallery_cols = st.columns(len(users_on_date))
        for i, user in enumerate(users_on_date):
            with gallery_cols[i]:
                st.write(f"**{USERS[user]} {user}의 인증샷**")
                
                pattern = os.path.join(IMAGE_DIR, f"{view_date}_{user}*.*")
                matching_files = glob.glob(pattern)
                
                if matching_files:
                    st.image(matching_files, use_container_width=True)
                else:
                    st.warning("사진 파일을 찾을 수 없어요 😢")
                    
        st.write("---")
        
        # --- 피드백(댓글) 기능 시작 ---
        st.write(f"💬 **{view_date} 스터디 피드백**")
        
        # 💡 [핵심 변경] 댓글 출력 부분에 삭제 버튼을 달았습니다.
        if view_date in comments_records and len(comments_records[view_date]) > 0:
            for idx, comment in enumerate(comments_records[view_date]):
                # 화면을 가로로 나눠서 왼쪽엔 댓글, 오른쪽엔 삭제 버튼 배치
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.info(f"{USERS[comment['author']]} **{comment['author']}**: {comment['text']}")
                with col2:
                    # 삭제 버튼 클릭 시 동작
                    if st.button("❌", key=f"del_{view_date}_{idx}", help="댓글 삭제"):
                        comments_records[view_date].pop(idx) # 데이터에서 삭제
                        save_data(comments_records, COMMENTS_FILE) # 저장
                        st.rerun() # 화면 즉시 새로고침
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
                    st.rerun() # 댓글 달면 즉시 보이도록 새로고침
else:
    st.info("아직 저장된 인증 사진이 없습니다. 첫 번째 인증을 남겨주세요!")