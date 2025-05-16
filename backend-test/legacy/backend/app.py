from flask import Flask
from backend.api.paper_api import paper_bp

def create_app():
    app = Flask(__name__)
    
    # 注册蓝图
    app.register_blueprint(paper_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)