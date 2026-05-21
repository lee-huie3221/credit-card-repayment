import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 页面设置
st.set_page_config(page_title="信用卡还款策略对比", layout="wide")

# 字体设置（修复部署后中文乱码问题）
plt.rcParams['font.sans-serif'] = [
    'SimHei', 'Microsoft YaHei', 'PingFang SC', 
    'Arial Unicode MS', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC'
]
plt.rcParams['axes.unicode_minus'] = False

st.title("💳 信用卡还款策略可视化")
st.markdown("### 最低还款 · 分期还款 · 全额还款")
st.markdown("---")

# ========== 侧边栏：用户输入参数 ==========
with st.sidebar:
    st.header("⚙️ 参数设置")
    st.markdown("**试试修改下面的数字，图表会实时变化**")
    st.markdown("---")
    
    # 用户输入金额
    amount = st.number_input(
        "💰 消费金额（元）", 
        min_value=100, 
        max_value=100000, 
        value=5000, 
        step=500,
        help="输入你想消费的金额"
    )
    
    # 用户选择期数
    months = st.selectbox(
        "📅 分期期数", 
        [3, 6, 9, 12, 18, 24], 
        index=3,
        help="选择分多少个月还款"
    )
    
    # 用户输入利率
    daily_rate_input = st.number_input(
        "📉 最低还款日利率（%）", 
        min_value=0.01, 
        max_value=0.10, 
        value=0.05, 
        step=0.01,
        help="银行通常为0.05%"
    ) / 100
    
    installment_rate_input = st.number_input(
        "📊 分期月费率（%）", 
        min_value=0.1, 
        max_value=2.0, 
        value=0.7, 
        step=0.1,
        help="银行通常为0.7%左右"
    ) / 100
    
    st.markdown("---")
    st.caption("💡 提示：修改任意参数，右侧图表会自动更新")

# ========== 计算函数 ==========
def calc_full(amount):
    return amount

def calc_installment(amount, months, rate):
    return amount + amount * rate * months

def calc_min_payment(amount, months, daily_rate):
    remaining = amount
    total_interest = 0
    for month in range(months):
        payment = remaining * 0.1
        interest = remaining * daily_rate * 30
        total_interest += interest
        remaining = remaining - payment + interest
        if remaining <= 0:
            break
    return amount + total_interest

# 计算结果
full_total = calc_full(amount)
inst_total = calc_installment(amount, months, installment_rate_input)
min_total = calc_min_payment(amount, months, daily_rate_input)

inst_interest = inst_total - amount
min_interest = min_total - amount

# ========== 三大指标卡片 ==========
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background:#e8f5e9; padding:1rem; border-radius:12px; text-align:center;">
        <p style="color:#2e7d32; font-size:1rem; margin:0;">✅ 全额还款</p>
        <p style="font-size:2rem; font-weight:bold; margin:0;">{full_total:,.0f}<span style="font-size:1rem;"> 元</span></p>
        <p style="color:#666; margin:0;">利息 0 元</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background:#fff3e0; padding:1rem; border-radius:12px; text-align:center;">
        <p style="color:#ed6c02; font-size:1rem; margin:0;">📅 分期还款</p>
        <p style="font-size:2rem; font-weight:bold; margin:0;">{inst_total:,.0f}<span style="font-size:1rem;"> 元</span></p>
        <p style="color:#666; margin:0;">利息 +{inst_interest:,.0f} 元</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background:#ffebee; padding:1rem; border-radius:12px; text-align:center;">
        <p style="color:#d32f2f; font-size:1rem; margin:0;">⚠️ 最低还款</p>
        <p style="font-size:2rem; font-weight:bold; margin:0;">{min_total:,.0f}<span style="font-size:1rem;"> 元</span></p>
        <p style="color:#666; margin:0;">利息 +{min_interest:,.0f} 元</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========== 柱状图 ==========
st.subheader(f"📊 还款金额对比（消费 {amount:,} 元 · 分 {months} 期）")

fig, ax = plt.subplots(figsize=(10, 5))
labels = ["全额还款", "分期还款", "最低还款"]
values = [full_total, inst_total, min_total]
colors = ["#2e7d32", "#ed6c02", "#d32f2f"]

bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor='white', linewidth=2)
ax.set_ylabel("总还款金额（元）", fontsize=12)
ax.axhline(y=amount, color='#999', linestyle='--', alpha=0.7, label=f'本金 {amount:,}元')

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 30,
            f'{int(height):,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend()
