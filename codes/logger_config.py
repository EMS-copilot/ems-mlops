import logging
import sys

def setup_logging():
    # 루트 로거 설정
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)])

    # 특정 모듈의 로깅 레벨을 조정할 수 있습니다.
    # 예: 'uvicorn' 로거의 레벨을 INFO로 설정
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

# 모듈이 임포트될 때 로깅 설정이 바로 적용되도록 호출
setup_logging()