import streamlit as st
import pandas as pd
import akshare as ak
import json
import os
from datetime import datetime

# --- 数据持久化配置 ---
FILE_NAME = "trade_journal_v3.json"
STOCKS_FILE = "stocks.txt"

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

# --- 核心逻辑：股票匹配（优先本地文件，解决未匹配问题） ---
@st.cache_data(ttl=3600)
def get_stock_dict():
    """获取全A股字典：1.本地文件 -> 2.内置保底 -> 3.API"""
    stock_map = {
        "002315": "焦点科技",
        "605499": "东鹏饮料",
        "600519": "贵州茅台",
        "000001": "平安银行"
    }
    
    # 尝试从本地 stocks.txt 读取
    if os.path.exists(STOCKS_FILE):
        try:
            with open(STOCKS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        code, name = parts
                        stock_map[code.strip().zfill(6)] = name.strip()
        except Exception as e:
            st.sidebar.error(f"本地 stocks.txt 读取失败: {e}")

    # 尝试 API 补充（如果网络通畅）
    try:
        df = ak.stock_zh_a_spot_em()
        api_map = dict(zip(df['代码'].astype(str).str.zfill(6), df['名称']))
        stock_map.update(api_map)
    except:
        pass # 联网失败则使用已有字典
        
    return stock_map

def get_stock_info(input_val, stock_dict):
    """增强型匹配逻辑"""
    if not input_val: return "", ""
    
    search_val = input_val.strip()
    # 自动补齐6位代码
    if search_val.isdigit() and len(search_val) < 6:
        search_val = search_val.zfill(6)
    
    # 代码精确匹配
    if search_val in stock_dict:
        return search_val, stock_dict[search_val]
    
    # 名称模糊匹配
    for code, name in stock_dict.items():
        if search_val in name:
            return code, name
            
    return search_val, "未匹配"

# --- UI 样式 ---
st.set_page_config(page_title="A股复盘系统 V3", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #ffffff; border-radius: 5px; border: 1px solid #e0e0e0; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stRadio > div { flex-direction: row !important; gap: 20px; }
    </style>
""", unsafe_allow_html=True)

# 初始化数据
if 'db' not in st.session_state:
    st.session_state.db = load_data()
stock_dict = get_stock_dict()

tabs = st.tabs(["📌 记录选股", "📅 每日复盘", "📖 交易日志", "📊 统计面板"])

# ================= Tab 1: 记录选股 =================
with tabs[0]:
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.subheader("基本信息")
        search_val = st.text_input("股票代码 / 名称", value="002315")
        t_code, t_name = get_stock_info(search_val, stock_dict)
        
        c1, c2 = st.columns(2)
        with c1: st.info(f"代码: **{t_code}**")
        with c2: st.info(f"名称: **{t_name}**")
        
        rec_date = st.date_input("记录日期", datetime.now())
        curr_price = st.number_input("当前价格", min_value=0.0, format="%.2f")
        
        c3, c4 = st.columns(2)
        with c3: target_p = st.text_input("目标价", value="--")
        with c4: stop_p = st.text_input("止损价", value="--")
        
        status = st.selectbox("持仓状态", ["观察中", "持仓中", "已出局"])

    with col_r:
        st.subheader("四维评分")
        f_s = st.radio("① 基本面评分", [1,2,3,4,5], index=2, key="fs")
        c_s = st.radio("② 资金面评分", [1,2,3,4,5], index=2, key="cs")
        t_s = st.radio("③ 技术面评分", [1,2,3,4,5], index=2, key="ts")
        m_s = st.radio("④ 宏观环境评分", [1,2,3,4,5], index=2, key="ms")
        
        total = f_s + c_s + t_s + m_s
        st.markdown(f"### 综合得分：**{total} / 20**")

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

    st.divider()
    st.subheader("分析笔记")
    n_col1, n_col2 = st.columns(2)
    with n_col1:
        n_base = st.text_area("基本面与资金面亮点", placeholder="业务护城河、主力动向...")
    with n_col2:
        n_tech = st.text_area("技术面与风险点", placeholder="形态分析、潜在回撤风险...")

    if st.button("💾 保存该选股记录", use_container_width=True):
        new_rec = {
            "代码": t_code, "名称": t_name, "日期": str(rec_date),
            "当前价": curr_price, "目标价": target_p, "止损价": stop_p,
            "状态": status, "综合得分": total, "笔记": n_base + " | " + n_tech
        }
        st.session_state.db["records"].append(new_rec)
        save_data(st.session_state.db)
        st.success(f"已保存: {t_name} ({t_code})")

# ================= Tab 2: 每日复盘 =================
with tabs[1]:
    r_col1, r_col2 = st.columns([1, 1.5])
    with r_col1:
        st.subheader("市场宏观记录")
        d_date = st.date_input("复盘日期", datetime.now(), key="rev_date")
        d_trend = st.selectbox("大盘走势", ["强劲上涨", "震荡向上", "窄幅震荡", "震荡下跌", "加速下跌"])
        d_emo = st.select_slider("市场情绪", options=["恐慌", "冷静", "正常", "亢奋"], value="正常")
        d_profit = st.number_input("今日账面盈亏 (元)", format="%.2f")
    
    with r_col2:
        st.subheader("盘面核心观察")
        d_strong = st.text_input("强势板块/主线", placeholder="如：AI算力、高股息等")
        d_news = st.text_area("重大消息/政策感触", height=100)
    
    st.divider()
    st.subheader("三问深思")
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1: q1 = st.text_area("做对了什么？", height=150)
    with q_col2: q2 = st.text_area("做错了什么？", height=150)
    with q_col3: q3 = st.text_area("明日计划/警示", height=150)

    if st.button("📝 提交今日复盘", use_container_width=True):
        new_rev = {
            "日期": str(d_date), "大盘走势": d_trend, "盈亏": d_profit, 
            "主线": d_strong, "做对": q1, "做错": q2, "计划": q3
        }
        st.session_state.db["reviews"].append(new_rev)
        save_data(st.session_state.db)
        st.success("今日复盘档案已存入数据库！")

# ================= Tab 3: 交易日志 =================
with tabs[2]:
    st.subheader("选股历史记录")
    if st.session_state.db["records"]:
        df_recs = pd.DataFrame(st.session_state.db["records"])
        st.dataframe(df_recs, use_container_width=True)
        
        if st.button("🗑️ 清空所有选股记录", type="secondary"):
            st.session_state.db["records"] = []
            save_data(st.session_state.db)
            st.rerun()
    else:
        st.info("暂无数据，请在‘记录选股’标签页添加。")

# ================= Tab 4: 统计面板 =================
with tabs[3]:
    if st.session_state.db["records"]:
        df_all = pd.DataFrame(st.session_state.db["records"])
        
        # 顶部统计指标
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("研究标的总数", len(df_all))
        m2.metric("平均综合评分", f"{round(df_all['综合得分'].mean(), 1)} / 20")
        
        # 状态分布
        st.subheader("持仓状态统计")
        status_count = df_all['状态'].value_counts()
        st.bar_chart(status_count)
        
        # 历史复盘回顾
        st.divider()
        st.subheader("历史复盘回顾")
        if st.session_state.db["reviews"]:
            st.table(pd.DataFrame(st.session_state.db["reviews"]).tail(5))
        else:
            st.write("暂无每日复盘记录")
    else:
        st.warning("数据量不足，无法生成统计图表。")
