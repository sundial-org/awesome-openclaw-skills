#!/usr/bin/env python3
"""
测试飞书认证配置
"""

import sys
import json
import requests

def test_auth(app_id, app_secret):
    """测试获取租户访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") == 0:
            print("✅ 认证成功！")
            print(f"租户访问令牌: {data['tenant_access_token'][:20]}...")
            print(f"过期时间: {data['expire']} 秒")
            return True
        else:
            print(f"❌ 认证失败: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_auth.py <app_id> <app_secret>")
        sys.exit(1)
    
    app_id = sys.argv[1]
    app_secret = sys.argv[2]
    
    success = test_auth(app_id, app_secret)
    sys.exit(0 if success else 1)