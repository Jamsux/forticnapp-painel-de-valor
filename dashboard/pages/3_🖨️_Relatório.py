import streamlit as st
import streamlit.components.v1 as components
from common import sidebar_refresh_control, sidebar_period_selector, get_data, has_data
from src import report

st.set_page_config(page_title="Relatório — FortiCNAPP", page_icon="🖨️", layout="wide")
sidebar_refresh_control()

st.markdown(report.REPORT_CSS, unsafe_allow_html=True)
# st.container(key=...) expõe uma classe CSS estável (.st-key-<key>) no wrapper do
# container — é o único jeito confiável de esconder widgets nativos do Streamlit
# (que não podem ser "envolvidos" por um <div> aberto/fechado em chamadas separadas
# de st.markdown) na hora de imprimir.
with st.container(key="report_controls"):
    st.title("🖨️ Relatório")
    st.caption(
        "Monta um relatório único, pronto para impressão ou para salvar como PDF "
        "(use o botão abaixo ou Ctrl+P / Cmd+P)."
    )

    if not has_data():
        st.warning("Nenhum dado coletado ainda. Use **Atualizar dados** na barra lateral.")
        st.stop()

    period = sidebar_period_selector()
    st.caption(f"Período aplicado aos indicadores de alertas: **{period['label']}** "
               "(ajuste na barra lateral).")

    col1, col2, col3 = st.columns([2, 1, 1])
    client_name = col1.text_input(
        "Nome do cliente/conta (aparece no cabeçalho do relatório)",
        placeholder="Ex.: Postura de Segurança — [Nome do Cliente]",
    )
    include_ops = col2.checkbox("Incluir anexo operacional", value=True,
                                 help="Adiciona tabelas de alertas críticos/altos em aberto e top hosts vulneráveis.")
    include_glossary = col3.checkbox("Incluir glossário", value=True,
                                      help="Adiciona ao final a definição de cada indicador — as mesmas "
                                           "explicações dos tooltips, que não aparecem na versão impressa.")

    # st.markdown(unsafe_allow_html=True) faz o Streamlit converter o HTML em elementos
    # React (via rehype-raw), o que quebra atributos de evento inline como onclick=
    # (a string acaba virando o valor da prop onClick, e o React rejeita — "Minified
    # React error #231"). components.v1.html roda em um <iframe> à parte com HTML/JS
    # de verdade, então o listener funciona; window.parent.print() imprime a página
    # inteira do Streamlit (o iframe é same-origin via srcdoc).
    components.html(
        """
        <button id="print-btn" style="background:#2563EB;color:white;border:none;
            border-radius:6px;padding:10px 18px;font-size:14px;font-weight:600;
            cursor:pointer;font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;">
            🖨️ Imprimir / Salvar como PDF
        </button>
        <script>
          document.getElementById('print-btn').addEventListener('click', function () {
            window.parent.print();
          });
        </script>
        """,
        height=50,
    )

# ---------------------------------------------------------------- Dados ----
# A montagem do relatório vive em src/report.build_report_html para poder ser
# gerada e validada fora do Streamlit (ver scripts/export_report.py).
report_html = report.build_report_html(
    get_data(),
    client_name=client_name,
    include_ops=include_ops,
    include_glossary=include_glossary,
    period_start=period["start"],
    period_end=period["end"],
)
st.markdown(report_html, unsafe_allow_html=True)
