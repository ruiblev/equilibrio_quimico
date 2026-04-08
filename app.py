import streamlit as st
import pandas as pd
from components.microplate import render_microplate

# --- Configuração da Página ---
st.set_page_config(
    page_title="Simulador de Equilíbrio Químico",
    page_icon="🧪",
    layout="wide"
)

# --- Constantes de Cores ---
COLORS = {
    "empty": "transparent",
    "red": "#c41b1b",        # [FeSCN]2+ padrão
    "dark_red_1": "#8a0c0c",   # Mais [FeSCN]2+
    "dark_red_2": "#4a0505",   # Muito mais [FeSCN]2+
    "orange": "#d18f2e",       # Menos [FeSCN]2+, mais Fe3+
    "pale_yellow": "#f0e6b6"   # Quase sem [FeSCN]2+, descolorado/amarelo pálido
}

# --- Inicialização do Estado ---
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'well_colors' not in st.session_state:
    # Initialize all 12 wells as empty
    st.session_state.well_colors = {
        f"{r}{c}": COLORS["empty"] 
        for r in ['A', 'B', 'C', 'D'] 
        for c in [1, 2, 3]
    }

if 'added_reagents' not in st.session_state:
    st.session_state.added_reagents = {
        'A': False,
        'B': False,
        'C': False,
        'D': False
    }

# --- Funções de Ajuda ---
def next_step():
    st.session_state.step += 1

def reset_simulation():
    st.session_state.step = 1
    st.session_state.well_colors = {
        f"{r}{c}": COLORS["empty"] 
        for r in ['A', 'B', 'C', 'D'] 
        for c in [1, 2, 3]
    }
    st.session_state.added_reagents = {k: False for k in st.session_state.added_reagents}

# Lógica das Reações do Passo 4
def add_to_row_A():
    st.session_state.well_colors["A2"] = COLORS["dark_red_1"]
    st.session_state.well_colors["A3"] = COLORS["dark_red_2"]
    st.session_state.added_reagents['A'] = True

def add_to_row_B():
    st.session_state.well_colors["B2"] = COLORS["dark_red_1"]
    st.session_state.well_colors["B3"] = COLORS["dark_red_2"]
    st.session_state.added_reagents['B'] = True

def add_to_row_C():
    st.session_state.well_colors["C2"] = COLORS["orange"]
    st.session_state.well_colors["C3"] = COLORS["pale_yellow"] # com precipitado
    st.session_state.added_reagents['C'] = True

def add_to_row_D():
    st.session_state.well_colors["D2"] = COLORS["orange"]
    st.session_state.well_colors["D3"] = COLORS["pale_yellow"]
    st.session_state.added_reagents['D'] = True


# --- Interface Principal ---
st.title("🧪 Efeito da concentração no equilíbrio químico")

