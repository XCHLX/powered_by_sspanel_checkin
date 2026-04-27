import os
import json
import base64
import requests
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from urllib.parse import urlparse


class SecureGistManager:
    """
    集成了 AES-256 加解密功能的 GitHub Gist 管理器
    """

    def __init__(self, gist_id: str, github_token: str, raw_key: str):
        # 1. 初始化 GitHub 配置
        self.gist_id = gist_id
        self.base_url = f"https://api.github.com/gists/{gist_id}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 2. 初始化加密密钥 (SHA-256 生成 32 字节 Key)
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(raw_key.encode())
        self.key = digest.finalize()

    # --- 内部加解密逻辑 ---
    def _encrypt(self, text: str) -> str:
        iv = os.urandom(16)
        cipher = Cipher(
            algorithms.AES(self.key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(text.encode()) + padder.finalize()

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + encrypted_data).decode("utf-8")

    def _decrypt(self, encrypted_text: str) -> str:
        raw_data = base64.b64decode(encrypted_text)
        iv = raw_data[:16]
        ciphertext = raw_data[16:]

        cipher = Cipher(
            algorithms.AES(self.key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data.decode("utf-8")

    # --- 外部操作接口 ---
    def get_secure_content(self, file_name: str) -> str:
        """从 Gist 获取加密内容并解密"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                gist_data = response.json()
                encrypted_content = (
                    gist_data.get("files", {}).get(file_name, {}).get("content")
                )

                if encrypted_content:
                    return self._decrypt(encrypted_content)
                # else:
                #     print(f"⚠️ 文件 '{file_name}' 不存在或为空")
            else:
                print(f"❌ 读取失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 获取过程发生错误: {e}")
        return None

    def update_secure_content(self, file_name: str, plain_text: str):
        """将明文加密后上传到 Gist"""
        encrypted_content = self._encrypt(plain_text)
        data = {"files": {file_name: {"content": encrypted_content}}}

        try:
            response = requests.patch(
                self.base_url, headers=self.headers, data=json.dumps(data)
            )
            if response.status_code == 200:
                print(f"✅ 加密内容已成功同步至 Gist")
                return True
            else:
                print(f"❌ 更新失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 更新过程发生错误: {e}")
        return False
