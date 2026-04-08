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

# --- Inicialização do Estado Básico ---
if 'sim_mode' not in st.session_state:
    st.session_state.sim_mode = "Modo de Estudo (Guiado)"

def reset_all_state():
    for key in list(st.session_state.keys()):
        if key != 'sim_mode':
            del st.session_state[key]

# Trocar modo
mode_choice = st.sidebar.radio("Modo de Operação:", ["Modo de Estudo (Guiado)", "Modo Prático-Experimental"])
if mode_choice != st.session_state.sim_mode:
    st.session_state.sim_mode = mode_choice
    reset_all_state()

# INICIALIZAÇÃO DE VARIÁVEIS (Partilhadas)
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

if 'active_animation' not in st.session_state:
    st.session_state.active_animation = None

if 'custom_labels' not in st.session_state:
    st.session_state.custom_labels = {}

current_animation = st.session_state.active_animation
st.session_state.active_animation = None

# --- INICIALIZAÇÃO DO MODO ESTUDO ---
if 'added_reagents' not in st.session_state:
    st.session_state.added_reagents = {
        'A': False, 'B': False, 'C': False, 'D': False
    }

# --- INICIALIZAÇÃO DO MODO PRÁTICO ---
if 'p_step' not in st.session_state:
    st.session_state.p_step = 1

if 'well_contents' not in st.session_state:
    st.session_state.well_contents = {
        f"{r}{c}": {"Fe3+": 0, "SCN-": 0, "Ag+": 0, "C2O4_2-": 0, "H2O": 0}
        for r in ['A', 'B', 'C', 'D'] for c in [1, 2, 3]
    }

if 'selected_wells_ui' not in st.session_state:
    st.session_state.selected_wells_ui = []


# --- FUNÇÕES GERAIS ---
def next_step(): st.session_state.step += 1
def next_p_step(): st.session_state.p_step += 1

def reset_simulation():
    reset_all_state()

# --- FUNÇÕES CALCULADORAS DO MODO PRÁTICO ---
def calculate_color(c):
    fe = c["Fe3+"]
    scn = c["SCN-"]
    ag = c["Ag+"]
    ox = c["C2O4_2-"]
    
    if fe == 0 and scn == 0:
        return COLORS["empty"]
        
    # Ag+ e Ox precipitam/complexam e removem os reagentes ativos da solução
    active_scn = max(0, scn - ag)
    active_fe = max(0, fe - ox)
    
    # Complexo formado depende do limitante
    complex_amount = min(active_fe, active_scn)
    
    if complex_amount >= 3: return COLORS["dark_red_2"]
    if complex_amount == 2: return COLORS["dark_red_1"]
    if complex_amount == 1: return COLORS["red"]
        
    # Quando o complexo vermelho é totalmente dissipado:
    if active_fe > 0:
        return COLORS["orange"] # Sobra Fe3+ sozinho
    else:
        return COLORS["pale_yellow"] # Fica descolorido

def apply_practical_dispenser(reagent, drops):
    selected = st.session_state.selected_wells_ui
    if not selected:
        st.warning("Selecione pelo menos uma cavidade alvo!")
        return

    st.session_state.active_animation = selected
    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
    
    key_map = {
        "Fe(NO₃)₃ (aq)": "Fe3+",
        "KSCN (aq)": "SCN-",
        "AgNO₃ (aq)": "Ag+",
        "Na₂C₂O₄ (aq)": "C2O4_2-",
        "Água destilada": "H2O"
    }
    k = key_map[reagent]
    
    for w in selected:
        st.session_state.well_contents[w][k] += drops
        st.session_state.well_colors[w] = calculate_color(st.session_state.well_contents[w])


# ==========================================
# RENDERIZAÇÃO DA INTERFACE FRONTEND
# ==========================================

st.title("🧪 Efeito da concentração no equilíbrio químico")

col1, col2 = st.columns([1.1, 1.1], gap="large")

