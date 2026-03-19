import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="SafeTrip - 정밀 위치 제보", layout="wide")

st.title("📍 해외 소매치기 정밀 제보 시스템")
st.info("지도를 움직여 화면 중앙의 **[+] 조준점**에 위험 지역을 맞춰주세요.")

# 2. 데이터 관리
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {"name": "파리 루브르 박물관", "lat": 48.8606, "lon": 2.3376, "desc": "설문조사단 접근 주의"},
        {"name": "로마 테르미니역", "lat": 41.9009, "lon": 12.5020, "desc": "티켓 머신 근처 소매치기 빈번"}
    ]

# 초기 지도 중심 설정
if 'map_center' not in st.session_state:
    st.session_state.map_center = [48.8566, 2.3522]

# 3. 지도 생성 및 조준점 추가
m = folium.Map(location=st.session_state.map_center, zoom_start=15)

# 기존 제보 마커 표시
for loc in st.session_state.locations:
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=f"<b>{loc['name']}</b>",
        icon=folium.Icon(color='red', icon='warning', prefix='fa')
    ).add_to(m)

# [중요] 지도 정중앙에 고정된 조준점(Crosshair) HTML 삽입
# 이 코드는 지도의 div 내부에 직접 UI를 그려서 위치가 절대 안 밀립니다.
img_center_marker = """
<div style="
    position: fixed; 
    top: 50%; 
    left: 50%; 
    width: 40px; 
    height: 40px; 
    margin-top: -20px; 
    margin-left: -20px; 
    z-index: 9999; 
    pointer-events: none;
    display: flex;
    justify-content: center;
    align-items: center;
">
    <div style="position: absolute; width: 2px; height: 100%; background: red;"></div>
    <div style="position: absolute; width: 100%; height: 2px; background: red;"></div>
    <div style="width: 10px; height: 10px; border: 2px solid red; border-radius: 50%; background: white;"></div>
</div>
"""
m.get_root().html.add_child(folium.Element(img_center_marker))

# 지도 렌더링
map_data = st_folium(m, width="100%", height=500, key="center_map")

# 현재 지도의 중심 좌표 캡처
c_lat = map_data['center']['lat'] if map_data['center'] else st.session_state.map_center[0]
c_lng = map_data['center']['lng'] if map_data['center'] else st.session_state.map_center[1]

# 4. 제보 입력 양식 (지도 아래 또는 옆)
st.divider()
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📢 현재 위치 제보")
    with st.form("report_form", clear_on_submit=True):
        new_name = st.text_input("장소 명칭", placeholder="예: 에펠탑 앞 광장")
        st.caption(f"🎯 좌표: {c_lat:.5f}, {c_lng:.5f}")
        new_desc = st.text_area("위험 내용", placeholder="수법이나 주의사항을 적어주세요.")
        
        submitted = st.form_submit_button("이 위치 제보하기")
        if submitted and new_name:
            st.session_state.locations.append({
                "name": new_name, "lat": c_lat, "lon": c_lng, "desc": new_desc
            })
            st.session_state.map_center = [c_lat, c_lng]
            st.success("제보가 완료되었습니다!")
            st.rerun()

with col2:
    st.subheader("📋 전체 제보 목록")
    st.dataframe(pd.DataFrame(st.session_state.locations), use_container_width=True)
