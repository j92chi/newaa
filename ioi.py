import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="SafeTrip - 전세계 소매치기 지도", layout="wide")

# 2. 구글 시트 연결 (URL을 본인의 시트 주소로 교체하세요)
# 주의: 시트 공유 설정이 '편집자(Editor)'로 되어 있어야 저장이 가능합니다.
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/여러분의_시트_ID/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기 함수 (캐시를 사용하지 않아야 실시간 업데이트 확인 가능)
def load_data():
    return conn.read(spreadsheet=SPREADSHEET_URL, usecols=[0, 1, 2, 3])

try:
    df = load_data()
except:
    # 시트가 비어있을 경우를 대비한 초기 데이터프레임
    df = pd.DataFrame(columns=["name", "lat", "lon", "desc"])

st.title("📍 실시간 해외 소매치기 제보 지도")
st.info("지도를 움직여 중앙 조준점에 위험 지역을 맞춘 후 제보를 남겨주세요. 데이터는 구글 시트에 영구 저장됩니다.")

# 3. 지도 중심점 세션 관리
if 'map_center' not in st.session_state:
    st.session_state.map_center = [48.8566, 2.3522] # 초기값: 파리

# 4. 지도 생성 및 마커 표시
m = folium.Map(location=st.session_state.map_center, zoom_start=15)

# DB(구글 시트)에 저장된 마커들 표시
for _, row in df.iterrows():
    if pd.notnull(row['lat']) and pd.notnull(row['lon']):
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"<b>{row['name']}</b><br>{row['desc']}",
            icon=folium.Icon(color='red', icon='warning', prefix='fa')
        ).add_to(m)

# 지도 정중앙 조준점(Crosshair) 디자인
img_center_marker = """
<div style="position: fixed; top: 50%; left: 50%; width: 30px; height: 30px; 
            margin-top: -15px; margin-left: -15px; z-index: 9999; pointer-events: none;">
    <div style="position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: red;"></div>
    <div style="position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: red;"></div>
</div>
"""
m.get_root().html.add_child(folium.Element(img_center_marker))

# 지도 렌더링
map_output = st_folium(m, width="100%", height=500, key="main_map")

# 현재 지도의 중심 좌표 획득
if map_output['center']:
    c_lat = map_output['center']['lat']
    c_lng = map_output['center']['lng']
else:
    c_lat, c_lng = st.session_state.map_center

# 5. 제보 입력란 (사이드바)
with st.sidebar:
    st.header("📢 위험 장소 제보")
    st.write(f"🎯 조준점 좌표: `{c_lat:.5f}, {c_lng:.5f}`")
    
    with st.form("report_form", clear_on_submit=True):
        new_name = st.text_input("장소 이름", placeholder="예: 루브르 박물관 입구")
        new_desc = st.text_area("위험 내용/수법", placeholder="예: 서명 캠페인을 하며 접근함")
        submit_button = st.form_submit_button("현재 위치로 제보 등록")

        if submit_button:
            if new_name:
                # 1. 새로운 데이터 생성
                new_row = pd.DataFrame([{"name": new_name, "lat": c_lat, "lon": c_lng, "desc": new_desc}])
                # 2. 기존 데이터와 병합
                updated_df = pd.concat([df, new_row], ignore_index=True)
                # 3. 구글 시트 업데이트 (전체 덮어쓰기)
                conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                
                st.session_state.map_center = [c_lat, c_lng]
                st.success("제보가 완료되었습니다!")
                st.rerun()
            else:
                st.warning("장소 이름을 입력해주세요.")

# 6. 하단 데이터 목록 조회
st.divider()
with st.expander("📋 전체 제보 기록 보기"):
    st.dataframe(df, use_container_width=True)
