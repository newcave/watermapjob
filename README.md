# 🌊 미래 물 직업 지도 (watermapjob)

학생과 시민을 위한 물 분야 진로 안내 Streamlit 앱 (습작 v0.1, 2026-10-28).
전 세계 물 연구 논문(OpenAlex)과 국내 학회지(KCI) 집계로 **지금 뜨는 물 기술 10**을 고르고,
그 기술을 하는 직업, 공부하면 좋은 전공, K-water 연구소, 그리고 **물을 공부할 수 있는 대학**을 지도로 보여 줍니다.

K-water연구원 AI연구소 · 물벗 R&D 에이전트(`newcave/water-tech-agent`)의 공개 집계 숫자를 씁니다.

## 화면 구성

| 순서 | 내용 | 그림 |
|---|---|---|
| 1 | 머리 — 'AI로 물 관리' 논문 11.2배 | 해도 등심선 바탕 |
| 2 | 1분 테스트 — 과목·하고 싶은 일·관심 문제 → 잘 맞는 기술 2개 | 결과 카드 |
| 3 | **직업 흐름 지도** — 전공 → 물 기술 → K-water 연구소 | Sankey (테스트 결과 주황 강조) |
| 4 | 지금 뜨는 물 기술 10 — 직업·전공·연구소·근거 | 카드 + 선 그림 |
| 5 | 얼마나 빨리 크고 있나 — 2022→2025 배율 | 가로 막대 + 전체 논문 기준선 |
| 6 | 국내 KCI 두 단어 표현 | 칩 |
| 7 | **대학 지도** — 물 관련 학부 학과가 있는 대학 45곳(캠퍼스 53) | 한반도 지도 + 서울 확대 지도, 점 누르면 학과 |
| 8 | 묶음별 대학 목록 (순위 없음, 묶음 안 가나다순) | 학과 칩 → 학교 누리집 |
| 9 | 방법과 출처 | |

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud에 올리기

1. https://share.streamlit.io → **Create app** → *Deploy a public app from GitHub*
2. Repository `newcave/watermapjob`, Branch `main`, Main file path `app.py`
3. App URL을 정하고 **Deploy** — 비밀값(Secrets)은 필요 없습니다.

main에 올라간 변경은 자동으로 다시 배포됩니다.

## 숫자·학교 고치기

화면 코드는 그대로 두고 `data/` 아래 JSON만 고치면 됩니다.

| 파일 | 내용 |
|---|---|
| `data/tech.json` | 기술 10 (직업·전공·연구소·논문 수 a=2022, b=2025), 1분 테스트 문항, 기준선 |
| `data/kci.json` | 국내 두 단어 표현 (배율·최근 3년 편수) — 집계만 |
| `data/univ.json` | 대학·캠퍼스·학과(이름, 누리집 주소)·묶음·대략 위치(lat/lon), K-water연구원 위치 |
| `data/icons.json` | 기술 카드의 64×64 선 그림 |
| `data/korea_outline.json` | 한반도·주변 해안선 (Natural Earth) |

학교를 더할 때는 `univs`에 한 항목을 넣습니다: `tier`(seoul_sci · capital · flagship · regional), `univ`, `campus`, `region`, `depts`, `lat`, `lon`.

## 출처와 이용 조건

- **OpenAlex** — 논문 수 집계 (CC0)
- **KCI(한국학술지인용색인) 데이터 활용** — 국문 제목·초록의 집계만 싣고 원문은 싣지 않습니다
- **대학·학과** — 각 대학 공식 누리집과 2026~2027학년도 모집요강(2026년 10월 확인). 지도의 점은 캠퍼스의 대략 위치
- **해안선** — Natural Earth 4.1.0 (퍼블릭 도메인), `world-atlas@2.0.2` 배포본에서 추출
- 대학 묶음은 입시에서 흔히 쓰는 대략적 구분이며 순위가 아닙니다

## 운영 원칙

- 공개 저장소에는 **집계 숫자만** 둡니다. KCI 원문, 비공개 저장소(`openalex-data` 등)의 원본·논문 목록은 옮기지 않습니다.
- API 키 등 비밀값은 코드·문서·커밋에 쓰지 않습니다 (필요해지면 Streamlit Secrets).
