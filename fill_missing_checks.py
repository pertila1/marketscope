"""
Одноразовый скрипт: заполняет пропуски в колонке средний_чек в CSV.
Если тип_заведения содержит «ресторан» и средний_чек пустой — ставит 3500.
Сохраняет результат в тот же файл (оригинал бэкапится с суффиксом .bak).
"""
import shutil
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).parent / "final_blyat_v3.csv"
DEFAULT_CHECK_RESTAURANT = 3500.0


def main() -> None:
    df = pd.read_csv(CSV_PATH, low_memory=False)

    nan_mask = df["средний_чек"].isna()
    total_nan = nan_mask.sum()
    print(f"Всего строк: {len(df)}")
    print(f"Пустой средний_чек: {total_nan}")

    has_restaurant = df["тип_заведения"].fillna("").str.contains("ресторан", case=False)

    fill_mask = nan_mask & has_restaurant
    fill_count = fill_mask.sum()
    print(f"Из них с типом «ресторан»: {fill_count} — заполняем {DEFAULT_CHECK_RESTAURANT}₽")

    if fill_count == 0:
        print("Нечего заполнять.")
        return

    backup = CSV_PATH.with_suffix(".csv.bak")
    shutil.copy2(CSV_PATH, backup)
    print(f"Бэкап: {backup}")

    df.loc[fill_mask, "средний_чек"] = DEFAULT_CHECK_RESTAURANT
    df.to_csv(CSV_PATH, index=False)

    remaining = df["средний_чек"].isna().sum()
    print(f"Заполнено: {fill_count}")
    print(f"Осталось пустых: {remaining}")


if __name__ == "__main__":
    main()
