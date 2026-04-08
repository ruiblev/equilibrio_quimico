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

st.markdown("""
<style>
div[data-testid="column"]:nth-of-type(2), 
div[data-testid="stColumn"]:nth-of-type(2) {
    position: sticky !important;
    top: 60px !important;
    align-self: flex-start !important;
    z-index: 100;
}
</style>
""", unsafe_allow_html=True)

# --- Constantes de Cores ---
COLORS = {
    "empty": "transparent",
    "red": "#c0392b",           # vermelho-vivo (Col 1 base)
    "dark_red_1": "#7b0c0c",   # vermelho mais intenso (A/B col 2 & 3)
    "white_ppt": "#e0dfd9",    # precipitado branco opaco (C col 2 & 3)
    "yellow_fe": "#c9a227",    # amarelado Fe³⁺ (D col 2 & 3)
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

if 'p_substep' not in st.session_state:
    st.session_state.p_substep = 1

if 'p_feedback' not in st.session_state:
    st.session_state.p_feedback = None

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
    if st.session_state.sim_mode == "Modo Prático-Experimental":
        st.session_state.p_substep = 1
        st.session_state.p_feedback = None
        st.session_state.well_colors = {f"{r}{c}": COLORS["empty"] for r in ['A', 'B', 'C', 'D'] for c in [1, 2, 3]}
        st.session_state.prev_well_colors = st.session_state.well_colors.copy()
        st.session_state.well_contents = {
            f"{r}{c}": {"Fe3+": 0, "SCN-": 0, "Ag+": 0, "C2O4_2-": 0, "H2O": 0}
            for r in ['A', 'B', 'C', 'D'] for c in [1, 2, 3]
        }
        st.session_state.selected_wells_ui = []
    else:
        reset_all_state()

# --- FUNÇÕES CALCULADORAS DO MODO PRÁTICO ---
def lerp_color(hex1, hex2, t):
    """Interpolação linear entre duas cores hex. t=0 retorna hex1, t=1 retorna hex2."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(hex1[1:3],16), int(hex1[3:5],16), int(hex1[5:7],16)
    r2, g2, b2 = int(hex2[1:3],16), int(hex2[3:5],16), int(hex2[5:7],16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def calculate_color(c):
    fe  = c["Fe3+"]
    scn = c["SCN-"]
    ag  = c["Ag+"]
    ox  = c["C2O4_2-"]
    
    # Sem reagentes base → vazio
    if fe == 0 and scn == 0:
        return COLORS["empty"]

    # Ag+ precipita SCN⁻ → branco opaco (sem gradiente, é precipitado sólido)
    active_scn = max(0, scn - ag)
    active_fe  = max(0, fe - ox)
    
    if ag > 0 and active_scn == 0:
        return COLORS["white_ppt"]
    
    # Oxalato removeu todo o Fe³⁺ → amarelo com intensidade crescente com ox
    if ox > 0 and active_fe == 0:
        # ox=1 → amarelo suave; ox alto → amarelo mais intenso/saturado
        t = min(1.0, (ox - 1) / 4.0)  # satura ao 5º excesso
        return lerp_color("#c9a227", "#b8860b", t)
    
    # Equilíbrio com ambos os reagentes ativos: vermelho crescente
    if active_fe > 0 and active_scn > 0:
        # Base: 1 gota Fe + 1 gota SCN = vermelho-vivo
        # Quanto mais Fe ou SCN adicionado, mais intenso
        intensity = (active_fe + active_scn) - 2  # começa em 0 para o par base (1+1)
        t = min(1.0, intensity / 6.0)              # satura com 6 gotas de excesso
        return lerp_color("#c0392b", "#5c0606", t)
    
    # Caso residual (fe ou scn sozinhos)
    return COLORS["yellow_fe"]

def apply_practical_dispenser(reagent, drops):
    selected = st.session_state.selected_wells_ui
    if not selected:
        st.session_state.p_feedback = {"type": "warning", "msg": "Selecione pelo menos uma cavidade alvo!"}
        return

    key_map = {
        "Fe(NO₃)₃ (aq)": "Fe3+",
        "KSCN (aq)": "SCN-",
        "AgNO₃ (aq)": "Ag+",
        "Na₂C₂O₄ (aq)": "C2O4_2-",
        "Água destilada": "H2O"
    }
    k = key_map[reagent]

    # Validação do Supervisor Secreto
    if st.session_state.p_substep == 1:
        if k not in ["Fe3+", "SCN-"]:
            st.session_state.p_feedback = {"type": "error", "msg": "Dica: Será prudente adicionar reagentes de perturbação ou solventes antes de formar o complexo base colorido [FeSCN]²⁺ em toda a placa?"}
            return
            
    elif st.session_state.p_substep == 2:
        if k != "H2O":
            st.session_state.p_feedback = {"type": "error", "msg": "Dica: Estudar os efeitos das concentrações exige rigor de volume inicial. Consulta o guião... não terás de equiparar os níveis da solução usando alguma porção do solvente universal?"}
            return

    st.session_state.p_feedback = {"type": "success", "msg": "Adição processada com sucesso."}
    st.session_state.active_animation = selected
    st.session_state.prev_well_colors = st.session_state.well_colors.copy()
    
    for w in selected:
        st.session_state.well_contents[w][k] += drops
        st.session_state.well_colors[w] = calculate_color(st.session_state.well_contents[w])

    # Validação de Missão Cumprida para avançar
    all_w = [f"{r}{c}" for r in ['A','B','C','D'] for c in [1,2,3]]
    if st.session_state.p_substep == 1:
        has_eq = all(st.session_state.well_contents[w]["Fe3+"] > 0 and st.session_state.well_contents[w]["SCN-"] > 0 for w in all_w)
        if has_eq:
            st.session_state.p_substep = 2
            st.session_state.p_feedback = {"type": "success", "msg": "Excelente! Equilíbrio padrão criado em toda a placa. Pronto para a fase de nivelamento de volumes."}
            
    elif st.session_state.p_substep == 2:
        has_water = any(st.session_state.well_contents[w]["H2O"] > 0 for w in all_w)
        if has_water:
            st.session_state.p_substep = 3
            st.session_state.p_feedback = {"type": "success", "msg": "Nivelamento atingido! Está agora desbloqueado(a) para executar adições perturbadoras nas cavidades à sua escolha."}


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
                # 1 gota -> intensidade leve, 2 gotas -> mais intenso
                st.session_state.well_colors["A2"] = lerp_color("#c0392b", "#5c0606", 2/6)
                st.session_state.well_colors["A3"] = lerp_color("#c0392b", "#5c0606", 4/6)
                st.session_state.added_reagents['A'] = True
            def mk_B(): 
                st.session_state.active_animation = 'B'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                st.session_state.well_colors["B2"] = lerp_color("#c0392b", "#5c0606", 2/6)
                st.session_state.well_colors["B3"] = lerp_color("#c0392b", "#5c0606", 4/6)
                st.session_state.added_reagents['B'] = True
            def mk_C(): 
                st.session_state.active_animation = 'C'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                st.session_state.well_colors["C2"] = COLORS["white_ppt"]
                st.session_state.well_colors["C3"] = COLORS["white_ppt"]
                st.session_state.added_reagents['C'] = True
            def mk_D(): 
                st.session_state.active_animation = 'D'
                st.session_state.prev_well_colors = st.session_state.well_colors.copy()
                # 1 gota -> amarelo base, 2 gotas -> amarelo mais intenso
                st.session_state.well_colors["D2"] = lerp_color("#c9a227", "#b8860b", 0/4)
                st.session_state.well_colors["D3"] = lerp_color("#c9a227", "#b8860b", 1/4)
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
                # Mapeia de forma aproximada para nomes simples
                if hex_code in ("transparent", ""):
                    return "Incolor"
                r, g, b = int(hex_code[1:3],16), int(hex_code[3:5],16), int(hex_code[5:7],16)
                if r > 150 and g < 80 and b < 80:
                    brightness = (g + b) / (2 * r + 0.01)
                    if brightness < 0.1: return "Vermelho intenso"
                    return "Vermelho-vivo"
                if r > 140 and g > 100 and b < 60:
                    return "Amarelado (Fe³⁺)"
                if r > 200 and g > 200 and b > 180:
                    return "Precipitado branco opaco"
                return "Incolor"
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
        with st.expander("1. Seleção de Material", expanded=(st.session_state.p_step == 1)):
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

        # FASE 3: IDENTIFICAÇÃO DE CAVIDADES (P_STEP 3)
        with st.expander("3. Identificação de Cavidades", expanded=(st.session_state.p_step == 3)):
            if st.session_state.p_step == 3:
                st.write("Identifique as cavidades para referência futura:")
                
                col_btn, _ = st.columns([1, 1])
                with col_btn:
                    if st.button("⚡ Preenchimento Automático (A1-D3)", key="auto_fill_p"):
                        st.session_state.custom_labels = {f"{r}{c}": f"{r}{c}" for r in ['A','B','C','D'] for c in [1,2,3]}
                        next_p_step()
                        st.rerun()
                        
                valid_p = True
                temp_labels_p = {}
                distinct_check_p = set()
                empty_count_p = 0
                has_duplicates_p = False
                
                for row in ['A', 'B', 'C', 'D']:
                    r_cols = st.columns([1, 1, 1])
                    for i, col_idx in enumerate([1, 2, 3]):
                        with r_cols[i]:
                            key = f"{row}{col_idx}"
                            val = st.text_input("Cav", key=f"p_in_{key}", label_visibility="collapsed")
                            v_strip = val.strip().upper()
                            if not v_strip:
                                valid_p = False
                                empty_count_p += 1
                            elif v_strip in distinct_check_p:
                                valid_p = False
                                has_duplicates_p += True
                            else:
                                temp_labels_p[key] = v_strip
                                distinct_check_p.add(v_strip)
                st.markdown("---")
                if valid_p and len(temp_labels_p) == 12:
                    st.success("✅ Identificações únicas validadas!")
                    def confirm_p_labels():
                        st.session_state.custom_labels = temp_labels_p
                        next_p_step()
                    st.button("Confirmar Nomenclatura ➔", on_click=confirm_p_labels, type="primary")
                else:
                    if empty_count_p < 12 and (empty_count_p > 0 or has_duplicates_p):
                        if empty_count_p > 0 and has_duplicates_p:
                            st.error(f"⚠️ Erro: Faltam preencher {empty_count_p} cavidade(s). E existem duplicações.")
                        elif empty_count_p > 0:
                            st.warning(f"⚠️ Atenção: Preencha as {empty_count_p} cavidade(s) vazia(s).")
                        elif has_duplicates_p:
                            st.error("⚠️ Atenção: Há referências repetidas.")
            elif st.session_state.p_step > 3:
                st.success("✅ Cavidades identificadas.")

        # FASE 4: PIPETAGEM LIVRE
        with st.expander("4. Estação de Adição Dinâmica", expanded=(st.session_state.p_step == 4)):
            if st.session_state.p_step == 4:
                st.info("Adicione os volumes livremente e observe o desenrolar das reações.")
                if st.session_state.p_substep == 1:
                    st.caption("Fase Atual: Criar Equilíbrio [FeSCN]²⁺ em toda a placa.")
                elif st.session_state.p_substep == 2:
                    st.caption("Fase Atual: Nivelamento de Volumes.")
                elif st.session_state.p_substep == 3:
                    st.caption("Fase Atual: Perturbações (Livre Estudante).")

                if st.session_state.p_feedback:
                    fb = st.session_state.p_feedback
                    if fb["type"] == "error": st.error(fb["msg"])
                    elif fb["type"] == "warning": st.warning(fb["msg"])
                    elif fb["type"] == "success": st.success(fb["msg"])

                p_reag = st.selectbox("Reagente a aplicar:", ["Fe(NO₃)₃ (aq)", "KSCN (aq)", "AgNO₃ (aq)", "Na₂C₂O₄ (aq)", "Água destilada"])
                p_drops = st.number_input("Nº de Gotas:", 1, 10, 1)
                
                st.markdown("**Atalhos de Seleção Múltipla:**")
                sc = st.columns(4)
                all_w = [f"{r}{c}" for r in ['A','B','C','D'] for c in [1,2,3]]
                def _sel(ww): 
                    st.session_state.selected_wells_ui = ww
                
                sc[0].button("Toda a Placa", on_click=_sel, args=(all_w,))
                
                with sc[1]:
                    linha_op = st.selectbox("Linha a selecionar:", ["-", "1ª Linha", "2ª Linha", "3ª Linha", "4ª Linha"], label_visibility="collapsed")
                    if linha_op != "-" and st.button("Aplicar Linha"):
                        r_map = {"1ª Linha": 'A', "2ª Linha": 'B', "3ª Linha": 'C', "4ª Linha": 'D'}
                        row_char = r_map[linha_op]
                        _sel([f"{row_char}{c}" for c in [1,2,3]])
                
                with sc[2]:
                    col_op = st.selectbox("Coluna a selecionar:", ["-", "1ª Coluna", "2ª Coluna", "3ª Coluna"], label_visibility="collapsed")
                    if col_op != "-" and st.button("Aplicar Coluna"):
                        c_num = col_op.split("ª")[0]
                        _sel([f"{r}{c_num}" for r in ['A','B','C','D']])

                sc[3].button("Limpar Alvos", on_click=_sel, args=([],))

                def name_fmt(w):
                    return st.session_state.custom_labels.get(w, w)

                st.multiselect("Cavidades Alvo Específicas:", all_w, format_func=name_fmt, key="selected_wells_ui")
                
                st.button("💉 Pipetar Reagente para Alvos", type="primary", on_click=apply_practical_dispenser, args=(p_reag, p_drops))

                # --- Deteção de Conclusão Automática ---
                if st.session_state.p_substep == 3:
                    wc = st.session_state.well_contents
                    all_w = [f"{r}{c}" for r in ['A','B','C','D'] for c in [1,2,3]]
                    # Verifica se cada tipo de perturbação já foi aplicada pelo menos uma vez
                    has_extra_fe  = any(wc[w]["Fe3+"] > 1 for w in all_w)   # Fe extra além do base
                    has_extra_scn = any(wc[w]["SCN-"] > 1 for w in all_w)   # SCN extra além do base
                    has_ag        = any(wc[w]["Ag+"]  > 0 for w in all_w)   # Prata adicionada
                    has_ox        = any(wc[w]["C2O4_2-"] > 0 for w in all_w) # Oxalato adicionado
                    
                    all_done = has_extra_fe and has_extra_scn and has_ag and has_ox
                    
                    if all_done:
                        st.markdown("---")
                        st.success(
                            "🎉 **Atividade concluída!** Todas as reações previstas pelo Princípio de Le Châtelier "
                            "foram observadas na placa.\n\n"
                            "📋 **Próximo passo:** Realize o registo das observações no guião laboratorial, "
                            "descrevendo as cores observadas em cada cavidade e justificando o deslocamento "
                            "do equilíbrio com base na perturbação efetuada."
                        )
                    else:
                        # Mostra o progresso das reações em falta
                        missing = []
                        if not has_extra_fe:  missing.append("excesso de Fe(NO₃)₃")
                        if not has_extra_scn: missing.append("excesso de KSCN")
                        if not has_ag:        missing.append("AgNO₃")
                        if not has_ox:        missing.append("Na₂C₂O₄")
                        st.info(f"📊 Perturbações em falta: **{', '.join(missing)}**")


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

