import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. CONFIGURAÇÕES INICIAIS DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="WebGIS Inundação",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("### 🚨 Análise de Risco de Inundação")
st.markdown("---")


# ==========================================
# 2. FUNÇÕES AUXILIARES
# ==========================================
@st.cache_data
def ler_arquivo_espacial(arquivo):
    """Lê arquivos espaciais baseado na extensão, com cache para performance."""
    if arquivo.name.endswith('.parquet'):
        return gpd.read_parquet(arquivo)
    return gpd.read_file(arquivo)


def formatar_numero_br(valor, sigla):
    """Formata números para o padrão brasileiro (ex: 1.234,56 km²)."""
    return f"{valor:,.2f} {sigla}".replace(',', 'X').replace('.', ',').replace('X', '.')


# ==========================================
# 3. MENU LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("#### Parâmetros da Análise")
    upload_ocupacao = st.file_uploader('1. Área de Ocupação / Perímetro', type=['zip', 'geojson', 'parquet', 'kml'])
    upload_inundacao = st.file_uploader('2. Mancha de Inundação', type=['zip', 'geojson', 'parquet', 'kml'])

    st.markdown("---")
    unidade_medida = st.selectbox(
        'Unidade de Medida (Área)',
        ['Metros Quadrados (m²)', 'Hectares (ha)', 'Quilômetros Quadrados (km²)'],
        index=2  # km² como padrão
    )

# ==========================================
# 4. MOTOR DE GEOPROCESSAMENTO E DASHBOARD
# ==========================================
if upload_ocupacao and upload_inundacao:

    with st.spinner('Calculando interseções espaciais e renderizando dashboard...'):
        try:
            # --- LEITURA E PADRONIZAÇÃO DE CRS ---
            gdf_ocupacao = ler_arquivo_espacial(upload_ocupacao)
            gdf_inundacao = ler_arquivo_espacial(upload_inundacao)

            if gdf_inundacao.crs != gdf_ocupacao.crs:
                gdf_inundacao = gdf_inundacao.to_crs(gdf_ocupacao.crs)

            # Conversão para CRS Métrico (SIRGAS 2000 UTM 22S - EPSG:31982)
            if gdf_ocupacao.crs.is_geographic:
                crs_metrico = 31982
                gdf_ocupacao_metrico = gdf_ocupacao.to_crs(epsg=crs_metrico)
                gdf_inundacao_metrico = gdf_inundacao.to_crs(epsg=crs_metrico)
            else:
                gdf_ocupacao_metrico = gdf_ocupacao.copy()
                gdf_inundacao_metrico = gdf_inundacao.copy()

            # --- CURA TOPOLÓGICA ---
            # Encadeamento de make_valid e buffer para maior velocidade e segurança
            gdf_ocupacao_metrico.geometry = gdf_ocupacao_metrico.geometry.make_valid().buffer(0)
            gdf_inundacao_metrico.geometry = gdf_inundacao_metrico.geometry.make_valid().buffer(0)

            gdf_ocupacao_metrico = gdf_ocupacao_metrico[~gdf_ocupacao_metrico.is_empty]
            gdf_inundacao_metrico = gdf_inundacao_metrico[~gdf_inundacao_metrico.is_empty]

            # --- OPERAÇÃO ESPACIAL (CLIP) ---
            ocupacao_inundada_metrica = gpd.clip(gdf_inundacao_metrico, gdf_ocupacao_metrico)
            ocupacao_inundada_metrica = ocupacao_inundada_metrica[~ocupacao_inundada_metrica.is_empty]

            # --- CÁLCULO DE ÁREAS ---
            area_m2_total = gdf_ocupacao_metrico.area.sum()
            area_m2_inundada = ocupacao_inundada_metrica.area.sum()
            porcentagem_afetada = (area_m2_inundada / area_m2_total) * 100 if area_m2_total > 0 else 0

            # --- LÓGICA DE CONVERSÃO DE UNIDADES ---
            if unidade_medida == 'Hectares (ha)':
                divisor, sigla = 10000, "ha"
            elif unidade_medida == 'Quilômetros Quadrados (km²)':
                divisor, sigla = 1000000, "km²"
            else:
                divisor, sigla = 1, "m²"

            area_exibicao_ocup = area_m2_total / divisor
            area_exibicao_inun = area_m2_inundada / divisor

            # ==========================================
            # 5. RENDERIZAÇÃO VISUAL (KPIS)
            # ==========================================
            col1, col2, col3 = st.columns(3)

            with col1:
                with st.container(border=True):
                    st.metric("Área Total Analisada", formatar_numero_br(area_exibicao_ocup, sigla))

            with col2:
                with st.container(border=True):
                    st.metric("Área Sujeita a Inundação", formatar_numero_br(area_exibicao_inun, sigla))

            with col3:
                with st.container(border=True):
                    st.metric("Comprometimento do Terreno", f"{porcentagem_afetada:.1f}%", delta="Impacto Crítico",
                              delta_color="inverse")

            st.markdown("---")

            # ==========================================
            # 6. RENDERIZAÇÃO DO MAPA (FOLIUM)
            # ==========================================
            # Reprojeção para WGS84 e simplificação leve para performance do navegador
            gdf_mapa_fundo = gdf_ocupacao_metrico.to_crs(epsg=4326)[['geometry']]
            gdf_mapa_fundo.geometry = gdf_mapa_fundo.geometry.simplify(0.00005)

            if not ocupacao_inundada_metrica.empty:
                gdf_mapa_mancha = ocupacao_inundada_metrica.to_crs(epsg=4326)[['geometry']]
                gdf_mapa_mancha.geometry = gdf_mapa_mancha.geometry.simplify(0.00005)
            else:
                gdf_mapa_mancha = gpd.GeoDataFrame()

            # Centralização do mapa baseada no Bounding Box
            bounds = gdf_mapa_fundo.total_bounds
            centro_y = (bounds[1] + bounds[3]) / 2
            centro_x = (bounds[0] + bounds[2]) / 2

            m = folium.Map(location=[centro_y, centro_x], tiles="CartoDB positron", control_scale=True)

            folium.GeoJson(
                gdf_mapa_fundo,
                style_function=lambda x: {'fillColor': 'transparent', 'color': '#475569', 'weight': 2,
                                          'dashArray': '5, 5'}
            ).add_to(m)

            if not gdf_mapa_mancha.empty:
                folium.GeoJson(
                    gdf_mapa_mancha,
                    style_function=lambda x: {'fillColor': '#ef4444', 'color': '#b91c1c', 'weight': 1,
                                              'fillOpacity': 0.5}
                ).add_to(m)

            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

            # returned_objects=[] evita re-renderizações desnecessárias ao clicar no mapa
            st_folium(m, width="100%", height=600, returned_objects=[])

        except Exception as e:
            st.error(f"Erro ao processar as geometrias: {e}")

else:
    st.info("👈 Utilize o menu lateral para enviar os polígonos e gerar o dashboard.")