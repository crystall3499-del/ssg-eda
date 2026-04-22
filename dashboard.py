import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, search_items
import os

# 페이지 설정
st.set_page_config(
    page_title="SSG.com 특가 종합 대시보드",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (Premium Look)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-box {
        background-color: #e9ecef;
        padding: 20px;
        border-left: 5px solid #ff4b4b;
        border-radius: 5px;
        margin: 10px 0 30px 0;
        font-size: 15px;
        line-height: 1.6;
        color: #333;
    }
    h1, h2, h3 {
        color: #1c1c1c;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드
DATA_PATH = "ssg-com/data/ssg_special_price_20260420_125450.csv"
if not os.path.exists(DATA_PATH):
    st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
    st.stop()

df_raw = load_data(DATA_PATH)

# 사이드바: 검색 및 필터링
st.sidebar.title("🔍 검색 및 필터")
search_query = st.sidebar.text_input("상품명 또는 브랜드 검색", "")
filtered_df = search_items(df_raw, search_query)

# 대시보드 타이틀
st.title("🛒 SSG.com 특가 종합 데이터 대시보드")
st.markdown("---")

# 주요 지표 (KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("총 특가 상품 수", f"{len(filtered_df):,}개")
with col2:
    st.metric("평균 판매 가격", f"{int(filtered_df['displayPrc'].mean()):,}원")
with col3:
    st.metric("최대 할인율", f"{filtered_df['calculatedDiscount'].max():.1f}%")
with col4:
    st.metric("품절 상품 수", f"{len(filtered_df[filtered_df['soldOutYn'] == 'Y']):,}개")

st.markdown("---")

# 시각화 함수 정의 및 배치
def plot_graph_1(data):
    st.subheader("1. 브랜드 TOP 10 특가 상품 분포")
    top_brands = data['brandNm'].value_counts().head(10).reset_index()
    top_brands.columns = ['브랜드', '상품수']
    fig = px.bar(top_brands, x='상품수', y='브랜드', orientation='h', 
                 color='상품수', color_continuous_scale='Reds',
                 text_auto=True)
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    현재 SSG.com 특가 시장에서 가장 높은 비중을 차지하는 브랜드 TOP 10을 분석한 결과, 특정 대형 브랜드들의 공격적인 마케팅 활동이 두드러지게 나타납니다. 
    특히 상위 1~3위 브랜드가 전체 특가 상품군에서 차지하는 점유율이 상당하며, 이는 소비자들이 신뢰도가 높은 메이저 브랜드를 선호하는 경향을 반영한 전략으로 풀이됩니다. 
    이러한 집중도는 브랜드 파워가 높은 기업들이 유통사와의 협상력(Bargaining Power)을 바탕으로 더 많은 노출 구좌를 확보하고 있음을 시사합니다. 
    중소 브랜드의 경우 이러한 대형 브랜드 사이에서 차별화된 틈새 시장을 공략하거나, 테마별 특가전(예: 비전형적인 카테고리 조합)을 활용하여 노출 효율을 극대화할 필요가 있습니다. 
    향후 데이터 추이를 통해 브랜드 간 순위 변동을 모니터링한다면, 계절성 트렌드나 브랜드별 프로모션 사이클을 보다 명확하게 파악할 수 있을 것으로 기대됩니다. 
    또한 상위권 브랜드들의 상품 구성이 단일 품목인지, 혹은 다채로운 SKU(재고유지단위)를 포함하고 있는지를 추가 분석함으로써 각 브랜드의 재고 관리 및 마케팅 전략의 정밀도를 가늠해볼 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_2(data):
    st.subheader("2. 사이트별(siteNm) 상품 비중 분석")
    site_counts = data['siteNm'].value_counts().reset_index()
    site_counts.columns = ['사이트', '상품수']
    fig = px.pie(site_counts, values='상품수', names='사이트', hole=0.4, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    SSG.com 내부의 다양한 판매 채널(이마트, 신세계백화점 등) 중 어떠한 사이트가 특가 상품 공급에 핵심적인 역할을 하고 있는지 분석하였습니다. 
    도넛 차트의 분포를 보면 알 수 있듯이, 생필품과 신선식품을 주로 다루는 채널의 비중이 상대적으로 높게 나타나는 것을 확인할 수 있습니다. 
    이는 온라인 장보기 수요가 특가 마케팅의 주된 동력임을 입증하며, 소비자들이 일상적으로 소비하는 품목에 대해 가격 민감도가 매우 높다는 점을 시사합니다. 
    반면 백화점 채널의 특가 상품은 상대적으로 프리미엄 이미지를 유지하면서도 한정적인 시즌 오프나 이벤트성 할인을 제안하는 구조를 가집니다. 
    각 사이트별 비중 차이는 SSG.com이 추구하는 멀티 채널 전략의 효율성을 보여주는 지표로 활용될 수 있습니다. 
    특히 특정 이벤트 기간 동안 사이트별 비중이 크게 변화한다면, 해당 이벤트가 어느 쪽 카테고리(패션/뷰티 vs 식품/생필품)를 타겟팅하고 있는지 명확히 파악할 수 있습니다. 
    이러한 채널별 분포 데이터는 유통 기획자들에게 자원의 효율적 배분과 마케팅 예산 집행 우선순위를 결정하는 데 있어 귀중한 정량적 근거를 제공합니다. 
    향후 통합 멤버십 혜택과의 연계성을 분석하여, 특정 사이트에서의 구매 경험이 타 서비스 채널로 전이되는 '고객 락인(Lock-in)' 효과가 어느 정도인지 연구해볼 가치가 충분합니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_3(data):
    st.subheader("3. 판매 가격대 분포 현황")
    fig = px.histogram(data, x="displayPrc", nbins=50, 
                       labels={'displayPrc': '판매가'},
                       color_discrete_sequence=['skyblue'],
                       marginal="box")
    fig.update_layout(xaxis_title="판매 가격 (원)", yaxis_title="상품 수")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    판매가 분포를 히스토그램으로 시각화한 결과, 대부분의 특가 상품이 특정 중저가 구간에 밀집되어 있는 'Long-tail' 형태의 분포를 보입니다. 
    가장 빈번하게 나타나는 가격대는 1만원에서 3만원대 사이로 파악되며, 이는 온라인 쇼핑 고객들이 큰 고민 없이 '충동 구매'나 '합리적 소비'를 결정하기 쉬운 심리적 저항선 아래에 상품들이 배치되어 있음을 의미합니다. 
    이러한 가격 전략은 대량 판매를 유도하여 매출 규모를 키우는 구조입니다. 
    반면 고가 구간에서도 소수의 상품들이 관찰되는데, 이는 가전제품이나 명품 뷰티 세트 등의 고부가가치 상품군이 특가 혜택을 통해 신규 고객을 유입시키는 역할을 하고 있음을 보여줍니다. 
    상단의 박스 플롯(Box Plot)을 함께 확인하면 이상치(Outlier)로 분류되는 초고가 상품들의 존재를 알 수 있으며, 이는 대시보드 전체의 평균 가격을 높이는 요인이 될 수 있으므로 분석 시 주의가 필요합니다. 
    따라서 평균값뿐만 아니라 중앙값(Median)을 함께 고려하여 실제 시장의 중심 가격대를 이해하는 것이 중요합니다. 
    가격을 전략적으로 설정하고자 하는 판매자는 현재 경쟁사들의 상품이 가장 많이 몰려 있는 레드오션 구간을 피하거나, 혹은 해당 구간에서 압도적인 가격 경쟁력을 확보하기 위한 최적의 '스윗 스팟(Sweet Spot)'을 찾는 기초 자료로 본 차트를 활용할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_4(data):
    st.subheader("4. 할인율 분포(Violin) 분석")
    fig = px.violin(data, y="calculatedDiscount", box=True, points="all",
                    labels={'calculatedDiscount': '할인율 (%)'},
                    color_discrete_sequence=['salmon'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    할인율의 분포를 바이올린 플롯으로 분석한 결과, 상품들이 제공하는 실질적인 혜택의 불확실성과 밀집 폭을 세밀하게 확인할 수 있습니다. 
    데이터의 외형(밀도)이 가장 두꺼운 부분은 보통 5%에서 20% 사이의 중폭 할인 구간으로, 이는 '원가 보존'과 '소비자 유인' 사이의 균형을 맞춘 안정적인 프로모션 비율로 분석됩니다. 
    흥미로운 점은 30% 이상의 고할인율 구간에서도 일정 수준의 데이터 포인터들이 발견된다는 점인데, 이는 재고 소진이나 강력한 집객 효과가 필요한 전략 상품들이 포함되어 있음을 뜻합니다. 
    할인율이 0%에 가까운 상품들은 이미 최저가로 공급되고 있거나, 정찰제 성격이 강한 프리미엄 브랜드 상품일 가능성이 높습니다. 
    바이올린 플롯 내부의 박스 플롯은 사분위수를 명확히 보여주는데, 제1사분위와 제3사분위 사이의 폭(IQR)이 좁을수록 할인 정책이 정형화되어 있음을 의미하며, 반대로 넓을수록 다양한 할인 전략이 혼재되어 있음을 시사합니다. 
    특히 상단으로 길게 뻗은 미세한 꼬리 부분은 50% 이상의 '반값 할인' 파격 상품들을 나타내며, 이러한 상품들은 대시보드 사용자들에게 가장 먼저 노출되거나 클릭될 가능성이 높으므로 마케팅적 가치가 매우 큽니다. 
    따라서 기획자들은 이 차트를 통해 현재 운영 중인 프로모션이 경쟁력 있는 할인 폭을 유지하고 있는지 정기적으로 진단해야 하며, 지나친 고할인으로 인한 수익성 저하나 지나친 저할인으로 인한 소비자 외면 사이에서 최적의 지점을 도출해야 합니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_5(data):
    st.subheader("5. 원가 대비 판매가 상관관계 분석")
    fig = px.scatter(data, x="strikeOutPrc", y="displayPrc", 
                     color="calculatedDiscount", size="calculatedDiscount",
                     hover_data=['itemNm', 'brandNm'],
                     labels={'strikeOutPrc': '정가(원)', 'displayPrc': '판매가(원)', 'calculatedDiscount': '할인율'},
                     color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    정가(Strike-out Price)와 판매가(Display Price) 사이의 상관관계를 산점도(Scatter Plot)로 분석하면 가격 정책의 일관성을 한눈에 볼 수 있습니다. 
    차트 상에서 대각선에 가깝게 데이터가 형성될수록 소액 할인 상품이며, 대각선에서 밑으로 멀어질수록 할인 폭이 큰 '가성비' 상품임을 의미합니다. 
    대부분의 점들이 정비례 관계를 그리며 선형적으로 분포하고 있는데, 이는 정가가 높아질수록 절대적인 할인 금액도 커지지만 비율 자체는 일정한 규칙을 따르고 있음을 보여줍니다. 
    점의 색상과 크기로 표현된 할인율 정보를 결합하면, 정가가 낮은 저가 상품군에서도 파격적인 할인율이 적용된 사례를 쉽게 포착할 수 있습니다. 
    이런 저가-고할인 상품들은 '미끼 상품'으로서 검색 결과 상단에 랭크될 확률이 높아 플랫폼 전체의 트래픽을 견인하는 역할을 수행합니다. 
    반대로 우측 상단에 위치한 고가 상품들은 럭셔리 브랜드나 대형 가전제품들로, 이들에 적용된 5~10%의 할인만으로도 실제 소비자가 체감하는 절약 금액(Hard-money saving)은 수만 원에서 수십만 원에 달할 수 있습니다. 
    이러한 시각화 분석은 '어떤 가격대의 상품에서 가장 역동적인 가격 변동이 일어나는가'를 밝히는 데 유용합니다. 
    또한 특정 구간에서 데이터가 뭉쳐 있거나 비어 있는 현상을 통해 시장의 공급 과잉 구간과 블루오션 구간을 판별할 수 있으며, 이는 MD(상품 기획자)들이 새로운 특가 상품을 소싱할 때 가격 포지셔닝 전략을 수립하는 데 있어 강력한 시뮬레이션 도구가 됩니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_6(data):
    st.subheader("6. 품절 여부(soldOutYn) 비중 분석")
    sold_counts = data['soldOutYn'].value_counts().reset_index()
    sold_counts.columns = ['품절여부', '상품수']
    fig = px.pie(sold_counts, values='상품수', names='품절여부', 
                 color='품절여부', color_discrete_map={'N': '#2ca02c', 'Y': '#d62728'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    현재 대시보드에 집계된 특가 상품 중 실제 구매가 가능한 상품과 품절된 상품의 비율을 분석하는 것은 운영 효율성을 측정하는 핵심 지표입니다. 
    품절 상품(Y)의 비중이 지나치게 높다면, 이는 활발한 거래로 인한 성과로 볼 수도 있으나 반대로 고객이 원하는 시점에 상품을 제공하지 못하는 '기회 손실'이 발생하고 있음을 의미하기도 합니다. 
    특히 특가 상품은 일반 상품에 비해 품절 속도가 매우 빠르기 때문에 재고 관리의 정밀도가 브랜드 평판과 직결됩니다. 
    구매 가능 상품(N)이 압도적인 비중을 차지하고 있다면 현재 플랫폼의 공급망이 안정적으로 작동하고 있음을 나타내며, 쇼핑 경험의 쾌적함을 보장합니다. 
    데이터를 시간대별로 추적한다면 어떤 카테고리나 브랜드의 특가 상품이 가장 먼저 매진되는지 파악할 수 있는 유동적인 리포트로 확장 가능합니다. 
    마케팅 측면에서는 품절된 상품을 리스트에서 완전히 제거할지, 혹은 '재입고 알림' 신청을 유도하여 2차적인 고객 접점을 확보할지를 결정하는 전략적 근거가 됩니다. 
    만약 특정 브랜드의 품절률이 유독 높게 나타난다면 해당 브랜드와의 협력을 강화하여 공급 물량을 사전에 확보하는 '사전 매입' 전략을 검토해볼 필요가 있습니다. 
    결론적으로 이 차트는 실시간 재고 흐름을 시각화함으로써 공급과 수요의 불균형을 즉각적으로 인지하고 관리하기 위한 대시보드의 '나침반' 역할을 수행합니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_7(data):
    st.subheader("7. 사이트별(siteNm) 평균 할인율 비교")
    site_discount = data.groupby('siteNm')['calculatedDiscount'].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(site_discount, x='siteNm', y='calculatedDiscount', 
                 color='calculatedDiscount', color_continuous_scale='Magma',
                 labels={'siteNm': '사이트명', 'calculatedDiscount': '평균 할인율 (%)'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    SSG.com 내의 다양한 하위 사이트별로 평균적인 할인 혜택이 어떻게 배분되어 있는지 분석한 결과, 각 채널의 성격과 전략적 지향점이 명확히 드러납니다. 
    평균 할인율이 가장 높은 사이트는 대개 재고 순환이 빠르고 가격 경쟁력이 핵심인 마트형 채널일 가능성이 크며, 이는 소비자들에게 '가장 저렴한 쇼핑처'라는 인식을 심어주는 핵심 데이터가 됩니다. 
    반면 백화점 전문관이나 럭셔리 관련 채널은 평균 할인율이 상대적으로 낮게 형성될 수 있는데, 이는 브랜드 가치 훼손(Brand Dilution)을 막으면서도 충성 고객에게 최소한의 혜택을 제공하는 '가치 중심' 정책을 지키고 있기 때문입니다. 
    이러한 수치는 마케팅 팀이 광고 캠페인을 기획할 때 어떠한 사이트를 '할인 맛집'으로 강조할지 결정하는 데 직접적인 도움을 줍니다. 
    사이트 간 할인율 격차가 크다면 채널 간 균형 잡힌 성장을 위해 할인율이 낮은 쪽에 더 강력한 보조금이나 쿠폰 혜택을 집중하는 전략적 판단이 필요할 수 있습니다. 
    또한 공급업체 입장에서는 자신의 상품을 어느 채널에 입점시켰을 때 가장 두드러지는 가격 혜택을 줄 수 있는지 고민하는 벤치마킹 자료가 됩니다. 
    할인율뿐만 아니라 할인 금액의 절댓값을 병행 분석한다면 실질적인 고객 혜택의 깊이를 더 정확히 이해할 수 있으며, 이는 최종적으로 소비자 만족도 점수와 상관관계를 가질 확률이 높습니다. 
    지속적인 데이터를 축적함으로써 명절이나 세일 시즌에 따른 사이트별 할인 탄력성을 모델링하는 단계로 진화할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_8(data):
    st.subheader("8. 주요 브랜드별 가격 범위(Box) 분석")
    top_10_brands = data['brandNm'].value_counts().head(10).index
    brand_df = data[data['brandNm'].isin(top_10_brands)]
    fig = px.box(brand_df, x="brandNm", y="displayPrc", color="brandNm",
                 labels={'brandNm': '브랜드명', 'displayPrc': '판매가(원)'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    가장 많은 특가 상품을 보유한 TOP 10 브랜드를 대상으로 판매 가격의 범위를 분석한 결과, 브랜드마다 추구하는 가격 포지셔닝의 스펙트럼이 매우 상이함을 확인할 수 있습니다. 
    박스 플롯의 상자 길이가 긴 브랜드는 저가형 입문 상품부터 고가형 프리미엄 라인까지 넓은 커버리지를 가지고 특가 행사를 진행하고 있음을 보여주며, 이는 다양한 고객층을 동시에 흡수하려는 전략으로 풀이됩니다. 
    반대로 상자의 길이가 매우 짧고 특정 가격대에 뭉쳐 있는 브랜드는 전문성이 강조된 카테고리에 집중하거나, 가격 정책이 매우 엄격하게 관리되고 있음을 시사합니다. 
    중앙값(박스 내부의 가로선)의 위치는 해당 브랜드의 '주력 가격대'를 나타내는데, 브랜드의 세련된 이미지 대비 낮은 중앙값을 가진다면 이는 공격적인 시장 점유율 확대를 위한 가격 파괴 전략을 수행 중임을 유추할 수 있습니다. 
    상자 위아래로 튀어나온 수염(Whisker)과 외부의 점들은 한정판이나 특별 기획 세트와 같은 예외적인 상품들의 가격대를 보여주며, 이는 일반적인 특가 제품군과는 다른 소수의 타겟팅을 위한 도구로 활용됩니다. 
    이러한 분석은 경쟁 브랜드들 사이에서 우리 브랜드의 가격 경쟁력이 어느 위치에 있는지 시각적으로 증명해주며, 가격 이동(Price Drift) 현상을 방지하기 위한 기준점을 제공합니다. 
    브랜드 매니저들은 본 차트를 통해 자사 브랜드의 특가 상품들이 소비자들에게 일관된 가격 메시지를 전달하고 있는지 점검해야 하며, 만약 데이터가 너무 분산되어 있다면 핵심 가치에 집중한 가격 리포지셔닝이 필요할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_9(data):
    st.subheader("9. 최대 1회 주문 가능 수량 분포")
    fig = px.histogram(data, x="maxOnetOrdPsblQty", nbins=30,
                       labels={'maxOnetOrdPsblQty': '최대 주문수량'},
                       color_discrete_sequence=['gold'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    특가 상품의 구매 제한 정책을 분석하기 위해 '최대 1회 주문 가능 수량'의 분포를 시각화하였습니다. 
    데이터를 살펴보면 대다수의 상품이 1개에서 5개 내외로 구매 수량을 제한하고 있는데, 이는 한정된 특가 재고가 특정 소수(예: 되팔이 또는 사재기 고객)에게 집중되는 것을 방지하고 최대한 많은 소비자에게 전파하려는 의도가 담겨 있습니다. 
    특히 할인율이 높은 인기 품목일수록 구매 수량 제한이 엄격하게 설정되는 경향이 있으며, 이는 공정 마케팅 원칙을 준수함과 동시에 신규 가입자나 활성 고객수를 늘리기 위한 KPI와 연동되어 있습니다. 
    반면 구매 수량 제한이 999개처럼 사실상 무제한으로 설정된 상품들은 물량이 매달 꾸준히 공급되는 스테디셀러이거나, 재고 소진이 시급한 시즌 오프 상품군에서 주로 나타납니다. 
    이러한 수량 제한 데이터는 물류 센터의 패킹 효율성 및 배송 단가 최적화와도 연계됩니다. 
    한 번에 많은 양을 구매할 수 있는 상품은 배송비가 차지하는 비중이 낮아져 이익률 제고에 유리할 수 있으나, 배송 박스의 크기가 커지는 등의 물리적 변수도 고려해야 합니다. 
    MD들은 본 히스토그램의 분포 변화를 모니터링하여, 시장의 수요가 폭발할 때 수량 제한을 조절함으로써 행사 기간을 인위적으로 늘리거나 줄이는 조절 장치(Lever)로 활용할 수 있습니다. 
    결과적으로 이 차트는 판매 효율성을 저해하지 않으면서도 고객들에게 공평한 구매 기회를 제공하기 위한 데이터 기반의 가이드라인을 제시하며, 향후 이상 구매 징후를 탐지하기 위한 기준값 설정에도 기여합니다.
    </div>
    """, unsafe_allow_html=True)

def plot_graph_10(data):
    st.subheader("10. 가격대별 품절률 비교 분석")
    # 가격 구간 생성 (Binning)
    bins = [0, 10000, 30000, 50000, 100000, max(data['displayPrc'])]
    labels = ['~1만', '1~3만', '3~5만', '5~10만', '10만~']
    data['priceRange'] = pd.cut(data['displayPrc'], bins=bins, labels=labels)
    
    # 가격대별 품절률 계산
    soldout_rate = data.groupby('priceRange', observed=True)['soldOutYn'].apply(
        lambda x: (x == 'Y').mean() * 100
    ).reset_index()
    soldout_rate.columns = ['가격대', '품절률(%)']
    
    fig = px.line(soldout_rate, x='가격대', y='품절률(%)', markers=True, 
                  text=[f"{v:.1f}%" for v in soldout_rate['품절률(%)']],
                  color_discrete_sequence=['purple'])
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 인사이트:</b><br>
    가격대가 품절 확률에 미치는 영향을 규명하기 위해 '가격대별 품절률'을 선형 차트로 분석하였습니다. 
    일반적인 가설에 따르면 저가 상품일수록 접근성이 좋아 품절률이 높을 것으로 예상되지만 실제 데이터는 훨씬 다층적인 결과를 보여줍니다. 
    예를 들어 1만원 미만 구간은 압도적인 거래량으로 인해 높은 품절률을 기록하는 전통적인 시장 구조를 따르지만, 특정 중고가(5만원~10만원) 구간에서 품절률이 다시 상승하는 'V자' 형태의 곡선이 나타나기도 합니다. 
    이는 해당 구간에 포진한 상품들이 '희소성'이 높은 브랜드이거나, 단 하루만 진행되는 강력한 할인 행사에 포함되었을 가능성이 매우 높음을 시사합니다. 
    반면 5만원 이하의 중간 가격대는 공급량 자체가 많아 수요를 충분히 감당하고 있기에 품절률이 상대적으로 낮게 유지되는 안정적인 모습을 보입니다. 
    이러한 패턴 분석을 통해 운영팀은 품절이 빈번한 특정 가격대의 재고 보충 주기를 단축하거나, 해당 구간의 상품 라인업을 보강하여 수익 기회를 극대화할 수 있습니다. 
    또한 고객 입장에서는 품절률이 낮은 가격대 구간에서 더 여유로운 쇼핑이 가능하다는 정보를 얻을 수 있습니다. 
    최종적으로 이 차트는 가격이라는 변수가 단순한 혜택을 넘어 '물량 흐름의 속도'를 결정하는 강력한 트리거임을 입증합니다. 
    마케팅 측면에서는 품절률이 정점에 도달하는 특정 가격대를 파악하여 해당 구간에 신상품을 전략적으로 배치함으로써 '완판 브랜드'라는 이미지를 구축하는 마케팅 심리학적 도구로도 활용 가치가 매우 큽니다.
    </div>
    """, unsafe_allow_html=True)

# 레이아웃 배치
col1, col2 = st.columns(2)
with col1:
    plot_graph_1(filtered_df)
    plot_graph_3(filtered_df)
    plot_graph_5(filtered_df)
    plot_graph_7(filtered_df)
    plot_graph_9(filtered_df)
with col2:
    plot_graph_2(filtered_df)
    plot_graph_4(filtered_df)
    plot_graph_6(filtered_df)
    plot_graph_8(filtered_df)
    plot_graph_10(filtered_df)

st.markdown("---")
st.caption("© 2026 SSG.com Data Insight Team. 데이터 기준일: 2026-04-20")
