"""
PDF/HTML Rapport Generator for Bæreevneberegning
"""

from datetime import datetime
from models import (JordParameter, FundamentGeometri, Belastning,
                   TerrengForhold, Resultat)


def generer_rapport_html(
    prosjekt_info: dict,
    jord: JordParameter,
    fundament: FundamentGeometri,
    belastning: Belastning,
    terreng: TerrengForhold,
    resultat: Resultat
) -> str:
    """Genererer HTML-rapport"""
    
    if resultat.utnyttelsesgrad <= 1.0:
        status = "OK - Bæreevnen er tilstrekkelig"
        status_class = "success"
    else:
        status = "IKKE OK - Bæreevnen er utilstrekkelig"
        status_class = "danger"
    
    analyse_tekst = "Effektivspenningsanalyse (drenert)" if jord.analysetype == 'effektiv' else "Totalspenningsanalyse (udrenert)"
    fund_type = "Stripefundament" if fundament.lengde is None else "Rektangulært fundament"
    enhet_kraft = "kN/m" if fundament.lengde is None else "kN"
    enhet_moment = "kNm/m" if fundament.lengde is None else "kNm"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bæreevneberegning - {prosjekt_info.get('prosjektnummer', '')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
            padding: 15mm;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 3px solid #006341;
            padding-bottom: 12px;
            margin-bottom: 15px;
        }}
        .header-left h1 {{
            font-size: 16pt;
            color: #006341;
            font-weight: 700;
        }}
        .header-left p {{
            font-size: 9pt;
            color: #666;
        }}
        .header-right {{
            text-align: right;
            font-size: 9pt;
            color: #666;
        }}
        .project-box {{
            background: #f5f5f5;
            border-left: 4px solid #006341;
            padding: 10px 12px;
            margin-bottom: 15px;
        }}
        .project-box table {{ width: 100%; }}
        .project-box td {{ padding: 2px 8px 2px 0; }}
        .project-box .label {{ font-weight: 600; color: #666; width: 110px; }}
        .section {{ margin-bottom: 15px; }}
        .section h2 {{
            font-size: 11pt;
            color: #006341;
            border-bottom: 1px solid #ddd;
            padding-bottom: 4px;
            margin-bottom: 8px;
        }}
        .param-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 9pt;
        }}
        .param-table th {{
            background: #006341;
            color: white;
            padding: 6px 8px;
            text-align: left;
            font-weight: 600;
        }}
        .param-table td {{
            padding: 5px 8px;
            border-bottom: 1px solid #eee;
        }}
        .param-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .param-table .value {{
            font-family: 'Consolas', monospace;
            text-align: right;
        }}
        .param-table .unit {{ color: #666; width: 50px; }}
        .result-box {{
            background: linear-gradient(135deg, #006341 0%, #004d32 100%);
            color: white;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }}
        .result-box h3 {{
            font-size: 12pt;
            margin-bottom: 12px;
        }}
        .result-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }}
        .result-item {{ text-align: center; }}
        .result-item .label {{
            font-size: 8pt;
            opacity: 0.8;
            text-transform: uppercase;
        }}
        .result-item .value {{
            font-family: 'Consolas', monospace;
            font-size: 18pt;
            font-weight: 500;
        }}
        .result-item .unit {{
            font-size: 9pt;
            opacity: 0.8;
        }}
        .status-box {{
            padding: 10px;
            border-radius: 4px;
            margin-top: 12px;
            font-weight: 600;
            text-align: center;
        }}
        .status-box.success {{
            background: rgba(255,255,255,0.2);
            border: 2px solid rgba(255,255,255,0.5);
        }}
        .status-box.danger {{
            background: rgba(198, 40, 40, 0.3);
            border: 2px solid #c62828;
        }}
        .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 8pt;
            color: #999;
            border-top: 1px solid #ddd;
            padding-top: 5px;
            display: flex;
            justify-content: space-between;
        }}
        @media print {{
            body {{ padding: 10mm; }}
            .result-box {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1>Bæreevneberegning</h1>
            <p>Geoteknisk analyse iht. NS-EN 1997-1 (Eurokode 7)</p>
        </div>
        <div class="header-right">
            <strong>NORCONSULT</strong><br>
            {datetime.now().strftime('%d.%m.%Y')}<br>
            Rev. {prosjekt_info.get('revisjon', '0')}
        </div>
    </div>
    
    <div class="project-box">
        <table>
            <tr>
                <td class="label">Prosjektnummer:</td>
                <td>{prosjekt_info.get('prosjektnummer', '-')}</td>
                <td class="label">Beregningsnavn:</td>
                <td>{prosjekt_info.get('beregningsnavn', '-')}</td>
            </tr>
            <tr>
                <td class="label">Prosjektnavn:</td>
                <td>{prosjekt_info.get('prosjektnavn', '-')}</td>
                <td class="label">Utført av:</td>
                <td>{prosjekt_info.get('utfort_av', '-')}</td>
            </tr>
        </table>
    </div>
    
    <div class="result-box">
        <h3>Beregningsresultat</h3>
        <div class="result-grid">
            <div class="result-item">
                <div class="label">Grunntrykk</div>
                <div class="value">{resultat.grunntrykk:.1f}</div>
                <div class="unit">kN/m²</div>
            </div>
            <div class="result-item">
                <div class="label">Bæreevne</div>
                <div class="value">{resultat.baereevne:.1f}</div>
                <div class="unit">kN/m²</div>
            </div>
            <div class="result-item">
                <div class="label">Utnyttelsesgrad</div>
                <div class="value">{resultat.utnyttelsesgrad*100:.1f}</div>
                <div class="unit">%</div>
            </div>
        </div>
        <div class="status-box {status_class}">
            {status}
        </div>
    </div>
    
    <div class="two-col">
        <div class="section">
            <h2>Jordparametre</h2>
            <table class="param-table">
                <tr>
                    <td>Analysetype</td>
                    <td class="value" colspan="2">{analyse_tekst}</td>
                </tr>"""
    
    if jord.analysetype == 'effektiv':
        html += f"""
                <tr>
                    <td>Friksjonsvinkel, φ'</td>
                    <td class="value">{jord.friksjonsvinkel:.1f}</td>
                    <td class="unit">°</td>
                </tr>
                <tr>
                    <td>Romvekt (effektiv), γ'</td>
                    <td class="value">{jord.romvekt_eff:.1f}</td>
                    <td class="unit">kN/m³</td>
                </tr>
                <tr>
                    <td>Attraksjon, a</td>
                    <td class="value">{jord.attraksjon:.1f}</td>
                    <td class="unit">kN/m²</td>
                </tr>"""
    else:
        html += f"""
                <tr>
                    <td>Udrenert skjærstyrke, su</td>
                    <td class="value">{jord.udrenert_skjaerstyrke:.1f}</td>
                    <td class="unit">kN/m²</td>
                </tr>"""
    
    html += f"""
                <tr>
                    <td>Materialfaktor, γM</td>
                    <td class="value">{jord.materialfaktor:.2f}</td>
                    <td class="unit">-</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Fundament ({fund_type})</h2>
            <table class="param-table">
                <tr>
                    <td>Bredde, B</td>
                    <td class="value">{fundament.bredde:.2f}</td>
                    <td class="unit">m</td>
                </tr>"""
    
    if fundament.lengde is not None:
        html += f"""
                <tr>
                    <td>Lengde, L</td>
                    <td class="value">{fundament.lengde:.2f}</td>
                    <td class="unit">m</td>
                </tr>"""
    
    html += f"""
                <tr>
                    <td>Tykkelse, T</td>
                    <td class="value">{fundament.tykkelse:.2f}</td>
                    <td class="unit">m</td>
                </tr>
                <tr>
                    <td>Fundamentdybde, D</td>
                    <td class="value">{terreng.fundamentdybde:.2f}</td>
                    <td class="unit">m</td>
                </tr>
            </table>
        </div>
    </div>
    
    <div class="two-col">
        <div class="section">
            <h2>Belastning</h2>
            <table class="param-table">
                <tr>
                    <td>Vertikallast, V</td>
                    <td class="value">{belastning.vertikal:.1f}</td>
                    <td class="unit">{enhet_kraft}</td>
                </tr>
                <tr>
                    <td>Total vertikallast (inkl. egenvekt)</td>
                    <td class="value">{resultat.V_total:.1f}</td>
                    <td class="unit">{enhet_kraft}</td>
                </tr>
                <tr>
                    <td>Horisontallast, H</td>
                    <td class="value">{belastning.horisontal_B:.1f}</td>
                    <td class="unit">{enhet_kraft}</td>
                </tr>
                <tr>
                    <td>Moment, M</td>
                    <td class="value">{belastning.moment_B:.1f}</td>
                    <td class="unit">{enhet_moment}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Beregnede størrelser</h2>
            <table class="param-table">
                <tr>
                    <td>Effektiv bredde, Bo</td>
                    <td class="value">{resultat.eff_bredde:.3f}</td>
                    <td class="unit">m</td>
                </tr>
                <tr>
                    <td>Eksentrisitet, e</td>
                    <td class="value">{resultat.eksentrisitet_B:.3f}</td>
                    <td class="unit">m</td>
                </tr>
                <tr>
                    <td>Ruhet, r</td>
                    <td class="value">{resultat.ruhet:.3f}</td>
                    <td class="unit">-</td>
                </tr>"""
    
    if resultat.Nq is not None:
        html += f"""
                <tr>
                    <td>Bæreevnefaktor, Nq</td>
                    <td class="value">{resultat.Nq:.2f}</td>
                    <td class="unit">-</td>
                </tr>
                <tr>
                    <td>Bæreevnefaktor, Nγ</td>
                    <td class="value">{resultat.Ny:.2f}</td>
                    <td class="unit">-</td>
                </tr>"""
    else:
        html += f"""
                <tr>
                    <td>Bæreevnefaktor, Nc</td>
                    <td class="value">{resultat.Nc:.2f}</td>
                    <td class="unit">-</td>
                </tr>"""
    
    html += f"""
                <tr>
                    <td>Skråningsreduksjon, fβ</td>
                    <td class="value">{resultat.reduksjonsfaktor:.3f}</td>
                    <td class="unit">-</td>
                </tr>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <span>Generert med Norconsult Bæreevneberegning v1.0</span>
        <span>Beregning iht. NS-EN 1997-1 • Brinch Hansen's metode</span>
    </div>
</body>
</html>"""
    
    return html
