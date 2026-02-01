# Excalidraw JSON Schema Reference

An `.excalidraw` file is a JSON object with the following top-level structure:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [ ... ],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": null
  }
}
```

## Element Types

### Common Properties (All Elements)
All elements share these fields:
- `id`: string (unique, e.g., "node-1")
- `x`: number (x position)
- `y`: number (y position)
- `width`: number
- `height`: number
- `angle`: number (usually 0)
- `strokeColor`: string (hex code, e.g., "#000000")
- `backgroundColor`: string (hex code, e.g., "#transparent")
- `fillStyle`: "hachure" | "cross-hatch" | "solid"
- `strokeWidth`: number (1 or 2)
- `strokeStyle`: "solid" | "dashed" | "dotted"
- `roughness`: number (0-2, 1 is standard hand-drawn look)
- `opacity`: number (100)
- `groupIds`: []
- `roundness`: { "type": 3 } (for rounded corners) or null
- `seed`: number (random integer)
- `version`: number (incrementing)
- `versionNonce`: number (random integer)
- `isDeleted`: false
- `boundElements`: [{ "id": "arrow-id", "type": "arrow" }] (for connecting arrows)

### 1. Rectangle (Container/Box)
```json
{
  "type": "rectangle",
  "label": { "text": "Label inside?" } // NOTE: Excalidraw uses separate "text" elements bound to containers usually, but simple rects just exist.
}
```
*Note: To put text 'inside' a box, creating a separate "text" element is often safer/standard, centered on the rect.*

### 2. Ellipse (Start/End nodes)
```json
{
  "type": "ellipse"
}
```

### 3. Diamond (Decision)
```json
{
  "type": "diamond"
}
```

### 4. Text (Labels)
```json
{
  "type": "text",
  "text": "Actual content\nNew line",
  "fontSize": 20,
  "fontFamily": 1, // 1: Virgil (Hand), 2: Helvetica, 3: Cascadia
  "textAlign": "center", // "left", "center", "right"
  "verticalAlign": "middle"
}
```

### 5. Arrow (Connectors)
Arrows connect two elements.
```json
{
  "type": "arrow",
  "points": [[0, 0], [100, 50]], // Relative points from x,y. [0,0] is the start.
  "startBinding": { "elementId": "node-1", "focus": 0.5, "gap": 1 },
  "endBinding": { "elementId": "node-2", "focus": 0.5, "gap": 1 }
}
```
*Tip: If binding is too complex to calc, just placing start/end points near the center of nodes works visualy.*

## Layout Strategy (Mental Model)

For a "Why, What, How" tree:
1. **Why (Root)**: Top or Left.
2. **What (Children)**: Level 2.
3. **How (Grandchildren)**: Level 3.

**User Journey**:
Linear flow: Step 1 -> Arrow -> Step 2 -> Arrow -> Step 3.
