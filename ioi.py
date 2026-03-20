import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
import os

# 1. 페이지 및 파일 설정
st.set_page_config(page_title="SafeTrip - 소매치기 제보 지도", layout="wide")
DB_FILE = "points.json"

# 2. 데이터 관리 함수 (JSON 파일 저장 방식)
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 세션 상태 초기화
if 'locations' not in st.session_state:
    st.session_state.locations = load_db()

st.title("📍 실시간 해외 소매치기 주의 지도")
st.info("지도를 움직여 **빨간색 조준점**에 위험 장소를 맞춘 뒤 제보를 남겨주세요.")

# 3. 지도 초기 설정
# 데이터가 있으면 마지막 위치를 중심으로, 없으면 파리를 중심으로 표시
if st.session_state.locations:
    last_loc = st.session_state.locations[-1]
    start_lat, start_lon = last_loc['lat'], last_loc['lon']
else:
    start_lat, start_lon = 48.8566, 2.3522  # 파리 기준

m = folium.Map(location=[start_lat, start_lon], zoom_start=15)

# 저장된 마커들 지도에 추가
for loc in st.session_state.locations:
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=f"<b>{loc['name']}</b><br>{loc['desc']}",
        tooltip=loc['name'],
        icon=folium.Icon(color='red', icon='warning', prefix='fa')
    ).add_to(m)

# [디자인] 화면 정중앙 고정 조준점 (CSS)
st.markdown("""
    <style>
    .crosshair {
        position: fixed; top: 50%; left: 50%; width: 30px; height: 30px;
        margin-top: -15px; margin-left: -15px; z-index: 9999; pointer-events: none;
    }
    .crosshair::before { content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: red; }
    .crosshair::after { content: ''; position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: red; }
    </style>
    <div class="crosshair"></div>
""", unsafe_allow_html=True)

# 4. 지도 렌더링 (변수명을 map_data로 확실히 통일!)
map_data = st_folium(m, width="100%", height=550, key="main_map")

# [중요] 중앙 좌표 실시간 가져오기 (오류 방지 로직 포함)
# map_data가 비어있지 않고 'center' 키가 있을 때만 좌표 업데이트
if map_data and map_data.get('center'):
    current_lat = map_data['center']['lat']
    current_lng = map_data['center']['lng']
else:
    current_lat, current_lng = start_lat, start_lon

# 5. 제보 입력 사이드바
with st.sidebar:
    st.header("📢 위험 장소 제보")
    st.write(f"🎯 조준점 좌표: `{current_lat:.5f}, {current_lng:.5f}`")
    
    with st.form("report_form", clear_on_submit=True):
        new_name = st.text_input("장소 이름", placeholder="예: 에펠탑 근처")
        new_desc = st.text_area("위험 내용/수법", placeholder="예: 서명해달라며 소지품 탈취")
        
        submit_button = st.form_submit_button("현재 위치 저장")
        
        if submit_button:
            if new_name:
                # 30개 항목 제한 체크 (원하실 경우 추가)
                if len(st.session_state.locations) >= 50: # 여유있게 50개 설정
                    st.warning("데이터가 너무 많습니다. 기존 제보를 먼저 확인하세요.")
                else:
                    # 새로운 데이터 구성
                    new_entry = {
                        "name": new_name,
                        "lat": current_lat,
                        "lon": current_lng,
                        "desc": new_desc
                    }
                    # 세션 및 파일에 저장
                    st.session_state.locations.append(new_entry)
                    save_db(st.session_state.locations)
                    
                    st.success("제보가 성공적으로 기록되었습니다!")
                    st.rerun() # 지도 새로고침하여 마커 반영
            else:
                st.error("장소 이름을 입력해주세요.")

# 6. 하단 데이터 목록
st.divider()
with st.expander("📋 전체 제보 목록 보기"):
    if st.session_state.locations:
        df_display = pd.DataFrame(st.session_state.locations)
        st.table(df_display[['name', 'desc']])
    else:
        st.write("등록된 제보가 없습니다.")
