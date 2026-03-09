"""
JWT 认证核心模块
基于 Auth0 的 JWT 验证
"""

import jwt
import requests
from functools import wraps
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization

from config.settings import (
    AUTH0_DOMAIN,
    AUTH0_CLIENT_ID,
    AUTH0_CLIENT_SECRET,
    AUTH0_API_AUDIENCE,
    AUTH0_ALGORITHM,
    AUTH0_JWKS_URL,
)


class JWTAuth:
    """Auth0 JWT 认证类"""
    
    def __init__(self):
        self.domain = AUTH0_DOMAIN
        self.client_id = AUTH0_CLIENT_ID
        self.client_secret = AUTH0_CLIENT_SECRET
        self.api_audience = AUTH0_API_AUDIENCE
        self.algorithm = AUTH0_ALGORITHM
        self.jwks_url = AUTH0_JWKS_URL
        self.issuer = f"https://{self.domain}/"
        self._jwks = None
    
    def get_jwks(self) -> Dict:
        """获取 JWKS 密钥集"""
        if self._jwks is None:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            self._jwks = response.json()
        return self._jwks
    
    def get_signing_key(self, token: str) -> str:
        """获取签名密钥"""
        jwks = self.get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing kid",
            )
        
        for key in jwks["keys"]:
            if key["kid"] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key",
        )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证 JWT Token"""
        try:
            # 获取签名密钥
            signing_key = self.get_signing_key(token)
            
            # 验证并解码 token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=[self.algorithm],
                audience=self.api_audience,
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid audience",
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid issuer",
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )
    
    def get_permissions(self, payload: Dict[str, Any]) -> list:
        """从 token 中提取权限"""
        # Auth0 权限可能在 'permissions' 或 'scope' 中
        permissions = payload.get("permissions", [])
        scope = payload.get("scope", "")
        
        # 将 scope 字符串转换为列表
        if scope and not permissions:
            permissions = scope.split()
        
        return permissions
    
    def has_permission(self, payload: Dict[str, Any], required_permission: str) -> bool:
        """检查用户是否有指定权限"""
        permissions = self.get_permissions(payload)
        return required_permission in permissions


# 创建全局实例
jwt_auth = JWTAuth()

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    获取当前认证用户
    用于需要认证的路由
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization credentials missing",
        )
    
    token = credentials.credentials
    payload = jwt_auth.verify_token(token)
    
    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "permissions": jwt_auth.get_permissions(payload),
        "payload": payload,
    }


async def require_auth(required_permission: Optional[str] = None):
    """
    认证装饰器
    :param required_permission: 可选的权限要求
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if required_permission:
            if not jwt_auth.has_permission(current_user["payload"], required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {required_permission}",
                )
        return current_user
    
    return permission_checker


def generate_test_token_hs256(
    user_id: str = "test_user",
    email: str = "test@example.com",
    permissions: Optional[list] = None,
    expires_in: int = 3600,
) -> str:
    """
    生成测试用 JWT Token（HS256 算法，仅用于开发环境）
    生产环境应使用 Auth0 获取 token (RS256)
    """
    if permissions is None:
        permissions = ["read:jobs", "write:jobs", "read:users", "write:users"]
    
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "email": email,
        "permissions": permissions,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "iss": f"https://{AUTH0_DOMAIN}/",
        "aud": AUTH0_API_AUDIENCE,
    }
    
    # 使用 HS256 进行测试（简单）
    token = jwt.encode(payload, "test-secret-key-for-development-only", algorithm="HS256")
    
    return token
