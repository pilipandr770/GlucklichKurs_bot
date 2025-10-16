"""
Safety Guards для AI агентів
Використовує OpenAI Moderation API + кастомні правила
"""
import os
import re
from typing import Tuple, Optional
from .openai_client import _client

# Trigger слова для різних категорій ризику
MEDICAL_TRIGGERS = [
    r'\b(депрес[ісія]|суїцид|самогубств|покінчити з життям|смерт|вбити себе)\b',
    r'\b(ліки|препарат|таблетк|антидепресант|психіатр)\b',
    r'\b(діагноз|лікування|хвороб|розлад|біполяр)\b',
]

LEGAL_TRIGGERS = [
    r'\b(позов|суд|адвокат|юрист|контракт|договір)\b',
    r'\b(незаконн|злочин|поліція|прокурор)\b',
]

FINANCIAL_TRIGGERS = [
    r'\b(кредит|позик|борг|інвестиц|акц[іії]|крипто)\b',
    r'\b(заробіт|гарантую|100%|мільйон)\b',
]

PERSONAL_DATA_TRIGGERS = [
    r'\b(\d{10}|\d{4}\s?\d{4}\s?\d{4}\s?\d{4})\b',  # номери карток
    r'\b[A-Z]{2}\d{6}\b',  # паспорти
]

def check_moderation(text: str) -> Tuple[bool, Optional[str]]:
    """
    Перевіряє текст через OpenAI Moderation API
    
    Returns:
        (is_safe, violation_category)
        is_safe=True якщо контент безпечний
    """
    try:
        response = _client.moderations.create(input=text)
        result = response.results[0]
        
        if result.flagged:
            # Знайти категорію порушення
            categories = result.categories
            violations = []
            
            if categories.hate: violations.append("hate speech")
            if categories.self_harm: violations.append("self-harm")
            if categories.sexual: violations.append("sexual content")
            if categories.violence: violations.append("violence")
            if categories.harassment: violations.append("harassment")
            
            return False, ", ".join(violations)
        
        return True, None
    
    except Exception as e:
        print(f"⚠️  Moderation API error: {e}")
        # Якщо API не працює — дозволяємо (fail-open)
        return True, None

def check_triggers(text: str, trigger_patterns: list) -> Optional[str]:
    """
    Перевіряє текст на trigger слова
    
    Returns:
        Matched pattern або None
    """
    text_lower = text.lower()
    for pattern in trigger_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return pattern
    return None

def sales_guard(user_message: str) -> Tuple[bool, Optional[str]]:
    """
    Guard для Sales Agent
    
    Перевіряє:
    - OpenAI Moderation (hate, violence, self-harm)
    - Медичні питання
    - Юридичні питання
    - Фінансові обіцянки
    
    Returns:
        (is_allowed, rejection_message)
    """
    # 1. OpenAI Moderation
    is_safe, violation = check_moderation(user_message)
    if not is_safe:
        return False, (
            "⚠️ Вибачте, але я не можу обробити це повідомлення через порушення правил безпеки.\n\n"
            "Якщо у вас є термінове питання, зверніться до нашої підтримки: /help"
        )
    
    # 2. Медичні trigger слова
    medical_match = check_triggers(user_message, MEDICAL_TRIGGERS)
    if medical_match:
        return False, (
            "⚠️ <b>Важлива інформація</b>\n\n"
            "Я помітив, що ваше питання стосується медичної теми. "
            "Наш курс — це освітня програма про позитивну психологію, а не медична консультація.\n\n"
            "🏥 <b>Якщо у вас:</b>\n"
            "• Депресія, тривога або інші психічні розлади\n"
            "• Думки про самогубство\n"
            "• Потреба в лікуванні\n\n"
            "📞 <b>Зверніться до професіоналів:</b>\n"
            "• Телефон довіри: 7333 (безкоштовно по Україні)\n"
            "• Психіатр або психотерапевт\n"
            "• Сімейний лікар\n\n"
            "💚 Наш курс може бути корисним доповненням до професійної допомоги, але не замінює її.\n\n"
            "Детальніше: /disclaimer"
        )
    
    # 3. Юридичні питання
    legal_match = check_triggers(user_message, LEGAL_TRIGGERS)
    if legal_match:
        return False, (
            "⚠️ Вибачте, але я не можу надавати юридичні консультації.\n\n"
            "Наш курс — про особистий розвиток та щастя, а не про правові питання.\n\n"
            "📋 Юридична інформація: /legal"
        )
    
    # 4. Фінансові обіцянки (захист від скаму)
    financial_match = check_triggers(user_message, FINANCIAL_TRIGGERS)
    if financial_match:
        return False, (
            "⚠️ <b>Важливе застереження</b>\n\n"
            "Я не надаю фінансових порад та не гарантую конкретних результатів.\n\n"
            "Наш курс — про психологічне благополуччя, а не про фінансовий успіх.\n\n"
            "📋 Детальніше про обмеження: /disclaimer"
        )
    
    return True, None

