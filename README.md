WebGIS criado para análise em área de risco sujeito a inundação 


<img width="2412" height="1133" alt="Opera Instantâneo_2026-05-18_170150_localhost" src="https://github.com/user-attachments/assets/fd38a7a5-8829-4c10-bb39-fb90e1fdec50" />


# 🚨 WebGIS - Análise de Risco de Inundação

Uma plataforma WebGIS minimalista e de alta performance desenvolvida em Python para a análise geoespacial de riscos hidrológicos em áreas urbanas ou perímetros de estudo. Projetada com foco na experiência do usuário (UX) inspirada em dashboards financeiros e plataformas SaaS.

---

## 💻 Sobre a Ferramenta

Este sistema permite que profissionais das áreas de engenharia, topografia, planejamento urbano e REURB realizem o cruzamento dinâmico entre perímetros urbanos/lotes e manchas de inundação. 

A aplicação processa geometrias complexas em tempo real, corrige inconsistências topográficas automaticamente e apresenta os resultados consolidados em um painel gerencial interativo acompanhado por um mapa dinâmico.

### 🚀 Principais Funcionalidades

*   **Upload Dinâmico de Vetores:** Suporte nativo para os formatos `Shapefile (.zip)`, `GeoJSON`, `KML` e `GeoParquet (.parquet)`.
*   **Processamento Otimizado (Clip):** Substituição de operações pesadas de overlay por recortes baseados em malhas espaciais indexadas, garantindo respostas rápidas mesmo com grandes volumes de dados.
*   **Conversão de Unidades Dinâmica:** Exibição dos resultados em metros quadrados, hectares ou quilômetros quadrados.
*   **Design Minimalista & Responsivo:** Interface limpa utilizando componentes modernos de Cards (Containers) e mapa base *CartoDB Positron* em tons de cinza para destacar os dados de risco em vermelho.

---

## 🛠️ Tecnologias Utilizadas

*   **[Streamlit](https://streamlit.io/):** Framework para estruturação da interface web e reatividade.
*   **[GeoPandas](https://geopandas.org/):** Motor de processamento vetorial e álgebra espacial.
*   **[Folium](https://python-visualization.github.io/folium/) & [Streamlit-Folium](https://github.com/randyzwitch/streamlit-folium):** Renderização e otimização do mapa interativo baseado em Leaflet.
*   **[Pyogrio](https://github.com/geopandas/pyogrio):** Driver de alta performance para leitura e escrita de dados espaciais.

---

## 📦 Como Executar o Projeto Localmente

Se quiser rodar este projeto na sua máquina, siga os passos abaixo:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)
   cd NOME-DO-REPOSITORIO


Esse projeto só foi possível graças ao curso "Formação WebGIS 2W" e também o GEMINI para organizar  o script e tirar dúvidas. 
