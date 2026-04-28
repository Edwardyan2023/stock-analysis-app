import json
import os
from datetime import datetime

FILE_NAME = "trade_journal.json"


# ===== 数据存储 =====
def load_data():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===== 输入工具 =====
def input_score(name):
    while True:
        try:
            score = int(input(f"{name}评分 (1-5): "))
            if 1 <= score <= 5:
                return score
        except:
            pass
        print("请输入1-5之间的数字")


# ===== 记录选股 =====
def add_record():
    data = load_data()

    print("\n=== 新增记录 ===")

    code = input("股票代码: ")
    name = input("股票名称: ")
    date = input("日期(默认今天): ") or datetime.now().strftime("%Y-%m-%d")
    price = input("当前价格: ")
    target = input("目标价: ")
    stop = input("止损价: ")
    status = input("状态(观察中/持仓中): ") or "观察中"

    print("\n--- 四维评分 ---")
    fundamental = input_score("基本面")
    capital = input_score("资金面")
    technical = input_score("技术面")
    macro = input_score("宏观面")

    total = fundamental + capital + technical + macro

    notes = input("分析笔记: ")

    record = {
        "code": code,
        "name": name,
        "date": date,
        "price": price,
        "target": target,
        "stop": stop,
        "status": status,
        "scores": {
            "fundamental": fundamental,
            "capital": capital,
            "technical": technical,
            "macro": macro
        },
        "total": total,
        "notes": notes
    }

    data.append(record)
    save_data(data)

    print(f"\n✅ 保存成功！综合评分: {total}/20\n")


# ===== 查看记录 =====
def list_records():
    data = load_data()

    if not data:
        print("\n暂无记录\n")
        return

    print("\n=== 所有记录 ===")
    for i, r in enumerate(data):
        print(f"""
[{i+1}] {r['code']} {r['name']}
日期: {r['date']}
状态: {r['status']}
评分: {r['total']}/20
目标价: {r['target']}  止损价: {r['stop']}
""")


# ===== 统计 =====
def stats():
    data = load_data()

    if not data:
        print("\n暂无数据\n")
        return

    total_records = len(data)
    avg_score = sum(r["total"] for r in data) / total_records

    print("\n=== 统计面板 ===")
    print(f"总记录数: {total_records}")
    print(f"平均评分: {avg_score:.2f}")


# ===== 每日复盘 =====
def daily_review():
    print("\n=== 每日复盘 ===")

    market = input("大盘走势(上涨/震荡/下跌): ")
    emotion = input("市场情绪(亢奋/正常/恐慌): ")
    strong = input("强势板块: ")
    weak = input("弱势板块: ")

    action = input("今日操作: ")
    profit = input("今日盈亏: ")

    good = input("做对了什么？: ")
    bad = input("做错了什么？: ")
    plan = input("明日计划: ")

    review = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "market": market,
        "emotion": emotion,
        "strong": strong,
        "weak": weak,
        "action": action,
        "profit": profit,
        "good": good,
        "bad": bad,
        "plan": plan
    }

    data = load_data()
    data.append({"daily_review": review})
    save_data(data)

    print("\n✅ 复盘已保存\n")


# ===== 主菜单 =====
def main():
    while True:
        print("""
==============================
📊 股票交易复盘系统
==============================
1. 记录选股
2. 查看记录
3. 统计面板
4. 每日复盘
0. 退出
""")

        choice = input("请选择: ")

        if choice == "1":
            add_record()
        elif choice == "2":
            list_records()
        elif choice == "3":
            stats()
        elif choice == "4":
            daily_review()
        elif choice == "0":
            print("退出系统")
            break
        else:
            print("输入错误")


if __name__ == "__main__":
    main()
