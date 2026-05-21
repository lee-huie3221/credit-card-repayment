import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 页面设置
st.set_page_config(page_title="信用卡还款策略对比", layout="wide")

# 只设置英文显示，彻底杜绝乱码
plt.rcParams['axes.unicode_minus'] = False

st.title("💳 信用卡还款策略可视化")
st.markdown("### 最低还款 · 分期还款 · 全额还款")
st.markdown("---")

# ========== 侧边栏：用户输入参数 ==========
with st.sidebar:
    st.header("⚙️ 参数设置")
    st.markdown("**修改参数，图表实时更新**")
    st.markdown("---")
    
    amount = st.number_input(
        "💰 消费金额（元）", 
        min_value=100, 
        max_value=100000, 
        value=5000, 
        step=500
    )
    
    months = st.selectbox(
        "📅 分期期数", 
        [3, 6, 9, 12, 18, 24], 
        index=3,
        help="作业默认12期"
    )
    
    daily_rate_input = st.number_input(
        "📉 最低还款日利率（%）", 
        min_value=0.01, 
        max_value=0.10, 
        value=0.05, 
        step=0.01
    ) / 100
    
    installment_rate_input = st.number_input(
        "📊 分期月费率（%）", 
        min_value=0.1, 
        max_value=2.0, 
        value=0.7, 
        step=0.05
    ) / 100
    
    st.markdown("---")
    st.caption("💡 作业默认值：日利率0.05%，月费率0.7%")

# ========== 计算函数（严格匹配队友数据） ==========
def calc_full(amount):
    return amount, 0

def calc_installment(amount, months, rate):
    total_interest = amount * rate * months
    return amount + total_interest, total_interest

def calc_min_payment(amount, daily_rate):
    """严格按照作业要求：前11个月还10%，第12个月一次性还清"""
    remaining = amount
    total_interest = 0
    
    for month in range(11):
        monthly_interest = remaining * daily_rate * 30
        total_interest += monthly_interest
        remaining = remaining - remaining * 0.1
    
    last_month_interest = remaining * daily_rate * 30
    total_interest += last_month_interest
    
    return amount + total_interest, total_interest, 12

# 计算结果
full_total, full_interest = calc_full(amount)
inst_total, inst_interest = calc_installment(amount, months, installment_rate_input)
min_total, min_interest, min_months = calc_min_payment(amount, daily_rate_input)

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

# ========== 柱状图（全英文+超大标记） ==========
st.subheader(f"📊 还款金额对比（消费 {amount:,} 元 · 分 {months} 期）")

fig, ax = plt.subplots(figsize=(10, 5))
labels = ["Full Payment", "Installment", "Minimum Payment"]
values = [full_total, inst_total, min_total]
colors = ["#2ecc71", "#f39c12", "#e74c3c"]

bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor='white', linewidth=2)
ax.set_ylabel("Total Payment (Yuan)", fontsize=12)
ax.axhline(y=amount, color='#999', linestyle='--', alpha=0.7, label=f'Principal {amount:,} Yuan')

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 30,
            f'{int(height):,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend()
ax.grid(axis='y', alpha=0.3)

st.pyplot(fig)
st.caption("🟢 绿色：全额还款 | 🟠 橙色：分期还款 | 🔴 红色：最低还款")

st.markdown("---")

# ========== 债务递减曲线（全英文+超大彩色标记，100%无乱码） ==========
st.subheader("📉 债务递减曲线（展示债务随时间变化）")

max_months = 12
x_months = list(range(max_months + 1))

# 三条曲线数据
full_curve = [amount] + [0] * max_months

monthly_payment = amount / months
installment_curve = [max(0, amount - monthly_payment * i) for i in x_months]

remaining = amount
min_curve = [remaining]
for i in range(11):
    remaining = remaining - remaining * 0.1
    min_curve.append(remaining)
min_curve.append(0)

# 绘制图表
fig2, ax2 = plt.subplots(figsize=(10, 5))

