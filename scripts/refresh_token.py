"""
Обновление long-lived Threads токена.

Long-lived токен живёт 60 дней, но его можно рефрешить после первых 24 часов
и продлить ещё на 60 дней. Запускается раз в неделю по cron.

После получения нового токена обновляет GitHub Secret через GitHub API.
Для этого нужен GH_PAT (Personal Access Token) с правом 'repo' и 'workflow'.
"""

import os
import sys
import base64
import requests
from nacl import encoding, public


def refresh_threads_token(current_token: str) -> str:
    """Дёргает refresh endpoint Threads API."""
    url = "https://graph.threads.net/refresh_access_token"
    params = {
        "grant_type": "th_refresh_token",
        "access_token": current_token,
    }
    r = requests.get(url, params=params, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Refresh failed [{r.status_code}]: {r.text}")
    data = r.json()
    new_token = data["access_token"]
    expires_in = data.get("expires_in", 5184000)
    print(f"[ok] получен новый токен, истекает через {expires_in} секунд")
    return new_token


def update_github_secret(repo: str, secret_name: str, value: str, pat: str):
    """Обновляет GitHub Secret через API. repo формата 'owner/repo'."""
    # Получаем public key репозитория для шифрования
    r = requests.get(
        f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {pat}",
        },
        timeout=30,
    )
    r.raise_for_status()
    key_data = r.json()
    public_key = key_data["key"]
    key_id = key_data["key_id"]

    # Шифруем значение секрета через NaCl sealed box
    pk = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed = public.SealedBox(pk)
    encrypted = sealed.encrypt(value.encode("utf-8"))
    encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")

    # Обновляем secret
    r = requests.put(
        f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {pat}",
        },
        json={
            "encrypted_value": encrypted_b64,
            "key_id": key_id,
        },
        timeout=30,
    )
    r.raise_for_status()
    print(f"[ok] GitHub Secret {secret_name} обновлён")


def main():
    current = os.environ["THREADS_ACCESS_TOKEN"]
    new_token = refresh_threads_token(current)

    # Обновляем секрет в GitHub
    repo = os.environ.get("GITHUB_REPOSITORY")  # автоматически выставляется в Actions
    pat = os.environ.get("GH_PAT")
    if not repo or not pat:
        print("[warn] GH_PAT или GITHUB_REPOSITORY не заданы, не могу обновить Secret")
        print(f"[manual] Новый токен:\n{new_token}")
        sys.exit(0)

    update_github_secret(repo, "THREADS_ACCESS_TOKEN", new_token, pat)


if __name__ == "__main__":
    main()
