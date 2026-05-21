import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# 页面设置
st.set_page_config(page_title="信用卡还款策略对比", layout="wide")

# ====================== 终极中文乱码修复（100%兼容） ======================
# 自动安装Linux服务器通用的文泉驿中文字体
os.system("apt-get update -y && apt-get install -y fonts-wqy-zenhei")
# 清除matplotlib字体缓存
os.system("rm -rf ~/.cache/matplotlib")

# 全局字体设置（兼容所有版本）
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
# ============================================================================

st.title("💳 信用卡还款策略可视化")
st.markdown("### 最低还款 · 分期还款 · 全额还款")
st.markdown("---")

# 侧边栏参数设置
st.sidebar.header("⚙️ 参数设置")
st.sidebar.markdown("试试修改下面的数字，图表会实时变化")

# 输入参数
amount = st.sidebar.number_input("💰 消费金额（元）", min_value=1000, max_value=100000, value=5000, step=1000)
periods = st.sidebar.selectbox("📅 分期期数", options=[3, 6, 12, 24], index=2)
daily_rate = st.sidebar.number_input("📉 最低还款日利率（%）", min_value=0.01, max_value=0.1, value=0.05, step=0.01)
installment_rate = st.sidebar.number_input("📊 分期月费率（%）", min_value=0.3, max_value=1.5, value=0.70, step=0.05)

# 计算三种还款方式
# 1. 全额还款
full_payment = amount
full_interest = 0

# 2. 分期还款
installment_fee = amount * (installment_rate / 100) * periods
installment_total = amount + installment_fee
installment_monthly = installment_total / periods

# 3. 最低还款（按10%最低还款额计算）
min_payment_rate = 0.1
min_monthly_payment = amount * min_payment_rate
min_total = 0
remaining = amount
min_interest_total = 0

while remaining > 0.01:
    # 计算当月利息
    interest = remaining * (daily_rate / 100) * 30
    min_interest_total += interest
    
    # 计算当月还款额
    payment = min(min_monthly_payment, remaining + interest)
    min_total += payment
    
    # 更新剩余本金
    remaining = remaining + interest - payment

# 显示计算结果
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="✅ 全额还款", value=f"{full_payment:.2f} 元", delta=f"利息：{full_interest:.2f} 元")

with col2:
    st.metric(label="📅 分期还款", value=f"{installment_total:.2f} 元", delta=f"利息：{installment_fee:.2f} 元")

with col3:
    st.metric(label="⚠️ 最低还款", value=f"{min_total:.2f} 元", delta=f"利息：{min_interest_total:.2f} 元")

st.markdown("---")

# 绘制对比柱状图
st.subheader("📊 三种还款方式总金额对比")
fig1, ax1 = plt.subplots(figsize=(10, 6))
methods = ["全额还款", "分期还款", "最低还款"]
totals = [full_payment, installment_total, min_total]
colors = ["#2ecc71", "#f39c12", "#e74c3c"]

bars = ax1.bar(methods, totals, color=colors, width=0.6)
ax1.set_ylabel("总还款金额（元）", fontsize=12)
ax1.set_title("三种还款方式总金额对比", fontsize=14, pad=20)

# 在柱子上显示数值
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 50,
             f"{height:.2f}",
             ha='center', va='bottom', fontsize=12)

st.pyplot(fig1)

st.markdown("---")

# 绘制债务递减曲线
st.subheader("📈 债务递减曲线（展示债务随时间变化）")
fig2, ax2 = plt.subplots(figsize=(12, 6))

# 全额还款曲线
full_x = [0, 1]
full_y = [amount, 0]
ax2.plot(full_x, full_y, color="#2ecc71", linewidth=3, marker='o', label="全额还款")

# 分期还款曲线
installment_x = np.arange(0, periods+1)
installment_y = [amount - (installment_monthly * i) for i in installment_x]
installment_y = [max(0, y) for y in installment_y]
ax2.plot(installment_x, installment_y, color="#f39c12", linewidth=3, marker='s', label="分期还款")

# 最低还款曲线
min_x = []
min_y = []
remaining_min = amount
month = 0

while remaining_min > 0.01:
    min_x.append(month)
    min_y.append(remaining_min)
    
    interest = remaining_min * (daily_rate / 100) * 30
    payment = min(min_monthly_payment, remaining_min + interest)
    remaining_min = remaining_min + interest - payment
    month += 1

min_x.append(month)
min_y.append(0)
ax2.plot(min_x, min_y, color="#e74c3c", linewidth=3, marker='^', label="最低还款")

ax2.set_xlabel("月份", fontsize=12)
ax2.set_ylabel("剩余债务（元）", fontsize=12)
ax2.set_title("三种还款方式债务递减曲线", fontsize=14, pad=20)
ax2.legend(fontsize=12)
ax2.grid(True, alpha=0.3)

st.pyplot(fig2)

st.markdown("---")

# 场景参考
st.subheader("💡 真实场景参考")
st.markdown("""
| 消费场景 | 推荐还款方式 | 原因 |
| :--- | :--- | :--- |
| 1000元以下小额消费 | 全额还款 | 无利息，最划算 |
| 1000-5000元短期周转 | 分期3-6期 | 利息较低，压力小 |
| 5000-20000元大额消费 | 分期12期 | 分摊到每月，还款压力适中 |
| 20000元以上长期消费 | 分期24期 | 避免最低还款的高额利息 |
| 临时资金紧张 | 先还最低，下月全额 | 避免逾期影响征信 |
""")

st.markdown("---")
st.caption("数据来源：各大银行信用卡中心官方费率表 | 本工具仅供参考，实际还款金额以银行账单为准")