def coach_guard(user_message: str) -> Tuple[bool, Optional[str]]:
    """
    Guard для Coach Agent (після оплати)
    
    Перевіряє:
    - OpenAI Moderation
    - Медичні питання (більш м'яка відповідь)
    - Персональні дані
    - Запити на збереження інформації
    
    Returns:
        (is_allowed, rejection_message)
    """
    # 1. OpenAI Moderation
    is_safe, violation = check_moderation(user_message)
    if not is_safe:
        return False, (
            "⚠️ Вибачте, я не можу обробити це повідомлення.\n\n"
            "Якщо потрібна допомога — напишіть /help"
        )
    
    # 2. Медичні питання (м'якша версія для платників)
    medical_match = check_triggers(user_message, MEDICAL_TRIGGERS)
    if medical_match:
        return False, (
            "⚠️ <b>Важлива примітка</b>\n\n"
            "Я бачу, що ваше питання стосується медичної теми. "
            "Хоча наш курс базується на науці, він НЕ замінює професійної медичної допомоги.\n\n"
            "🏥 <b>Рекомендую звернутися:</b>\n"
            "• Психотерапевт або психіатр\n"
            "• Телефон довіри: 7333\n\n"
            "💚 Я можу допомогти з практиками з курсу (вдячність, усвідомленість тощо), "
            "які можуть бути корисним доповненням до професійної допомоги.\n\n"
            "📋 Детальніше: /disclaimer"
        )
    
    # 3. Персональні дані
    personal_data_match = check_triggers(user_message, PERSONAL_DATA_TRIGGERS)
    if personal_data_match:
        return False, (
            "⚠️ <b>Захист персональних даних</b>\n\n"
            "Я помітив, що ви надіслали особисті дані (номер картки, паспорт тощо).\n\n"
            "🔒 <b>Важливо:</b>\n"
            "• Я не зберігаю ваші повідомлення\n"
            "• Не діліться чутливою інформацією в чаті\n"
            "• Видаліть повідомлення з даними (утримайте → Видалити)\n\n"
            "📋 Політика конфіденційності: /datenschutz"
        )
    
    # 4. Запити на збереження
    if re.search(r'\b(запам\'ятай|збережи|запиши|нотатк)\b', user_message.lower()):
        return False, (
            "ℹ️ <b>Про збереження даних</b>\n\n"
            "Я не зберігаю історію наших розмов між сесіями.\n\n"
            "Кожне нове повідомлення — це новий контекст. "
            "Рекомендую вести власні нотатки про ваш прогрес у курсі.\n\n"
            "📋 Детальніше: /datenschutz"
        )
    
    return True, None

async def apply_guard(user_message: str, agent_type: str) -> Tuple[bool, Optional[str]]:
    """
    Застосовує відповідний guard в залежності від типу агента
    
    Args:
        user_message: Повідомлення користувача
        agent_type: "sales" або "coach"
    
    Returns:
        (is_allowed, rejection_message)
    """
    if agent_type == "sales":
        return sales_guard(user_message)
    elif agent_type == "coach":
        return coach_guard(user_message)
    else:
        # Для невідомих агентів — завжди перевіряти moderation
        is_safe, _ = check_moderation(user_message)
        return is_safe, None
