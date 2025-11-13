from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..config import AppConfig, load_config
from ..domain.models import AggregatedAnalysis, AggregatedEstablishment
from ..llm.client import LlmSettings, get_llm_client, LlmError


NICHE_ANALYSIS_PROMPT = (
    "Ты — аналитик рынка общественного питания. На основе предоставленной информации о заведениях "
    "сформируй развёрнутое описание ниши и общего запроса. Опиши: "
    "1) Общую характеристику ниши (тип кухни, концепция, целевая аудитория), "
    "2) Типичные особенности заведений в этой нише, "
    "3) Средний ценовой сегмент и его особенности, "
    "4) Общие тренды и паттерны, "
    "5) Ключевые конкурентные преимущества и недостатки. "
    "Верни СТРОГО валидный JSON: {\"niche_description\": \"текст описания\"} без пояснений."
)


async def _generate_niche_description(analysis: AggregatedAnalysis, config: AppConfig) -> str:
    """Генерирует общее описание ниши на основе анализа заведений."""
    if not config.llm_api_key:
        return "Описание ниши недоступно (отсутствует LLM API ключ)."
    
    # Формируем краткую сводку по заведениям для LLM
    establishments_summary = []
    for item in analysis.items[:5]:  # Берем топ-5 для анализа
        est = item.establishment
        finance = item.finance
        reviews = item.reviews
        
        summary_parts = [
            f"Название: {est.name}",
            f"Категория: {est.category or 'не указана'}",
            f"Город: {est.city or 'не указан'}",
        ]
        
        if finance and finance.avg_check:
            summary_parts.append(f"Средний чек: {finance.avg_check:.0f} руб")
        
        if reviews and reviews.avg_rating:
            summary_parts.append(f"Рейтинг: {reviews.avg_rating:.1f}")
        
        if reviews and reviews.overall_opinion:
            summary_parts.append(f"Особенности: {reviews.overall_opinion[:200]}...")
        
        establishments_summary.append(" | ".join(summary_parts))
    
    user_prompt = "\n".join([
        f"Запрос пользователя: {analysis.query}",
        "",
        "Информация о найденных заведениях:",
        "\n".join(f"{i+1}. {s}" for i, s in enumerate(establishments_summary)),
        "",
        "Сформируй развёрнутое описание ниши на основе этой информации.",
    ])
    
    settings = LlmSettings(
        provider=config.llm_provider or "perplexity",
        api_key=config.llm_api_key,
        model=config.llm_model or "sonar-reasoning-pro",
    )
    client = get_llm_client(settings)
    
    try:
        payload = await client.complete_json(
            system=NICHE_ANALYSIS_PROMPT,
            user=user_prompt,
            max_tokens=2000,
        )
        # Извлекаем описание из ответа
        if isinstance(payload, dict):
            description = payload.get("niche_description") or payload.get("description")
            if description:
                return str(description)
        # Fallback если структура неожиданная
        return "Не удалось сгенерировать описание ниши."
    except LlmError:
        return "Не удалось сгенерировать описание ниши (ошибка LLM)."


