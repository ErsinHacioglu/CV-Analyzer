import streamlit as st

from cv_analyzer.auth import AnalysisRepository
from cv_analyzer.models import AnalysisResult
from cv_analyzer.ui.session import get_current_user


def save_analysis_if_logged_in(result: AnalysisResult, filename: str = "unknown") -> None:
    user = get_current_user()
    if not user:
        return
    try:
        AnalysisRepository().save(user["id"], result, filename=filename)
        st.caption("Kaydedildi.")
    except Exception as exc:
        st.warning(f"Kayıt olmadı: {exc}")


def render_analysis_result(result: AnalysisResult) -> None:
    m1, m2, m3 = st.columns(3)
    m1.metric("Kategori", result.category)
    m2.metric("Güven", f"{result.category_confidence:.0%}")
    m3.metric("Skor", f"{result.match_score:.0f}/100")

    st.progress(result.match_score / 100)

    pii_finding = getattr(result, "pii_finding", None)
    masked_preview = getattr(result, "masked_text_preview", "")
    file_deleted = getattr(result, "file_deleted", False)

    with st.expander("Güvenlik", expanded=bool(pii_finding and pii_finding.has_pii)):
        if pii_finding and pii_finding.has_pii:
            st.warning(f"{pii_finding.total_count} alan maskelendi ({pii_finding.summary_tr()}).")
        if file_deleted:
            st.success("Dosya silindi.")
        if masked_preview:
            st.text(masked_preview)

    st.markdown("**Yetenekler**")
    if result.resume.skills:
        st.info(", ".join(f"{s.name} ({s.level.value})" for s in result.resume.skills))
    else:
        st.warning("Yetenek bulunamadı.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Eşleşen**")
        st.write(", ".join(result.found_skills) or "-")
    with c2:
        st.markdown("**Eksik**")
        st.write(", ".join(result.missing_skills) or "-")

    st.markdown("**Öneriler**")
    for rec in result.recommendations:
        st.markdown(f"- {rec}")
