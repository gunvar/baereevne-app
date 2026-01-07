"""
PDF/HTML Rapport Generator for Bæreevneberegning
"""

from datetime import datetime
from models import (JordParameter, FundamentGeometri, Belastning,
                   TerrengForhold, Resultat)


def generer_fundament_svg(fundament, terreng, resultat, belastning):
    """Genererer SVG-figur av fundamentet"""
    B = fundament.bredde
    T = fundament.tykkelse
    D = terreng.fundamentdybde
    Bo = resultat.eff_bredde
    e_B = resultat.eksentrisitet_B
    
    # SVG dimensjoner og skalering
    width = 400
    height = 300
    scale = 80 / max(B, D + T + 0.5)
    cx = width / 2
    cy = 100
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Bakgrunn jord -->
        <rect x="0" y="{cy}" width="{width}" height="{height-cy}" fill="#d4c4b0" opacity="0.4"/>
        
        <!-- Terrengoverflate -->
        <line x1="0" y1="{cy}" x2="{width}" y2="{cy}" stroke="#2d5016" stroke-width="3"/>
        
        <!-- Fundament -->
        <rect x="{cx - B*scale/2}" y="{cy + D*scale - T*scale}" 
              width="{B*scale}" height="{T*scale}" 
              fill="#b0b0b0" stroke="#404040" stroke-width="2"/>
        
        <!-- Vegg/søyle -->
        <rect x="{cx - fundament.vegg_bredde*scale/2}" y="{cy}" 
              width="{fundament.vegg_bredde*scale}" height="{D*scale - T*scale}" 
              fill="#a0a0a0" stroke="#404040" stroke-width="2"/>
        
        <!-- Effektiv bredde markering -->
        <rect x="{cx - Bo*scale/2}" y="{cy + D*scale}" 
              width="{Bo*scale}" height="4" 
              fill="#006341"/>
        
        <!-- Vertikallast pil -->
        <line x1="{cx + e_B*scale}" y1="{cy - 60}" x2="{cx + e_B*scale}" y2="{cy - 10}" 
              stroke="#c62828" stroke-width="3"/>
        <polygon points="{cx + e_B*scale},{cy - 5} {cx + e_B*scale - 8},{cy - 15} {cx + e_B*scale + 8},{cy - 15}" 
                 fill="#c62828"/>
        <text x="{cx + e_B*scale}" y="{cy - 70}" text-anchor="middle" 
              font-size="12" fill="#c62828">V = {belastning.vertikal:.0f} kN</text>
        '''
    
    # Horisontallast
    if abs(belastning.horisontal_B) > 0.1:
        H_dir = 1 if belastning.horisontal_B > 0 else -1
        svg += f'''
        <line x1="{cx}" y1="{cy - 30}" x2="{cx + H_dir*40}" y2="{cy - 30}" 
              stroke="#1565c0" stroke-width="3"/>
        <polygon points="{cx + H_dir*45},{cy - 30} {cx + H_dir*35},{cy - 35} {cx + H_dir*35},{cy - 25}" 
                 fill="#1565c0"/>
        <text x="{cx + H_dir*60}" y="{cy - 25}" text-anchor="middle" 
              font-size="11" fill="#1565c0">H = {abs(belastning.horisontal_B):.0f}</text>
        '''
    
    # Moment
    if abs(belastning.moment_B) > 0.1:
        svg += f'''
        <path d="M {cx-20} {cy-40} A 20 20 0 0 1 {cx+20} {cy-40}" 
              fill="none" stroke="#7b1fa2" stroke-width="2"/>
        <text x="{cx}" y="{cy - 50}" text-anchor="middle" 
              font-size="11" fill="#7b1fa2">M = {abs(belastning.moment_B):.0f} kNm</text>
        '''
    
    # Dimensjoner
    svg += f'''
        <!-- Bredde B -->
        <line x1="{cx - B*scale/2}" y1="{cy + D*scale + 20}" x2="{cx + B*scale/2}" y2="{cy + D*scale + 20}" 
              stroke="#666" stroke-width="1" stroke-dasharray="4"/>
        <text x="{cx}" y="{cy + D*scale + 35}" text-anchor="middle" 
              font-size="10" fill="#666">B = {B:.2f} m</text>
        
        <!-- Effektiv bredde Bo -->
        <text x="{cx}" y="{cy + D*scale + 15}" text-anchor="middle" 
              font-size="10" fill="#006341" font-weight="bold">Bo = {Bo:.2f} m</text>
        
        <!-- Grunntrykk -->
        <text x="{cx}" y="{cy + D*scale + 55}" text-anchor="middle" 
              font-size="11" fill="#ff6b35" font-weight="bold">q = {resultat.grunntrykk:.1f} kN/m²</text>
        
        <!-- Dybde D -->
        <line x1="{cx + B*scale/2 + 15}" y1="{cy}" x2="{cx + B*scale/2 + 15}" y2="{cy + D*scale}" 
              stroke="#666" stroke-width="1" stroke-dasharray="4"/>
        <text x="{cx + B*scale/2 + 25}" y="{cy + D*scale/2}" 
              font-size="10" fill="#666" transform="rotate(90 {cx + B*scale/2 + 25} {cy + D*scale/2})">D = {D:.2f} m</text>
    </svg>'''
    
    return svg


def generer_rapport_html(prosjekt_info, jord, fundament, belastning, terreng, resultat):
    """Genererer HTML-rapport"""
    
    status = "OK - Bæreevnen er tilstrekkelig" if resultat.utnyttelsesgrad <= 1.0 else "IKKE OK"
    status_class = "success" if resultat.utnyttelsesgrad <= 1.0 else "danger"
    analyse_tekst = "Effektivspenningsanalyse" if jord.analysetype == 'effektiv' else "Totalspenningsanalyse"
    fund_type = "Stripefundament" if fundament.lengde is None else "Rektangulært"
    enhet = "kN/m" if fundament.lengde is None else "kN"
    
    svg_figur = generer_fundament_svg(fundament, terreng, resultat, belastning)
    
    # Formler basert på analysetype
    if jord.analysetype == 'effektiv':
        formler_html = '''
        <div style="background:#f5f5f5;padding:10px;margin:10px 0;border-left:3px solid #006341;">
            <b>Bæreevneformel (Effektiv):</b><br>
            <code>s = fβ·sq·Nq·(γ'D + q₀ + a) + fβ·sγ·½·Nγ·γ'·Bo - a</code>
        </div>
        <div style="background:#f5f5f5;padding:10px;margin:10px 0;border-left:3px solid #006341;">
            <b>Nq:</b> <code>Nq = ½(Kp+1+(Kp-1)cos2θm)·e^((π-2θm)tanφ'd)</code><br>
            <b>Nγ:</b> Interpolert fra tabell (Brinch Hansen)
        </div>'''
    else:
        formler_html = '''
        <div style="background:#f5f5f5;padding:10px;margin:10px 0;border-left:3px solid #006341;">
            <b>Bæreevneformel (Udrenert):</b><br>
            <code>s = fβ·sc·Nc·su/γM + (γD + q₀)·cos²β</code>
        </div>
        <div style="background:#f5f5f5;padding:10px;margin:10px 0;border-left:3px solid #006341;">
            <b>Nc:</b> <code>Nc = π + 2 + √(1-r²) - arcsin(r)</code>
        </div>'''
    
    formler_html += '''
    <div style="background:#f5f5f5;padding:10px;margin:10px 0;border-left:3px solid #006341;">
        <b>Eksentrisitet:</b> <code>e = M/V</code><br>
        <b>Effektiv bredde:</b> <code>Bo = B - 2|e|</code><br>
        <b>Grunntrykk:</b> <code>q = V/Aeff</code>
    </div>'''
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Bæreevne</title>
<style>
body{{font-family:Arial,sans-serif;font-size:10pt;padding:15mm;color:#333;}}
.header{{border-bottom:3px solid #006341;padding-bottom:10px;margin-bottom:15px;}}
.header h1{{color:#006341;margin:0;font-size:16pt;}}
table{{width:100%;border-collapse:collapse;margin:10px 0;}}
td,th{{padding:5px 8px;border-bottom:1px solid #eee;}}
th{{background:#006341;color:white;text-align:left;}}
.result{{background:#006341;color:white;padding:15px;border-radius:6px;margin:15px 0;}}
.result-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;text-align:center;}}
.result-value{{font-size:20pt;font-weight:bold;}}
.status{{padding:10px;border-radius:4px;text-align:center;font-weight:bold;margin-top:10px;
         background:{"rgba(255,255,255,0.2)" if status_class=="success" else "rgba(198,40,40,0.3)"};}}
.figure{{border:1px solid #ddd;padding:15px;margin:15px 0;text-align:center;background:#fafafa;}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:15px;}}
@media print{{.result{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}}}
</style></head><body>

<div class="header">
    <table><tr>
        <td><h1>Bæreevneberegning</h1><small>NS-EN 1997-1 (EC7)</small></td>
        <td style="text-align:right"><b>NORCONSULT</b><br>{datetime.now().strftime('%d.%m.%Y')}<br>Rev. {prosjekt_info.get('revisjon','0')}</td>
    </tr></table>
</div>

<table style="background:#f5f5f5;">
    <tr><td><b>Prosjekt:</b> {prosjekt_info.get('prosjektnummer','-')} - {prosjekt_info.get('prosjektnavn','-')}</td>
        <td><b>Beregning:</b> {prosjekt_info.get('beregningsnavn','-')}</td>
        <td><b>Utført:</b> {prosjekt_info.get('utfort_av','-')}</td></tr>
</table>

<div class="result">
    <div class="result-grid">
        <div><small>GRUNNTRYKK</small><div class="result-value">{resultat.grunntrykk:.1f}</div><small>kN/m²</small></div>
        <div><small>BÆREEVNE</small><div class="result-value">{resultat.baereevne:.1f}</div><small>kN/m²</small></div>
        <div><small>UTNYTTELSE</small><div class="result-value">{resultat.utnyttelsesgrad*100:.1f}%</div></div>
    </div>
    <div class="status">{status}</div>
</div>

<div class="figure">
    <b>Fundamenttverrsnitt</b><br>
    {svg_figur}
</div>

<div class="two-col">
<div>
    <h3 style="color:#006341;">Jordparametre ({analyse_tekst})</h3>
    <table>
        {"<tr><td>Friksjonsvinkel φ'</td><td><b>"+str(jord.friksjonsvinkel)+"°</b></td></tr>" if jord.analysetype=='effektiv' else "<tr><td>Udrenert skjærstyrke su</td><td><b>"+str(jord.udrenert_skjaerstyrke)+" kN/m²</b></td></tr>"}
        {"<tr><td>Effektiv romvekt γ'</td><td><b>"+str(jord.romvekt_eff)+" kN/m³</b></td></tr>" if jord.analysetype=='effektiv' else ""}
        <tr><td>Materialfaktor γM</td><td><b>{jord.materialfaktor}</b></td></tr>
    </table>
    
    <h3 style="color:#006341;">Fundament ({fund_type})</h3>
    <table>
        <tr><td>Bredde B</td><td><b>{fundament.bredde} m</b></td></tr>
        {"<tr><td>Lengde L</td><td><b>"+str(fundament.lengde)+" m</b></td></tr>" if fundament.lengde else ""}
        <tr><td>Tykkelse T</td><td><b>{fundament.tykkelse} m</b></td></tr>
        <tr><td>Dybde D</td><td><b>{terreng.fundamentdybde} m</b></td></tr>
    </table>
</div>
<div>
    <h3 style="color:#006341;">Belastning</h3>
    <table>
        <tr><td>Vertikallast V</td><td><b>{belastning.vertikal} {enhet}</b></td></tr>
        <tr><td>Total V (m/egenvekt)</td><td><b>{resultat.V_total:.1f} {enhet}</b></td></tr>
        <tr><td>Horisontallast H</td><td><b>{belastning.horisontal_B} {enhet}</b></td></tr>
        <tr><td>Moment M</td><td><b>{belastning.moment_B} {"kNm/m" if fundament.lengde is None else "kNm"}</b></td></tr>
    </table>
    
    <h3 style="color:#006341;">Beregnede størrelser</h3>
    <table>
        <tr><td>Eksentrisitet e</td><td><b>{resultat.eksentrisitet_B:.3f} m</b></td></tr>
        <tr><td>Effektiv bredde Bo</td><td><b>{resultat.eff_bredde:.3f} m</b></td></tr>
        {"<tr><td>Nq</td><td><b>"+f"{resultat.Nq:.2f}"+"</b></td></tr><tr><td>Nγ</td><td><b>"+f"{resultat.Ny:.2f}"+"</b></td></tr>" if resultat.Nq else "<tr><td>Nc</td><td><b>"+f"{resultat.Nc:.2f}"+"</b></td></tr>"}
        <tr><td>Ruhet r</td><td><b>{resultat.ruhet:.3f}</b></td></tr>
    </table>
</div>
</div>

<h3 style="color:#006341;margin-top:20px;">Anvendte formler</h3>
{formler_html}

<div style="margin-top:20px;padding-top:10px;border-top:1px solid #ddd;font-size:8pt;color:#999;">
    Norconsult Bæreevneberegning v1.0 | NS-EN 1997-1 | Brinch Hansen's metode
</div>
</body></html>'''
    
    return html
