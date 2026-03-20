import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
import os

# 1. 설정
st.set_page_config(page_title="SafeTrip 30", layout="wide")
DB_FILE = "points.json"

# 2. 데이터 불러오기/저장 함수
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 초기 데이터 1개
        return [{"name": "파리 루브르", "lat": 48.8606, "lon": 2.3376, "desc": "기본 데이터"}]

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 데이터 로드
if 'locations' not in st.session_state:
    st.session_state.locations = load_data()

st.title("📍 소매치기 제보 지도 (소규모 데이터용)")

# 3. 지도 표시
m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)

for loc in st.session_state.locations:
    folium.Marker(
        [loc['lat'], loc['lon']], 
        popup=f"<b>{loc['name']}</b>",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# 조준점 디자인
st.markdown("""
    <style>
    .crosshair { position: fixed; top: 50%; left: 50%; width: 20px; height: 20px; 
                  border: 2px solid red; border-radius: 50%; transform: translate(-50%, -50%); 
                  z-index: 9999; pointer-events: none; }
    .crosshair::before { content: ''; position: absolute; top: 50%; left: -10px; width: 40px; height: 2px; background: red; }
    .crosshair::after { content: ''; position: absolute; left: 50%; top: -10px; width: 2px; height: 40px; background: red; }
    </style>
    <div class="crosshair"></div>
""", unsafe_allow_html=True)

map_data = st_folium(m, width="100%", height=500)

# 현재 중앙 좌표
c_lat = map_data['center']['lat'] if map_data['center'] else 48.8566
c_lng = map_data['center']['lng'] if map_output['center'] else 2.3522

# 4. 제보 및 저장
with st.sidebar:
    st.header("📢 위치 제보")
    with st.form("add_form"):
        name = st.text_input("장소")
        desc = st.text_area("설명")
        if st.form_submit_button("저장"):
            if name:
                new_point = {"name": name, "lat": c_lat, "lon": c_lng, "desc": desc}
                st.session_state.locations.append(new_point)
                
                # [핵심] 파일에 직접 저장
                save_data(st.session_state.locations)
                
                st.success("저장 완료!")
                st.rerun()

st.write(f"현재 저장된 항목 수: {len(st.session_state.locations)} / 30")
