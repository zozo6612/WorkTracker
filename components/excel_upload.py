import streamlit as st


def render_excel_upload(
    *,
    caption,
    uploader_key,
    state_prefix,
    parse_fn,
    preview_rows_fn,
    save_fn,
    save_button_label="💾 Excel 데이터 저장",
):
    """Excel 업로드 → 미리보기 → 저장 UI (History / My Work 공통)."""
    preview_key = f"{state_prefix}_preview"
    errors_key = f"{state_prefix}_errors"
    file_key_key = f"{state_prefix}_file_key"

    st.caption(caption)
    uploaded = st.file_uploader(
        "Excel 파일 선택",
        type=["xlsx"],
        key=uploader_key,
        label_visibility="collapsed",
    )

    if uploaded is None:
        st.session_state.pop(preview_key, None)
        st.session_state.pop(errors_key, None)
        st.session_state.pop(file_key_key, None)
    else:
        file_key = f"{uploaded.name}_{uploaded.size}"
        if st.session_state.get(file_key_key) != file_key:
            records, errors = parse_fn(uploaded.getvalue())
            st.session_state[file_key_key] = file_key
            st.session_state[preview_key] = records
            st.session_state[errors_key] = errors

    preview = st.session_state.get(preview_key, [])
    errors = st.session_state.get(errors_key, [])

    for err in errors:
        row = err.get("row")
        msg = err.get("message", "")
        if row:
            st.warning(f"{row}행: {msg}")
        else:
            st.error(msg)

    if preview:
        st.markdown(f"**업로드 미리보기** ({len(preview)}건)")
        st.dataframe(
            [preview_rows_fn(r) for r in preview],
            use_container_width=True,
            hide_index=True,
        )
        if st.button(save_button_label, type="primary", use_container_width=True, key=f"{state_prefix}_save"):
            saved = save_fn(preview)
            if saved:
                st.session_state.pop(preview_key, None)
                st.session_state.pop(errors_key, None)
                st.session_state.pop(file_key_key, None)
                st.success(f"{saved}건 저장됐어요!")
                st.rerun()
            else:
                st.error("저장에 실패했어요. 다시 시도해주세요.")
