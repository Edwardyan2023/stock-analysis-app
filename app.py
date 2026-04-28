import streamlit as st
import pandas as pd
import akshare as ak
import json
import os
from datetime import datetime

# ===== 配置与数据持久化 =====
FILE_NAME = "trade_journal_v3.json"

def load_data():
    if not os.path.exists(FILE_NAME):
        return {"records": [], "reviews": []}
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"records": [], "reviews": []}

def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@st.cache_data(ttl=3600)
def get_stock_list():
    """实时获取全A股代码名称表"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df[['代码', '名称']]
    except:
        return pd.DataFrame(columns=['代码', '名称'])

# ===== 逻辑处理 =====
def get_stock_info(input_val, stock_df):
    if not input_val: return "", ""
    # 优先匹配代码
    match = stock_df[stock_df['代码'] == input_val]
    if not match.empty:
        return input_val, match.iloc[0]['名称']
    # 模糊匹配名称
    match = stock_df[stock_df['名称'].str.contains(input_val, na=False)]
    if not match.empty:
        return match.iloc[0]['代码'], match.iloc[0]['名称']
    return input_val, "未匹配"

# ===== 页面 UI =====
st.set_page_config(page_title="A股复盘系统", layout="wide")

# 加载数据到 SessionState
if 'db' not in st.session_state:
    st.session_state.db = load_data()

stock_df = get_stock_list()

# 自定义 CSS 样式
st.markdown("""
    <style>
    .stRadio > div { flex-direction: row !important; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 顶部导航
tab1, tab2, tab3, tab4 = st.tabs(["📌 记录选股", "📅 每日复盘", "📖 交易日志", "📊 统计面板"])

# --- 1. 记录选股 ---
with tab1:
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.subheader("基本信息")
        search_val = st.text_input("股票代码 / 名称", value="002315")
        t_code, t_name = get_stock_info(search_val, stock_df)
        
        c1, c2 = st.columns(2)
        with c1: st.info(f"代码: **{t_code}**")
        with c2: st.info(f"名称: **{t_name}**")
        
        rec_date = st.date_input("记录日期", datetime.now())
        price = st.number_input("当前价格", min_value=0.0, step=0.01)
        
        c3, c4 = st.columns(2)
        with c3: target_p = st.text_input("目标价")
        with c4: stop_p = st.text_input("止损价")
        
        status = st.selectbox("持仓状态", ["观察中", "持仓中", "已出局"])

    with col_r:
        st.subheader("四维评分")
        f_score = st.radio("① 基本面评分", [1,2,3,4,5], index=2, horizontal=True)
        c_score = st.radio("② 资金面评分", [1,2,3,4,5], index=2, horizontal=True)
        t_score = st.radio("③ 技术面评分", [1,2,3,4,5], index=2, horizontal=True)
        m_score = st.radio("④ 宏观面评分", [1,2,3,4,5], index=2, horizontal=True)
        
        total = f_score + c_score + t_score + m_score
        st.metric("核心决策得分", f"{total} / 20")

    st.divider()
    notes = st.text_area("分析笔记", placeholder="输入入场逻辑、护城河、风险点...")
    
    if st.button("保存记录", use_container_width=True):
        new_rec = {
            "code": t_code, "name": t_name, "date": str(rec_date),
            "price": price, "target": target_p, "stop": stop_p,
            "status": status, "total": total, "notes": notes,
            "scores": [f_score, c_score, t_score, m_score]
        }
        st.session_state.db["records"].append(new_rec)
        save_data(st.session_state.db)
        st.success(f"已保存 {t_name} 的复盘记录！")

# --- 2. 每日复盘 ---
with tab2:
    st.subheader("每日市场环境综述")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        m_trend = st.selectbox("大盘走势", ["上涨", "震荡", "下跌"])
        m_emotion = st.selectbox("市场情绪", ["亢奋", "正常", "恐慌"])
    with r_col2:
        s_sector = st.text_input("强势板块")
        w_sector = st.text_input("弱势板块")
    
    daily_act = st.text_area("今日操作与盈亏")
    
    review_col1, review_col2 = st.columns(2)
    with review_col1:
        good_point = st.text_area("做对了什么？")
    with review_col2:
        bad_point = st.text_area("做错了什么？")
    
    next_plan = st.text_area("明日计划")
    
    if st.button("提交复盘", use_container_width=True):
        new_rev = {
            "date": str(datetime.now().date()), "trend": m_trend, 
            "emotion": m_emotion, "action": daily_act, 
            "good": good_point, "bad": bad_point, "plan": next_plan
        }
        st.session_state.db["reviews"].append(new_rev)
        save_data(st.session_state.db)
        st.toast("今日复盘已存档")

# --- 4. 统计面板 ---
with tab4:
    recs = st.session_state.db["records"]
    if recs:
        df = pd.DataFrame(recs)
        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("总记录数", len(df))
        s_col2.metric("平均评分", round(df['total'].mean(), 2))
        s_col3.metric("最高评分", df['total'].max())
        
        st.subheader("评分分布趋势")
        st.line_chart(df['total'])
    else:
        st.info("暂无数据，请先开始记录。")

# --- 3. 交易日志 (查看历史) ---
with tab3:
    if st.session_state.db["records"]:
        st.dataframe(pd.DataFrame(st.session_state.db["records"]), use_container_width=True)
    else:
        st.write("日志为空")
