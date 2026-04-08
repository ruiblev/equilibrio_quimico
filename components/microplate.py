import streamlit as st

def render_microplate(well_colors, active_animation=None, custom_labels=None, prev_well_colors=None):
    """
    Renders a 4x3 microplate.
    active_animation limits the animation to certain targets ('all', 'water', 'A', 'B', 'C', 'D', None)
    custom_labels is a dict that maps the standard ID (e.g. 'A1') to the user's custom string. 
    If None, no labels are displayed.
    """
    if custom_labels is None:
        custom_labels = {}
    if prev_well_colors is None:
        prev_well_colors = well_colors

    css = """
    <style>
    @keyframes drop-fall {
        0% { top: -40px; opacity: 0; transform: scale(1); }
        20% { top: -10px; opacity: 1; transform: scale(1); }
        40% { top: 25px; opacity: 1; transform: scale(0.5); }
        50% { top: 25px; opacity: 0; transform: scale(0); }
        100% { opacity: 0; }
    }
    
    @keyframes rod-stir {
        0% { transform: translate(20px, -30px) rotate(15deg); opacity: 0; }
        40% { transform: translate(20px, -30px) rotate(15deg); opacity: 0; }
        50% { transform: translate(10px, 0px) rotate(15deg); opacity: 1; }
        60% { transform: translate(-10px, 20px) rotate(-10deg); opacity: 1; }
        70% { transform: translate(10px, 0px) rotate(15deg); opacity: 1; }
        80% { transform: translate(-10px, 20px) rotate(-10deg); opacity: 1; }
        90% { transform: translate(20px, -20px) rotate(15deg); opacity: 0; }
        100% { opacity: 0; }
    }

    .microplate-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        background-color: #f2f2f2;
        padding: 25px;
        border-radius: 15px;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.1), 5px 5px 15px rgba(0,0,0,0.1);
        width: max-content;
        margin: 0 auto;
    }
    .plate-grid {
        display: grid;
        grid-template-columns: repeat(3, 80px);
        grid-template-rows: repeat(4, 90px);
        gap: 15px;
        align-items: center;
        justify-items: center;
    }
    .well-wrapper {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        position: relative;
    }
    .well {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: transparent;
        box-shadow: inset 4px 4px 8px rgba(0,0,0,0.15), inset -3px -3px 6px rgba(255,255,255,0.8);
        border: 1px solid #ddd;
        position: relative;
        overflow: hidden;
        margin-bottom: 8px;
    }
    .well-liquid {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        opacity: 0.9;
        box-shadow: inset 0px -10px 15px rgba(0,0,0,0.2);
        transition: background-color 1s ease-in-out;
    }
    @keyframes color-mix {
        0% { background-color: var(--old-color); }
        40% { background-color: var(--old-color); }
        90% { background-color: var(--new-color); }
        100% { background-color: var(--new-color); }
    }
    
    .well-liquid.animating {
        animation: color-mix 2.5s forwards;
    }
    .custom-label {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: bold;
        color: #444;
        font-size: 14px;
        text-align: center;
        width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .dropper {
        position: absolute;
        font-size: 28px;
        opacity: 0;
        pointer-events: none;
        z-index: 10;
        top: -40px;
        left: 26px;
    }
    .rod {
        position: absolute;
        font-size: 34px;
        opacity: 0;
        pointer-events: none;
        z-index: 11;
        top: -10px;
        left: 28px;
        transform-origin: bottom left;
    }
    .animating .dropper {
        animation: drop-fall 2.5s ease-in-out;
    }
    .animating .rod {
        animation: rod-stir 2.5s ease-in-out;
    }
    </style>
    """

    html = f"{css}<div class='microplate-container'><div class='plate-grid'>"

    rows = ['A', 'B', 'C', 'D']
    for row in rows:
        for col in [1, 2, 3]:
            well_id = f"{row}{col}"
            color = well_colors.get(well_id, "transparent")
            old_color = prev_well_colors.get(well_id, "transparent")
            
            liquid_style = f"background-color: {color};" if color != "transparent" else "background-color: transparent;"
            liquid_style += f" --old-color: {old_color}; --new-color: {color};"

            is_animating = False
            if isinstance(active_animation, list):
                if well_id in active_animation:
                    is_animating = True
            elif active_animation == 'all':
                is_animating = True
            elif active_animation == 'water' and col in [1, 2]:
                is_animating = True
            elif active_animation == row:
                if col in [2, 3]: 
                    is_animating = True

            anim_class = "animating" if is_animating else ""

            extra_dom = ""
            if is_animating:
                dropper_icon = "💧" 
                rod_icon = "🥢"
                extra_dom = f"<div class='dropper'>{dropper_icon}</div><div class='rod'>{rod_icon}</div>"

            # Custom label display
            label_text = custom_labels.get(well_id, "")
            label_dom = f"<div class='custom-label'>{label_text}</div>" if label_text else ""

            html += f"""
            <div class='well-wrapper {anim_class}'>
                <div class='well' title='{label_text}'>
                    <div class='well-liquid {anim_class}' style='{liquid_style}'></div>
                </div>
                {label_dom}
                {extra_dom}
            </div>
            """

    html += "</div></div>"
    st.components.v1.html(html, height=550)
