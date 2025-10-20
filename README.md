# EMS-copilot MLOps
- EMS-copilot의 ML 모델의 개발과 배포를 위한 커스텀 컨테이너
- Vertex AI 로 학습된 모델 배포
- 추론에 대한 preprocess, postprocess를 위한 래퍼

## 기술 스택
- Google Cloud
    - Cloud Storage
    - Vertex AI
        - Custom Predictor Routine
- Docker
- Python