with col1:
    
    # ----------------------------------------------------
    # MODO DE ESTUDO (Atual)
    # ----------------------------------------------------
    if st.session_state.sim_mode == "Modo de Estudo (Guiado)":
        st.subheader("Modo Estudo: Guião Passo-a-Passo")
        
        with st.expander("Passo 1: Identificação", expanded=(st.session_state.step == 1)):
            st.write("Identifique as cavidades ou utilize o preenchimento rápido.")
            if st.session_state.step == 1:
                col_btn, _ = st.columns([1, 1])
                with col_btn:
                    if st.button("⚡ Preenchimento Automático (A1-D3)"):
                        st.session_state.custom_labels = {f"{r}{c}": f"{r}{c}" for r in ['A','B','C','D'] for c in [1,2,3]}
                        next_step()
                        st.rerun()

                st.markdown("---")
                valid = True
                temp_labels = {}
                distinct_check = set()
                empty_count = 0
                has_duplicates = False
                
                for row in ['A', 'B', 'C', 'D']:
                    r_cols = st.columns([1, 1, 1])
                    for i, col_idx in enumerate([1, 2, 3]):
                        with r_cols[i]:
                            key = f"{row}{col_idx}"
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
                    st.success("✅ Todas as 12 cavidades preenchidas!")
                    def confirm_labels():
                        st.session_state.custom_labels = temp_labels
                        next_step()
                    st.button("Avançar para Passo 2 ➔", on_click=confirm_labels, type="primary")
                else:
                    if empty_count < 12 and (empty_count > 0 or has_duplicates):
                        if empty_count > 0 and has_duplicates:
                            st.error(f"⚠️ Erro: Faltam preencher {empty_count} cavidade(s). E existem duplicações.")
                        elif empty_count > 0:
                            st.warning(f"⚠️ Atenção: Preencha as {empty_count} cavidade(s) vazia(s).")
                        elif has_duplicates:
                            st.error("⚠️ Atenção: Há referências repetidas.")
            else:
                st.success("✅ Identificações registadas.")

        lbl = st.session_state.custom_labels

        with st.expander("Passo 2: Criar Equilíbrio", expanded=(st.session_state.step == 2)):
            st.write("Adicione 1 gota Fe(NO₃)₃ e 1 gota KSCN a cada cavidade.")
            if st.session_state.step == 2:
                def trigger_step_2():
                    st.session_state.active_animation = 'all'
                    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                    for k in st.session_state.well_colors:
                        st.session_state.well_colors[k] = COLORS["red"]
                    next_step()
                st.button("Adicionar Reagentes", on_click=trigger_step_2, type="primary")

        with st.expander("Passo 3: Adição de Água (Volume)", expanded=(st.session_state.step == 3)):
            st.write("2 gotas de água na Col 1; 1 gota na Col 2.")
            if st.session_state.step == 3:
                def trigger_step_3():
                    st.session_state.active_animation = 'water'
                    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                    next_step()
                st.button("Adicionar Água ➔", on_click=trigger_step_3, type="primary")

        with st.expander("Passo 4: Adiões Finais e Perturbação", expanded=(st.session_state.step == 4)):
            st.write("Estude como o deslocamento de cor afeta Le Châtelier:")
            def mk_A(): 
                st.session_state.active_animation = 'A'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                st.session_state.well_colors["A2"] = COLORS["dark_red_1"]
                st.session_state.well_colors["A3"] = COLORS["dark_red_2"]
                st.session_state.added_reagents['A'] = True
            def mk_B(): 
                st.session_state.active_animation = 'B'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                st.session_state.well_colors["B2"] = COLORS["dark_red_1"]
                st.session_state.well_colors["B3"] = COLORS["dark_red_2"]
                st.session_state.added_reagents['B'] = True
            def mk_C(): 
                st.session_state.active_animation = 'C'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                st.session_state.well_colors["C2"] = COLORS["orange"]
                st.session_state.well_colors["C3"] = COLORS["pale_yellow"]
                st.session_state.added_reagents['C'] = True
            def mk_D(): 
                st.session_state.active_animation = 'D'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                st.session_state.well_colors["D2"] = COLORS["orange"]
                st.session_state.well_colors["D3"] = COLORS["pale_yellow"]
                st.session_state.added_reagents['D'] = True

            st.caption(f"{lbl.get('A2', '')} (1 gota Fe³⁺); {lbl.get('A3', '')} (2 gotas Fe³⁺)")
            if not st.session_state.added_reagents['A']: st.button("Adicionar Trinitrato de Ferro — Fe(NO₃)₃", on_click=mk_A)
            st.caption(f"{lbl.get('B2', '')} (1 gota SCN⁻); {lbl.get('B3', '')} (2 gotas SCN⁻)")
            if not st.session_state.added_reagents['B']: st.button("Adicionar Tiocianato de Potássio — KSCN", on_click=mk_B)
            st.caption(f"{lbl.get('C2', '')} (1 gota Ag⁺); {lbl.get('C3', '')} (2 gotas Ag⁺)")
            if not st.session_state.added_reagents['C']: st.button("Adicionar Nitrato de Prata — AgNO₃", on_click=mk_C)
            st.caption(f"{lbl.get('D2', '')} (1 gota Oxalato); {lbl.get('D3', '')} (2 gotas Oxalato)")
            if not st.session_state.added_reagents['D']: st.button("Adicionar Oxalato de Dissódio — Na₂C₂O₄", on_click=mk_D)

            if all(st.session_state.added_reagents.values()):
                st.success("Reagentes adicionados.")

        with st.expander("📋 Registo de Cores Finais", expanded=(st.session_state.step >= 4 and all(st.session_state.added_reagents.values()))):
            def get_color_name(hex_code):
                mapping = {"#c41b1b": "Vermelho", "#8a0c0c": "Vermelho intenso", "#4a0505": "Vermelho escuro", "#d18f2e": "Alaranjado", "#f0e6b6": "Amarelo claro"}
                return mapping.get(hex_code, "Incolor")
            if all(st.session_state.added_reagents.values()):
                df = pd.DataFrame({
                    "Adicionado (aq)": ["Fe(NO₃)₃", "KSCN", "AgNO₃", "Na₂C₂O₄"],
                    "Controlo": [f"[{lbl.get(f'{r}1', '')}] {get_color_name(st.session_state.well_colors[f'{r}1'])}" for r in ['A','B','C','D']],
                    "1 Gota Adicionada": [f"[{lbl.get(f'{r}2', '')}] {get_color_name(st.session_state.well_colors[f'{r}2'])}" for r in ['A','B','C','D']],
                    "2 Gotas Adicionadas": [f"[{lbl.get(f'{r}3', '')}] {get_color_name(st.session_state.well_colors[f'{r}3'])}" for r in ['A','B','C','D']]
                })
                st.dataframe(df, hide_index=True)


    # ----------------------------------------------------
    # MODO PRÁTICO-EXPERIMENTAL
    # ----------------------------------------------------
    else:
        st.subheader("Modo Prático: BANCADA DO ALUNO")

        # FASE 1: MATERIAL
        with st.expander("1. Seleção de Material Escolar", expanded=(st.session_state.p_step == 1)):
            if st.session_state.p_step == 1:
                st.write("Assinale o material necessário para realizar a atividade segundo o protocolo:")
                target_mat = {"Placa de microanálise", "Conta-gotas", "Microvaretas", "Óculos de Proteção"}
                distractors = {"Gobelé", "Erlenmeyer", "Placa de aquecimento"}
                
                ops = ["Placa de microanálise", "Gobelé", "Conta-gotas", "Erlenmeyer", "Óculos de Proteção", "Placa de aquecimento", "Microvaretas"]
                sels = st.multiselect("Bancada disponível:", ops)

                if st.button("Confirmar Material"):
                    sels_set = set(sels)
                    if sels_set == target_mat:
                        st.success("✅ Excelente! Reuniu o equipamento certo.")
                        st.session_state.p_step = 2
                        st.rerun()
                    else:
                        misses = target_mat - sels_set
                        extras = sels_set - target_mat
                        if extras: st.error("❌ Escolheu material desnecessário (Ex: Gobelé, Erlenmeyer, etc).")
                        elif misses: st.warning("⚠️ Faltam itens vitais (Esqueceu-se da placa, varetas, óculos ou conta-gotas?).")
            else:
                st.success("✅ Material Escolar Separado.")

        # FASE 2: REAGENTES
        with st.expander("2. Seleção de Reagentes", expanded=(st.session_state.p_step == 2)):
            if st.session_state.p_step == 2:
                st.write("Identifique no armário os reagentes necessários para formar e perturbar o [FeSCN]²⁺:")
                reagents_all = ["Fe(NO₃)₃ (aq)", "NaCl (aq)", "KSCN (aq)", "HCl (aq)", "AgNO₃ (aq)", "CuSO₄ (aq)", "Na₂C₂O₄ (aq)", "Água destilada"]
                target_reagents = {"Fe(NO₃)₃ (aq)", "KSCN (aq)", "AgNO₃ (aq)", "Na₂C₂O₄ (aq)", "Água destilada"}
                
                rsels = st.multiselect("Armário de Químicos:", reagents_all)
                if st.button("Confirmar Reagentes"):
                    rset = set(rsels)
                    if rset == target_reagents:
                        st.success("✅ Perfeito.")
                        st.session_state.p_step = 3
                        st.rerun()
                    else:
                        st.error("Reagentes inválidos. Reveja o protocolo.")
            elif st.session_state.p_step > 2:
                st.success("✅ Reagentes Separados.")

        # FASE 3: PIPETAGEM LIVRE
        with st.expander("3. Estação de Adição Dinâmica", expanded=(st.session_state.p_step == 3)):
            if st.session_state.p_step == 3:
                st.info("Adicione os volumes livremente e observe o desenrolar das reações termodinâmicas.")
                p_reag = st.selectbox("Reagente a aplicar:", ["Fe(NO₃)₃ (aq)", "KSCN (aq)", "AgNO₃ (aq)", "Na₂C₂O₄ (aq)", "Água destilada"])
                p_drops = st.number_input("Nº de Gotas:", 1, 10, 1)
                
                st.markdown("**Atalhos de Seleção Múltipla:**")
                sc = st.columns(4)
                all_w = [f"{r}{c}" for r in ['A','B','C','D'] for c in [1,2,3]]
                def _sel(ww): st.session_state.selected_wells_ui = ww
                sc[0].button("Toda a Placa", on_click=_sel, args=(all_w,))
                sc[1].button("Toda Linha A", on_click=_sel, args=([f"A{c}" for c in [1,2,3]],))
                sc[2].button("Toda Coluna 1", on_click=_sel, args=([f"{r}1" for r in ['A','B','C','D']],))
                sc[3].button("Limpar Alvos", on_click=_sel, args=([],))

                st.multiselect("Cavidades Alvo Específicas:", all_w, key="selected_wells_ui")
                
                if st.button("💉 Pipetar Reagente para Alvos", type="primary"):
                    apply_practical_dispenser(p_reag, p_drops)


with col2:
    st.subheader("Placa de Microanálise")
    render_microplate(
        st.session_state.well_colors, 
        active_animation=current_animation,
        custom_labels=st.session_state.custom_labels,
        prev_well_colors=st.session_state.prev_well_colors
    )

    _, colB, _ = st.columns([1,1,1])
    with colB:
        st.button("🔄 Reiniciar Ambiente", on_click=reset_simulation)
