
import streamlit as st
import pandas as pd
import datetime

# --- 股票名称自动关联逻辑 ---
# 在此内置您关注的标的映射，后续可扩展接入 AkShare 等实时接口
def get_stock_name(symbol):
    stock_dict = {
        "002315": "焦点科技",
        "603156": "养元饮品", 
        "603369": "今世缘",
        "603198": "迎驾贡酒",
        "603345": "安井食品",
        "603711": "香飘飘",
        "601519": "大智慧",
        "600570": "恒生电子",
        "002594": "比亚迪",
        "300750": "宁德时代",
        "600519": "贵州茅台",
        "000858": "五粮液",
        "603387": "基蛋生物",
        "002737": "葵花药业",
        "002368": "太极股份",
        "603392": "万丰奥威",
        "002229": "鸿博股份"
    }
    return stock_dict.get(symbol, "未知股票 (请手动确认)")

# --- 页面配置 ---
st.set_page_config(page_title="投资复盘系统 V2", layout="wide", initial_sidebar_state="expanded")

# --- 自定义 CSS 样式 ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextArea textarea { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 个人投资决策与复盘系统")
st.caption("版本：V2.0 | 核心逻辑：四维评分 + 资产轻量化复利模型")

# --- 侧边栏导航 ---
st.sidebar.header("导航控制")
menu = st.sidebar.radio("功能模块", ["记录选股", "每日复盘", "交易日志", "统计面板"])

# 初始化数据存储 (Session State)
if 'logs' not in st.session_state:
    st.session_state.logs = []

if menu == "记录选股":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. 标的信息")
        # 核心优化：输入代码自动显示名称
        symbol = st.text_input("股票代码", value="002315", help="输入6位代码，系统将自动检索名称")
        stock_name = get_stock_name(symbol)
        st.info(f"关联标的名称：**{stock_name}**")
        
        record_date = st.date_input("记录日期", datetime.date.today())
        curr_price = st.number_input("当前价格", min_value=0.0, step=0.01)
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            target_p = st.number_input("目标价", min_value=0.0, step=0.01)
        with c_p2:
            stop_l = st.number_input("止损价", min_value=0.0, step=0.01)
        
        status = st.selectbox("持仓状态", ["观察中", "建仓中", "重仓持有", "已出局"])

    with col2:
        st.subheader("2. 四维评分 (1-5分)")
        f1 = st.select_slider("① 基本面 (业绩/行业地位)", options=[1,2,3,4,5], value=3)
        f2 = st.select_slider("② 资金面 (机构/主力动向)", options=[1,2,3,4,5], value=3)
        f3 = st.select_slider("③ 技术面 (趋势/形态)", options=[1,2,3,4,5], value=3)
        f4 = st.select_slider("④ 宏观环境 (政策/情绪)", options=[1,2,3,4,5], value=3)
        
        total_score = f1 + f2 + f3 + f4
        st.metric("综合决策分", f"{total_score} / 20", delta=f"建议入场" if total_score >= 15 else "")

    st.divider()
    st.subheader("3. 逻辑清单")
    c_note1, c_note2 = st.columns(2)
    with c_note1:
        note_f = st.text_area("基本面核心亮点", placeholder="业务护城河、财务安全边际、分红率...")
        note_c = st.text_area("资金与板块观察", placeholder="板块热度排位、资金净流入情况...")
    with c_note2:
        note_t = st.text_area("技术入场点位分析", placeholder="支撑位确认、量价背离、均线多头...")
        note_r = st.text_area("主要风险点备注", placeholder="业绩波动、宏观政策转向、个股负面...")

    if st.button("💾 确认保存至云端"):
        new_entry = {
            "代码": symbol, "名称": stock_name, "日期": record_date,
            "价格": curr_price, "评分": total_score, "状态": status,
            "录入时间": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        st.session_state.logs.append(new_entry)
        st.success(f"已成功记录 {stock_name} ({symbol}) 的决策分析。")

elif menu == "统计面板":
    st.subheader("📊 数据看板")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df, use_container_width=True)
        # 导出功能
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 导出数据为 CSV", csv, "invest_review_data.csv", "text/csv")
    else:
        st.info("暂无历史记录。")

# --- 页脚 ---
st.sidebar.divider()
st.sidebar.caption("💡 策略提示：严格执行止损，拥抱复利成长。")
