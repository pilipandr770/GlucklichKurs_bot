# file: app/bot/utils/lesson_loader.py
import os
import json
from typing import List, Dict, Optional

LESSONS_DIR = os.path.join("data", "lessons")

def load_all_lessons() -> List[Dict]:
    """Завантажує всі 10 уроків з data/lessons/ у відсортованому порядку"""
    lessons = []
    for i in range(1, 11):
        path = os.path.join(LESSONS_DIR, f"lesson_{i}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                lessons.append(json.load(f))
    return lessons

def load_lesson(lesson_id: int) -> Optional[Dict]:
    """Завантажує конкретний урок за ID"""
    path = os.path.join(LESSONS_DIR, f"lesson_{lesson_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_lessons_summary() -> str:
    """Повертає короткий опис всіх уроків для контексту агента"""
    lessons = load_all_lessons()
    summary = "📚 УРОКИ КУРСУ «10 КРОКІВ ДО ЩАСТЯ»:\n\n"
    for lesson in lessons:
        summary += f"Урок {lesson['lesson_id']}: {lesson['title']}\n"
        summary += f"Суть: {lesson['core'][:150]}...\n\n"
    return summary

def get_full_lessons_context() -> str:
    """Повертає повний контекст всіх уроків для коуч-агента"""
    lessons = load_all_lessons()
    context = "=== ПОВНА БАЗА ЗНАНЬ КУРСУ ===\n\n"
    
    for lesson in lessons:
        context += f"{'='*60}\n"
        context += f"УРОК {lesson['lesson_id']}: {lesson['title'].upper()}\n"
        context += f"{'='*60}\n\n"
        context += f"🎯 ХУК: {lesson['hook']}\n\n"
        context += f"📖 ОСНОВА:\n{lesson['core']}\n\n"
        context += f"🔬 ДОКАЗИ:\n{lesson['evidence']}\n\n"
        
        context += "💡 ПРАКТИКИ:\n"
        context += "Усвідомлення (Awareness):\n"
        for idx, practice in enumerate(lesson['practices']['awareness'], 1):
            context += f"  {idx}. {practice}\n"
        
        context += f"\nДія (Action):\n"
        context += f"  Завдання: {lesson['practices']['action']['task']}\n"
        context += f"  Час: {lesson['practices']['action']['time_estimate']}\n"
        
        context += f"\nЗакріплення (Reinforcement):\n"
        context += f"  {lesson['practices']['reinforcement']}\n\n"
        
        context += "❓ КВІЗ:\n"
        for idx, q in enumerate(lesson['quiz'], 1):
            context += f"  Q{idx}: {q['question']}\n"
            context += f"  Правильна відповідь: {q['options'][q['correct_index']]}\n"
            context += f"  Пояснення: {q['explanation']}\n\n"
    
    return context
