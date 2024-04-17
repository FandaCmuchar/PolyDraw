# PolyDraw

Domain specific language for drawing polygons and other geometrical shapes.

# Návrh DSL pro Geometrické Objekty

## 1. Syntaxe
### Definice Geometrických Objektů
- **Polygon**:
  - Víceřádková definice:
    ```dsl
    polygon p1
        body = 0,0 1,0 0,1
        barva = 255,0,0  # Červená v RGB
    ```
  - Jednořádková alternativa:
    ```dsl
    polygon p2: body = (0,0 1,0 0,1) barva = (255,0,0)
    ```

- **Kruh**:
  - Víceřádková definice:
    ```dsl
    kruh k1
        stred = 2,2
        polomer = 1.5
        barva = 0,0,255  # Modrá v RGB
    ```
  - Jednořádková alternativa:
    ```dsl
    kruh k2: stred = (2,2) polomer = (1.5) barva = (0,0,255)
    ```

### Skupiny a Výpočty
- **Skupina Objektů**:
  - Víceřádková definice:
    ```dsl
    skupina g1
        pridat p1 k1
        zobraz
    ```
  - Jednořádková alternativa:
    ```dsl
    skupina g2: pridat (p2 k2) zobraz
    ```

- **Výpočty a Množinové Operace**:
  - Víceřádková definice:
    ```dsl
    vypocet g1
        sjednoceni p1 k1
        prunik p1 k1
        obvod
        obsah
    ```
  - Jednořádková alternativa:
    ```dsl
    vypocet g2: sjednoceni (p2 k2) prunik (p2 k2) obvod obsah
    ```

## 2. Vykreslovací Scénáře
### Definice Scénáře
- **Animace Geometrických Objektů**:
  - Víceřádková definice:
    ```dsl
    scenar animace_ctverce
        objekt = ctverec
        transformace
            rotace = 5  # stupně za krok
            zmenseni = 0.9  # násobek za krok
        krokova_podminka
            max_iterace = 20  # Maximálně 20 kroků
            min_velikost = 0.1  # Nezastavit dokud velikost není menší než 0.1
        vystup = gif  # Uložení výsledku jako GIF
    ```
  - Jednořádková alternativa:
    ```dsl
    scenar animace_ctverce: objekt = (ctverec) transformace = (rotace = 5 zmenseni = 0.9) krokova_podminka = (max_iterace = 20 min_velikost = 0.1) vystup = gif
    ```
