"""
NORCONSULT BÆREEVNEBEREGNING
Geoteknisk bæreevneanalyse iht. Eurokode 7 (NS-EN 1997-1)
"""

import streamlit as st
import numpy as np
from datetime import datetime

from models import JordParameter, FundamentGeometri, Belastning, TerrengForhold
from calculator import BaereevneKalkulator
from visualizations import lag_fundament_figur, lag_utnyttelse_gauge
from report import generer_rapport_html

st.set_page_config(
    page_title="Bæreevne | Norconsult",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
    
    .stApp { background: linear-gradient(135deg, #f8faf9 0%, #f0f4f2 100%); }
    
    .main-header {
        background: linear-gradient(135deg, #006341 0%, #004d32 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 99, 65, 0.15);
    }
    .main-header h1 { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.85); font-size: 1rem; margin: 0.3rem 0 0 0; }
    
    .result-card {
        background: white;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e0e7e3;
        margin-bottom: 0.5rem;
    }
    .result-card.success { border-left: 4px solid #2e7d32; }
    .result-card.warning { border-left: 4px solid #f57c00; }
    .result-card.danger { border-left: 4px solid #c62828; }
    
    .result-label {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .result-value { font-size: 1.8rem; font-weight: 600; color: #1a1a2e; }
    .result-unit { font-size: 0.9rem; color: #666; margin-left: 4px; }
    
    .utilization-bar {
        height: 6px;
        background: #e0e0e0;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 0.6rem;
    }
    .utilization-fill { height: 100%; border-radius: 3px; }
    
    .status-ok {
        display: inline-block;
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-fail {
        display: inline-block;
        background: #ffebee;
        color: #c62828;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .project-info {
        background: #f5f5f5;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 1rem;
        border-left: 3px solid #006341;
    }
    .project-info strong { color: #006341; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ Geoteknisk Bæreevneberegning</h1>
        <p>Analyse iht. NS-EN 1997-1 (Eurokode 7) • Brinch Hansen's metode</p>
    </div>
    """, unsafe_allow_html=True)
    
    kalkulator = BaereevneKalkulator()
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("### 📋 Prosjektinfo")
        prosjekt_info = {
            'prosjektnummer': st.text_input("Prosjektnummer", placeholder="f.eks. 5200001"),
            'prosjektnavn': st.text_input("Prosjektnavn", placeholder="f.eks. E39 Rogfast"),
            'beregningsnavn': st.text_input("Beregningsnavn", placeholder="f.eks. Fund. F1"),
            'utfort_av': st.text_input("Utført av", placeholder="Initialer"),
            'revisjon': st.text_input("Revisjon", value="0")
        }
        
        st.markdown("---")
        st.markdown("### ⚙️ Analysetype")
        analysetype = st.radio(
            "Metode",
            ['effektiv', 'udrenert'],
            format_func=lambda x: "Effektivsp. (drenert)" if x == 'effektiv' else "Totalsp. (udrenert)",
            horizontal=True
        )
        
        st.markdown("### 🧱 Fundamenttype")
        fund_type = st.radio(
            "Type",
            ['stripe', 'rektangulær'],
            format_func=lambda x: "Stripe" if x == 'stripe' else "Rektangulær",
            horizontal=True
        )
        
        st.markdown("---")
        st.markdown("### 📤 Eksport")
        export_btn = st.button("📄 Generer rapport", use_container_width=True)
    
    if prosjekt_info['prosjektnummer'] or prosjekt_info['prosjektnavn']:
        st.markdown(f"""
        <div class="project-info">
            <strong>{prosjekt_info.get('prosjektnummer', '')}</strong> - 
            {prosjekt_info.get('prosjektnavn', '')}
            {f" | {prosjekt_info.get('beregningsnavn', '')}" if prosjekt_info.get('beregningsnavn') else ""}
        </div>
        """, unsafe_allow_html=True)
    
    # INPUT
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🌍 Jordparametre")
        if analysetype == 'effektiv':
            phi = st.number_input("Friksjonsvinkel, φ' [°]", 0.0, 50.0, 33.0, 0.5)
            su = 0.0
            gamma_eff = st.number_input("Effektiv romvekt, γ' [kN/m³]", 0.0, 25.0, 10.0, 0.5)
            attraksjon = st.number_input("Attraksjon, a [kN/m²]", 0.0, 50.0, 0.0, 1.0)
        else:
            phi = 0.0
            su = st.number_input("Udrenert skjærstyrke, su [kN/m²]", 0.0, 500.0, 50.0, 5.0)
            gamma_eff = 0.0
            attraksjon = 0.0
        
        gamma_M = st.number_input("Materialfaktor, γM [-]", 1.0, 2.0, 1.4, 0.05)
        
        st.markdown("---")
        st.markdown("#### Terrengforhold")
        D = st.number_input("Fundamentdybde, D [m]", 0.0, 10.0, 1.0, 0.1)
        gamma_jord = st.number_input("Romvekt over fund. [kN/m³]", 0.0, 25.0, 18.0, 0.5)
        q0 = st.number_input("Overflatelast, q₀ [kN/m²]", 0.0, 100.0, 0.0, 1.0)
        beta_s = st.number_input("Skråningshelning, βs [°]", 0.0, 45.0, 0.0, 1.0)
    
    with col2:
        st.markdown("### 🧱 Fundament")
        B = st.number_input("Bredde, B [m]", 0.1, 20.0, 2.0, 0.1)
        
        if fund_type == 'rektangulær':
            L = st.number_input("Lengde, L [m]", 0.1, 50.0, 4.0, 0.1)
            if L < B:
                st.warning("⚠️ L bør være ≥ B")
        else:
            L = None
            st.info("ℹ️ Stripefund.: Per løpemeter")
        
        T = st.number_input("Tykkelse, T [m]", 0.1, 3.0, 0.5, 0.05)
        gamma_c = st.number_input("Romvekt betong [kN/m³]", 20.0, 30.0, 25.0, 0.5)
        
        st.markdown("---")
        st.markdown("#### Konstruksjon")
        
        if fund_type == 'stripe':
            bs = st.number_input("Veggtykkelse [m]", 0.0, 1.0, 0.2, 0.02)
            Ls = 1.0
        else:
            bs = st.number_input("Søylebredde [m]", 0.0, 2.0, 0.4, 0.05)
            Ls = st.number_input("Søylelengde [m]", 0.0, 2.0, 0.4, 0.05)
    
    # Kolonne 3: Belastning
    with col3:
        st.markdown("### ⬇️ Belastning")
        
        enhet_kraft = "kN/m" if fund_type == 'stripe' else "kN"
        enhet_moment = "kNm/m" if fund_type == 'stripe' else "kNm"
        
        V = st.number_input(f"Vertikallast, V [{enhet_kraft}]", 0.0, 50000.0, 500.0, 10.0,
                           help="Ekskl. fundamentvekt")
        H_B = st.number_input(f"Horisontallast, H [{enhet_kraft}]", -5000.0, 5000.0, 0.0, 5.0)
        M_B = st.number_input(f"Moment, M [{enhet_moment}]", -10000.0, 10000.0, 0.0, 10.0)
        
        if fund_type == 'rektangulær':
            H_L = st.number_input(f"Horisontallast L-retn. [{enhet_kraft}]", -5000.0, 5000.0, 0.0, 5.0)
            M_L = st.number_input(f"Moment L-retn. [{enhet_moment}]", -10000.0, 10000.0, 0.0, 10.0)
        else:
            H_L = 0.0
            M_L = 0.0
        
        st.markdown("---")
        st.markdown("#### Eksentrisitet")
        e_input_B = st.number_input("Centeravvik B [m]", -5.0, 5.0, 0.0, 0.01)
        if fund_type == 'rektangulær':
            e_input_L = st.number_input("Centeravvik L [m]", -5.0, 5.0, 0.0, 0.01)
        else:
            e_input_L = 0.0
    
    # === BEREGNING ===
    st.markdown("---")
    
    # Opprett objekter
    jord = JordParameter(
        analysetype=analysetype,
        friksjonsvinkel=phi,
        udrenert_skjaerstyrke=su,
        romvekt_eff=gamma_eff,
        attraksjon=attraksjon,
        materialfaktor=gamma_M
    )
    
    fundament = FundamentGeometri(
        bredde=B,
        lengde=L,
        tykkelse=T,
        romvekt=gamma_c,
        vegg_bredde=bs,
        soyle_lengde=Ls
    )
    
    belastning = Belastning(
        vertikal=V,
        horisontal_B=H_B,
        horisontal_L=H_L,
        moment_B=M_B,
        moment_L=M_L,
        centeravvik_B=e_input_B,
        centeravvik_L=e_input_L
    )
    
    if analysetype == 'effektiv':
        phi_d = np.degrees(np.arctan(np.tan(np.radians(phi)) / gamma_M))
        Ka, Kp = kalkulator.beregn_jordtrykkskoeffisienter(phi_d)
    else:
        Ka, Kp = 0.5, 2.0
    
    terreng = TerrengForhold(
        fundamentdybde=D,
        romvekt_over=gamma_jord,
        overflatelast=q0,
        skraaningshelning=beta_s,
        terrenghelning=0.0,
        Ka=Ka,
        Kp=Kp
    )
    
    # Kjør beregning
    try:
        resultat = kalkulator.beregn(jord, fundament, belastning, terreng)
        beregning_ok = True
    except Exception as e:
        st.error(f"Beregningsfeil: {str(e)}")
        beregning_ok = False
        resultat = None
    
    # === VIS RESULTATER ===
    if beregning_ok and resultat:
        st.markdown("## 📊 Resultater")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-label">Grunntrykk</div>
                <div class="result-value">{resultat.grunntrykk:.1f}<span class="result-unit">kN/m²</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with res_col2:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-label">Bæreevne</div>
                <div class="result-value">{resultat.baereevne:.1f}<span class="result-unit">kN/m²</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with res_col3:
            if resultat.utnyttelsesgrad <= 0.7:
                status_class = "success"
                status_text = "OK"
                bar_color = "#2e7d32"
            elif resultat.utnyttelsesgrad <= 1.0:
                status_class = "warning"
                status_text = "OK (marginal)"
                bar_color = "#f57c00"
            else:
                status_class = "danger"
                status_text = "IKKE OK"
                bar_color = "#c62828"
            
            utn_pct = resultat.utnyttelsesgrad * 100
            bar_width = min(utn_pct, 100)
            
            st.markdown(f"""
            <div class="result-card {status_class}">
                <div class="result-label">Utnyttelsesgrad</div>
                <div class="result-value">{utn_pct:.1f}<span class="result-unit">%</span></div>
                <div class="utilization-bar">
                    <div class="utilization-fill" style="width: {bar_width}%; background: {bar_color};"></div>
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="status-{'ok' if status_class != 'danger' else 'fail'}">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Figurer
        fig_col, gauge_col = st.columns([1.2, 0.8])
        
        with fig_col:
            st.markdown("#### Fundamenttverrsnitt")
            fig = lag_fundament_figur(fundament, terreng, resultat, belastning)
            st.plotly_chart(fig, use_container_width=True)
        
        with gauge_col:
            st.markdown("#### Kapasitetsutnyttelse")
            gauge = lag_utnyttelse_gauge(resultat.utnyttelsesgrad)
            st.plotly_chart(gauge, use_container_width=True)
        
        # Detaljer
        st.markdown("---")
        st.markdown("### 📋 Detaljer")
        
        d1, d2, d3 = st.columns(3)
        
        with d1:
            st.markdown("#### Effektivt areal")
            data1 = {
                "Parameter": ["Eksentrisitet e_B", "Effektiv bredde Bo"],
                "Verdi": [f"{resultat.eksentrisitet_B:.3f}", f"{resultat.eff_bredde:.3f}"],
                "Enhet": ["m", "m"]
            }
            if resultat.eff_lengde:
                data1["Parameter"].extend(["Eksentrisitet e_L", "Effektiv lengde Lo", "Effektivt areal"])
                data1["Verdi"].extend([f"{resultat.eksentrisitet_L:.3f}", f"{resultat.eff_lengde:.3f}", 
                                       f"{resultat.eff_bredde * resultat.eff_lengde:.3f}"])
                data1["Enhet"].extend(["m", "m", "m²"])
            st.table(data1)
        
        with d2:
            st.markdown("#### Bæreevnefaktorer")
            if resultat.Nq is not None:
                data2 = {
                    "Parameter": ["Nq", "Nγ", "Ruhet r", "Skråningsred. fβ"],
                    "Verdi": [f"{resultat.Nq:.2f}", f"{resultat.Ny:.2f}", 
                             f"{resultat.ruhet:.3f}", f"{resultat.reduksjonsfaktor:.3f}"]
                }
            else:
                data2 = {
                    "Parameter": ["Nc", "Ruhet r", "Skråningsred. fβ"],
                    "Verdi": [f"{resultat.Nc:.2f}", f"{resultat.ruhet:.3f}", 
                             f"{resultat.reduksjonsfaktor:.3f}"]
                }
            st.table(data2)
        
        with d3:
            st.markdown("#### Kontroll")
            e_B_ratio = abs(resultat.eksentrisitet_B) / B
            data3 = {
                "Kontroll": ["q/s ≤ 1.0", "e_B/B ≤ 1/3"],
                "Verdi": [f"{resultat.utnyttelsesgrad:.3f}", f"{e_B_ratio:.3f}"],
                "Status": ["✅" if resultat.utnyttelsesgrad <= 1.0 else "❌",
                          "✅" if e_B_ratio <= 1/3 else "⚠️"]
            }
            st.table(data3)
            
            if e_B_ratio > 1/3:
                st.warning("⚠️ e > B/3: Gapping under fundament")
            if resultat.ruhet > 0.9:
                st.warning("⚠️ r > 0.9: Nær glidning")
        
        # Eksport
        if export_btn:
            html = generer_rapport_html(prosjekt_info, jord, fundament, belastning, terreng, resultat)
            
            filnavn = f"baereevne_{prosjekt_info.get('prosjektnummer', 'rapport')}_{datetime.now().strftime('%Y%m%d')}.html"
            
            st.download_button(
                label="📥 Last ned rapport (HTML)",
                data=html,
                file_name=filnavn,
                mime="text/html"
            )
            st.info("💡 Åpne HTML i nettleser → Skriv ut → Lagre som PDF")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.85rem; padding: 1rem 0;">
        <strong>Norconsult Bæreevneberegning</strong> v1.0<br>
        NS-EN 1997-1 (Eurokode 7) • Brinch Hansen's metode
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()0, 25.0, 0.5)
        
        st.markdown("---")
        st.markdown("#### Konstruksjon")
        if fund_type == 'stripe':
            bs = st.number_input("Veggtykkelse [m]", 0.0, 1.0, 0.2, 0.02)
            Ls = 1.0
        else:
            bs = st.number_input("Søylebredde [m]", 0.0, 2.0, 0.4, 0.05)
            Ls = st.number_input("Søylelengde [m]", 0.0, 2.0, 0.4, 0.05)
    
    with col3:
        st.markdown("### ⬇️ Belastning")
        enhet_kraft = "kN/m" if fund_type == 'stripe' else "kN"
        enhet_moment = "kNm/m" if fund_type == 'stripe' else "kNm"
        
        V = st.number_input(f"Vertikallast, V [{enhet_kraft}]", 0.0, 50000.0, 500.0, 10.0)
        H_B = st.number_input(f"Horisontallast, H [{enhet_kraft}]", -5000.0, 5000.0, 0.0, 5.0)
        M_B = st.number_input(f"Moment, M [{enhet_moment}]", -10000.0, 10000.0, 0.0, 10.0)
        
        if fund_type == 'rektangulær':
            H_L = st.number_input(f"Horisontallast (L) [{enhet_kraft}]", -5000.0, 5000.0, 0.0, 5.0)
            M_L = st.number_input(f"Moment (L) [{enhet_moment}]", -10000.0, 10000.0, 0.0, 10.0)
        else:
            H_L = 0.0
            M_L = 0.0
        
        st.markdown("---")
        st.markdown("#### Eksentrisitet")
        e_input_B = st.number_input("Centeravvik (B) [m]", -5.0, 5.0, 0.0, 0.01)
        e_input_L = st.number_input("Centeravvik (L) [m]", -5.0, 5.0, 0.0, 0.01) if fund_type == 'rektangulær' else 0.0
    
    # BEREGNING
    st.markdown("---")
    
    jord = JordParameter(analysetype, phi, su, gamma_eff, attraksjon, gamma_M)
    fundament = FundamentGeometri(B, L, T, gamma_c, bs, Ls)
    belastning = Belastning(V, H_B, H_L, M_B, M_L, e_input_B, e_input_L)
    
    if analysetype == 'effektiv':
        phi_d = np.degrees(np.arctan(np.tan(np.radians(phi)) / gamma_M))
        Ka, Kp = kalkulator.beregn_jordtrykkskoeffisienter(phi_d)
    else:
        Ka, Kp = 0.5, 2.0
    
    terreng = TerrengForhold(D, gamma_jord, q0, beta_s, 0.0, Ka, Kp)
    
    try:
        resultat = kalkulator.beregn(jord, fundament, belastning, terreng)
        beregning_ok = True
    except Exception as e:
        st.error(f"Feil: {str(e)}")
        beregning_ok = False
        resultat = None
    
    # RESULTATER
    if beregning_ok and resultat:
        st.markdown("## 📊 Beregningsresultater")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-label">Grunntrykk</div>
                <div class="result-value">{resultat.grunntrykk:.1f}<span class="result-unit">kN/m²</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with res_col2:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-label">Bæreevne</div>
                <div class="result-value">{resultat.baereevne:.1f}<span class="result-unit">kN/m²</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with res_col3:
            if resultat.utnyttelsesgrad <= 0.7:
                status_class, status_text, bar_color = "success", "OK", "#2e7d32"
            elif resultat.utnyttelsesgrad <= 1.0:
                status_class, status_text, bar_color = "warning", "OK (marginal)", "#f57c00"
            else:
                status_class, status_text, bar_color = "danger", "IKKE OK", "#c62828"
            
            utn_pct = resultat.utnyttelsesgrad * 100
            bar_width = min(utn_pct, 100)
            
            st.markdown(f"""
            <div class="result-card {status_class}">
                <div class="result-label">Utnyttelsesgrad</div>
                <div class="result-value">{utn_pct:.1f}<span class="result-unit">%</span></div>
                <div class="utilization-bar">
                    <div class="utilization-fill" style="width: {bar_width}%; background: {bar_color};"></div>
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="status-{'ok' if status_class != 'danger' else 'fail'}">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig_col, gauge_col = st.columns([1.2, 0.8])
        
        with fig_col:
            st.markdown("#### Fundamenttverrsnitt")
            fig_fund = lag_fundament_figur(fundament, terreng, resultat, belastning)
            st.plotly_chart(fig_fund, use_container_width=True)
        
        with gauge_col:
            st.markdown("#### Utnyttelsesgrad")
            fig_gauge = lag_utnyttelse_gauge(resultat.utnyttelsesgrad)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📋 Detaljert beregningsoversikt")
        
        det_col1, det_col2, det_col3 = st.columns(3)
        
        with det_col1:
            st.markdown("#### Effektivt areal")
            st.markdown(f"""
| Parameter | Verdi | Enhet |
|-----------|------:|-------|
| Eksentrisitet, eB | {resultat.eksentrisitet_B:.3f} | m |
| Effektiv bredde, Bo | {resultat.eff_bredde:.3f} | m |""")
            if resultat.eff_lengde:
                st.markdown(f"""| Eksentrisitet, eL | {resultat.eksentrisitet_L:.3f} | m |
| Effektiv lengde, Lo | {resultat.eff_lengde:.3f} | m |""")
        
        with det_col2:
            st.markdown("#### Bæreevnefaktorer")
            if resultat.Nq is not None:
                st.markdown(f"""
| Parameter | Verdi |
|-----------|------:|
| Nq | {resultat.Nq:.2f} |
| Nγ | {resultat.Ny:.2f} |
| Ruhet, r | {resultat.ruhet:.3f} |
| fβ | {resultat.reduksjonsfaktor:.3f} |""")
            else:
                st.markdown(f"""
| Parameter | Verdi |
|-----------|------:|
| Nc | {resultat.Nc:.2f} |
| Ruhet, r | {resultat.ruhet:.3f} |
| fβ | {resultat.reduksjonsfaktor:.3f} |""")
        
        with det_col3:
            st.markdown("#### Kontroll")
            st.markdown(f"""
| Kontroll | Verdi | Status |
|----------|------:|--------|
| q / s | {resultat.utnyttelsesgrad:.3f} | {'✅' if resultat.utnyttelsesgrad <= 1.0 else '❌'} |
| s / q | {resultat.margin:.2f} | {'✅' if resultat.margin >= 1.0 else '❌'} |
| eB / B | {abs(resultat.eksentrisitet_B)/B:.3f} | {'✅' if abs(resultat.eksentrisitet_B)/B <= 1/3 else '⚠️'} |""")
            
            if abs(resultat.eksentrisitet_B) > B/3:
                st.warning("⚠️ Eksentrisitet > B/3")
        
        if export_btn:
            html_rapport = generer_rapport_html(prosjekt_info, jord, fundament, belastning, terreng, resultat)
            filnavn = f"baereevne_{prosjekt_info.get('prosjektnummer', 'rapport')}_{datetime.now().strftime('%Y%m%d')}.html"
            st.download_button("📥 Last ned rapport", html_rapport, filnavn, "text/html")
            st.info("💡 Åpne HTML → Skriv ut → Lagre som PDF")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.85rem; padding: 1rem 0;">
        <strong>Norconsult Bæreevneberegning</strong> v1.0 • NS-EN 1997-1 (EC7) • Brinch Hansen
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
