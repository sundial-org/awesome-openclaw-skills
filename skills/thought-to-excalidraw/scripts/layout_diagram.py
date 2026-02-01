import json
import sys
import random
import time

def generate_id():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

def create_element(type, x, y, width, height, **kwargs):
    group_ids = kwargs.pop('groupIds', [])
    return {
        "id": generate_id(),
        "type": type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": "#000000",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": group_ids,
        "roundness": {"type": 3} if type == "rectangle" else None,
        "seed": random.randint(1, 100000),
        "version": 1,
        "versionNonce": random.randint(1, 100000),
        "isDeleted": False,
        "boundElements": [],
        "updated": int(time.time() * 1000),
        **kwargs
    }

def wrap_text(text, max_chars):
    words = text.split(' ')
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) + 1 > max_chars:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)

def estimate_text_dims(text, fontSize):
    lines = text.split('\n')
    max_line_chars = max(len(line) for line in lines) if lines else 0
    text_width = max(50, max_line_chars * (fontSize * 0.6)) 
    text_height = len(lines) * (fontSize * 1.5)
    return text_width, text_height

def create_text(x, y, text, fontSize=20, groupIds=[], width=None, textAlign="left", verticalAlign="top"):
    lines = text.split('\n')
    if width is None:
        width = max(len(line) for line in lines) * (fontSize * 0.6)
    height = len(lines) * (fontSize * 1.25)
    return create_element("text", x, y, width, height, 
        text=text, fontSize=fontSize, fontFamily=1, 
        textAlign=textAlign, verticalAlign=verticalAlign, groupIds=groupIds
    )

def create_smart_box_with_text(x, y, text, fontSize=16, fixed_width=None, bgColor="transparent", group=None):
    if group is None:
        group = generate_id()
    padding_x = 20
    padding_y = 20
    final_text = text
    if fixed_width:
        char_w = fontSize * 0.6
        available_w = fixed_width - (padding_x * 2)
        max_chars = int(available_w / char_w)
        final_text = wrap_text(text, max_chars)
        box_width = fixed_width
    else:
        final_text = wrap_text(text, 30) 
        t_w, _ = estimate_text_dims(final_text, fontSize)
        box_width = t_w + (padding_x * 2)
    t_w, t_h = estimate_text_dims(final_text, fontSize)
    box_height = t_h + (padding_y * 2)
    box = create_element("rectangle", x, y, box_width, box_height, backgroundColor=bgColor, groupIds=[group])
    text_x = x + (box_width - t_w) / 2
    text_y = y + (box_height - t_h) / 2
    text_el = create_element("text", text_x, text_y, t_w, t_h,
        text=final_text, fontSize=fontSize, fontFamily=1, 
        textAlign="center", verticalAlign="middle", groupIds=[group]
    )
    box["boundElements"] = [{"type": "text", "id": text_el["id"]}]
    text_el["containerId"] = box["id"]
    return box, text_el, box_width, box_height

def create_container_frame(x, y, w, h, label, color="#000000"):
    frame_group = generate_id()
    frame = create_element("rectangle", x, y, w, h,
        backgroundColor="transparent", strokeStyle="dashed", strokeWidth=2,
        strokeColor=color, opacity=50, roughness=2, groupIds=[frame_group]
    )
    label_w, label_h = estimate_text_dims(label, 20)
    label_el = create_element("text", x + 10, y - label_h - 5, label_w, label_h,
        text=label, fontSize=20, fontFamily=1, strokeColor=color, groupIds=[frame_group]
    )
    return [frame, label_el]

def create_arrow(start_id, end_id, start_x, start_y, end_x, end_y):
    return create_element("arrow", start_x, start_y, end_x - start_x, end_y - start_y,
        points=[[0, 0], [end_x - start_x, end_y - start_y]],
        startBinding={"elementId": start_id, "focus": 0, "gap": 10},
        endBinding={"elementId": end_id, "focus": 0, "gap": 10},
        strokeWidth=2, endArrowhead="arrow"
    )