def _format_establishment_table(items: List[AggregatedEstablishment], font_name: str = "Helvetica") -> Table:
    """Формирует таблицу с информацией о заведениях."""
    data = [["№", "Название", "Город", "Категория", "Ср. чек", "Рейтинг", "Схожесть"]]
    
    for idx, item in enumerate(items, 1):
        est = item.establishment
        finance = item.finance
        reviews = item.reviews
        
        avg_check = f"{finance.avg_check:.0f} руб" if finance and finance.avg_check else "—"
        rating = f"{reviews.avg_rating:.1f}" if reviews and reviews.avg_rating else "—"
        similarity = f"{est.similarity_score:.2f}" if est.similarity_score is not None else "—"
        
        data.append([
            str(idx),
            est.name[:30],  # Ограничиваем длину
            est.city or "—",
            (est.category or "—")[:20],
            avg_check,
            rating,
            similarity,
        ])
    
    bold_font = f"{font_name}-Bold" if font_name != "UnicodeFont" else "UnicodeFont"
    table = Table(data, colWidths=[1*cm, 5*cm, 3*cm, 3*cm, 2.5*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),  # Заголовки по центру
        ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Колонка № по центру
        ("ALIGN", (1, 1), (1, -1), "LEFT"),  # Название слева
        ("ALIGN", (2, 1), (2, -1), "LEFT"),  # Город слева
        ("ALIGN", (3, 1), (3, -1), "LEFT"),  # Категория слева
        ("ALIGN", (4, 1), (4, -1), "RIGHT"),  # Ср. чек справа
        ("ALIGN", (5, 1), (5, -1), "CENTER"),  # Рейтинг по центру
        ("ALIGN", (6, 1), (6, -1), "CENTER"),  # Схожесть по центру
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ("FONTNAME", (0, 1), (-1, -1), font_name),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def _register_unicode_fonts():
    """Регистрирует шрифты с поддержкой кириллицы."""
    # Пробуем найти и зарегистрировать шрифт с поддержкой Unicode
    font_paths = [
        # macOS - пробуем разные варианты (проверено, что Arial Unicode есть)
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Windows (если запускается на Windows)
        "C:/Windows/Fonts/arialuni.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                # Регистрируем обычный и жирный шрифты
                pdfmetrics.registerFont(TTFont("UnicodeFont", font_path))
                # Пробуем зарегистрировать жирный вариант
                try:
                    bold_path = font_path.replace("Regular", "Bold").replace(".ttf", "Bold.ttf")
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont("UnicodeFont-Bold", bold_path))
                except Exception:
                    pass
                print(f"[Отчёт] Используется шрифт с поддержкой Unicode: {font_path}", file=sys.stderr)
                return "UnicodeFont"
            except Exception as e:
                print(f"[Отчёт] Ошибка при загрузке шрифта {font_path}: {e}", file=sys.stderr)
                continue
    
    # Если не нашли внешний шрифт, предупреждаем
    print(f"[Отчёт] ВНИМАНИЕ: Не найден шрифт с поддержкой Unicode. Кириллица может отображаться некорректно.", file=sys.stderr)
    print(f"[Отчёт] Используется стандартный шрифт Helvetica (без поддержки кириллицы)", file=sys.stderr)
    return "Helvetica"


def generate_pdf_report(analysis: AggregatedAnalysis, niche_description: str, output_path: str) -> None:
    """Генерирует PDF отчет с анализом заведений."""
    # Регистрируем шрифт с поддержкой кириллицы
    base_font_name = _register_unicode_fonts()
    
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Обновляем стандартные стили для поддержки кириллицы ДО их использования
    for style_name in ["Normal", "Heading1", "Heading2", "Heading3"]:
        if style_name in styles:
            styles[style_name].fontName = base_font_name
    
    # Заголовок
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName=base_font_name,
        fontSize=20,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=30,
        alignment=1,  # Center
    )
    story.append(Paragraph("Отчет по анализу рынка", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Информация о запросе
    info_style = ParagraphStyle(
        "InfoStyle",
        parent=styles["Normal"],
        fontName=base_font_name,
        fontSize=11,
    )
    story.append(Paragraph(f"<b>Запрос:</b> {analysis.query}", info_style))
    story.append(Paragraph(f"<b>Дата анализа:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}", info_style))
    story.append(Paragraph(f"<b>Количество заведений:</b> {len(analysis.items)}", info_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Описание ниши
    story.append(Paragraph("<b>Описание ниши и общего запроса</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.3*cm))
    
    niche_style = ParagraphStyle(
        "NicheDescription",
        parent=styles["Normal"],
        fontName=base_font_name,
        fontSize=11,
        leading=16,
        spaceAfter=12,
    )
    
    # Проверяем, что описание ниши не пустое
    if niche_description and niche_description.strip():
        story.append(Paragraph(niche_description.replace("\n", "<br/>"), niche_style))
    else:
        story.append(Paragraph("Описание ниши недоступно.", niche_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Таблица заведений
    story.append(Paragraph("<b>Топ заведений</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(_format_establishment_table(analysis.items, base_font_name))
    story.append(PageBreak())
    
    # Детальная информация по каждому заведению
    story.append(Paragraph("<b>Детальная информация по заведениям</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.5*cm))
    
    for idx, item in enumerate(analysis.items, 1):
        est = item.establishment
        finance = item.finance
        reviews = item.reviews
        
        # Заголовок заведения
        est_title = f"{idx}. {est.name}"
        story.append(Paragraph(est_title, styles["Heading3"]))
        story.append(Spacer(1, 0.2*cm))
        
        # Основная информация
        info_lines = []
        if est.address:
            info_lines.append(f"<b>Адрес:</b> {est.address}")
        if est.city:
            info_lines.append(f"<b>Город:</b> {est.city}")
        if est.category:
            info_lines.append(f"<b>Категория:</b> {est.category}")
        if est.similarity_score is not None:
            info_lines.append(f"<b>Схожесть с запросом:</b> {est.similarity_score:.2f}")
        
        if info_lines:
            story.append(Paragraph("<br/>".join(info_lines), styles["Normal"]))
            story.append(Spacer(1, 0.3*cm))
        
        # Финансовая информация
        if finance:
            story.append(Paragraph("<b>Финансовые показатели:</b>", styles["Normal"]))
            finance_lines = []
            if finance.avg_check:
                finance_lines.append(f"Средний чек: {finance.avg_check:.0f} руб")
            if finance.avg_revenue:
                finance_lines.append(f"Средняя выручка: {finance.avg_revenue:,.0f} руб/год")
            if finance.avg_expenses:
                finance_lines.append(f"Средние расходы: {finance.avg_expenses:,.0f} руб/год")
            if finance.avg_income:
                finance_lines.append(f"Средний доход: {finance.avg_income:,.0f} руб/год")
            
            if finance_lines:
                story.append(Paragraph(" | ".join(finance_lines), styles["Normal"]))
            story.append(Spacer(1, 0.3*cm))
        
        # Отзывы
        if reviews:
            story.append(Paragraph("<b>Отзывы и рейтинги:</b>", styles["Normal"]))
            review_lines = []
            if reviews.avg_rating:
                review_lines.append(f"Средний рейтинг: {reviews.avg_rating:.1f}")
            if reviews.reviews_count and reviews.reviews_count > 0:
                review_lines.append(f"Количество отзывов: {reviews.reviews_count}")
            
            if review_lines:
                story.append(Paragraph(" | ".join(review_lines), styles["Normal"]))
            
            if reviews.overall_opinion:
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph("<b>Общее описание:</b>", styles["Normal"]))
                story.append(Paragraph(reviews.overall_opinion.replace("\n", "<br/>"), niche_style))
            
            if reviews.pros:
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph("<b>Плюсы:</b>", styles["Normal"]))
                for pro in reviews.pros:
                    story.append(Paragraph(f"• {pro}", styles["Normal"]))
            
            if reviews.cons:
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph("<b>Минусы:</b>", styles["Normal"]))
                for con in reviews.cons:
                    story.append(Paragraph(f"• {con}", styles["Normal"]))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Разделитель между заведениями (кроме последнего)
        if idx < len(analysis.items):
            story.append(Spacer(1, 0.3*cm))
    
    # Генерируем PDF
    doc.build(story)


async def create_report(analysis: AggregatedAnalysis, output_dir: str = ".") -> str:
    """Создает PDF отчет и возвращает путь к файлу."""
    import sys
    config = load_config()
    
    print(f"[Этап 3/3] Начинаю генерацию PDF отчёта...", file=sys.stderr)
    # Генерируем описание ниши
    print(f"[Отчёт] Генерирую описание ниши...", file=sys.stderr)
    niche_description = await _generate_niche_description(analysis, config)
    
    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in analysis.query[:50])
    filename = f"marketscoup_report_{safe_query.replace(' ', '_')}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Генерируем PDF
    print(f"[Отчёт] Формирую PDF документ...", file=sys.stderr)
    generate_pdf_report(analysis, niche_description, output_path)
    print(f"[Этап 3/3] PDF отчёт успешно создан", file=sys.stderr)
    
    return output_path

