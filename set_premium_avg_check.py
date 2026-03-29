# -*- coding: utf-8 -*-
"""
Во всех CSV с колонками тип_заведения и средний_чек:
где в тип_заведения есть «премиум» (в т.ч. премиум-ресторан) — ставим средний_чек = 4500.
"""
import pandas as pd
import sys

AVG_CHECK = 4500


def update_csv(path: str, dry_run: bool = False) -> int:
    df = pd.read_csv(path)
    if "тип_заведения" not in df.columns or "средний_чек" not in df.columns:
        print(f"  Пропуск {path}: нет тип_заведения или средний_чек")
        return 0
    mask = df["тип_заведения"].fillna("").astype(str).str.lower().str.contains("премиум")
    n = mask.sum()
    if n == 0:
        print(f"  {path}: строк с «премиум» в типе нет")
        return 0
    if dry_run:
        print(f"  {path}: будет обновлено {n} строк (средний_чек -> {AVG_CHECK})")
        return int(n)
    df.loc[mask, "средний_чек"] = AVG_CHECK
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"  {path}: обновлено {n} строк")
    return int(n)


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        sys.argv = [a for a in sys.argv if a != "--dry-run"]
    paths = [
        "final_blyat_v3.csv",
        "final_blyat_v2.csv",
        "final_blyat.csv",
        "ruski.csv",
    ]
    if len(sys.argv) > 1:
        paths = [p for p in sys.argv[1:] if p != "--dry-run"]
    total = 0
    for p in paths:
        try:
            total += update_csv(p, dry_run=dry_run)
        except Exception as e:
            print(f"  {p}: ошибка — {e}")
    print(f"Всего обновлено строк: {total}")


if __name__ == "__main__":
    main()