ax.grid(axis='y', alpha=0.3)

st.pyplot(fig)

# ========== 债务递减曲线 ==========
st.subheader("📉 债务递减曲线（展示债务随时间变化）")

x_months = list(range(months + 1))

# 全额曲线
full_curve = [amount] + [0] * months

# 分期曲线
monthly_payment = amount / months
installment_curve = [amount - monthly_payment * i for i in range(months + 1)]

# 最低还款曲线
remaining = amount
min_curve = [remaining]
for i in range(months):
    interest = remaining * daily_rate_input * 30
    remaining = remaining - remaining * 0.1 + interest
    if remaining < 0:
        remaining = 0
    min_curve.append(remaining)

fig2, ax2 = plt.subplots(figsize=(10, 5))

ax2.fill_between(x_months, 0, full_curve, alpha=0.3, label='全额还款', color='#2e7d32')
ax2.fill_between(x_months, 0, installment_curve, alpha=0.3, label='分期还款', color='#ed6c02')
ax2.fill_between(x_months, 0, min_curve, alpha=0.3, label='最低还款', color='#d32f2f')

ax2.plot(x_months, full_curve, 'o-', label='全额还款线', color='#2e7d32', linewidth=1.5)
ax2.plot(x_months, installment_curve, 's-', label='分期还款线', color='#ed6c02', linewidth=1.5)
ax2.plot(x_months, min_curve, '^-', label='最低还款线', color='#d32f2f', linewidth=1.5)

ax2.set_xlabel("月份", fontsize=12)
ax2.set_ylabel("剩余债务（元）", fontsize=12)
ax2.set_title(f"债务随时间递减趋势", fontsize=14)
ax2.legend(loc='upper right')
ax2.grid(alpha=0.3)

st.pyplot(fig2)
st.caption("💡 曲线越陡，还款越快；最低还款（红线）下降最慢，利息成本最高")

st.markdown("---")

# ========== 五大场景参考表 ==========
st.subheader("📋 五大场景参考数据（基于真实银行利率）")

# 固定场景数据
reference_scenes = pd.DataFrame({
    "场景": ["买手机", "旅游", "美妆护肤", "家电换新", "健身私教"],
    "本金(元)": [5000, 20000, 3000, 8000, 15000],
    "分期利息(元)": [420, 1680, 252, 672, 1260],
    "最低还款利息(元)": [978, 3912, 587, 1565, 2934],
    "分期总还款(元)": [5420, 21680, 3252, 8672, 16260],
    "最低总还款(元)": [5978, 23912, 3587, 9565, 17934]
})

st.dataframe(reference_scenes, use_container_width=True, hide_index=True)

st.markdown("""
> 📌 **说明**：上表数据基于五大行官网公示利率计算：
> - 最低还款：日利率0.05%，按月复利
> - 分期还款：月费率0.7%（12期）
""")

# ========== 结论 ==========
st.info(f"""
💡 **即时结论**（基于当前参数：本金 {amount:,} 元，{months} 期）

- **全额还款**：利息 0 元，✅ 最划算
- **分期还款**：多付 {inst_interest:,.0f} 元，适合大额消费短期周转
- **最低还款**：多付 {min_interest:,.0f} 元，⚠️ 利息最高，应尽量避免
""")

# ========== 数据来源 ==========
with st.expander("📄 数据来源（可溯源）"):
    st.markdown("""
    | 银行 | 利率规则 | 来源链接 |
    |------|---------|---------|
    | 工商银行 | 日利率万分之五，按月复利 | [查看官网](https://www.icbc.com.cn/page/890517450792525824.html) |
    | 农业银行 | 日利率万分之五，按月复利，分期费率0.80% | [查看官网](https://www.abchina.com/cn/CreditCard/WealthManagement/Bill/) |
    | 中国银行 | 日利率万分之五，按月复利 | [查看官网](https://www.boc.cn/bcservice/bc3/bc31/201203/t20120331_1767028.html) |
    | 建设银行 | 日利率万分之五，按月复利，分期费率0.75% | [查看官网](https://creditcard1.ccb.com/chn/2022-08/29/article_2022082916344488399.shtml) |
    | 交通银行 | 日利率万分之五，按月复利，分期费率0.70% | [查看官网](https://creditcardapp.bankcomm.com/openapps/cms/1431733796531773.html) |
    
    > 分期费率取平均值0.75%，数据来源于各银行官网公示的服务价目表
    """)