# 🎨 UI_UX_STYLE_GUIDE — Guía de interfaz

> **Reglas inquebrantables de UI/UX para todos los sistemas del proyecto.**
> Diseñado para **móvil (60% de la audiencia Fortnite)** y **usuario TDAH-friendly** (mucha info simultánea).

---

## 🧭 Índice

1. [Filosofía visual](#1-filosofía-visual)
2. [Paleta de colores](#2-paleta-de-colores)
3. [Tipografía](#3-tipografía)
4. [Espaciado y tamaños](#4-espaciado-y-tamaños)
5. [Mobile-first rules](#5-mobile-first-rules)
6. [Activity Log UI (specs)](#6-activity-log-ui-specs)
7. [Rarezas: colores y efectos](#7-rarezas-colores-y-efectos)
8. [Notificaciones y popups](#8-notificaciones-y-popups)
9. [Iconografía](#9-iconografía)
10. [Animaciones y feedback](#10-animaciones-y-feedback)
11. [Estados de error y vacío](#11-estados-de-error-y-vacío)
12. [Checklist de UI antes de marcar Done](#12-checklist-de-ui-antes-de-marcar-done)

---

## 1. Filosofía visual

### 1.1 Principios

1. **Claridad sobre belleza**: cada elemento tiene un propósito legible.
2. **Móvil first, desktop second**: si funciona en 380px, funciona en todo.
3. **TDAH-friendly**: un foco visual a la vez. Sin animaciones distractoras de fondo.
4. **Accesible**: contraste alto, tap targets grandes, fuentes legibles.
5. **Consistencia obsesiva**: mismo color = mismo significado en todo el juego.

### 1.2 Lo que NO hacemos

- ❌ Animaciones de fondo perpetuas (distraen al TDAH)
- ❌ Texto blanco sobre amarillo o gradientes de bajo contraste
- ❌ Tap targets <44px en móvil
- ❌ 3+ colores primarios compitiendo en una pantalla
- ❌ Iconos sin etiqueta de texto en menús nuevos
- ❌ Pop-ups que tapan el HUD del juego durante combate

---

## 2. Paleta de colores

### 2.1 Colores del sistema

| Rol | Hex | Uso |
|---|---|---|
| **Primary** | `#3B82F6` | Botones principales, links, call-to-action |
| **Primary Dark** | `#1E40AF` | Hover/pressed states |
| **Secondary** | `#8B5CF6` | Botones secundarios, premium accents |
| **Background Main** | `#0F172A` | Fondo principal de UI panels |
| **Background Card** | `#1E293B` | Tarjetas, items en lista |
| **Background Elevated** | `#334155` | Modales sobre cards |
| **Text Primary** | `#F1F5F9` | Texto principal, casi blanco |
| **Text Secondary** | `#CBD5E1` | Texto secundario, descriptions |
| **Text Muted** | `#64748B` | Texto deshabilitado, placeholder |
| **Border** | `#334155` | Bordes de cards, dividers |

### 2.2 Colores semánticos (categorías)

| Rol | Hex | Uso |
|---|---|---|
| **Success / Gain** | `#10B981` | Ganaste algo, +XP, +gold |
| **Warning** | `#F59E0B` | Atención, próximo a expirar |
| **Danger / Loss** | `#EF4444` | Perdiste algo, -gold por muerte |
| **Info** | `#06B6D4` | Mensajes informativos |
| **Event** | `#EC4899` | Live events activos |
| **Rare drop** | `#A855F7` | Encontraste algo raro |

### 2.3 Colores premium

| Rol | Hex | Uso |
|---|---|---|
| **V-Bucks** | `#1E90FF` | Color oficial V-Bucks de Fortnite |
| **Gems** | `#10B981` | Verde esmeralda |
| **Gold (currency)** | `#FCD34D` | Oro brillante |

### 2.4 Reglas de combinación

- **Texto sobre Background Main**: usar Text Primary o Text Secondary.
- **NUNCA** texto Primary sobre Background Card (mismo tono): contraste fail.
- **Tap targets** siempre con borde ≥1px en color Border o Primary.
- **Estados hover/pressed**: bajar 1 nivel en la paleta (Primary → Primary Dark).

---

## 3. Tipografía

### 3.1 Familia de fuentes

UEFN soporta las fuentes built-in de Fortnite. Usar:

- **Display / Títulos**: BurbankBigCondensed-Black (la fuente "épica" de Fortnite)
- **Body / UI**: BurbankSmall-Medium (legible, condensada)
- **Numbers / Stats**: BurbankBigCondensed-Bold (números clavados)

### 3.2 Tamaños

| Rol | Desktop | Móvil | Uso |
|---|---|---|---|
| **Display** | 48px | 36px | Títulos pantalla completa |
| **H1** | 32px | 26px | Headers de paneles |
| **H2** | 24px | 20px | Sub-headers |
| **H3** | 20px | 18px | Títulos de cards |
| **Body** | 16px | 16px | Texto general |
| **Small** | 14px | 14px | Captions, secundarias |
| **Tiny** | 12px | 12px | Labels, time stamps |

**Nunca usar fuente <12px en móvil**. No es legible.

### 3.3 Pesos

- **Black**: títulos, números importantes
- **Bold**: emphasis, labels
- **Medium**: body por defecto
- **Regular**: solo para textos largos descriptivos

### 3.4 Spacing

- **Line height**: 1.4× para body, 1.2× para títulos
- **Letter spacing**: 0 normal, +0.05em en títulos uppercase

---

## 4. Espaciado y tamaños

### 4.1 Sistema de espaciado (8px base)

```
xs:  4px   ← entre elementos relacionados (label + input)
sm:  8px   ← padding interno de pequeños elementos
md:  16px  ← padding estándar de cards
lg:  24px  ← separación entre secciones
xl:  32px  ← márgenes grandes
xxl: 48px  ← separadores mayores
```

### 4.2 Tamaños de componentes

| Componente | Desktop | Móvil |
|---|---|---|
| **Botón primario** | 48×40px (height) | 56×48px |
| **Botón secundario** | 40×32px | 48×40px |
| **Tap target mínimo** | 32×32px | **44×44px** |
| **Icon button** | 40×40px | 48×48px |
| **Card padding** | 16px | 16px |
| **Modal max width** | 600px | 90vw |
| **Input height** | 40px | 48px |

### 4.3 Border radius

- **Botones, inputs**: 8px
- **Cards**: 12px
- **Modales**: 16px
- **Avatars, badges**: 50% (circle)

---

## 5. Mobile-first rules

### 5.1 Reglas duras

1. **Tap targets ≥ 44×44px**. Sin excepciones.
2. **Espacio entre tap targets ≥ 8px**. Anti mis-click.
3. **Layout funciona en 380px width**. Es el mínimo.
4. **Texto legible sin zoom**. Mínimo 14px.
5. **Sin hover states**. Móvil no tiene hover. Usar pressed states.
6. **Scroll vertical**, no horizontal. Excepto carousels específicos.
7. **One-handed reachable**. Botones críticos en zona inferior.

### 5.2 Touch zones

```
┌─────────────────────────────────┐
│ ZONA SUPERIOR (HUD info-only)    │
│ Difícil de alcanzar.             │
├─────────────────────────────────┤
│                                 │
│ ZONA CENTRAL (contenido)         │
│ Lectura, scroll.                 │
│                                 │
├─────────────────────────────────┤
│ ZONA INFERIOR (acciones)         │
│ ✓ Botones críticos aquí          │
│ ✓ Tap targets más grandes        │
└─────────────────────────────────┘
```

### 5.3 Performance móvil

- **No animaciones simultáneas >3 elementos**
- **Sprites siempre con LODs**
- **Texturas UI ≤ 512×512**
- **Atlasses para iconos repetidos**
- **Sin shaders complejos en UI** (procesado de fragments mata fps)

---

## 6. Activity Log UI (specs)

> Sistema crítico, especificado en CONCEPT.md SYS-049.

### 6.1 Layout

```
┌─────────────────────────────┐
│ [esquina inferior-izquierda]│
│                             │
│ ┌─────────────────────┐    │
│ │ +50 Gold (Common)    │ ← │ línea 1 (más reciente)
│ │ Quest "Recoge madera"│   │ línea 2
│ │ Up Level 12!         │   │ línea 3
│ │ Boss "Forest Dragon" │   │ línea 4 (más antigua)
│ └─────────────────────┘    │
│                             │
└─────────────────────────────┘
```

### 6.2 Specs

| Atributo | Valor |
|---|---|
| **Posición** | Esquina inferior-izquierda |
| **Líneas visibles** | 4 |
| **Width** | 320px desktop / 280px móvil |
| **Tipografía** | Body (14px móvil, 16px desktop) |
| **Background** | `#0F172A` con 80% opacity |
| **Border-left** | 4px sólido con color de categoría |
| **Padding** | 12px horizontal, 8px vertical |
| **Auto-fade timing** | Configurable en código (default 5s) |
| **Stack direction** | Más nuevo arriba, más viejo abajo (push down) |
| **Click action** | NO tiene (decisión cerrada) |

### 6.3 Categorías y colores

| Categoría | Border-left color | Icono prefix |
|---|---|---|
| **Gain (gold/items)** | `#10B981` (success) | + |
| **Loss (death/spend)** | `#EF4444` (danger) | - |
| **Quest progress** | `#06B6D4` (info) | ✓ |
| **Level up / progression** | `#3B82F6` (primary) | ↑ |
| **Rare drop / achievement** | `#A855F7` (rare) | ★ |
| **Event / live ops** | `#EC4899` (event) | ⚡ |
| **Warning** | `#F59E0B` (warning) | ⚠ |

### 6.4 Animaciones

- **Entrada**: slide from left + fade in, 200ms
- **Salida**: fade out, 300ms
- **Push down**: cuando llega nueva línea, las viejas desplazan hacia abajo, 150ms

### 6.5 Lo que NO hace el Activity Log

- ❌ NO suena (las notificaciones críticas usan otro sistema con sonido)
- ❌ NO bloquea la pantalla
- ❌ NO se puede clicar
- ❌ NO muestra mensajes de error de sistema (eso es popup)
- ❌ NO muestra cinemáticas o popups grandes

---

## 7. Rarezas: colores y efectos

### 7.1 Tabla de rarezas (consistente con CONCEPT.md SYS-011)

| Rareza | Hex | Glow | Animación |
|---|---|---|---|
| **Common** | `#9CA3AF` (gris) | Sin glow | Estática |
| **Uncommon** | `#22C55E` (verde) | Sin glow | Estática |
| **Rare** | `#3B82F6` (azul) | Glow sutil | Estática |
| **Epic** | `#A855F7` (morado) | Glow medio | Pulse lento |
| **Legendary** | `#F97316` (naranja) | Glow fuerte | Pulse + sparkles |
| **Mythic** | `#EF4444` (rojo) | Glow brillante | Pulse + flames idle |
| **Secret** | `#000000` con border iridiscente | Glow rainbow shifting | Rainbow border animation |
| **Admin** | `#FCD34D` (dorado) | Glow dorado intenso | Crown sparkles + halo |

### 7.2 Aplicación

- **Border**: 2px sólido del color de rareza, 4px en items destacados
- **Background tint**: 10% del color de rareza sobre Background Card
- **Texto del nombre**: usar el color de rareza directamente
- **Iconos de stats**: tint con el color de rareza al pasar tier

### 7.3 Variantes (sub-rareza)

| Variante | Tratamiento visual |
|---|---|
| **Normal** | Color base de rareza |
| **Oro** | Overlay dorado + sparkles dorados |
| **Diamante** | Overlay azul-blanco + reflejo de diamante |
| **Arcoiris** | Background iridiscente shifting |
| **Hacker** (evento) | Glitch effect + scan lines |
| **Lava** (evento) | Particles de lava + emisión naranja |

---

## 8. Notificaciones y popups

### 8.1 Activity Log vs Toast vs Modal

| Tipo | Cuándo usar | Tiempo en pantalla |
|---|---|---|
| **Activity Log** | Eventos rutinarios (gold, XP, quest progress) | Auto-fade 5s |
| **Toast** | Eventos importantes pero no bloqueantes (achievement, daily login) | Auto-fade 3s + sonido |
| **Modal** | Eventos críticos que requieren acción (rebirth confirmation, error, level up) | Hasta cerrar manualmente |
| **Banner** | Anuncios persistentes (evento activo, mantenimiento) | Hasta que termine condición |

### 8.2 Toast

- **Posición**: top center
- **Width**: 320px / 280px móvil
- **Animación entrada**: slide down + fade, 250ms
- **Animación salida**: fade, 300ms
- **Tiene sonido** (corto, no distractivo)

### 8.3 Modal

- **Posición**: centrado
- **Backdrop**: 60% opacity black, click cierra (excepto críticos)
- **Width**: max 600px desktop, 90vw móvil
- **Padding interno**: 24px
- **Cierre con X** en esquina superior-derecha
- **Botón principal abajo**, alineado derecha

---

## 9. Iconografía

### 9.1 Estilo

- **Estilo flat con outline 2px** (no 3D, no skeumórfico)
- **Tamaño**: 24×24px estándar, 32×32px en cards prominentes
- **Color**: usar Text Primary o color semántico según contexto

### 9.2 Iconos clave (referencia)

| Concepto | Icono recomendado |
|---|---|
| Gold | 🪙 (moneda) o icono custom |
| Gems | 💎 |
| V-Bucks | Logo oficial Fortnite |
| Inventory | Mochila |
| Dex | Libro |
| Shop | Carrito o storefront |
| Quest | Pergamino o checkmark |
| Settings | Engranaje |
| Stats | Gráfico de barras |
| Map | Mapa enrollado |

### 9.3 Reglas

- **NUNCA solo iconos sin etiqueta de texto** en menús no familiares
- **OK iconos sin texto** en HUD durante gameplay (ya familiar)
- **Iconos animados solo en CTA principales** (call-to-action), no en lista

---

## 10. Animaciones y feedback

### 10.1 Tiempos estándar

| Acción | Duración |
|---|---|
| **Hover/Pressed feedback** | 100ms |
| **Toast entrance** | 250ms |
| **Modal entrance** | 300ms |
| **Card flip** | 400ms |
| **Lootbox open reveal** | 800ms (build-up) |
| **Level up** | 1500ms (gran fanfare) |
| **Rebirth ceremony** | 3000ms |

### 10.2 Easing

- **Default**: ease-out (más natural)
- **Bounces**: cubic-bezier(0.68, -0.55, 0.27, 1.55)
- **Suave**: ease-in-out

### 10.3 Feedback táctil/sonoro

- **Tap success**: vibración suave + click sound
- **Tap fail (no gold, etc.)**: vibración doble + buzz sound
- **Achievement unlock**: vibración prolongada + fanfare
- **Lootbox open**: build-up audio + reveal sound

### 10.4 Reglas anti-distracción TDAH

- **Sin animaciones de fondo perpetuas** en la UI principal
- **Sin loops de partículas** salvo en items rare+ (y de baja intensidad)
- **Sin auto-rotación** de elementos
- **Sparkles y glow**: limitar a 2-3 elementos en pantalla simultáneamente

---

## 11. Estados de error y vacío

### 11.1 Estado vacío (empty state)

Cuando una lista no tiene contenido (ej: inventario vacío, sin quests activas):

- **Icono grande** ilustrativo (60×60px)
- **Texto explicativo** breve (1 línea)
- **Call-to-action** si aplica ("Empieza tu primera quest")

### 11.2 Estados de error

```
┌─────────────────────────────┐
│ ⚠️ ERROR                     │
│                             │
│ No tienes suficientes gemas. │
│ Necesitas 100, tienes 45.    │
│                             │
│ [Conseguir gemas]  [Cerrar] │
└─────────────────────────────┘
```

**Reglas**:
- **NUNCA silencio** ante un error
- **Mensaje específico** (no "error desconocido")
- **Acción sugerida** si aplica
- **Tono empático**, no robótico

### 11.3 Estados de carga

- **Spinners**: solo si la operación tarda >300ms
- **Skeleton screens**: mejor que spinners para listas
- **Progress bar**: si el tiempo es predecible (descarga, build-up de pity)

---

## 12. Checklist de UI antes de marcar Done

> **DeepSeek y otras IAs ejecutoras: usar este checklist al implementar cualquier UI.**

```
COLORES:
[ ] Uso colores de la paleta (sección 2)
[ ] Contraste suficiente (texto sobre background)
[ ] Color semántico correcto (gain/loss/info/event)
[ ] Color de rareza consistente con SYS-011

TIPOGRAFÍA:
[ ] Tamaños de la sección 3.2
[ ] Pesos de la sección 3.3
[ ] Línea no excede ancho cómodo de lectura

ESPACIADO:
[ ] Sistema 8px aplicado
[ ] Padding interno consistente con sección 4

MÓVIL:
[ ] Tap targets ≥ 44×44px
[ ] Espacio entre tap targets ≥ 8px
[ ] Layout funciona en 380px width
[ ] Texto legible sin zoom
[ ] Sin hover-only states
[ ] Acciones críticas en zona inferior

ACCESIBILIDAD:
[ ] Contraste suficiente
[ ] Iconos con etiqueta de texto en menús
[ ] Estados de error claros
[ ] Estados vacíos no quedan en blanco

CONSISTENCIA:
[ ] Activity Log respeta sección 6
[ ] Notificaciones respetan sección 8
[ ] Animaciones según sección 10
[ ] Sin animaciones perpetuas distractoras

TESTING:
[ ] Probado en Mobile Preview
[ ] FPS ≥ 30 con UI abierta
[ ] No solapa con HUD del juego durante gameplay
```

---

**Fin del documento.**
