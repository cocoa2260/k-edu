# Fine-tuning U01~U04 / L7 준비 결과

**강의 네 단원과 실제 Dataset·Tokenizer·label 준비를 완료했다. 자료는 70개 중 40개 작성이며, L7의 실제 훈련은 아직 시작하지 않았다.**

[강의](../../lessons/fine-tuning/lesson.md) → [데이터·입력 검토](REVIEW.md) 순서로 보면 된다. 실행은 [L7 안내](../../practice/document-assistant/L7.md)를 사용한다. 사람이 JSON 전체를 읽을 필요는 없다.

| 항목 | 관찰 |
|---|---|
| 원본 | 가상 원문 8가족·40개 예제 |
| 증강 | 고정 바꿔쓰기 후보 12개 중 8개 채택·4개 기각 |
| 실제 준비 | Train 28 / Validation 10 / Test 10 |
| 실제 라이브러리 | Datasets 4.4.1 로드·Features·filter/map·Arrow 저장/재로드 |
| 실제 Tokenizer | Qwen3-0.6B 고정 리비전, Template/정답~EOS/Padding label 확인 |
| 경계·회귀 | 기존 243개+신규 28개, 총 271개 테스트 통과 |
| 모델 훈련/생성 | Optimizer Step 0회·가중치 로드 0회·로컬 생성 0회·유료 API 0회 |

자료·교사 정답 초안은 같은 Work의 AI가 작성·검토했다. 실제 강사/교육생의 독립 검수는 없다. 그룹 분리·해시·정확한 중복 검사는 의미적 누수나 정답성을 완전히 증명하지 않는다. 기존 회귀 18개와 새 Test도 공개된 자료이며 블라인드 평가가 아니다. 합성 모델 API를 호출한 증강 파이프라인은 실행하지 않았다.

최소/최대 길이는 233/382 Token이고 상한은 512다. 가짜 Logit의 Gradient는 마스크 정렬 확인용이며 Qwen의 훈련/검증 Loss가 아니다. 이번 출력이 만들어졌다고 성능 향상을 주장하지 않는다.

별도 설치 계층에서 L5 고정 패키지를 읽기 전용으로 재사용하고 Datasets 의존성을 추가했다. 실제 버전·동결 스냅샷과 pip check 통과를 남겼다. 새 학생 환경의 전체 설치를 처음부터 재실행한 검증은 아니고 다른 OS·교육장 장비/동시 실행도 미검증이다.

로컬 JSON의 사용 통계 요청 시도를 발견한 뒤 명시적 오프라인 설정과 requests/httpx 가드로 재실행해 시도 0회·데이터/Token 동일성을 확인했다. 기본 local_files_only만으로 모든 라이브러리의 네트워크 동작이 차단된다고 가정하지 않는다. 모델·Tokenizer 캐시와 Arrow 바이너리는 Git에 넣지 않았다.

다음은 K2-12.U05~U08: 실제 LoRA Parameter·Optimizer Step·평가·Adapter 저장/새 프로세스 Reload, QLoRA 자원 호환 여부다. **추천 추론 강도는 High.** 학습 대상·Gradient·저장/재로드와 메모리/평가를 연결해 확인해야 한다. L4/L5/L6 답변 품질·나머지 기초/안내·OCR/통합·독립 수업 검증도 미완료로 유지한다.

<details>
<summary>선택해서 읽을 기술 기록</summary>

| 파일 | 역할 |
|---|---|
| [observed.json](observed.json) | 실제 Datasets 처리·수량·버전·해시·길이·증강 결정 |
| [token-example.json](token-example.json) | 실제 한 예제의 렌더링·Token·label |
| [batch-example.json](batch-example.json) | EOS와 Padding의 실제 배치 구분 |
| [offline-check.json](offline-check.json) | 초기 요청 시도 원인·명시적 오프라인 재실행 |
| [tests.json](tests.json) | 검사 명령·출력·의존성 검사 |
| [source-check.json](source-check.json) | 공식 문서 조회 범위·실제 설치 API와 구분 |
| [validation.json](validation.json) | 검증·한계·미실행 |
| [run.json](run.json) | 게시·재개 상태 |

</details>
