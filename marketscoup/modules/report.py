from __future__ import annotations

import os
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

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


def _format_establishment_table(items: List[AggregatedEstablishment]) -> Table:
    """Формирует таблицу с информацией о заведениях."""
    data = [["№", "Название", "Город", "Категория", "Ср. чек", "Рейтинг", "Схожесть"]]
    
    for idx, item in enumerate(items, 1):
        est = item.establishment
        finance = item.finance
        reviews = item.reviews
        
        avg_check = f"{finance.avg_check:.0f} ₽" if finance and finance.avg_check else "—"
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
    
    table = Table(data, colWidths=[1*cm, 5*cm, 3*cm, 3*cm, 2.5*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def generate_pdf_report(analysis: AggregatedAnalysis, niche_description: str, output_path: str) -> None:
    """Генерирует PDF отчет с анализом заведений."""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Заголовок
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=30,
        alignment=1,  # Center
    )
    story.append(Paragraph("Отчет по анализу рынка", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Информация о запросе
    story.append(Paragraph(f"<b>Запрос:</b> {analysis.query}", styles["Normal"]))
    story.append(Paragraph(f"<b>Дата анализа:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Количество заведений:</b> {len(analysis.items)}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))
    
    # Описание ниши
    story.append(Paragraph("<b>Описание ниши и общего запроса</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.3*cm))
    
    niche_style = ParagraphStyle(
        "NicheDescription",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=12,
    )
    story.append(Paragraph(niche_description.replace("\n", "<br/>"), niche_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Таблица заведений
    story.append(Paragraph("<b>Топ заведений</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(_format_establishment_table(analysis.items))
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
        if est.url:
            info_lines.append(f"<b>URL:</b> {est.url}")
        
        if info_lines:
            story.append(Paragraph("<br/>".join(info_lines), styles["Normal"]))
            story.append(Spacer(1, 0.3*cm))
        
        # Финансовая информация
        if finance:
            story.append(Paragraph("<b>Финансовые показатели:</b>", styles["Normal"]))
            finance_lines = []
            if finance.avg_check:
                finance_lines.append(f"Средний чек: {finance.avg_check:.0f} ₽")
            if finance.avg_revenue:
                finance_lines.append(f"Средняя выручка: {finance.avg_revenue:,.0f} ₽/год")
            if finance.avg_expenses:
                finance_lines.append(f"Средние расходы: {finance.avg_expenses:,.0f} ₽/год")
            if finance.avg_income:
                finance_lines.append(f"Средний доход: {finance.avg_income:,.0f} ₽/год")
            
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
    config = load_config()
    
    # Генерируем описание ниши
    niche_description = await _generate_niche_description(analysis, config)
    
    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in analysis.query[:50])
    filename = f"marketscoup_report_{safe_query.replace(' ', '_')}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Генерируем PDF
    generate_pdf_report(analysis, niche_description, output_path)
    
    return output_path

