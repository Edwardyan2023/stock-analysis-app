import streamlit as st
import pandas as pd
import akshare as ak
import json
import os
from datetime import datetime

# --- 数据持久化配置 ---
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

# --- 核心逻辑：股票匹配与数据抓取 ---
@st.cache_data(ttl=3600)
def get_stock_list():
    """获取全A股代码名称映射表"""
    try:
        df = ak.stock_zh_a_spot_em()
        df['代码'] = df['代码'].astype(str)
        return df[['代码', '名称']]
    except:
        return pd.DataFrame(columns=['代码', '名称'])

def get_stock_info(input_val, stock_df):
    """增强型双向匹配逻辑，解决补零与未匹配问题"""
    if not input_val: return "", ""
    
    # 自动补齐6位代码 (针对深市等0开头的股票)
    if input_val.isdigit() and len(input_val) < 6:
        input_val = input_val.zfill(6)
    
    # 代码精确匹配
    match = stock_df[stock_df['代码'] == input_val]
    if not match.empty:
        return input_val, match.iloc[0]['名称']
    
    # 名称模糊匹配
    match = stock_df[stock_df['名称'].str.contains(input_val, na=False)]
    if not match.empty:
        return match.iloc[0]['代码'], match.iloc[0]['名称']
    
    return input_val, "未匹配"

# --- UI 样式定制 ---
st.set_page_config(page_title="A股复盘系统 V3", layout="wide")
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8f9fa; border-radius: 5px; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
    .stRadio > div { flex-direction: row !important; gap: 15px; }
    </style>
""", unsafe_allow_html=True)

# 初始化数据
if 'db' not in st.session_state:
    st.session_state.db = load_data()
stock_df = get_stock_list()

# --- 侧边栏/导航 ---
tabs = st.tabs(["记录选股", "每日复盘", "交易日志", "统计面板"])

# ================= Tab 1: 记录选股 =================
with tabs[0]:
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.subheader("基本信息")
        search_val = st.text_input("股票代码 / 名称", value="002315", help="输入2315会自动匹配002315")
        t_code, t_name = get_stock_info(search_val, stock_df)
        
        c1, c2 = st.columns(2)
        with c1: st.info(f"代码: **{t_code}**")
        with c2: st.info(f"名称: **{t_name}**")
        
        rec_date = st.date_input("记录日期", datetime.now())
        curr_price = st.number_input("当前价格", min_value=0.0, format="%.2f")
        
        c3, c4 = st.columns(2)
        with c3: target_p = st.text_input("目标价")
        with c4: stop_p = st.text_input("止损价")
        
        status = st.selectbox("持仓状态", ["观察中", "持仓中", "已出局"])

    with col_r:
        st.subheader("四维评分")
        f_s = st.radio("① 基本面评分", [1,2,3,4,5], index=2, key="fs")
        c_s = st.radio("② 资金面评分", [1,2,3,4,5], index=2, key="cs")
        t_s = st.radio("③ 技术面评分", [1,2,3,4,5], index=2, key="ts")
        m_s = st.radio("④ 宏观环境评分", [1,2,3,4,5], index=2, key="ms")
        
        total = f_s + c_s + t_s + m_s
        st.markdown(f"### 综合得分：**{total} / 20**")

    # 入场逻辑清单
    st.divider()
    st.subheader("入场逻辑 · 检查清单")
    ck_col1, ck_col2 = st.columns(2)
    with ck_col1:
        ck1 = st.checkbox("基本面逻辑清晰，催化剂明确")
        ck2 = st.checkbox("主力资金净流入，板块处于风口")
        ck3 = st.checkbox("技术面处于上升趋势或突破确认")
    with ck_col2:
        ck4 = st.checkbox("止损位设定，风险收益比 ≥ 1:2")
        ck5 = st.checkbox("宏观环境无明显系统性风险")
        ck6 = st.checkbox("仓位符合整体仓位管理规则")

    # 分析笔记
    st.divider()
    st.subheader("分析笔记")
    nb_col1, nb_col2 = st.columns(2)
    with nb_col1:
        n_base = st.text_area("基本面亮点", placeholder="业务护城河、财务指标、成长催化剂...")
        n_cap = st.text_area("资金面观察", placeholder="超大单净流入、板块轮动、情绪...")
    with nb_col2:
        n_tech = st.text_area("技术面分析", placeholder="趋势、支撑压力位、K线形态、量价...")
        n_risk = st.text_area("风险与不确定性", placeholder="宏观扰动、政策风险、个股风险...")

    if st.button("保存记录", use_container_width=True):
        new_rec = {
            "code": t_code, "name": t_name, "date": str(rec_date),
            "price": curr_price, "target": target_p, "stop": stop_p,
            "status": status, "total": total, "notes": n_base,
            "checklist": [ck1, ck2, ck3, ck4, ck5, ck6]
        }
        st.session_state.db["records"].append(new_rec)
        save_data(st.session_state.db)
        st.success(f"{t_name} 记录已保存！")

# ================= Tab 2: 每日复盘 =================
with tabs[1]:
    st.subheader("今日市场 · 宏观环境")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        d_date = st.date_input("复盘日期", datetime.now())
        d_trend = st.selectbox("大盘走势", ["强劲上涨", "震荡向上", "窄幅震荡", "震荡下跌", "加速下跌"])
        d_emo = st.selectbox("市场情绪", ["亢奋", "正常", "冷静", "恐慌"])
    with r_col2:
        d_strong = st.text_input("强势板块", placeholder="AI、跨境电商、新能源...")
        d_weak = st.text_input("弱势板块", placeholder="地产、消费...")
        d_news = st.text_area("关键政策 / 新闻", placeholder="影响今日盘面的重大消息...")
    
    st.subheader("持仓复盘")
    d_act = st.text_area("今日操作", placeholder="买入/卖出哪些标的，执行情况...")
    d_profit = st.text_input("今日盈亏 (元)", placeholder="正数盈利，负数亏损")
    d_discipline = st.radio("执行纪律自评", ["1 很差", "2 较差", "3 一般", "4 较好", "5 完美"], horizontal=True)
    
    st.subheader("三问复盘")
    q1 = st.text_area("做对了什么？", placeholder="今天哪些判断和操作是正确的...")
    q2 = st.text_area("做错了什么？", placeholder="哪些地方出现偏差，原因是什么...")
    q3 = st.text_area("明日计划", placeholder="重点关注标的、操作计划、注意事项...")
    
    if st.button("保存复盘", use_container_width=True):
        new_rev = {"date": str(d_date), "trend": d_trend, "profit": d_profit, "plan": q3}
        st.session_state.db["reviews"].append(new_rev)
        save_data(st.session_state.db)
        st.success("今日复盘已保存！")

# ================= Tab 3 & 4: 统计与展示 (略) =================
with tabs[2]:
    if st.session_state.db["records"]:
        st.dataframe(pd.DataFrame(st.session_state.db["records"]), use_container_width=True)
    else:
        st.info("尚无选股记录")

with tabs[3]:
    st.subheader("复盘数据概览")
    if st.session_state.db["records"]:
        df_recs = pd.DataFrame(st.session_state.db["records"])
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("总记录数", len(df_recs))
        s2.metric("胜率", "--")
        s3.metric("平均评分", round(df_recs['total'].mean(), 1))
        s4.metric("累计盈亏", "0.00")
    else:
        st.warning("暂无统计数据")
