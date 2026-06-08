import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cv_analyzer.auth import AnalysisRepository
from cv_analyzer.db import init_database
from cv_analyzer.ui import get_current_user, init_session_state, render_auth_sidebar

st.set_page_config(page_title="Geçmiş Analizler", layout="wide")

init_session_state()
render_auth_sidebar()

try:
    init_database()
except Exception as exc:
    st.error(f"Veritabanına bağlanılamadı: {exc}")
    st.stop()

user = get_current_user()
st.title("Geçmiş Analizler")

if not user:
    st.warning("Giriş yapmanız lazım.")
    st.stop()

repo = AnalysisRepository()
history = repo.list_by_user(user["id"])

if not history:
    st.info("Kayıtlı analiz yok.")
    st.stop()

if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False

st.caption(f"{len(history)} analiz")

label_map = {}
for item in history:
    created = item["created_at"].strftime("%d.%m.%Y %H:%M") if item["created_at"] else "-"
    label_map[f"{item['category']} | {item['match_score']:.0f}/100 | {created}"] = item["id"]

toolbar_left, toolbar_right = st.columns([2, 1])

with toolbar_left:
    selected_labels = st.multiselect("Toplu silmek için seçin", list(label_map.keys()))

with toolbar_right:
    st.write("")
    if st.button("Seçilenleri sil", use_container_width=True, disabled=not selected_labels):
        ids = [label_map[label] for label in selected_labels]
        repo.delete_many(user["id"], ids)
        st.rerun()

    if not st.session_state.confirm_delete_all:
        if st.button("Tümünü sil", use_container_width=True):
            st.session_state.confirm_delete_all = True
            st.rerun()
    else:
        st.warning("Tüm analizler silinecek.")
        c1, c2 = st.columns(2)
        if c1.button("Evet", use_container_width=True):
            repo.delete_all_by_user(user["id"])
            st.session_state.confirm_delete_all = False
            st.rerun()
        if c2.button("İptal", use_container_width=True):
            st.session_state.confirm_delete_all = False
            st.rerun()

st.divider()

for item in history:
    created = item["created_at"].strftime("%d.%m.%Y %H:%M") if item["created_at"] else "-"
    label = f"{item['category']} | {item['match_score']:.0f}/100 | {created}"
    with st.expander(label):
        c1, c2, c3 = st.columns(3)
        c1.metric("Dosya", item["filename"])
        c2.metric("Güven", f"{item['category_confidence']:.0%}")
        c3.metric("Maskelenen", item["pii_count"])

        st.markdown(f"Eşleşen: {', '.join(item['found_skills']) or '-'}")
        st.markdown(f"Eksik: {', '.join(item['missing_skills']) or '-'}")

        if item["recommendations"]:
            for rec in item["recommendations"]:
                st.markdown(f"- {rec}")

        if item["masked_preview"]:
            st.text(item["masked_preview"])

        if st.button("Bu analizi sil", key=f"delete_{item['id']}"):
            if repo.delete_by_id(user["id"], item["id"]):
                st.rerun()
            else:
                st.error("Silinemedi.")
