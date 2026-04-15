"""
CONCORDIA 3.0 - Detectora de discordancias gramaticales
"Donde el artículo encuentra al sustantivo que merece"

Características completas:
✅ Artículo + Sustantivo (género y número)
✅ Sustantivo + Adjetivo (género y número)
✅ Sujeto + Verbo (persona y número)
✅ Pronombres (le/la/lo, me/te/se)
✅ Preposiciones (de que/que, en/de)
✅ Interfaz web con Flask
✅ Persistencia completa en JSON
"""

import re
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Intento de importar Flask para web
try:
    from flask import Flask, render_template_string, request, jsonify
    FLASK_DISPONIBLE = True
except ImportError:
    FLASK_DISPONIBLE = False
    print("⚠️ Flask no instalado. La interfaz web no estará disponible.")
    print("   Instalar con: pip install flask")

class ConcordIA:
    def __init__(self, archivo_diccionario="diccionario_concordia.json", archivo_historial="historial_concordia.json"):
        self.nombre = "ConcordIA"
        self.version = "3.0"
        self.lema = "Armonía gramatical total"
        
        # Archivos de datos
        self.archivo_diccionario = archivo_diccionario
        self.archivo_historial = archivo_historial
        
        # Diccionarios principales
        self.sustantivos = {'masculino': set(), 'femenino': set()}
        self.adjetivos = {'masculino': set(), 'femenino': set()}
        self.verbos = {}  # {verbo_infinitivo: {conjugaciones}}
        
        # Excepciones
        self.excepciones = {
            'agua': 'femenino', 'águila': 'femenino', 'hacha': 'femenino',
            'mano': 'femenino', 'día': 'masculino', 'mapa': 'masculino',
            'problema': 'masculino', 'sistema': 'masculino', 'poema': 'masculino',
            'clima': 'masculino', 'idioma': 'masculino', 'tema': 'masculino'
        }
        
        # Artículos
        self.articulos = {
            'el': {'genero': 'masculino', 'numero': 'singular'},
            'los': {'genero': 'masculino', 'numero': 'plural'},
            'la': {'genero': 'femenino', 'numero': 'singular'},
            'las': {'genero': 'femenino', 'numero': 'plural'},
            'un': {'genero': 'masculino', 'numero': 'singular'},
            'unos': {'genero': 'masculino', 'numero': 'plural'},
            'una': {'genero': 'femenino', 'numero': 'singular'},
            'unas': {'genero': 'femenino', 'numero': 'plural'}
        }
        
        # Pronombres
        self.pronombres = {
            'yo': {'persona': 1, 'numero': 'singular'},
            'tú': {'persona': 2, 'numero': 'singular'},
            'vos': {'persona': 2, 'numero': 'singular'},
            'él': {'persona': 3, 'numero': 'singular'},
            'ella': {'persona': 3, 'numero': 'singular'},
            'ello': {'persona': 3, 'numero': 'singular'},
            'nosotros': {'persona': 1, 'numero': 'plural'},
            'nosotras': {'persona': 1, 'numero': 'plural'},
            'vosotros': {'persona': 2, 'numero': 'plural'},
            'vosotras': {'persona': 2, 'numero': 'plural'},
            'ellos': {'persona': 3, 'numero': 'plural'},
            'ellas': {'persona': 3, 'numero': 'plural'}
        }
        
        # Pronombres de objeto (leísmo, laísmo, loísmo)
        self.pronombres_objeto = {
            'le': {'caso': 'dativo', 'genero': 'ambiguo'},
            'les': {'caso': 'dativo', 'genero': 'ambiguo'},
            'la': {'caso': 'acusativo', 'genero': 'femenino'},
            'las': {'caso': 'acusativo', 'genero': 'femenino'},
            'lo': {'caso': 'acusativo', 'genero': 'masculino'},
            'los': {'caso': 'acusativo', 'genero': 'masculino'},
            'me': {'caso': 'reflexivo', 'persona': 1},
            'te': {'caso': 'reflexivo', 'persona': 2},
            'se': {'caso': 'reflexivo', 'persona': 3}
        }
        
        # Preposiciones y sus usos problemáticos
        self.preposiciones_problematicas = {
            r'de que(?!\s+[aeiouáéíóú])': {'correcto': 'que', 'explicacion': 'Dequeísmo: "de que" usado incorrectamente'},
            r'que(?!\s+[aeiouáéíóú])': {'correcto': 'de que', 'explicacion': 'Queísmo: falta la preposición "de"'},
            r'en base a': {'correcto': 'con base en', 'explicacion': 'Uso incorrecto de "en base a"'},
            r'de acuerdo a': {'correcto': 'de acuerdo con', 'explicacion': 'Uso incorrecto de "de acuerdo a"'}
        }
        
        # Cargar datos
        self.cargar_diccionario()
        self._inicializar_diccionarios_default()
        self._inicializar_verbos()
    
    def _inicializar_diccionarios_default(self):
        """Diccionarios por defecto"""
        if not self.sustantivos['masculino'] and not self.sustantivos['femenino']:
            sustantivos_default = {
                'masculino': ['perro', 'gato', 'libro', 'sol', 'coche', 'árbol', 'teléfono',
                             'ordenador', 'cuaderno', 'lápiz', 'zapato', 'vaso', 'plato',
                             'puente', 'edificio', 'problema', 'día', 'mes', 'año', 'trabajo',
                             'camino', 'cielo', 'mar', 'amor', 'tiempo', 'dinero', 'niño',
                             'hombre', 'señor', 'amigo', 'profesor', 'médico', 'estudiante'],
                'femenino': ['casa', 'mesa', 'flor', 'luna', 'ventana', 'silla', 'puerta',
                            'mano', 'noche', 'tarde', 'semana', 'ciudad', 'escuela',
                            'biblioteca', 'computadora', 'música', 'canción', 'película',
                            'playa', 'montaña', 'alegría', 'tristeza', 'vida', 'muerte',
                            'niña', 'mujer', 'señora', 'amiga', 'profesora', 'médica', 'estudiante']
            }
            
            adjetivos_default = {
                'masculino': ['bonito', 'feo', 'grande', 'pequeño', 'rojo', 'azul', 'verde',
                             'interesante', 'difícil', 'fácil', 'rápido', 'lento', 'nuevo',
                             'viejo', 'bueno', 'malo', 'alto', 'bajo', 'largo', 'corto',
                             'inteligente', 'amable', 'fuerte', 'débil', 'joven', 'viejo'],
                'femenino': ['bonita', 'fea', 'grande', 'pequeña', 'roja', 'azul', 'verde',
                            'interesante', 'difícil', 'fácil', 'rápida', 'lenta', 'nueva',
                            'vieja', 'buena', 'mala', 'alta', 'baja', 'larga', 'corta',
                            'inteligente', 'amable', 'fuerte', 'débil', 'joven', 'vieja']
            }
            
            for genero in ['masculino', 'femenino']:
                self.sustantivos[genero].update(sustantivos_default[genero])
                self.adjetivos[genero].update(adjetivos_default[genero])
            
            self.guardar_diccionario()
    
    def _inicializar_verbos(self):
        """Inicializa conjugaciones verbales comunes"""
        self.verbos = {
            'ser': {
                'yo': 'soy', 'tú': 'eres', 'él': 'es', 'ella': 'es',
                'nosotros': 'somos', 'vosotros': 'sois', 'ellos': 'son',
                'infinitivo': 'ser'
            },
            'estar': {
                'yo': 'estoy', 'tú': 'estás', 'él': 'está', 'ella': 'está',
                'nosotros': 'estamos', 'vosotros': 'estáis', 'ellos': 'están',
                'infinitivo': 'estar'
            },
            'tener': {
                'yo': 'tengo', 'tú': 'tienes', 'él': 'tiene', 'ella': 'tiene',
                'nosotros': 'tenemos', 'vosotros': 'tenéis', 'ellos': 'tienen',
                'infinitivo': 'tener'
            },
            'haber': {
                'yo': 'he', 'tú': 'has', 'él': 'ha', 'ella': 'ha',
                'nosotros': 'hemos', 'vosotros': 'habéis', 'ellos': 'han',
                'infinitivo': 'haber'
            },
            'ir': {
                'yo': 'voy', 'tú': 'vas', 'él': 'va', 'ella': 'va',
                'nosotros': 'vamos', 'vosotros': 'vais', 'ellos': 'van',
                'infinitivo': 'ir'
            },
            'hacer': {
                'yo': 'hago', 'tú': 'haces', 'él': 'hace', 'ella': 'hace',
                'nosotros': 'hacemos', 'vosotros': 'hacéis', 'ellos': 'hacen',
                'infinitivo': 'hacer'
            },
            'decir': {
                'yo': 'digo', 'tú': 'dices', 'él': 'dice', 'ella': 'dice',
                'nosotros': 'decimos', 'vosotros': 'decís', 'ellos': 'dicen',
                'infinitivo': 'decir'
            }
        }
        
        # Reglas para detectar conjugaciones
        self.terminaciones_verbales = {
            'ar': {'yo': 'o', 'tú': 'as', 'él': 'a', 'nosotros': 'amos', 'vosotros': 'áis', 'ellos': 'an'},
            'er': {'yo': 'o', 'tú': 'es', 'él': 'e', 'nosotros': 'emos', 'vosotros': 'éis', 'ellos': 'en'},
            'ir': {'yo': 'o', 'tú': 'es', 'él': 'e', 'nosotros': 'imos', 'vosotros': 'ís', 'ellos': 'en'}
        }
    
    # ============ FUNCIONES DE ANÁLISIS LINGÜÍSTICO ============
    
    def _limpiar_palabra(self, palabra: str) -> str:
        """Elimina signos de puntuación"""
        return palabra.strip('.,;:!¿?¡()[]{}"\'').lower()
    
    def _obtener_genero_sustantivo(self, sustantivo: str) -> str:
        """Determina el género de un sustantivo"""
        sustantivo = self._limpiar_palabra(sustantivo)
        
        if sustantivo in self.excepciones:
            return self.excepciones[sustantivo]
        
        if sustantivo in self.sustantivos['masculino']:
            return 'masculino'
        elif sustantivo in self.sustantivos['femenino']:
            return 'femenino'
        
        # Reglas básicas
        if sustantivo.endswith('a') and not sustantivo.endswith('ista') and not sustantivo.endswith('ema'):
            return 'femenino'
        elif sustantivo.endswith('o'):
            return 'masculino'
        elif sustantivo.endswith('e') or sustantivo.endswith('ista'):
            return 'ambiguo'
        
        return 'desconocido'
    
    def _obtener_genero_adjetivo(self, adjetivo: str) -> str:
        """Determina el género de un adjetivo"""
        adjetivo = self._limpiar_palabra(adjetivo)
        
        if adjetivo in self.adjetivos['masculino']:
            return 'masculino'
        elif adjetivo in self.adjetivos['femenino']:
            return 'femenino'
        
        if adjetivo.endswith('o'):
            return 'masculino'
        elif adjetivo.endswith('a'):
            return 'femenino'
        else:
            return 'invariable'
    
    def _obtener_numero(self, palabra: str) -> str:
        """Determina si una palabra es singular o plural"""
        palabra = self._limpiar_palabra(palabra)
        
        if palabra.endswith('s') and not palabra.endswith('ás') and not palabra.endswith('és') and not palabra.endswith('ís') and not palabra.endswith('ós') and not palabra.endswith('ús'):
            if len(palabra) > 2 and palabra[-2] not in 'áéíóú':
                return 'plural'
        return 'singular'
    
    def _obtener_persona_verbo(self, verbo: str, sujeto: Optional[str] = None) -> Optional[Dict]:
        """Determina la persona y número de un verbo conjugado"""
        verbo = self._limpiar_palabra(verbo)
        
        # Buscar en diccionario de verbos
        for infinitivo, conjugaciones in self.verbos.items():
            for persona, forma in conjugaciones.items():
                if persona != 'infinitivo' and forma == verbo:
                    pronombre_info = self.pronombres.get(persona, {})
                    return {
                        'persona': pronombre_info.get('persona', 3),
                        'numero': pronombre_info.get('numero', 'singular'),
                        'infinitivo': infinitivo,
                        'forma': forma
                    }
        
        # Intentar detectar por terminación (muy básico)
        if verbo.endswith('o'):
            return {'persona': 1, 'numero': 'singular', 'infinitivo': 'desconocido', 'forma': verbo}
        elif verbo.endswith('as') or verbo.endswith('es'):
            return {'persona': 2, 'numero': 'singular', 'infinitivo': 'desconocido', 'forma': verbo}
        elif verbo.endswith('a') or verbo.endswith('e'):
            return {'persona': 3, 'numero': 'singular', 'infinitivo': 'desconocido', 'forma': verbo}
        elif verbo.endswith('amos') or verbo.endswith('emos') or verbo.endswith('imos'):
            return {'persona': 1, 'numero': 'plural', 'infinitivo': 'desconocido', 'forma': verbo}
        elif verbo.endswith('áis') or verbo.endswith('éis') or verbo.endswith('ís'):
            return {'persona': 2, 'numero': 'plural', 'infinitivo': 'desconocido', 'forma': verbo}
        elif verbo.endswith('an') or verbo.endswith('en'):
            return {'persona': 3, 'numero': 'plural', 'infinitivo': 'desconocido', 'forma': verbo}
        
        return None
    
    # ============ DETECTORES DE ERRORES ============
    
    def detectar_articulo_sustantivo(self, texto: str) -> List[Dict]:
        """Detecta discordancias entre artículo y sustantivo"""
        errores = []
        patron = r'\b(?:el|la|los|las|un|una|unos|unas)\s+(\w+)(?:\s+(\w+))?'
        
        for match in re.finditer(patron, texto.lower()):
            articulo_completo = match.group(0)
            articulo = articulo_completo.split()[0]
            
            info_articulo = self.articulos.get(articulo)
            if not info_articulo:
                continue
            
            # Buscar el sustantivo real
            palabras_despues = match.group(0).split()[1:]
            sustantivo_encontrado = None
            
            for palabra in palabras_despues:
                palabra_limpia = self._limpiar_palabra(palabra)
                genero_sust = self._obtener_genero_sustantivo(palabra_limpia)
                if genero_sust != 'desconocido' and genero_sust != 'ambiguo':
                    sustantivo_encontrado = palabra_limpia
                    break
            
            if not sustantivo_encontrado:
                sustantivo_encontrado = self._limpiar_palabra(palabras_despues[0])
            
            genero_sustantivo = self._obtener_genero_sustantivo(sustantivo_encontrado)
            numero_sustantivo = self._obtener_numero(sustantivo_encontrado)
            
            if genero_sustantivo not in ['desconocido', 'ambiguo']:
                # Verificar género
                if info_articulo['genero'] != genero_sustantivo:
                    sugerencia = self._sugerir_articulo_correcto(articulo, sustantivo_encontrado, genero_sustantivo, numero_sustantivo)
                    errores.append({
                        'tipo': 'artículo-sustantivo',
                        'categoria': 'género',
                        'original': articulo_completo,
                        'sugerencia': sugerencia,
                        'explicacion': f"El artículo '{articulo}' es {info_articulo['genero']} pero '{sustantivo_encontrado}' es {genero_sustantivo}"
                    })
                # Verificar número
                elif info_articulo['numero'] != numero_sustantivo:
                    sugerencia = self._sugerir_articulo_correcto(articulo, sustantivo_encontrado, genero_sustantivo, numero_sustantivo)
                    errores.append({
                        'tipo': 'artículo-sustantivo',
                        'categoria': 'número',
                        'original': articulo_completo,
                        'sugerencia': sugerencia,
                        'explicacion': f"El artículo '{articulo}' es {info_articulo['numero']} pero '{sustantivo_encontrado}' es {numero_sustantivo}"
                    })
        
        return errores
    
    def detectar_sustantivo_adjetivo(self, texto: str) -> List[Dict]:
        """Detecta discordancias entre sustantivo y adjetivo"""
        errores = []
        
        # Dividir en oraciones
        oraciones = re.split(r'[.!?]\s+', texto)
        
        for oracion in oraciones:
            palabras = re.findall(r'\b\w+\b', oracion.lower())
            
            for i in range(len(palabras) - 1):
                palabra_actual = palabras[i]
                palabra_siguiente = palabras[i + 1]
                
                genero_actual = self._obtener_genero_sustantivo(palabra_actual)
                if genero_actual in ['desconocido', 'ambiguo']:
                    continue
                
                genero_siguiente = self._obtener_genero_adjetivo(palabra_siguiente)
                if genero_siguiente == 'invariable':
                    continue
                
                if genero_siguiente != 'desconocido' and genero_actual != genero_siguiente:
                    numero_actual = self._obtener_numero(palabra_actual)
                    numero_siguiente = self._obtener_numero(palabra_siguiente)
                    
                    if numero_actual == numero_siguiente:
                        sugerencia = self._sugerir_adjetivo_correcto(palabra_siguiente, genero_actual)
                        errores.append({
                            'tipo': 'sustantivo-adjetivo',
                            'categoria': 'género',
                            'original': f"{palabra_actual} {palabra_siguiente}",
                            'sugerencia': f"{palabra_actual} {sugerencia}",
                            'explicacion': f"El sustantivo '{palabra_actual}' es {genero_actual} pero el adjetivo '{palabra_siguiente}' parece ser {genero_siguiente}"
                        })
        
        return errores
    
    def detectar_sujeto_verbo(self, texto: str) -> List[Dict]:
        """Detecta discordancias entre sujeto y verbo"""
        errores = []
        
        # Patrón para sujeto + verbo cercano
        patron_sujeto_verbo = r'\b(yo|tú|vos|él|ella|ello|nosotros|nosotras|vosotros|vosotras|ellos|ellas|(\w+))\s+(\w+)\b'
        
        for match in re.finditer(patron_sujeto_verbo, texto.lower()):
            sujeto = match.group(1)
            verbo = match.group(3)
            
            # Obtener información del sujeto
            if sujeto in self.pronombres:
                info_sujeto = self.pronombres[sujeto]
            else:
                # Si no es pronombre, intentar determinar género por el artículo
                info_sujeto = {'persona': 3, 'numero': self._obtener_numero(sujeto)}
            
            # Obtener información del verbo
            info_verbo = self._obtener_persona_verbo(verbo, sujeto)
            
            if info_verbo and info_verbo['persona']:
                if info_sujeto['persona'] != info_verbo['persona']:
                    errores.append({
                        'tipo': 'sujeto-verbo',
                        'categoria': 'persona',
                        'original': f"{sujeto} {verbo}",
                        'sugerencia': f"Revisar concordancia de persona entre '{sujeto}' y '{verbo}'",
                        'explicacion': f"El sujeto es {self._persona_a_texto(info_sujeto['persona'])} pero el verbo está conjugado en {self._persona_a_texto(info_verbo['persona'])}"
                    })
                elif info_sujeto['numero'] != info_verbo['numero']:
                    errores.append({
                        'tipo': 'sujeto-verbo',
                        'categoria': 'número',
                        'original': f"{sujeto} {verbo}",
                        'sugerencia': f"Revisar concordancia de número entre '{sujeto}' y '{verbo}'",
                        'explicacion': f"El sujeto es {info_sujeto['numero']} pero el verbo está en {info_verbo['numero']}"
                    })
        
        return errores
    
    def detectar_pronombres(self, texto: str) -> List[Dict]:
        """Detecta errores de leísmo, laísmo, loísmo"""
        errores = []
        
        # Patrones para detectar le/la/lo incorrectos
        # Leísmo (usar "le" para objeto directo masculino)
        patron_leismo = r'\ble\s+([^,\s]+)\b'
        for match in re.finditer(patron_leismo, texto.lower()):
            verbo = match.group(1)
            # Verificar si el verbo es transitivo (debería usar "lo")
            errores.append({
                'tipo': 'pronombres',
                'categoria': 'leísmo',
                'original': match.group(0),
                'sugerencia': f"lo {verbo}",
                'explicacion': "Posible leísmo: 'le' usado como objeto directo. La forma correcta para complemento directo masculino es 'lo'"
            })
            break  # Solo detectar uno por ahora
        
        # Laísmo (usar "la" para objeto indirecto)
        patron_laismo = r'\bla\s+(\w+)\s+(a\s+él|a\s+ella)'
        for match in re.finditer(patron_laismo, texto.lower()):
            errores.append({
                'tipo': 'pronombres',
                'categoria': 'laísmo',
                'original': match.group(0),
                'sugerencia': match.group(0).replace('la', 'le', 1),
                'explicacion': "Posible laísmo: 'la' usado como objeto indirecto. Para complemento indirecto se usa 'le'"
            })
        
        return errores
    
    def detectar_preposiciones(self, texto: str) -> List[Dict]:
        """Detecta errores comunes con preposiciones"""
        errores = []
        
        for patron, info in self.preposiciones_problematicas.items():
            for match in re.finditer(patron, texto.lower()):
                errores.append({
                    'tipo': 'preposiciones',
                    'categoria': 'dequeísmo' if 'de que' in patron else 'queísmo',
                    'original': match.group(0),
                    'sugerencia': info['correcto'],
                    'explicacion': info['explicacion']
                })
        
        return errores
    
    def _persona_a_texto(self, persona: int) -> str:
        """Convierte número de persona a texto"""
        return {1: 'primera persona', 2: 'segunda persona', 3: 'tercera persona'}.get(persona, 'desconocida')
    
    def _sugerir_articulo_correcto(self, articulo: str, sustantivo: str, genero: str, numero: str) -> str:
        """Sugiere el artículo correcto"""
        mapa_articulos = {
            ('masculino', 'singular'): 'el',
            ('masculino', 'plural'): 'los',
            ('femenino', 'singular'): 'la',
            ('femenino', 'plural'): 'las'
        }
        
        # Casos especiales como "el agua"
        if sustantivo in ['agua', 'águila', 'hacha'] and genero == 'femenino' and numero == 'singular':
            return f"el {sustantivo}"
        
        articulo_correcto = mapa_articulos.get((genero, numero), articulo)
        return f"{articulo_correcto} {sustantivo}"
    
    def _sugerir_adjetivo_correcto(self, adjetivo: str, genero_deseado: str) -> str:
        """Sugiere la forma correcta del adjetivo"""
        if genero_deseado == 'masculino':
            if adjetivo.endswith('a'):
                return adjetivo[:-1] + 'o'
        else:  # femenino
            if adjetivo.endswith('o'):
                return adjetivo[:-1] + 'a'
        return adjetivo
    
    def detectar_todos(self, texto: str) -> List[Dict]:
        """Detecta todos los tipos de errores"""
        errores = []
        errores.extend(self.detectar_articulo_sustantivo(texto))
        errores.extend(self.detectar_sustantivo_adjetivo(texto))
        errores.extend(self.detectar_sujeto_verbo(texto))
        errores.extend(self.detectar_pronombres(texto))
        errores.extend(self.detectar_preposiciones(texto))
        return errores
    
    def corregir(self, texto: str) -> Tuple[str, List[Dict]]:
        """Corrige automáticamente los errores detectados"""
        errores = self.detectar_todos(texto)
        texto_corregido = texto
        
        # Aplicar correcciones en orden inverso para no afectar índices
        for error in reversed(errores):
            if 'original' in error and 'sugerencia' in error:
                texto_corregido = texto_corregido.replace(error['original'], error['sugerencia'], 1)
        
        return texto_corregido, errores
    
    # ============ PERSISTENCIA ============
    
    def guardar_historial(self, texto_original: str, texto_corregido: str, errores: List[Dict]):
        """Guarda el historial de correcciones"""
        historial = []
        
        if os.path.exists(self.archivo_historial):
            with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                historial = json.load(f)
        
        entrada = {
            'fecha': datetime.now().isoformat(),
            'texto_original': texto_original,
            'texto_corregido': texto_corregido,
            'errores_detectados': len(errores),
            'detalle_errores': errores
        }
        historial.append(entrada)
        
        with open(self.archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    
    def cargar_diccionario(self):
        """Carga diccionarios desde archivo JSON"""
        if os.path.exists(self.archivo_diccionario):
            try:
                with open(self.archivo_diccionario, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    self.sustantivos = {k: set(v) for k, v in datos.get('sustantivos', {}).items()}
                    self.adjetivos = {k: set(v) for k, v in datos.get('adjetivos', {}).items()}
                    self.excepciones = datos.get('excepciones', self.excepciones)
            except Exception as e:
                print(f"⚠️ Error al cargar diccionario: {e}")
    
    def guardar_diccionario(self):
        """Guarda diccionarios en archivo JSON"""
        datos = {
            'sustantivos': {k: list(v) for k, v in self.sustantivos.items()},
            'adjetivos': {k: list(v) for k, v in self.adjetivos.items()},
            'excepciones': self.excepciones
        }
        with open(self.archivo_diccionario, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    
    def agregar_palabra(self, palabra: str, tipo: str, genero: str):
        """Agrega una palabra al diccionario"""
        palabra = palabra.lower()
        if tipo == 'sustantivo':
            self.sustantivos[genero].add(palabra)
        elif tipo == 'adjetivo':
            self.adjetivos[genero].add(palabra)
        else:
            return
        
        self.guardar_diccionario()
        print(f"✓ Añadido '{palabra}' como {tipo} {genero}")
    
    # ============ REPORTES ============
    
    def reporte(self, texto: str, guardar: bool = True) -> Tuple[str, List[Dict]]:
        """Genera un reporte completo"""
        texto_corregido, errores = self.corregir(texto)
        
        print(f"\n{'='*60}")
        print(f"🔮 {self.nombre} {self.version}")
        print(f"   {self.lema}")
        print(f"{'='*60}\n")
        
        if not errores:
            print("✅ ¡No se detectaron errores! Todo en armonía.\n")
        else:
            # Agrupar por tipo
            tipos = {}
            for error in errores:
                tipo = error['tipo']
                if tipo not in tipos:
                    tipos[tipo] = []
                tipos[tipo].append(error)
            
            print(f"🔍 Se detectaron {len(errores)} error(es):\n")
            
            for tipo, lista_errores in tipos.items():
                print(f"📌 {tipo.upper()} ({len(lista_errores)}):")
                for i, error in enumerate(lista_errores, 1):
                    print(f"   {i}. ❌ '{error['original']}'")
                    print(f"      ✨ Sugerencia: {error['sugerencia']}")
                    print(f"      💡 {error['explicacion']}\n")
            
            print(f"📝 Original: {texto}")
            print(f"✨ Corregido: {texto_corregido}\n")
        
        if guardar and errores:
            self.guardar_historial(texto, texto_corregido, errores)
        
        return texto_corregido, errores
    
    # ============ INTERFAZ WEB ============
    
    def iniciar_web(self, puerto=5000):
        """Inicia la interfaz web"""
        if not FLASK_DISPONIBLE:
            print("❌ Flask no está instalado. No se puede iniciar la interfaz web.")
            print("   Instálalo con: pip install flask")
            return
        
        app = Flask(__name__)
        
        # HTML template
        template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>ConcordIA - Corrector Gramatical</title>
            <meta charset="UTF-8">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    max-width: 900px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                .header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }
                .header p {
                    font-size: 1.1em;
                    opacity: 0.9;
                }
                .content {
                    padding: 30px;
                }
                textarea {
                    width: 100%;
                    padding: 15px;
                    font-size: 16px;
                    font-family: monospace;
                    border: 2px solid #ddd;
                    border-radius: 10px;
                    resize: vertical;
                    min-height: 150px;
                }
                button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    font-size: 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    margin-top: 15px;
                    transition: transform 0.2s;
                }
                button:hover {
                    transform: translateY(-2px);
                }
                .results {
                    margin-top: 30px;
                    padding: 20px;
                    background: #f7f7f7;
                    border-radius: 10px;
                    display: none;
                }
                .error-item {
                    background: white;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #ff6b6b;
                    border-radius: 8px;
                }
                .corregido {
                    background: #d4edda;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 20px;
                }
                .badge {
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 5px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .badge-genero { background: #ff6b6b; color: white; }
                .badge-numero { background: #4ecdc4; color: white; }
                .loading {
                    text-align: center;
                    padding: 20px;
                    display: none;
                }
                .stats {
                    margin-top: 20px;
                    padding: 15px;
                    background: #e3f2fd;
                    border-radius: 8px;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔮 ConcordIA 3.0</h1>
                    <p>"Donde el artículo encuentra al sustantivo que merece"</p>
                </div>
                <div class="content">
                    <textarea id="texto" placeholder="Escribe aquí tu texto en español...">El casa bonito es muy grande. Los niño juega en el parque.</textarea>
                    <button onclick="corregir()">🔍 Corregir texto</button>
                    <div class="loading" id="loading">Procesando...</div>
                    <div class="results" id="results"></div>
                </div>
            </div>
            
            <script>
                async function corregir() {
                    const texto = document.getElementById('texto').value;
                    if (!texto.trim()) return;
                    
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('results').style.display = 'none';
                    
                    try {
                        const response = await fetch('/corregir', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({texto: texto})
                        });
                        const data = await response.json();
                        mostrarResultados(data);
                    } catch (error) {
                        console.error('Error:', error);
                    } finally {
                        document.getElementById('loading').style.display = 'none';
                    }
                }
                
                function mostrarResultados(data) {
                    const resultsDiv = document.getElementById('results');
                    let html = '<h3>📊 Resultados del análisis</h3>';
                    
                    if (data.errores.length === 0) {
                        html += '<div style="background: #d4edda; padding: 15px; border-radius: 8px;">✅ ¡No se detectaron errores! Todo en armonía.</div>';
                    } else {
                        html += `<p>🔍 Se detectaron ${data.errores.length} error(es):</p>`;
                        for (let error of data.errores) {
                            const badgeClass = error.categoria === 'género' ? 'badge-genero' : 'badge-numero';
                            html += `
                                <div class="error-item">
                                    <span class="badge ${badgeClass}">${error.tipo} - ${error.categoria}</span>
                                    <strong>❌ ${error.original}</strong><br>
                                    ✨ Sugerencia: ${error.sugerencia}<br>
                                    💡 ${error.explicacion}
                                </div>
                            `;
                        }
                        html += `
                            <div class="corregido">
                                <strong>✨ Texto corregido:</strong><br>
                                ${data.texto_corregido}
                            </div>
                        `;
                    }
                    
                    html += `<div class="stats">📈 ConcordIA ${data.version} | Análisis completado</div>`;
                    resultsDiv.innerHTML = html;
                    resultsDiv.style.display = 'block';
                }
            </script>
        </body>
        </html>
        '''
        
        @app.route('/')
        def index():
            return render_template_string(template)
        
        @app.route('/corregir', methods=['POST'])
        def corregir_endpoint():
            data = request.json
            texto = data.get('texto', '')
            texto_corregido, errores = self.corregir(texto)
            return jsonify({
                'version': self.version,
                'texto_original': texto,
                'texto_corregido': texto_corregido,
                'errores': errores,
                'total_errores': len(errores)
            })
        
        print(f"\n🌐 Servidor web iniciado en http://localhost:{puerto}")
        print("   Presiona Ctrl+C para detener\n")
        app.run(debug=False, port=puerto)
    
    # ============ MODO INTERACTIVO ============
    
    def modo_interactivo(self):
        """Modo interactivo por consola"""
        print(f"\n{'='*60}")
        print(f"🔮 {self.nombre} {self.version} - Modo Interactivo")
        print(f"   {self.lema}")
        print(f"{'='*60}")
        print("\nComandos especiales:")
        print("  :salir      - Terminar sesión")
        print("  :web        - Iniciar interfaz web")
        print("  :historial  - Ver historial")
        print("  :agregar    - Agregar palabras")
        print("  :stats      - Ver estadísticas")
        print("-" * 60)
        
        while True:
            print("\n✏️ Escribe una frase (o comando):")
            entrada = input("> ").strip()
            
            if entrada.lower() == ':salir':
                print("👋 ¡Hasta luego!")
                break
            elif entrada.lower() == ':web':
                self.iniciar_web()
            elif entrada.lower() == ':historial':
                self.ver_historial()
            elif entrada.lower() == ':agregar':
                self._interactivo_agregar()
            elif entrada.lower() == ':stats':
                self._mostrar_stats()
            elif entrada:
                self.reporte(entrada)
    
    def ver_historial(self):
        """Muestra el historial"""
        if os.path.exists(self.archivo_historial):
            with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                historial = json.load(f)
            
            if not historial:
                print("📭 Historial vacío")
                return
            
            print(f"\n📚 HISTORIAL ({len(historial)} entradas)")
            for entry in historial[-5:]:
                fecha = entry['fecha'][:16].replace('T', ' ')
                print(f"  {fecha} - {entry['errores_detectados']} errores")
        else:
            print("📭 Sin historial")
    
    def _interactivo_agregar(self):
        """Agrega palabras interactivamente"""
        print("\n📝 Agregar palabra:")
        palabra = input("Palabra: ").strip().lower()
        tipo = input("Tipo (sustantivo/adjetivo): ").strip().lower()
        genero = input("Género (masculino/femenino): ").strip().lower()
        
        if tipo in ['sustantivo', 'adjetivo'] and genero in ['masculino', 'femenino']:
            self.agregar_palabra(palabra, tipo, genero)
        else:
            print("⚠️ Datos inválidos")
    
    def _mostrar_stats(self):
        """Muestra estadísticas"""
        print(f"\n📊 ESTADÍSTICAS")
        print(f"  Sustantivos: {len(self.sustantivos['masculino']) + len(self.sustantivos['femenino'])}")
        print(f"    - Masculinos: {len(self.sustantivos['masculino'])}")
        print(f"    - Femeninos: {len(self.sustantivos['femenino'])}")
        print(f"  Adjetivos: {len(self.adjetivos['masculino']) + len(self.adjetivos['femenino'])}")
        print(f"  Verbos en diccionario: {len(self.verbos)}")


# ============ EJECUCIÓN PRINCIPAL ============

def ejecutar_pruebas():
    """Ejecuta pruebas completas"""
    concordia = ConcordIA()
    
    casos_prueba = [
        "El casa bonito es grande.",
        "Los niño juega en el parque.",
        "La problema es difícil de resolver.",
        "Yo hace la tarea todos los días.",
        "Le dije a él que venga.",
        "No sé de que hablas.",
        "El agua fría está buena."
    ]
    
    print("\n🧪 CONCORDIA 3.0 - PRUEBAS COMPLETAS\n")
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📄 Caso {i}: {caso}")
        concordia.reporte(caso, guardar=False)
        print("-" * 60)


if __name__ == "__main__":
    concordia = ConcordIA()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🔮 CONCORDIA 3.0 - Corrector Gramatical de Español    ║
║                                                          ║
║   "Donde el artículo encuentra al sustantivo que merece" ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("Elige modo de ejecución:")
    print("  1. Modo interactivo (consola)")
    print("  2. Servidor web")
    print("  3. Ejecutar pruebas")
    
    opcion = input("\nOpción (1/2/3): ").strip()
    
    if opcion == '1':
        concordia.modo_interactivo()
    elif opcion == '2':
        concordia.iniciar_web()
    else:
        ejecutar_pruebas()