st.markdown("""
Esta atividade simula o comportamento do equilíbrio químico homogéneo:
**Fe³⁺ (aq)** *(Amarelo)* **+ SCN⁻ (aq)** *(Incolor)* **⇌ [FeSCN]²⁺ (aq)** *(Vermelho)*
""")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("Trabalho Laboratorial: Procedimento")
    
    # Passo 1
    with st.expander("Passo 1", expanded=(st.session_state.step == 1)):
        st.write("1. Numere as cavidades da placa de microanálise da seguinte forma:")
        st.write("- Linhas: A, B, C, D")
        st.write("- Colunas: 1, 2, 3")
        if st.session_state.step == 1:
            st.button("Avançar para Passo 2 ➔", on_click=next_step, type="primary")

    # Passo 2
    with st.expander("Passo 2", expanded=(st.session_state.step == 2)):
        st.write("2. Adicione a cada uma das cavidades:")
        st.write("- 1 gota de Fe(NO₃)₃ (aq)")
        st.write("- 1 gota de KSCN (aq)")
        st.info("Agite até observar a cor vermelha característica de [FeSCN]²⁺(aq).")
        if st.session_state.step == 2:
            if st.button("Adicionar Reagentes a todas as cavidades", type="primary"):
                for k in st.session_state.well_colors:
                    st.session_state.well_colors[k] = COLORS["red"]
                next_step()

    # Passo 3
    with st.expander("Passo 3", expanded=(st.session_state.step == 3)):
        st.write("3. Adicione:")
        st.write("- 2 gotas de água nas cavidades da coluna 1")
        st.write("- 1 gota de água nas cavidades da coluna 2")
        st.caption("Isto garante que os volumes finais sejam idênticos em todas as cavidades.")
        if st.session_state.step == 3:
            if st.button("Adicionar Água (Volumes nivelados) ➔", type="primary"):
                next_step()

    # Passo 4
    with st.expander("Passo 4", expanded=(st.session_state.step == 4)):
        st.write("4. Adicione gotas das várias soluções reagentes, agitando:")
        
        st.markdown("**Linha A** (Efeito de Fe³⁺)")
        st.write("- A2: 1 gota de Fe(NO₃)₃ (aq)\n- A3: 2 gotas de Fe(NO₃)₃ (aq)")
        if not st.session_state.added_reagents['A']:
            st.button("Adicionar na Linha A", on_click=add_to_row_A, key="btn_A")
            
        st.markdown("**Linha B** (Efeito de SCN⁻)")
        st.write("- B2: 1 gota de KSCN (aq)\n- B3: 2 gotas de KSCN (aq)")
        if not st.session_state.added_reagents['B']:
            st.button("Adicionar na Linha B", on_click=add_to_row_B, key="btn_B")
            
        st.markdown("**Linha C** (Efeito de Ag⁺)")
        st.write("- C2: 1 gota de AgNO₃ (aq)\n- C3: 2 gotas de AgNO₃ (aq)")
        if not st.session_state.added_reagents['C']:
            st.button("Adicionar na Linha C", on_click=add_to_row_C, key="btn_C")
            
        st.markdown("**Linha D** (Efeito de C₂O₄²⁻)")
        st.write("- D2: 1 gota de Na₂C₂O₄ (aq)\n- D3: 2 gotas de Na₂C₂O₄ (aq)")
        if not st.session_state.added_reagents['D']:
            st.button("Adicionar na Linha D", on_click=add_to_row_D, key="btn_D")

        if all(st.session_state.added_reagents.values()):
            st.success("Trabalho concluído! Registe as cores observadas.")
            if st.button("Ver Questões Pós-Laboratoriais", type="primary"):
                next_step()

    # Pós-laboratório
    with st.expander("📋 Questões Pós-Laboratoriais", expanded=(st.session_state.step > 4)):
        st.write("Registo das observações:")
        
        # Gerar DataFrame baseado no estado atual
        def get_color_name(hex_code):
            rev_colors = {v: k for k, v in COLORS.items()}
            # Map back to human readable
            mapping = {
                "red": "Vermelho (Padrão)",
                "dark_red_1": "Vermelho mais intenso",
                "dark_red_2": "Vermelho muito intenso",
                "orange": "Alaranjado",
                "pale_yellow": "Amarelo pálido (Descolorido)"
            }
            color_key = rev_colors.get(hex_code, "Incolor")
            return mapping.get(color_key, "Incolor")

        if st.session_state.step > 4:
            data = {
                "Cavidade": ["A", "B", "C", "D"],
                "Reagente Adicionado": ["Fe(NO₃)₃ (aq)", "KSCN (aq)", "AgNO₃ (aq)", "Na₂C₂O₄ (aq)"],
                "Coluna 1 (Controlo)": [get_color_name(st.session_state.well_colors[f"{r}1"]) for r in ['A','B','C','D']],
                "Coluna 2": [get_color_name(st.session_state.well_colors[f"{r}2"]) for r in ['A','B','C','D']],
                "Coluna 3": [get_color_name(st.session_state.well_colors[f"{r}3"]) for r in ['A','B','C','D']]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, hide_index=True)

with col2:
    st.subheader("Visualização da Placa de Microanálise")
    # Render component
    render_microplate(st.session_state.well_colors)

    st.markdown("---")
    st.button("🔄 Reiniciar Simulação", on_click=reset_simulation)
