# -*- coding: utf-8 -*-
import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

from llm.groq_client import answer_query

load_dotenv()

print("=== answer_query ===")
for q in ["atımı nasıl tımar ederim", "Bugün hava nasıl?"]:
    print(f"\nSORU: {q}")
    print(answer_query(q))
    print("-" * 40)

password = os.environ.get("APP_PASSWORD") or ""
base = "http://127.0.0.1:8000"

print("\n=== /ask ===")
for q in ["atımı nasıl tımar ederim", "Bugün hava nasıl?"]:
    req = urllib.request.Request(
        base + "/ask",
        data=json.dumps({"question": q}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-App-Password": password,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(f"\nSORU: {q}")
            print("HTTP", resp.status)
            print(body.get("answer"))
    except urllib.error.HTTPError as e:
        print(f"\nSORU: {q}")
        print("HTTP", e.code, e.read().decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"\nSORU: {q}")
        print("BAGLANTI HATASI:", type(e).__name__, e)
    print("-" * 40)
