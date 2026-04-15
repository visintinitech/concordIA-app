# 🔮 ConcordIA

<div align="center">

![Versión](https://img.shields.io/badge/versión-3.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Licencia](https://img.shields.io/badge/licencia-MIT-yellow)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)

**"Donde el artículo encuentra al sustantivo que merece"**

Un corrector gramatical de español que detecta discordancias de género, número, 
concordancia verbal, pronombres y preposiciones.

</div>

---

## 📖 ¿Qué es ConcordIA?

ConcordIA es un proyecto **práctico y educativo** que explora las dificultades del procesamiento de lenguaje natural (NLP) en español. 

A diferencia de correctores comerciales como LanguageTool o Microsoft Word, ConcordIA:

- ✅ Es **100% código abierto**
- ✅ Se enfoca en **reglas gramaticales explícitas**
- ✅ Sirve como **ejemplo didáctico** de NLP básico
- ✅ Es **fácil de extender** con nuevas reglas

---

## 🎯 ¿Qué detecta ConcordIA?

| Tipo de error | Ejemplo | Corrección |
|---------------|---------|------------|
| **Artículo + sustantivo (género)** | "el casa" | "la casa" |
| **Artículo + sustantivo (número)** | "el casas" | "las casas" |
| **Sustantivo + adjetivo** | "casa bonito" | "casa bonita" |
| **Sujeto + verbo (persona)** | "yo hace" | "yo hago" |
| **Sujeto + verbo (número)** | "los niño juega" | "los niños juegan" |
| **Leísmo** | "le vi" (a él) | "lo vi" |
| **Laísmo** | "la dije" (a él) | "le dije" |
| **Dequeísmo** | "pienso de que..." | "pienso que..." |
| **Queísmo** | "me di cuenta que..." | "me di cuenta de que..." |

---

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/concordia.git
cd concordia

# Instalar dependencias (opcional, solo para web)
pip install flask

# Ejecutar
python concordia.py
