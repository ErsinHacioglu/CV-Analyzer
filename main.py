import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from cv_analyzer.db import init_database
from cv_analyzer.security import PIISanitizer, SecureFileHandler
from cv_analyzer.services.pipeline import CVAnalyzerPipeline
from cv_analyzer.ui import (
    init_session_state,
    render_analysis_result,
    render_auth_sidebar,
    save_analysis_if_logged_in,
)


def _apply_security_fields(result, file_uploaded: bool = False) -> None:
    if not getattr(result, "pii_finding", None):
        finding, preview = PIISanitizer().analyze(result.resume.raw_text)
        result.pii_finding = finding
        result.masked_text_preview = preview
    if file_uploaded:
        result.file_deleted = True


st.set_page_config(page_title="CV Analyzer", layout="wide")

init_session_state()
render_auth_sidebar()

st.title("CV Analyzer")
st.caption("SEN 4015 Dönem Projesi")

try:
    init_database()
except Exception as exc:
    st.error(f"Veritabanına bağlanılamadı: {exc}")
    st.stop()

pipeline = CVAnalyzerPipeline()
secure_handler = SecureFileHandler()

if not pipeline.classifier.is_trained:
    st.error("Model bulunamadı. Önce train_classifier.py çalıştırın.")
    st.stop()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("CV Girişi")
    input_mode = st.radio("Giriş", ["Dosya", "Metin"], horizontal=True)

    target_category = st.selectbox(
        "Hedef pozisyon",
        ["Otomatik"] + pipeline.classifier.categories,
    )
    category_override = None if target_category == "Otomatik" else target_category

    if input_mode == "Dosya":
        uploaded = st.file_uploader("PDF veya TXT", type=["pdf", "txt"])
        analyze_btn = st.button("Analiz Et", type="primary", use_container_width=True)
        text_input = None
    else:
        uploaded = None
        text_input = st.text_area("CV metni", height=300)
        analyze_btn = st.button("Analiz Et", type="primary", use_container_width=True)

    st.caption("Dosyalar analiz bitince silinir.")

with col2:
    st.subheader("Sonuçlar")

    if analyze_btn:
        try:
            filename = "pasted_cv.txt"
            if input_mode == "Dosya":
                if uploaded is None:
                    st.warning("Dosya seçin.")
                    st.stop()
                filename = uploaded.name
                with secure_handler.temporary_cv_file(uploaded.name, uploaded.getvalue()) as temp_path:
                    result = pipeline.analyze_file(str(temp_path), category_override)
                    _apply_security_fields(result, file_uploaded=True)
            else:
                if not text_input or not text_input.strip():
                    st.warning("Metin girin.")
                    st.stop()
                result = pipeline.analyze_text(text_input.strip(), target_category=category_override)
                _apply_security_fields(result)

            st.success("Bitti.")
            render_analysis_result(result)
            save_analysis_if_logged_in(result, filename=filename)

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Hata: {e}")
    else:
        st.info("CV yükleyip analiz edin.")
