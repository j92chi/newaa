import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="SafeTrip - 해외 소매치기 제보 지도", layout="wide")

st.title("📍 해외 소매치기 주의 장소 공유 서비스")
st.info("여행객들이 직접 제보한 실시간 위험 지역 지도입니다.")

# 2. 데이터 관리 (세션 저장소 활용)
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {"name": "파리 루브르 박물관", "lat": 48.8606, "lon": 2.3376, "desc": "설문조사단 접근 주의"},
        {"name": "로마 테르미니역", "lat": 41.9009, "lon": 12.5020, "desc": "티켓 머신 근처 소매치기 빈번"},
        {"name": "바르셀로나 람블라스 거리", "lat": 41.3817, "lon": 2.1728, "desc": "오물 뿌리기 수법 주의"}
    ]

# 3. 사이드바: 제보 입력란
with st.sidebar:
    st.header("📢 위험 장소 제보")
    with st.form("report_form"):
        new_name = st.text_input("장소 명칭 (예: 에펠탑 근처)")
        # 위도/경도 초기값을 0.0이 아닌 지도 중심점 근처로 설정하면 입력이 더 편합니다.
        new_lat = st.number_input("위도 (Latitude)", value=45.0, format="%.6f")
        new_lon = st.number_input("경도 (Longitude)", value=15.0, format="%.6f")
        new_desc = st.text_area("위험 내용/수법")
        submit_button = st.form_submit_button("제보 등록")
        
        if submit_button:
            if new_name:
                st.session_state.locations.append({
                    "name": new_name, "lat": new_lat, "lon": new_lon, "desc": new_desc
                })
                st.success("제보가 완료되었습니다!")
                st.rerun()

# 4. 지도 표시 영역
st.subheader("⚠️ 실시간 위험 지도")
# 지도 생성 (초기 위치: 유럽 중심부)
m = folium.Map(location=[45.0, 15.0], zoom_start=4)

# 마커 추가
for loc in st.session_state.locations:
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=folium.Popup(f"<b>{loc['name']}</b><br>{loc['desc']}", max_width=300),
        tooltip=loc['name'],
        icon=folium.Icon(color='red', icon='warning', prefix='fa')
    ).add_to(m)  # <--- 이 부분의 오타를 수정했습니다!

# 지도 화면에 출력
st_folium(m, width="100%", height=550)

# 5. 하단 데이터 표
st.divider()
st.subheader("📋 전체 제보 목록")
df = pd.DataFrame(st.session_state.locations)
st.dataframe(df, use_container_width=True)
