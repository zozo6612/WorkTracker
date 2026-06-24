import json
import os
import anthropic


def _get_client():
    """API 키를 읽어서 Anthropic 클라이언트 반환"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    # .streamlit/secrets.toml 에서 읽기 시도
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            pass

    if not api_key:
        return None

    return anthropic.Anthropic(api_key=api_key)


def extract_keywords(text: str) -> list:
    """이력 텍스트 → 핵심 키워드 5개 이내 추출"""
    client = _get_client()
    if not client:
        import streamlit as st
        st.warning("API 키가 설정되지 않았어요. .streamlit/secrets.toml을 확인해주세요.")
        return []
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""다음 업무 이력에서 핵심 키워드를 5개 이내로 추출해줘.
반드시 JSON 배열 형식으로만 응답해. 설명이나 다른 텍스트 없이 배열만.
예시: ["프로젝트A", "일정변경", "클라이언트요청"]

이력 내용:
{text}"""
            }]
        )
        raw = message.content[0].text.strip()
        return json.loads(raw)
    except Exception as e:
        import streamlit as st
        st.warning(f"키워드 추출 중 오류: {e}")
        return []


def generate_weekly_report(work_list: list, week_label: str) -> str:
    """업무 목록 → 자연어 주간 보고서 생성"""
    client = _get_client()
    if not client:
        return "API 키가 설정되지 않아 보고서를 생성할 수 없어요."
    try:
        sections = {"done": [], "ing": [], "issue": [], "plan": []}
        for w in work_list:
            desc = f" ({w['description']})" if w.get("description") else ""
            sections[w["status"]].append(w["title"] + desc)

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""아래 업무 데이터를 바탕으로 {week_label} 주간 업무 보고서를 격식체로 작성해줘.
각 섹션 제목은 유지하고 자연스러운 보고서 문체로 다듬어줘.

완료한 업무: {sections['done']}
진행중인 업무: {sections['ing']}
이슈/리스크: {sections['issue']}
다음주 계획: {sections['plan']}"""
            }]
        )
        return message.content[0].text
    except Exception as e:
        return f"보고서 생성 중 오류: {e}"
        