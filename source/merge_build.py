#!/usr/bin/env python3
"""questions_A/B/C.json を検証・結合し、app_template.html に埋め込んで最終HTMLを生成する"""
import json, sys, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DESKTOP = os.path.expanduser("~/Desktop/簿記3級勉強アプリ.html")
OUT_UPLOAD = os.path.join(BASE, "boki3quiz.html")

VALID_CATS = {"仕訳", "決算", "帳簿・理論"}

def load(name):
    path = os.path.join(BASE, name)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    errors = []
    for i, q in enumerate(data):
        for key in ("c", "t", "q", "ch", "e"):
            if key not in q or not q[key]:
                errors.append(f"{name}[{i}]: missing/empty '{key}'")
        if q.get("c") not in VALID_CATS:
            errors.append(f"{name}[{i}]: bad category {q.get('c')!r}")
        ch = q.get("ch", [])
        if len(ch) != 4:
            errors.append(f"{name}[{i}]: {len(ch)} choices")
        elif len(set(ch)) != 4:
            errors.append(f"{name}[{i}]: duplicate choices: {q.get('q','')[:40]}")
    return data, errors

def main():
    all_q, all_err = [], []
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BASE, "part*.json")))
    print("対象ファイル:", files)
    for name in files:
        data, errors = load(name)
        print(f"{name}: {len(data)}問, エラー{len(errors)}件")
        all_q.extend(data)
        all_err.extend(errors)

    # 問題文の完全重複を除去
    seen, unique = set(), []
    for q in all_q:
        if q["q"] in seen:
            all_err.append(f"重複問題文を除去: {q['q'][:40]}")
            continue
        seen.add(q["q"])
        unique.append(q)

    for e in all_err[:30]:
        print("  !", e)

    if any("missing" in e or "bad category" in e or "choices" in e for e in all_err):
        print("致命的エラーあり。中断。")
        sys.exit(1)

    print(f"合計 {len(unique)}問")
    from collections import Counter
    print("分野別:", dict(Counter(q["c"] for q in unique)))
    print("論点別:", dict(Counter(q["t"] for q in unique)))

    with open(os.path.join(BASE, "app_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    payload = json.dumps(unique, ensure_ascii=False, separators=(",", ":"))
    # </script> がJSON文字列内に現れてもタグとして解釈されないようエスケープ
    payload = payload.replace("</", "<\\/")
    assert "__QUESTIONS_JSON__" in tpl
    html = tpl.replace("__QUESTIONS_JSON__", payload)

    for out in (OUT_DESKTOP, OUT_UPLOAD):
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print("書き出し:", out, f"({os.path.getsize(out)//1024}KB)")

if __name__ == "__main__":
    main()
