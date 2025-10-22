import os
from flask import Flask, request, abort, jsonify
from predictor import CustomPredictor 

MODEL_DIR = os.environ.get("AIP_MODEL_DIR", ".") 

predictor = None 

def create_app():
    """Flask 애플리케이션 팩토리"""
    global predictor
    app = Flask(__name__)
    
    if predictor is None:
        try:
            predictor = CustomPredictor(MODEL_DIR)
            predictor.load(MODEL_DIR)
        except Exception as e:
            print(f"Error initializing predictor: {e}")
            # 서버 시작 실패 시 오류 반환
            abort(500, description="Model Initialization Failed")

    @app.route("/ping", methods=["GET"])
    def ping():
        """헬스 체크 (컨테이너가 정상 작동 중인지 확인)"""
        return jsonify({"status": "ready"}), 200

    @app.route("/predict", methods=["POST"])
    def predict():
        """추론 엔드포인트"""
        if not request.json or 'instances' not in request.json:
            abort(400, description="Invalid request format")

        try:
            instances = request.json['instances']
            predictions = predictor.predict(instances)
            return jsonify({"predictions": predictions})

        except Exception as e:
            print(f"Prediction execution failed: {e}")
            return jsonify({"error": str(e)}), 500

    return app

if __name__ == "__main__":
    # 로컬 테스트용
    app = create_app()
    app.run(host="0.0.0.0", port=8080)
else:
    # Gunicorn 배포용
    gunicorn_app = create_app()