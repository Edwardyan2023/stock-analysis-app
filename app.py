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
"000001": "平安银行",
        "000002": "万科Ａ",
        "000004": "*ST国华",
        "000005": "ST星源",
        "000006": "深振业Ａ",
        "000007": "全新好",
        "000008": "神州高铁",
        "000009": "中国宝安",
        "000010": "美丽生态",
        "000011": "深物业A",
        "000012": "南玻Ａ",
        "000014": "沙河股份",
        "000016": "深康佳Ａ",
        "000017": "深中华A",
        "000019": "深粮控股",
        "000020": "深华发Ａ",
        "000021": "深科技",
        "000023": "*ST深天",
        "000025": "特力Ａ",
        "000026": "飞亚达",
        "000027": "深圳能源",
        "000028": "国药一致",
        "000029": "深深房Ａ",
        "000030": "富奥股份",
        "000031": "大悦城",
        "000032": "深桑达Ａ",
        "000034": "神州数码",
        "000035": "中国天楹",
        "000036": "华联控股",
        "000037": "深南电A",
        "000039": "中集集团",
        "000040": "*ST旭蓝",
        "000042": "中洲控股",
        "000045": "深纺织Ａ",
        "000048": "京基智农",
        "000049": "德赛电池",
        "000050": "深天马Ａ",
        "000055": "方大集团",
        "000056": "皇庭国际",
        "000058": "深赛格",
        "000059": "华锦股份",
        "000060": "中金岭南",
        "000061": "农产品",
        "000062": "深圳华强",
        "000063": "中兴通讯",
        "000065": "北方国际",
        "000066": "中国长城",
        "000068": "华控赛格",
        "000069": "华侨城Ａ",
        "000070": "特发信息",
        "000078": "海王生物",
        "000088": "盐田港",
        "000089": "深圳机场",
        "000090": "天健集团",
        "000096": "广聚能源",
        "000099": "中信海直",
        "000100": "TCL科技",
        "000151": "中成股份",
        "000153": "丰原药业",
        "000155": "川能动力",
        "000156": "华数传媒",
        "000157": "中联重科",
        "000158": "常山北明",
        "000159": "国际实业",
        "000166": "申万宏源",
        "000301": "东方盛虹",
        "000333": "美的集团",
        "000338": "潍柴动力",
        "000400": "许继电气",
        "000401": "金隅冀东",
        "000402": "金融街",
        "000403": "派林生物",
        "000404": "长虹华意",
        "000407": "胜利股份",
        "000408": "藏格矿业",
        "000409": "云鼎科技",
        "000410": "沈阳机床",
        "000411": "英特集团",
        "000413": "ST旭电",
        "000415": "渤海租赁",
        "000416": "*ST民控",
        "000417": "合百集团",
        "000419": "通程控股",
        "000420": "吉林化纤",
        "000421": "南京公用",
        "000422": "湖北宜化",
        "000423": "东阿阿胶",
        "000425": "徐工机械",
        "000426": "兴业银锡",
        "000428": "华天酒店",
        "000429": "粤高速Ａ",
        "000430": "ST张家界",
        "000488": "ST晨鸣",
        "000498": "山东路桥",
        "000501": "武商集团",
        "000503": "国新健康",
        "000504": "*ST生物",
        "000505": "京粮控股",
        "000506": "招金黄金",
        "000507": "珠海港",
        "000509": "华塑控股",
        "000510": "新金路",
        "000513": "丽珠集团",
        "000514": "渝开发",
        "000516": "国际医学",
        "000517": "荣安地产",
        "000518": "*ST四环",
        "000519": "中兵红箭",
        "000520": "凤凰航运",
        "000521": "长虹美菱",
        "000523": "红棉股份",
        "000524": "岭南控股",
        "000525": "红太阳",
        "000526": "学大教育",
        "000528": "柳工",
        "000529": "广弘控股",
        "000530": "冰山冷热",
        "000531": "穗恒运Ａ",
        "000532": "华金资本",
        "000533": "顺钠股份",
        "000534": "万泽股份",
        "000536": "华映科技",
        "000537": "绿发电力",
        "000538": "云南白药",
        "000539": "粤电力Ａ",
        "000541": "佛山照明",
        "000543": "皖能电力",
        "000544": "中原环保",
        "000545": "金浦钛业",
        "000546": "金圆股份",
        "000547": "航天发展",
        "000548": "湖南投资",
        "002315": "焦点科技",
        "002527": "新时达",
        "300002": "神州泰岳",
        "300011": "鼎汉技术",
        "300023": "宝德股份",
        "300028": "金亚科技",
        "300031": "宝通科技",
        "300032": "金龙机电",
        "300034": "钢研高纳",
        "300040": "九洲集团",
        "300041": "回天新材",
        "300043": "星辉娱乐",
        "300048": "合康新能",
        "300057": "万顺新材",
        "300063": "天龙集团",
        "300069": "金利华电",
        "300074": "华平股份",
        "300082": "奥克股份",
        "300092": "科新机电",
        "300095": "华伍股份",
        "300104": "乐视网",
        "300108": "吉药控股",
        "300114": "中航成飞",
        "300121": "阳谷华泰",
        "300126": "锐奇股份",
        "300128": "锦富技术",
        "300135": "宝利国际",
        "300151": "昌红科技",
        "300154": "瑞凌股份",
        "300156": "神雾环保",
        "300175": "朗源股份",
        "300179": "四方达",
        "300185": "通裕重工",
        "300198": "纳川股份",
        "300210": "森远股份",
        "300216": "千山药机",
        "300239": "东宝生物",
        "300247": "融捷健康",
        "300257": "开山股份",
        "300258": "精锻科技",
        "300260": "新莱应材",
        "300281": "金明精机",
        "300283": "温州宏丰",
        "300291": "百纳千成",
        "300309": "吉艾科技",
        "300402": "宝色股份",
        "300405": "科隆股份",
        "300407": "凯发电气",
        "300411": "金盾股份",
        "300412": "迦南科技",
        "300419": "浩丰科技",
        "300426": "唐德影视",
        "300428": "立中集团",
        "300431": "暴风集团",
        "300564": "筑博设计",
        "300715": "凯伦股份",
        "300750": "宁德时代",
        "300757": "罗博特科",
        "300790": "宇瞳光学",
        "300791": "仙乐健康",
        "300792": "壹网壹创",
        "300795": "米奥会展",
        "300796": "贝斯美",
        "300797": "钢研纳克",
        "300798": "锦鸡股份",
        "300800": "力合科技",
        "300801": "泰和科技",
        "300805": "电声股份",
        "300806": "斯迪克",
        "300807": "天迈科技",
        "300808": "久量股份",
        "300809": "华辰装备",
        "300810": "中科海讯",
        "300811": "铂科新材",
        "300812": "易天股份",
        "300813": "泰林生物",
        "300815": "玉禾田",
        "300816": "艾可蓝",
        "300817": "双飞股份",
        "300818": "耐普矿机",
        "300819": "聚杰微纤",
        "300820": "英杰电气",
        "300821": "东岳硅材",
        "300822": "贝仕达克",
        "300823": "建科机械",
        "300824": "北鼎股份",
        "300825": "阿尔特",
        "300826": "测绘股份",
        "300827": "上能电气",
        "300828": "锐新科技",
        "300829": "金丹科技",
        "300833": "浩洋股份",
        "300835": "龙磁科技",
        "300836": "佰奥智能",
        "300837": "浙矿股份",
        "300838": "浙江力诺",
        "300839": "博汇股份",
        "300840": "酷特智能",
        "300841": "康华生物",
        "300842": "帝科股份",
        "300843": "胜蓝股份",
        "300845": "捷安高科",
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
