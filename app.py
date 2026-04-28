import streamlit as st
import pandas as pd
import akshare as ak
import datetime

# --- 数据缓存逻辑：避免频繁请求导致封 IP ---
@st.cache_data(ttl=3600)  # 缓存 1 小时
def get_all_stock_info():
    """获取 A 股所有上市公司基本名单"""
    try:
        df = ak.stock_zh_a_spot_em()
        # 仅保留代码和名称，方便匹配
        return df[['代码', '名称']].set_index('代码')
    except:
        return pd.DataFrame(columns=['名称'])

@st.cache_data(ttl=86400) # 财务数据缓存 1 天
def get_stock_financials(symbol):
    """获取 2025 年财务摘要"""
    try:
        # 获取个股财务摘要（含最新年报数据）
        finance_df = ak.stock_financial_abstract_ths(symbol=symbol, indicator="按报告期")
        # 筛选 2025 年数据 (假设 2025-12-31)
        target_date = "2025-12-31"
        row = finance_df[finance_df['报告期'] == target_date]
        if not row.empty:
            return row.iloc[0].to_dict()
        return finance_df.iloc[0].to_dict() # 若无 25 年，返回最新一期
    except:
        return None

# --- 页面配置 ---
st.set_page_config(page_title="A股全量复盘系统 V3", layout="wide")

# 初始化 Session
if 'logs' not in st.session_state:
    st.session_state.logs = []

# 获取全市场名单
with st.spinner("正在同步全量 A 股名单..."):
    all_stocks = get_all_stock_info()

st.title("🚀 A股全量复盘与决策系统 (API版)")

# --- 侧边栏 ---
menu = st.sidebar.radio("模块", ["记录选股", "财务看板", "交易日志"])

if menu == "记录选股":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔍 标的匹配")
        symbol = st.text_input("输入 6 位股票代码", value="002315")
        
        # 自动关联名称
        if symbol in all_stocks.index:
            stock_name = all_stocks.loc[symbol, '名称']
            st.success(f"匹配成功：**{stock_name}**")
        else:
            stock_name = "未知标的"
            st.warning("未在 A 股库中发现该代码")

        # 自动调取财务数据
        fin_data = get_stock_financials(symbol)
        if fin_data:
            with st.expander("📊 查看 2025 年财务概要"):
                st.write(f"营收：{fin_data.get('营业总收入', 'N/A')}")
                st.write(f"净利润：{fin_data.get('净利润', 'N/A')}")
                st.write(f"毛利率：{fin_data.get('毛利率', 'N/A')}")
        
        curr_price = st.number_input("当前价格", step=0.01)
        status = st.selectbox("仓位管理", ["观察", "建仓", "重仓", "止损出局"])

    with col2:
        st.subheader("⚖️ 四维评分 (尊重市场资金)")
        f1 = st.slider("基本面 (财务/研报)", 1, 5, 3)
        f2 = st.slider("资金面 (主力/板块热度)", 1, 5, 3)
        f3 = st.slider("技术面 (均线/量价)", 1, 5, 3)
        f4 = st.slider("宏观面 (政策/情绪)", 1, 5, 3)
        
        score = f1 + f2 + f3 + f4
        st.metric("核心决策得分", f"{score}/20", delta="极佳" if score >= 16 else "")

    st.divider()
    note = st.text_area("入场逻辑 (基于 2025 财报表现与资金流向分析)")
    
    if st.button("保存至我的复盘日志", use_container_width=True):
        st.session_state.logs.append({
            "日期": datetime.date.today(), "代码": symbol, "名称": stock_name, 
            "得分": score, "状态": status, "逻辑": note
        })
        st.toast("数据已成功存入本地缓存")

elif menu == "交易日志":
    st.subheader("📖 历史复盘记录")
    if st.session_state.logs:
        df_logs = pd.DataFrame(st.session_state.logs)
        st.dataframe(df_logs, use_container_width=True)
        st.download_button("导出 CSV", df_logs.to_csv(index=False).encode('utf-8-sig'), "trade_log.csv")
    else:
        st.info("暂无记录。")
