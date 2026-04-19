import os
import sys

# 將 backend 目錄加入環境路徑
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_path)

# Vercel 要求的 handler
from app.main import app
