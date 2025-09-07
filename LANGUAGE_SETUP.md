# 🌍 Language Configuration Guide

The receipt printer system supports **12+ languages** with full AI-generated content including greetings, dates, titles, and cultural formatting.

## 🚀 Quick Start

### Method 1: Environment Variable (Recommended)
Add to your `.env` file:
```bash
RECEIPT_LANGUAGE=english
```

### Method 2: Python Code
```python
from src.config import set_language, Language
set_language(Language.ENGLISH)
```

### Method 3: Direct Configuration
```python
from src.config import get_config, Language
config = get_config()
config.language = Language.ENGLISH
```

## 🌍 Supported Languages

| Language | Code | Example Output |
|----------|------|----------------|
| **German** | `german` | "Guten Morgen, Luka!" |
| **English** | `english` | "Good morning, Luka!" |
| **Spanish** | `spanish` | "¡Buenos días, Luka!" |
| **French** | `french` | "Bonjour, Luka!" |
| **Italian** | `italian` | "Buongiorno, Luka!" |
| **Dutch** | `dutch` | "Goedemorgen, Luka!" |
| **Portuguese** | `portuguese` | "Bom dia, Luka!" |
| **Russian** | `russian` | "Доброе утро, Luka!" |
| **Japanese** | `japanese` | "おはようございます、Lukaさん！" |
| **Korean** | `korean` | "좋은 아침이에요, Luka!" |
| **Chinese** | `chinese` | "早上好，Luka！" |
| **Arabic** | `arabic` | "صباح الخير، Luka!" |

## ⚙️ Configuration Methods

### 1. Environment Variable (Persistent)
Edit your `.env` file:
```bash
# Language Settings
RECEIPT_LANGUAGE=english
USER_NAME=YourName
USER_TIMEZONE=Europe/Berlin
```

### 2. Python Script (Runtime)
Create a script to change language:
```python
#!/usr/bin/env python3
from src.config import set_language, Language
from src.daily_brief import main

# Switch to Spanish
set_language(Language.SPANISH)

# Run daily brief in Spanish
main()
```

### 3. Command Line (Temporary)
```bash
# Set environment variable and run
RECEIPT_LANGUAGE=spanish python3 daily_brief.py

# Or export for session
export RECEIPT_LANGUAGE=french
python3 daily_brief.py
```

### 4. Interactive Language Selector
```python
#!/usr/bin/env python3
from src.config import set_language, Language

def select_language():
    print("🌍 Available Languages:")
    for i, lang in enumerate(Language, 1):
        print(f"{i}. {lang.value.title()}")
    
    choice = int(input("Select language (1-12): ")) - 1
    selected_lang = list(Language)[choice]
    set_language(selected_lang)
    print(f"✅ Language set to: {selected_lang.value.title()}")

if __name__ == "__main__":
    select_language()
```

## 🎯 What Gets Localized

When you change the language, **everything** gets AI-generated in that language:

### ✅ **Headers & Greetings**
- Time-appropriate greetings (morning/afternoon/evening)
- Personalized with your name
- Cultural context awareness

### ✅ **Dates & Time**
- Proper date formatting for each culture
- Day names in local language
- Month names in local language

### ✅ **Content & Briefs**
- Contextual daily briefs
- Cultural references and tone
- Local weather descriptions

### ✅ **Section Headers**
- "Tasks" → "Aufgaben" (German) → "Tareas" (Spanish)
- "Shopping" → "Einkaufen" (German) → "Compras" (Spanish)

### ✅ **Footer & Labels**
- "Generated at" → "Erstellt um" (German) → "Generado a las" (Spanish)

## 🔧 Advanced Configuration

### Custom Language Support
To add a new language, edit `src/config.py`:

```python
class Language(str, Enum):
    # Add your language
    SWEDISH = "swedish"
    NORWEGIAN = "norwegian"

# Add to language codes
def get_language_code(self) -> str:
    language_codes = {
        # ... existing languages ...
        Language.SWEDISH: "Swedish",
        Language.NORWEGIAN: "Norwegian"
    }
```

### Timezone Configuration
```bash
# In .env file
USER_TIMEZONE=America/New_York  # For US users
USER_TIMEZONE=Asia/Tokyo        # For Japan users
USER_TIMEZONE=Europe/London     # For UK users
```

### Shopping List Names
The system automatically uses localized shopping list names:
- German: "Einkaufsliste"
- English: "Shopping List" 
- Spanish: "Lista de Compras"
- etc.

## 🚀 Usage Examples

### Example 1: Daily German Brief
```bash
# Set in .env
RECEIPT_LANGUAGE=german
python3 daily_brief.py
```

### Example 2: Multilingual Testing
```python
from src.config import set_language, Language
from src.daily_brief import create_daily_brief

# Test multiple languages
for lang in [Language.ENGLISH, Language.SPANISH, Language.FRENCH]:
    set_language(lang)
    print(f"Testing {lang.value}...")
    create_daily_brief()
```

### Example 3: Language-Specific Features
```python
from src.config import get_config

config = get_config()
print(f"Current language: {config.language}")
print(f"Language code: {config.get_language_code()}")
print(f"Shopping list name: {config.get_shopping_list_name_localized()}")
```

## 🎉 Ready to Go!

Your receipt printer now supports **12+ languages** with full AI-generated content. Just set your preferred language and enjoy culturally appropriate daily briefs! 🌍✨
