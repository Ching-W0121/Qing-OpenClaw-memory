"""
测试 JWT 认证 - 阶段 5
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth.jwt_auth import JWTAuth, jwt_auth, generate_test_token_hs256
from config.settings import AUTH0_DOMAIN, AUTH0_API_AUDIENCE


class TestJWTAuth:
    """JWT 认证测试"""
    
    def test_jwt_auth_init(self):
        """测试 JWTAuth 初始化"""
        auth = JWTAuth()
        
        assert auth.domain == AUTH0_DOMAIN
        assert auth.api_audience == AUTH0_API_AUDIENCE
        assert auth.algorithm == "RS256"
        print("[OK] JWTAuth 初始化成功")
    
    def test_jwks_url(self):
        """测试 JWKS URL 生成"""
        auth = JWTAuth()
        expected_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        
        assert auth.jwks_url == expected_url
        print(f"[OK] JWKS URL: {auth.jwks_url}")
    
    def test_get_permissions_from_payload(self):
        """测试从 payload 提取权限"""
        auth = JWTAuth()
        
        # 测试 permissions 字段
        payload1 = {
            "sub": "user123",
            "permissions": ["read:jobs", "write:jobs"],
        }
        perms1 = auth.get_permissions(payload1)
        assert "read:jobs" in perms1
        assert "write:jobs" in perms1
        print("[OK] 从 permissions 字段提取权限成功")
        
        # 测试 scope 字段
        payload2 = {
            "sub": "user123",
            "scope": "read:jobs write:jobs read:users",
        }
        perms2 = auth.get_permissions(payload2)
        assert "read:jobs" in perms2
        assert "write:jobs" in perms2
        assert "read:users" in perms2
        print("[OK] 从 scope 字段提取权限成功")
    
    def test_has_permission(self):
        """测试权限检查"""
        auth = JWTAuth()
        
        payload = {
            "sub": "user123",
            "permissions": ["read:jobs", "write:jobs"],
        }
        
        assert auth.has_permission(payload, "read:jobs") == True
        assert auth.has_permission(payload, "write:jobs") == True
        assert auth.has_permission(payload, "read:users") == False
        print("[OK] 权限检查成功")


class TestTestToken:
    """测试 Token 生成（仅开发环境）"""
    
    def test_generate_test_token_hs256(self):
        """测试生成测试 token (HS256)"""
        token = generate_test_token_hs256(
            user_id="test_user_001",
            email="test@example.com",
            permissions=["read:jobs", "write:jobs"],
            expires_in=3600,
        )
        
        assert token is not None
        assert len(token) > 0
        print(f"[OK] 测试 Token 生成成功：{token[:50]}...")
        
        # 注意：这是自签名 token，不能用 JWTAuth 验证
        # 因为 JWTAuth 需要 Auth0 的 JWKS 公钥
        print("[INFO] 注意：测试 token 是自签名的，仅用于开发环境")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("JWT 认证测试 - 阶段 5")
    print("=" * 60)
    
    test_auth = TestJWTAuth()
    test_token = TestTestToken()
    
    # 运行测试
    try:
        test_auth.test_jwt_auth_init()
        test_auth.test_jwks_url()
        test_auth.test_get_permissions_from_payload()
        test_auth.test_has_permission()
        test_token.test_generate_test_token_hs256()
        
        print("\n" + "=" * 60)
        print("[PASS] 所有 JWT 认证测试通过！")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败：{e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] 测试错误：{e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
