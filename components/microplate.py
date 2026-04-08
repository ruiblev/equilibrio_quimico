import streamlit as st

def render_microplate(well_colors, active_animation=None):
    """
    Renders a 4x3 microplate with given colors for each well.
    active_animation limits the animation to certain targets ('all', 'water', 'A', 'B', 'C', 'D', None)
    """
    # CSS for the microplate and animations
    css = """
    <style>
    @keyframes drop-fall {
        0% { top: -40px; opacity: 0; transform: scale(1); }
        20% { top: -20px; opacity: 1; transform: scale(1); }
        40% { top: 20px; opacity: 1; transform: scale(0.5); }
        50% { top: 20px; opacity: 0; transform: scale(0); }
        100% { opacity: 0; }
    }
    
    @keyframes rod-stir {
        0% { transform: translate(20px, -30px) rotate(15deg); opacity: 0; }
        40% { transform: translate(20px, -30px) rotate(15deg); opacity: 0; }
        50% { transform: translate(10px, -10px) rotate(15deg); opacity: 1; }
        60% { transform: translate(-10px, 10px) rotate(-10deg); opacity: 1; }
        70% { transform: translate(10px, -10px) rotate(15deg); opacity: 1; }
        80% { transform: translate(-10px, 10px) rotate(-10deg); opacity: 1; }
        90% { transform: translate(20px, -30px) rotate(15deg); opacity: 0; }
        100% { opacity: 0; }
    }

    .microplate-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        background-color: #f2f2f2;
        padding: 20px;
        border-radius: 15px;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.1), 5px 5px 15px rgba(0,0,0,0.1);
        width: max-content;
        margin: 0 auto;
    }
    .plate-grid {
        display: grid;
        grid-template-columns: 40px 60px 60px 60px;
        grid-template-rows: 40px 60px 60px 60px 60px;
        gap: 15px;
        align-items: center;
        justify-items: center;
    }
    .plate-label {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: bold;
        color: #555;
        font-size: 18px;
    }
    .well-wrapper {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .well {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: transparent;
        box-shadow: inset 3px 3px 6px rgba(0,0,0,0.15), inset -2px -2px 5px rgba(255,255,255,0.8);
        border: 1px solid #ddd;
        position: relative;
        overflow: hidden;
    }
    .well-liquid {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        opacity: 0.9;
        box-shadow: inset 0px -10px 15px rgba(0,0,0,0.2);
        transition: background-color 1s ease-in-out;
    }
    /* Delay the color change if animating */
    .well-liquid.animating {
        transition-delay: 2.5s;
    }
    
    .dropper {
        position: absolute;
        font-size: 24px;
        opacity: 0;
        pointer-events: none;
        z-index: 10;
        top: -40px;
        left: 17px;
    }
    .rod {
        position: absolute;
        font-size: 30px;
        opacity: 0;
        pointer-events: none;
        z-index: 11;
        top: -10px;
        left: 20px;
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

    html += "<div></div>"
    for col in [1, 2, 3]:
        html += f"<div class='plate-label'>{col}</div>"

    rows = ['A', 'B', 'C', 'D']
    for row in rows:
        html += f"<div class='plate-label'>{row}</div>"
        for col in [1, 2, 3]:
            well_id = f"{row}{col}"
            color = well_colors.get(well_id, "transparent")
            liquid_style = f"background-color: {color};" if color != "transparent" else "background-color: transparent;"

            # Determine if this specific well should animate
            is_animating = False
            if active_animation == 'all':
                is_animating = True
            elif active_animation == 'water' and col in [1, 2]:
                is_animating = True
            elif active_animation == row: # Add drop in the specific row (reagents only added to col 2, col 3 typically, but let's animate the columns affected based on standard additions: A2, A3, B2, B3, C2, C3, D2, D3)
                if col in [2, 3]: 
                    is_animating = True

            anim_class = "animating" if is_animating else ""

            # Only show dropper and rod if this well is animating
            extra_dom = ""
            if is_animating:
                # Usa emoji de gota para o reagente
                dropper_icon = "💧" 
                # Usa emoji de um pauzinho simulando a microvareta
                rod_icon = "🥢"
                extra_dom = f"<div class='dropper'>{dropper_icon}</div><div class='rod'>{rod_icon}</div>"

            html += f"""
            <div class='well-wrapper {anim_class}'>
                <div class='well' title='Cavidade {well_id}'>
                    <div class='well-liquid {anim_class}' style='{liquid_style}'></div>
                </div>
                {extra_dom}
            </div>
            """

    html += "</div></div>"
    st.components.v1.html(html, height=450)
