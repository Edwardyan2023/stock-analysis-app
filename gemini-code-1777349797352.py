import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 页面配置
st.set_page_config(page_title="股市复盘分析系统", layout="wide")

# 初始化数据存储 (模拟数据库)
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = pd.DataFrame(columns=[
        "日期", "代码", "名称", "状态", "基本面", "资金面", "技术面", "宏观", "总分", "逻辑"
    ])

# --- 侧边栏导航 ---
menu = st.sidebar.radio("导航菜单", ["记录选股", "每日复盘", "交易日志", "统计面板"])

# --- 1. 记录选股 ---
if menu == "记录选股":
    st.header("📝 记录选股")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("基本信息")
        code = st.text_input("股票代码", value="002315")
        name = st.text_input("股票名称", value="焦点科技")
        date = st.date_input("记录日期", datetime.now())
        price = st.number_input("当前价格", value=0.0)
        target = st.text_input("目标价 / 止损价")
        status = st.selectbox("持仓状态", ["观察中", "持仓中", "已清仓"])

    with col2:
        st.subheader("四维评分 (1-5分)")
        f_score = st.slider("① 基本面评分", 1, 5, 3)
        m_score = st.slider("② 资金面评分", 1, 5, 3)
        t_score = st.slider("③ 技术面评分", 1, 5, 3)
        e_score = st.slider("④ 宏观环境评分", 1, 5, 3)
        total_score = f_score + m_score + t_score + e_score
        st.metric("综合得分", f"{total_score} / 20")

    st.subheader("入场逻辑 · 检查清单")
    check_cols = st.columns(2)
    c1 = check_cols[0].checkbox("基本面逻辑清晰，催化剂明确")
    c2 = check_cols[0].checkbox("主力资金净流入，板块处于风口")
    c3 = check_cols[1].checkbox("止损位设定，风险收益比 ≥ 3")
    c4 = check_cols[1].checkbox("仓位符合整体仓位管理规则")

    logic_note = st.text_area("分析笔记 (基本面亮点、资金面观察、技术面分析等)")

    if st.button("保存记录"):
        new_entry = {
            "日期": date, "代码": code, "名称": name, "状态": status,
            "基本面": f_score, "资金面": m_score, "技术面": t_score, "宏观": e_score,
            "总分": total_score, "逻辑": logic_note
        }
        st.session_state.stock_data = pd.concat([st.session_state.stock_data, pd.DataFrame([new_entry])], ignore_index=True)
        st.success(f"{name} 记录已保存！")

# --- 2. 每日复盘 ---
elif menu == "每日复盘":
    st.header("📅 每日复盘")
    col_a, col_b = st.columns(2)
    with col_a:
        st.selectbox("大盘走势", ["强势上涨", "震荡调整", "弱势下跌"])
        st.text_input("强势板块", placeholder="AI、跨境电商...")
    with col_b:
        st.selectbox("市场情绪", ["极度贪婪", "正常", "恐慌"])
        st.text_input("弱势板块", placeholder="地产、消费...")
    
    st.text_area("三问复盘法 (做对了什么？做错了什么？明日计划？)")
    st.button("保存今日复盘")

# --- 3. 交易日志 (统计列表) ---
elif menu == "交易日志":
    st.header("📖 交易日志")
    st.dataframe(st.session_state.stock_data, use_container_width=True)
    
    # 导出 Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        st.session_state.stock_data.to_excel(writer, index=False, sheet_name='Sheet1')
    
    st.download_button(
        label="导出为 Excel",
        data=buffer,
        file_name=f"交易复盘_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.ms-excel"
    )

# --- 4. 统计面板 ---
elif menu == "统计面板":
    st.header("📊 统计面板")
    if not st.session_state.stock_data.empty:
        df = st.session_state.stock_data
        m1, m2, m3 = st.columns(3)
        m1.metric("总记录数", len(df))
        m2.metric("平均综合评分", round(df["总分"].mean(), 1))
        m3.metric("资金面平均分", round(df["资金面"].mean(), 1))
        
        st.subheader("四维平均分分布")
        avg_scores = df[["基本面", "资金面", "技术面", "宏观"]].mean()
        st.bar_chart(avg_scores)
    else:
        st.info("暂无数据，请先在‘记录选股’中添加。")