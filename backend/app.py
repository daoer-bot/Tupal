"""
Flask主应用
提供RESTful API和SSE实时推送
"""
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

from config import config

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册静态文件路由
    register_static_routes(app)
    
    return app


def register_blueprints(app):
    """注册所有蓝图"""
    from api import (
        outline_bp,
        image_bp,
        history_bp,
        trending_bp,
        upload_bp,
        material_bp,
        template_bp
    )

    # 注册所有功能域蓝图
    app.register_blueprint(outline_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(image_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(history_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(trending_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(upload_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(material_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(template_bp, url_prefix=app.config['API_PREFIX'])


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal error: {error}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad request'
        }), 400
    
    # 注册根路由
    @app.route('/')
    def index():
        """健康检查端点"""
        return jsonify({
            'success': True,
            'message': '图宝 API is running',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'service': 'tupal-api'
        })


def register_static_routes(app):
    """注册静态文件路由"""
    
    # 确保 uploads 目录存在
    uploads_dir = Path('uploads')
    if not uploads_dir.exists():
        uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建子目录
    for subdir in ['references', 'generated', 'temp']:
        subdir_path = uploads_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True, exist_ok=True)
    
    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        """
        提供上传文件的静态访问
        
        支持访问 uploads 目录下的所有文件，包括：
        - /uploads/references/xxx.png - 参考图片
        - /uploads/generated/xxx.png - 生成的图片
        - /uploads/temp/xxx.png - 临时文件
        """
        return send_from_directory('uploads', filename)


if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    port = int(os.getenv('PORT', 5030))
    logger.info(f'Starting Flask app on port {port}')
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )