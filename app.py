import streamlit as st
import pandas as pd
from components import microplate
import importlib
importlib.reload(microplate)
render_microplate = microplate.render_microplate

# --- Configuração da Página ---
st.set_page_config(
    page_title="Simulador de Equilíbrio Químico",
    page_icon="🧪",
    layout="wide"
)

# --- Constantes de Cores ---
COLORS = {
    "empty": "transparent",
    "red": "#c41b1b",        
    "dark_red_1": "#8a0c0c",   
    "dark_red_2": "#4a0505",   
    "orange": "#d18f2e",       
    "pale_yellow": "#f0e6b6"   
}

# --- Inicialização do Estado ---
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'well_colors' not in st.session_state:
    st.session_state.well_colors = {
        f"{r}{c}": COLORS["empty"] 
        for r in ['A', 'B', 'C', 'D'] 
        for c in [1, 2, 3]
    }
    
if 'prev_well_colors' not in st.session_state:
    st.session_state.prev_well_colors = st.session_state.well_colors.copy()

if 'added_reagents' not in st.session_state:
    st.session_state.added_reagents = {
        'A': False,
        'B': False,
        'C': False,
        'D': False
    }

if 'active_animation' not in st.session_state:
    st.session_state.active_animation = None

if 'custom_labels' not in st.session_state:
    st.session_state.custom_labels = {}

# Captura animação pendente
current_animation = st.session_state.active_animation
# Limpa para a próxima interação
st.session_state.active_animation = None

# --- Funções de Ajuda ---
def next_step():
    st.session_state.step += 1

def reset_simulation():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Lógica das Reações do Passo 4
def add_to_row_A():
    st.session_state.active_animation = 'A'
    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
    st.session_state.well_colors["A2"] = COLORS["dark_red_1"]
    st.session_state.well_colors["A3"] = COLORS["dark_red_2"]
    st.session_state.added_reagents['A'] = True

def add_to_row_B():
    st.session_state.active_animation = 'B'
    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
    st.session_state.well_colors["B2"] = COLORS["dark_red_1"]
    st.session_state.well_colors["B3"] = COLORS["dark_red_2"]
    st.session_state.added_reagents['B'] = True

def add_to_row_C():
    st.session_state.active_animation = 'C'
    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
    st.session_state.well_colors["C2"] = COLORS["orange"]
    st.session_state.well_colors["C3"] = COLORS["pale_yellow"]
    st.session_state.added_reagents['C'] = True

def add_to_row_D():
    st.session_state.active_animation = 'D'
    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
    st.session_state.well_colors["D2"] = COLORS["orange"]
    st.session_state.well_colors["D3"] = COLORS["pale_yellow"]
    st.session_state.added_reagents['D'] = True


# --- Interface Principal ---
st.title("🧪 Efeito da concentração no equilíbrio químico")

st.markdown("""
Esta atividade simula o comportamento do equilíbrio químico homogéneo:
**Fe³⁺ (aq)** *(Amarelo)* **+ SCN⁻ (aq)** *(Incolor)* **⇌ [FeSCN]²⁺ (aq)** *(Vermelho)*
""")

col1, col2 = st.columns([1.1, 1.1], gap="large")

with col1:
    st.subheader("Trabalho Laboratorial: Procedimento")
    
    # Passo 1
    with st.expander("Passo 1", expanded=(st.session_state.step == 1)):
        st.write("1. Identifique as cavidades da sua placa inserindo texto livre abaixo (ex: AA, 11, WX, Cav1):")
        if st.session_state.step == 1:
            st.markdown("---")
            
            valid = True
            temp_labels = {}
            distinct_check = set()
            empty_count = 0
            has_duplicates = False
            
            # Grelha Cega (3x4)
            for row in ['A', 'B', 'C', 'D']:
                r_cols = st.columns([1, 1, 1])
                for i, col in enumerate([1, 2, 3]):
                    with r_cols[i]:
                        key = f"{row}{col}"
                        val = st.text_input("Cav", key=f"in_{key}", label_visibility="collapsed")
                        v_strip = val.strip().upper()
                        
                        if not v_strip:
                            valid = False
                            empty_count += 1
                        elif v_strip in distinct_check:
                            valid = False
                            has_duplicates = True
                        else:
                            temp_labels[key] = v_strip
                            distinct_check.add(v_strip)

            st.markdown("---")
            if valid and len(temp_labels) == 12:
                st.success("✅ Todas as 12 cavidades possuem identificações únicas validadas!")
                def confirm_labels():
                    st.session_state.custom_labels = temp_labels
                    next_step()
                st.button("Atribuir e Avançar para Passo 2 ➔", on_click=confirm_labels, type="primary")
            else:
                if empty_count == 12:
                    st.info("Aguardando inserção... Preencha todas as 12 caixas com referências para poder prosseguir.")
                else:
                    if empty_count > 0 and has_duplicates:
                        st.error(f"⚠️ **Erro no preenchimento:** Detetadas referências duplicadas e faltam preencher {empty_count} cavidade(s).")
                    elif empty_count > 0:
                        st.warning(f"⚠️ **Preenchimento incompleto:** Por favor, preencha as {empty_count} cavidade(s) que se encontra(m) em branco.")
                    elif has_duplicates:
                        st.error("⚠️ **Erro de duplicação:** Encontram-se referências repetidas. Cada cavidade deve possuir um nome estritamente único.")
        else:
            st.success("✅ Nomenclaturas registadas com sucesso.")

    lbl = st.session_state.custom_labels

    # Passo 2
    with st.expander("Passo 2", expanded=(st.session_state.step == 2)):
        st.write("2. Adicione a cada uma das cavidades:")
        st.write("- 1 gota de Fe(NO₃)₃ (aq)")
        st.write("- 1 gota de KSCN (aq)")
        st.info("Observe a cor característica ao agitar.")
        if st.session_state.step == 2:
            def trigger_step_2():
                st.session_state.active_animation = 'all'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                for k in st.session_state.well_colors:
                    st.session_state.well_colors[k] = COLORS["red"]
                next_step()
                
            st.button("Adicionar Reagentes a todas as cavidades", on_click=trigger_step_2, type="primary")

    # Passo 3
    with st.expander("Passo 3", expanded=(st.session_state.step == 3)):
        st.write("3. Nivele os volumes:")
        st.write("- 2 gotas de água nas cavidades da primeira coluna")
        st.write("- 1 gota de água nas cavidades da segunda coluna")
        if st.session_state.step == 3:
            def trigger_step_3():
                st.session_state.active_animation = 'water'
                next_step()
                
            st.button("Adicionar Água nas Colunas referidas ➔", on_click=trigger_step_3, type="primary")

    # Passo 4
    with st.expander("Passo 4", expanded=(st.session_state.step == 4)):
        st.write("4. Adicione gotas das várias soluções reagentes, agitando:")
        
        st.markdown(f"**Efeito de Fe³⁺**")
        st.caption(f"{lbl.get('A2', '')} (1 gota); {lbl.get('A3', '')} (2 gotas)")
        if not st.session_state.added_reagents['A']:
            st.button("Adicionar Fe(NO₃)₃", on_click=add_to_row_A, key="btn_A")
            
        st.markdown(f"**Efeito de SCN⁻**")
        st.caption(f"{lbl.get('B2', '')} (1 gota); {lbl.get('B3', '')} (2 gotas)")
        if not st.session_state.added_reagents['B']:
            st.button("Adicionar KSCN", on_click=add_to_row_B, key="btn_B")
            
        st.markdown(f"**Efeito de Ag⁺**")
        st.caption(f"{lbl.get('C2', '')} (1 gota); {lbl.get('C3', '')} (2 gotas)")
        if not st.session_state.added_reagents['C']:
            st.button("Adicionar AgNO₃", on_click=add_to_row_C, key="btn_C")
            
        st.markdown(f"**Efeito de C₂O₄²⁻**")
        st.caption(f"{lbl.get('D2', '')} (1 gota); {lbl.get('D3', '')} (2 gotas)")
        if not st.session_state.added_reagents['D']:
            st.button("Adicionar Na₂C₂O₄", on_click=add_to_row_D, key="btn_D")

        if all(st.session_state.added_reagents.values()):
            st.success("Reagentes adicionados. Verifique a placa e as tonalidades decorrentes do Princípio de Le Châtelier (Análise pós-laboratorial).")

    # Pós-laboratório
    with st.expander("📋 Registo de Cores Finais", expanded=(st.session_state.step >= 4 and all(st.session_state.added_reagents.values()))):
        def get_color_name(hex_code):
            rev_colors = {v: k for k, v in COLORS.items()}
            mapping = {
                "red": "Vermelho",
                "dark_red_1": "Vermelho intenso",
                "dark_red_2": "Vermelho escuro",
                "orange": "Alaranjado",
                "pale_yellow": "Amarelo claro"
            }
            color_key = rev_colors.get(hex_code, "Incolor")
            return mapping.get(color_key, "Incolor")

        if all(st.session_state.added_reagents.values()):
            data = {
                "Adicionado (aq)": ["Fe(NO₃)₃", "KSCN", "AgNO₃", "Na₂C₂O₄"],
                "Controlo": [
                    f"[{lbl.get(f'{r}1', '')}] {get_color_name(st.session_state.well_colors[f'{r}1'])}" for r in ['A','B','C','D']
                ],
                "1 Gota Adicionada": [
                    f"[{lbl.get(f'{r}2', '')}] {get_color_name(st.session_state.well_colors[f'{r}2'])}" for r in ['A','B','C','D']
                ],
                "2 Gotas Adicionadas": [
                    f"[{lbl.get(f'{r}3', '')}] {get_color_name(st.session_state.well_colors[f'{r}3'])}" for r in ['A','B','C','D']
                ]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, hide_index=True)

with col2:
    st.subheader("Placa de Microanálise")
    
    # Passa o custom_labels e animation para atualizar interativamente a placa do lado direito
    render_microplate(
        st.session_state.well_colors, 
        active_animation=current_animation,
        custom_labels=st.session_state.custom_labels,
        prev_well_colors=st.session_state.prev_well_colors
    )

    colA, colB, colC = st.columns([1,1,1])
    with colB:
        st.button("🔄 Reiniciar", on_click=reset_simulation)
