# 🧪 Simulador: Efeito da Concentração no Equilíbrio Químico

Este simulador interativo foi desenvolvido em Python utilizando o framework **Streamlit** para apoiar o estudo do equilíbrio químico em sistemas aquosos, especificamente focado no Princípio de Le Châtelier.

O simulador reproduz o protocolo experimental da **Atividade Laboratorial 2**, investigando a reação entre o ião ferro(III), Fe³⁺, e o ião tiocianato, SCN⁻.

## 🌟 Funcionalidades

- **Identificação Livre de Cavidades**: O utilizador pode nomear as cavidades da placa de microanálise de forma personalizada (ex: AA, 11, WX), promovendo a atenção espacial.
- **Animações Realistas**: Inclui animações de conta-gotas e microvareta de agitação.
- **Mistura Gradual de Cores**: A cor da solução homogeniza gradualmente durante a agitação, simulando o comportamento físico real.
- **Registo Automático**: Gera uma tabela de observações final com nomes de cores simplificados para facilitar a análise.
- **Nomenclatura Química Rigorosa**: Utiliza tanto as fórmulas como os nomes por extenso dos compostos.

## 🧪 Equilíbrio em Estudo

O sistema homogéneo foca-se na seguinte reação:

**Fe³⁺ (aq)** *(Amarelo)* **+ SCN⁻ (aq)** *(Incolor)* **⇌ [FeSCN]²⁺ (aq)** *(Vermelho)*

---

## 🚀 Como Executar Localmente

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/ruiblev/equilibrio_quimico.git
   cd equilibrio_quimico
   ```

2. **Executar o script de arranque:**
   ```bash
   ./run.sh
   ```
   *(O script verificará as dependências e iniciará o servidor Streamlit automaticamente).*

---

## 🛠️ Tecnologias Utilizadas

- **Python**: Lógica da aplicação.
- **Streamlit**: Framework de interface web.
- **HTML/CSS (via st.components.v1)**: Renderização da placa de microanálise e animações customizadas.
- **Pandas**: Gestão dos dados da tabela final.

---

## 📚 Enquadramento Escolar
Baseado no protocolo laboratorial da Atividade Laboratorial 2: "Efeito da concentração no equilíbrio químico".