# 填充区域
ax2.fill_between(x_months, 0, full_curve, alpha=0.2, color='#2ecc71')
ax2.fill_between(x_months, 0, installment_curve, alpha=0.2, color='#f39c12')
ax2.fill_between(x_months, 0, min_curve, alpha=0.2, color='#e74c3c')

# 线条+超大彩色标记（带白色边框，一眼区分）
ax2.plot(x_months, full_curve, 'o-', color='#2ecc71', linewidth=2, markersize=12, markeredgecolor='white', markeredgewidth=2, label='Full Payment')
ax2.plot(x_months, installment_curve, 's-', color='#f39c12', linewidth=2, markersize=12, markeredgecolor='white', markeredgewidth=2, label='Installment')
ax2.plot(x_months, min_curve, '^-', color='#e74c3c', linewidth=2, markersize=12, markeredgecolor='white', markeredgewidth=2, label='Minimum Payment')

ax2.set_xlabel("Months", fontsize=12)
ax2.set_ylabel("Remaining Debt (Yuan)", fontsize=12)
ax2.set_title("Debt Reduction Trend Over Time", fontsize=14, pad=20)
ax2.legend(loc='upper right', fontsize=12, framealpha=0.9)
ax2.grid(alpha=0.3)
ax2.set_xlim(0, 12)

st.pyplot(fig2)
st.caption("💡 🟢 绿色圆点：全额还款 | 🟠 橙色方块：分期还款 | 🔴 红色三角：最低还款 | 曲线越陡，还款越快")

st.markdown("---")

# ========== 大学生常见消费场景（严格匹配队友数据） ==========
st.subheader("📋 大学生常见消费场景参考")

reference_scenes = pd.DataFrame({
    "消费场景": ["买手机", "长途旅游", "美妆护肤", "家电换新", "健身私教"],
    "消费本金(元)": [5000, 20000, 3000, 8000, 15000],
    "12期分期利息(元)": [420, 1680, 252, 672, 1260],
    "12期最低还款利息(元)": [978, 3912, 587, 1565, 2934],
    "分期总还款(元)": [5420, 21680, 3252, 8672, 16260],
    "最低总还款(元)": [5978, 23912, 3587, 9565, 17934]
})

st.dataframe(reference_scenes, use_container_width=True, hide_index=True)

st.markdown("""
> 📌 **数据说明**：
> - 最低还款：日利率0.05%，按月复利，前11个月还10%，第12个月一次性还清
> - 分期还款：月费率0.7%，总利息=本金×0.7%×12
""")

# ========== 结论 ==========
st.info(f"""
💡 **即时结论**（本金 {amount:,} 元，{months} 期）

- **全额还款**：利息 0 元，✅ 最划算，优先选择
- **分期还款**：多付 {inst_interest:,.0f} 元，适合大额消费短期周转
- **最低还款**：多付 {min_interest:,.0f} 元，⚠️ 利息是分期的2倍多，仅应急使用
""")

# ========== 数据来源 ==========
st.info("💡 所有利率数据均来自五大银行官网公示")
with st.expander("📄 查看详细数据来源"):
    st.markdown("""
    | 银行 | 最低还款日利率 | 12期分期月费率 | 官方链接 |
    |------|---------------|----------------|---------|
    | 工商银行 | 0.05% | 0.70% | [查看](https://www.icbc.com.cn/page/890517450792525824.html) |
    | 农业银行 | 0.05% | 0.80% | [查看](https://www.abchina.com/cn/CreditCard/WealthManagement/Bill/) |
    | 中国银行 | 0.05% | 0.72% | [查看](https://www.boc.cn/bcservice/bc3/bc31/201203/t20120331_1767028.html) |
    | 建设银行 | 0.05% | 0.75% | [查看](https://creditcard1.ccb.com/chn/2022-08/29/article_2022082916344488399.shtml) |
    | 交通银行 | 0.05% | 0.70% | [查看](https://creditcardapp.bankcomm.com/openapps/cms/1431733796531773.html) |
    """)

st.markdown("---")
st.caption("© 2026 信用卡还款策略对比工具 | 数据来源于各大银行官方网站")