def main():
    if len(sys.argv) < 3:
        print("Usage: python layout_diagram.py <input.json> <output.excalidraw>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, 'r') as f:
        data = json.load(f)

    # --- LAYOUT CONFIGURATION ---
    START_X = 100
    START_Y = 100
    COL_GAP = 40
    ROW_GAP = 30
    
    # Colors
    C_WHY = "#ffec99"  # Yellow
    C_WHAT = "#b2f2bb" # Green
    C_HOW = "#a5d8ff"  # Blue
    C_JOURNEY = "#ffc9c9" # Red
    
    # PM Framework Explanations (The "Meta-Text")
    PM_GUIDES = {
        "Why": "Focus on: User pain points,\nbusiness value, and 'Why now?'",
        "What": "Focus on: Key features,\nfunctional requirements, and MVP scope.",
        "How": "Focus on: Technical implementation,\ndata flow, and feasibility.",
        "Journey": "Focus on: The step-by-step flow from user trigger to goal completion."
    }
    
    final_elements = []
    
    # ==========================================
    # 1. STRATEGY CORE (Why, What, How)
    # ==========================================
    
    strategy_elements = []
    COL_WIDTH = 300 
    
    cols_data = [
        ("Why", data.get("why", []), C_WHY),
        ("What", data.get("what", []), C_WHAT),
        ("How", data.get("how", []), C_HOW)
    ]
    
    current_col_x = START_X + 40 # Padding for frame
    strategy_start_y = START_Y + 60 # Padding for frame
    max_strategy_y = strategy_start_y
    
    for title, items, color in cols_data:
        # Column Title
        t_box, t_txt, _, t_h = create_smart_box_with_text(
            current_col_x, strategy_start_y, title, fontSize=24, fixed_width=COL_WIDTH, bgColor="transparent"
        )
        t_box['strokeStyle'] = "solid"
        t_box['backgroundColor'] = "#ffffff"
        t_box['strokeWidth'] = 2
        
        # Meta-Text (Guide)
        guide_y = strategy_start_y + t_h + 10
        guide_text = create_text(current_col_x, guide_y, PM_GUIDES[title], fontSize=14, textAlign="center", width=COL_WIDTH)
        guide_text['strokeColor'] = "#868e96" # Grey
        
        strategy_elements.extend([t_box, t_txt, guide_text])
        
        item_y = guide_y + guide_text['height'] + 30 # Gap before first box
        
        for item in items:
            box, txt, w, h = create_smart_box_with_text(
                current_col_x, item_y, item, fontSize=16, fixed_width=COL_WIDTH, bgColor=color
            )
            strategy_elements.extend([box, txt])
            item_y += h + ROW_GAP
            
        if item_y > max_strategy_y:
            max_strategy_y = item_y
            
        current_col_x += COL_WIDTH + COL_GAP

    # Calculate bounding box for Strategy Section
    strat_w = (current_col_x - COL_GAP) - START_X + 40
    strat_h = (max_strategy_y) - START_Y + 20
    strat_frame = create_container_frame(START_X, START_Y, strat_w, strat_h, "Strategy Core", "#555555")
    
    final_elements.extend(strat_frame)
    final_elements.extend(strategy_elements)
    
    # ==========================================
    # 2. USER JOURNEY (Adaptive Layout)
    # ==========================================
    
    journey = data.get("journey", [])
    if journey:
        journey_start_y = START_Y + strat_h + 100 # Gap between sections
        journey_start_x = START_X
        
        journey_elements = []
        IS_VERTICAL = len(journey) > 6
        
        # Guide for Journey
        j_guide_text = create_text(journey_start_x + 40, journey_start_y + 40, PM_GUIDES["Journey"], fontSize=14, textAlign="left", width=600)
        j_guide_text['strokeColor'] = "#868e96"
        journey_elements.append(j_guide_text)
        
        prev_id = None
        prev_bounds = None
        
        cur_jx = journey_start_x + 40
        cur_jy = journey_start_y + 80 # Adjusted for guide
        
        max_j_w = 0
        max_j_h = 0
        
        for step in journey:
            box, txt, w, h = create_smart_box_with_text(
                cur_jx, cur_jy, step, fontSize=16, fixed_width=None, bgColor=C_JOURNEY
            )
            box['roundness'] = {"type": 3}
            if w < 150: pass 

            journey_elements.extend([box, txt])
            
            if prev_id:
                px, py, pw, ph = prev_bounds
                if IS_VERTICAL:
                    s_x, s_y = px + pw/2, py + ph
                    e_x, e_y = box['x'] + box['width']/2, box['y']
                else:
                    s_x, s_y = px + pw, py + ph/2
                    e_x, e_y = box['x'], box['y'] + box['height']/2
                arrow = create_arrow(prev_id, box['id'], s_x, s_y, e_x, e_y)
                journey_elements.append(arrow)
            
            prev_id = box['id']
            prev_bounds = (box['x'], box['y'], box['width'], box['height'])
            
            if IS_VERTICAL:
                cur_jy += h + 60
                right_edge = cur_jx + w
                if right_edge > max_j_w: max_j_w = right_edge
                max_j_h = cur_jy
            else:
                cur_jx += w + 60
                bottom_edge = cur_jy + h
                if bottom_edge > max_j_h: max_j_h = bottom_edge
                max_j_w = cur_jx
                
        j_frame_w = (max_j_w - journey_start_x) + 40
        if IS_VERTICAL: j_frame_w += 40
        j_frame_h = (max_j_h - journey_start_y) 
        if not IS_VERTICAL: j_frame_h += 40
        
        j_frame = create_container_frame(journey_start_x, journey_start_y, j_frame_w, j_frame_h, "User Journey", "#555555")
        final_elements.extend(j_frame)
        final_elements.extend(journey_elements)

    title_text = data.get("title", "Product Requirements")
    final_elements.append(create_text(START_X, START_Y - 120, title_text, fontSize=40))

    output_data = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://openclaw.ai",
        "elements": final_elements,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
        "files": {}
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated diagram with {len(final_elements)} elements.")

if __name__ == "__main__":
    main()
