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
        
def generate_ai_todo(work_list: list, history_list: list, week_label: str) -> list:
    import re
    import json

    client = _get_client()

    # 크레딧 없을 때 샘플 데이터로 테스트
    if not client:
        return _sample_todos()

    try:
        work_summary = "\n".join([
            f"- [{w['status']}] {w['title']} "
            f"({w['start_date']}~{w['end_date']}, "
            f"진행률:{w.get('progress', 0)}%) : {w.get('description', '')}"
            for w in work_list
        ])

        history_summary = "\n".join([
            f"- [{h['date']}][{h['type']}] {h.get('title', '')} : {h['content'][:100]}"
            for h in history_list[:20]
        ])

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"""당신은 업무 관리 AI 어시스턴트입니다.
아래 업무 현황과 업무 이력을 분석해서 다음 주에 반드시 처리해야 할 Todo를 추천해주세요.

[{week_label} 업무 현황]
{work_summary}

[최근 업무 이력]
{history_summary}

위 데이터를 분석해서 다음 주 우선순위 Todo를 5개 이내로 추천해주세요.
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON 배열만 출력하세요.

[
  {{
    "priority": "긴급",
    "title": "할 일 제목",
    "reason": "이 일을 해야 하는 구체적인 이유 (업무 데이터나 이력에서 근거 언급)",
    "tags": ["관련태그1", "관련태그2"]
  }}
]

priority는 반드시 "긴급", "중요", "일반" 중 하나로만 작성하세요.
긴급: 마감이 임박하거나 이슈가 있는 것
중요: 진행 중이고 속도가 필요한 것
일반: 사전 준비나 여유 있는 것"""
            }]
        )

        raw = message.content[0].text.strip()
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return _sample_todos()

    except Exception as e:
        import streamlit as st
        st.warning(f"AI Todo 생성 중 오류: {e}")
        # 오류 시 샘플 데이터 반환
        return _sample_todos()


def _sample_todos() -> list:
    """크레딧 없을 때 보여줄 샘플 Todo"""
    return [
        {
            "priority": "긴급",
            "title": "⚠️ API 크레딧 충전 필요",
            "reason": "현재 Anthropic API 크레딧이 부족해서 실제 AI 분석이 불가능해요. "
                      "console.anthropic.com → Billing → Add credit에서 충전 후 다시 시도해주세요.",
            "tags": ["크레딧충전필요"]
        },
        {
            "priority": "중요",
            "title": "이슈/리스크 업무 조치",
            "reason": "My Work에 등록된 이슈/리스크 상태 업무를 우선 처리해주세요.",
            "tags": ["이슈처리"]
        },
        {
            "priority": "중요",
            "title": "진행중 업무 진행률 업데이트",
            "reason": "My Work에서 진행중인 업무의 진행률을 최신 상태로 업데이트해주세요.",
            "tags": ["진행률업데이트"]
        },
        {
            "priority": "일반",
            "title": "다음주 계획 업무 착수 준비",
            "reason": "다음주 계획으로 등록된 업무의 사전 준비를 시작해주세요.",
            "tags": ["사전준비"]
        }
    ]