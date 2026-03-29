#!/usr/bin/env python3
"""
Пошаговая проверка всех блоков в режиме «Анализ конкурентов».
Запуск: python test_competitive_blocks.py [--block N] [--continue-on-error]

Без --block: выполняет все блоки 1→2→3→4→5→6 последовательно.
С --block N: выполняет только блок N (нужны выходы предыдущих блоков).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "restaurant_pipeline"
EXCHANGE = PIPELINE / "data_exchange"

if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INPUT = EXCHANGE / "input_request.json"
B1 = EXCHANGE / "block1_output.json"
B2 = EXCHANGE / "block2_output.json"
B3 = EXCHANGE / "block3_output.json"
B4 = EXCHANGE / "block4_output.json"
B5 = EXCHANGE / "block5_output.json"
B6 = EXCHANGE / "block6_output.json"


def check_input():
    """Проверяет, что input_request.json в режиме competitive."""
    if not INPUT.exists():
        print(f"❌ Не найден {INPUT}")
        return False
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("report_type") != "competitive":
        print(f"❌ report_type должен быть 'competitive', сейчас: {data.get('report_type')}")
        return False
    ref = data.get("reference_place") or {}
    if not ref.get("name"):
        print("❌ reference_place.name обязателен для competitive")
        return False
    print(f"✓ Вход: competitive, опорное заведение: {ref.get('name')}")
    return True


def run_block1():
    from restaurant_pipeline.blocks.block1_relevance.run import run as run_block1
    run_block1(str(INPUT), str(B1))
    print(f"  → {B1}")


def run_block2():
    if not B1.exists():
        print("  ⚠ block1_output.json не найден, пропуск block2")
        return
    from restaurant_pipeline.blocks.block2_menu.run import run as run_block2
    run_block2(str(B1), str(B2))
    print(f"  → {B2}")


def run_block3():
    if not B1.exists():
        print("  ⚠ block1_output.json не найден, пропуск block3")
        return
    from restaurant_pipeline.blocks.block3_reviews.run import run as run_block3
    run_block3(str(B1), str(B3))
    print(f"  → {B3}")


def run_block4():
    if not B1.exists():
        print("  ⚠ block1_output.json не найден, пропуск block4")
        return
    from restaurant_pipeline.blocks.block4_marketing.run import run as run_block4
    run_block4(str(B1), str(B4))
    print(f"  → {B4}")


def run_block5():
    if not B1.exists():
        print("  ⚠ block1_output.json не найден, пропуск block5")
        return
    from restaurant_pipeline.blocks.block5_tech.run import run as run_block5
    run_block5(str(B1), str(B5))
    print(f"  → {B5}")


def run_block6():
    for p in [B1, B2, B3, B4, B5]:
        if not p.exists():
            print(f"  ⚠ {p.name} не найден, block6 может работать неполно")
    from restaurant_pipeline.blocks.block6_aggregator.run import run as run_block6
    run_block6(str(B1), str(B2), str(B3), str(B4), str(B5), str(B6), "competitive")
    print(f"  → {B6}")


BLOCKS = {
    1: ("block1_relevance (поиск конкурентов + опорное)", run_block1),
    2: ("block2_menu (меню)", run_block2),
    3: ("block3_reviews (отзывы + тональность)", run_block3),
    4: ("block4_marketing (соцсети)", run_block4),
    5: ("block5_tech (сайты)", run_block5),
    6: ("block6_aggregator (финальный отчёт)", run_block6),
}


def main():
    parser = argparse.ArgumentParser(description="Пошаговая проверка блоков competitive")
    parser.add_argument("--block", type=int, choices=[1, 2, 3, 4, 5, 6],
                        help="Запустить только блок N")
    parser.add_argument("--continue-on-error", action="store_true",
                        help="Продолжать при ошибке в блоке")
    args = parser.parse_args()

    if not check_input():
        sys.exit(1)

    to_run = [args.block] if args.block else [1, 2, 3, 4, 5, 6]
    print(f"\n=== Запуск блоков: {to_run} ===\n")

    for n in to_run:
        label, fn = BLOCKS[n]
        print(f"[{n}/6] {label} ...", flush=True)
        try:
            fn()
            print(f"  ✓ готово\n", flush=True)
        except Exception as e:
            print(f"  ❌ ОШИБКА: {e}\n", flush=True)
            if not args.continue_on_error:
                import traceback
                traceback.print_exc()
                sys.exit(1)

    print("=== Готово ===")
    if 6 in to_run and B6.exists():
        print(f"Итоговый отчёт: {B6}")


if __name__ == "__main__":
    main()
