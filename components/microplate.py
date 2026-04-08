import streamlit as st

def render_microplate(well_colors):
    """
    Renders a 4x3 microplate with given colors for each well.
    well_colors is a dict mapping e.g., 'A1' to a CSS color string.
    """
    # CSS for the microplate
    css = """
    <style>
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
        transition: background-color 1s ease-in-out;
    }
    .well-liquid {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        opacity: 0.9;
        transition: background-color 1s ease-in-out, height 0.5s ease-in-out;
        box-shadow: inset 0px -10px 15px rgba(0,0,0,0.2);
    }
    </style>
    """

    # Start building the HTML
    html = f"{css}<div class='microplate-container'><div class='plate-grid'>"

    # Top left corner empty
    html += "<div></div>"

    # Column labels (1, 2, 3)
    for col in [1, 2, 3]:
        html += f"<div class='plate-label'>{col}</div>"

    rows = ['A', 'B', 'C', 'D']
    
    for row in rows:
        # Row label
        html += f"<div class='plate-label'>{row}</div>"
        
        for col in [1, 2, 3]:
            well_id = f"{row}{col}"
            color = well_colors.get(well_id, "transparent")
            
            # Use 'transparent' for empty wells
            if color == "transparent":
                liquid_style = "background-color: transparent;"
            else:
                liquid_style = f"background-color: {color};"

            html += f"""
            <div class='well-wrapper'>
                <div class='well' title='Cavidade {well_id}'>
                    <div class='well-liquid' style='{liquid_style}'></div>
                </div>
            </div>
            """

    html += "</div></div>"
    
    st.components.v1.html(html, height=450)
