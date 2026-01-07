"""
Visualiseringer for bæreevneberegning
Profesjonelle Plotly-figurer med moment-visning
"""

import numpy as np
import plotly.graph_objects as go
from models import FundamentGeometri, TerrengForhold, Resultat, Belastning


def lag_fundament_figur(fundament: FundamentGeometri,
                        terreng: TerrengForhold,
                        resultat: Resultat,
                        belastning: Belastning) -> go.Figure:
    """Lager tverrsnittsfigur av fundamentet med alle laster inkludert moment"""
    B = fundament.bredde
    T = fundament.tykkelse
    D = terreng.fundamentdybde
    Bo = resultat.eff_bredde
    e_B = resultat.eksentrisitet_B
    
    fig = go.Figure()
    
    # Bakgrunn - jord
    fig.add_shape(
        type="rect",
        x0=-B*1.5, y0=-D-T-0.5, x1=B*1.5, y1=0,
        fillcolor="rgba(139, 119, 101, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    
    # Terrengoverflate
    fig.add_shape(
        type="line",
        x0=-B*1.5, y0=0, x1=B*1.5, y1=0,
        line=dict(color="#2d5016", width=3)
    )
    
    # Gress
    for x in np.arange(-B*1.4, B*1.4, 0.15):
        fig.add_annotation(
            x=x, y=0.05,
            text="▼",
            showarrow=False,
            font=dict(size=8, color="#2d5016"),
            yanchor="bottom"
        )
    
    # Fundament
    fig.add_shape(
        type="rect",
        x0=-B/2, y0=-D, x1=B/2, y1=-D+T,
        fillcolor="rgba(180, 180, 180, 0.8)",
        line=dict(color="#404040", width=2)
    )
    
    # Vegg/søyle
    vegg_b = fundament.vegg_bredde
    if D > T:
        fig.add_shape(
            type="rect",
            x0=-vegg_b/2, y0=-D+T, x1=vegg_b/2, y1=0,
            fillcolor="rgba(160, 160, 160, 0.8)",
            line=dict(color="#404040", width=2)
        )
    
    # Effektiv bredde markering
    fig.add_shape(
        type="rect",
        x0=-B/2 + abs(e_B), y0=-D-0.05, x1=B/2 - abs(e_B), y1=-D,
        fillcolor="rgba(0, 99, 65, 0.6)",
        line=dict(color="#006341", width=2)
    )
    
    # === LASTER ===
    
    # Vertikallast (rød pil ned)
    fig.add_annotation(
        x=e_B, y=0.15,
        ax=e_B, ay=0.55,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor="#c62828"
    )
    fig.add_annotation(
        x=e_B, y=0.62,
        text=f"V = {belastning.vertikal:.0f} kN",
        showarrow=False,
        font=dict(size=11, color="#c62828")
    )
    
    # Horisontallast (blå pil)
    if abs(belastning.horisontal_B) > 0.1:
        H_dir = 1 if belastning.horisontal_B > 0 else -1
        fig.add_annotation(
            x=H_dir * 0.35, y=0.15,
            ax=0, ay=0.15,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=3,
            arrowcolor="#1565c0"
        )
        fig.add_annotation(
            x=H_dir * 0.5, y=0.15,
            text=f"H = {abs(belastning.horisontal_B):.0f} kN",
            showarrow=False,
            font=dict(size=10, color="#1565c0"),
            xanchor="left" if H_dir > 0 else "right"
        )
    
    # === MOMENT (lilla buet pil) ===
    if abs(belastning.moment_B) > 0.1:
        # Tegn en buet moment-indikator
        M_dir = 1 if belastning.moment_B > 0 else -1
        
        # Lag buet pil med punkter
        theta = np.linspace(0, np.pi * 0.7, 20)
        r = 0.25
        x_arc = r * np.cos(theta) * M_dir
        y_arc = r * np.sin(theta) + 0.15
        
        # Tegn buen
        fig.add_trace(go.Scatter(
            x=x_arc,
            y=y_arc,
            mode='lines',
            line=dict(color='#7b1fa2', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Pilspiss på enden av buen
        end_x = x_arc[-1]
        end_y = y_arc[-1]
        
        # Legg til pilspiss som annotation
        fig.add_annotation(
            x=end_x, y=end_y,
            ax=x_arc[-3], ay=y_arc[-3],
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=3,
            arrowcolor="#7b1fa2"
        )
        
        # Moment-tekst
        fig.add_annotation(
            x=0, y=0.5,
            text=f"M = {abs(belastning.moment_B):.0f} kNm",
            showarrow=False,
            font=dict(size=10, color="#7b1fa2")
        )
    
    # === DIMENSJONER ===
    
    # Bredde B
    fig.add_shape(type="line", x0=-B/2, y0=-D-0.3, x1=B/2, y1=-D-0.3,
                  line=dict(color="#666", width=1, dash="dot"))
    fig.add_shape(type="line", x0=-B/2, y0=-D-0.25, x1=-B/2, y1=-D-0.35,
                  line=dict(color="#666", width=1))
    fig.add_shape(type="line", x0=B/2, y0=-D-0.25, x1=B/2, y1=-D-0.35,
                  line=dict(color="#666", width=1))
    fig.add_annotation(x=0, y=-D-0.38, text=f"B = {B:.2f} m",
                      showarrow=False, font=dict(size=10, color="#666"))
    
    # Effektiv bredde Bo
    fig.add_annotation(x=0, y=-D-0.12, text=f"Bo = {Bo:.2f} m",
                      showarrow=False, font=dict(size=10, color="#006341", weight="bold"))
    
    # Fundamentdybde D
    if D > 0:
        fig.add_shape(type="line", x0=B/2+0.15, y0=0, x1=B/2+0.15, y1=-D,
                      line=dict(color="#666", width=1, dash="dot"))
        fig.add_shape(type="line", x0=B/2+0.1, y0=0, x1=B/2+0.2, y1=0,
                      line=dict(color="#666", width=1))
        fig.add_shape(type="line", x0=B/2+0.1, y0=-D, x1=B/2+0.2, y1=-D,
                      line=dict(color="#666", width=1))
        fig.add_annotation(x=B/2+0.28, y=-D/2, text=f"D = {D:.2f} m",
                          showarrow=False, font=dict(size=10, color="#666"),
                          textangle=-90)
    
    # Tykkelse T
    fig.add_shape(type="line", x0=-B/2-0.15, y0=-D, x1=-B/2-0.15, y1=-D+T,
                  line=dict(color="#666", width=1, dash="dot"))
    fig.add_annotation(x=-B/2-0.25, y=-D+T/2, text=f"T = {T:.2f} m",
                      showarrow=False, font=dict(size=9, color="#666"),
                      textangle=-90)
    
    # Eksentrisitet e (hvis > 0)
    if abs(e_B) > 0.01:
        fig.add_shape(type="line", x0=0, y0=-D+T+0.05, x1=e_B, y1=-D+T+0.05,
                      line=dict(color="#ff6b35", width=2, dash="dash"))
        fig.add_annotation(x=e_B/2, y=-D+T+0.12, text=f"e = {e_B:.3f} m",
                          showarrow=False, font=dict(size=9, color="#ff6b35"))
    
    # === SPENNINGSFORDELING ===
    q = resultat.grunntrykk
    q_scale = 0.25 * T
    n_piler = 7
    
    for x in np.linspace(-Bo/2 + abs(e_B), Bo/2 - abs(e_B), n_piler):
        fig.add_annotation(
            x=x, y=-D-0.02,
            ax=x, ay=-D-q_scale,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=0.8,
            arrowwidth=2,
            arrowcolor="#ff6b35"
        )
    
    fig.add_annotation(x=0, y=-D-q_scale-0.12,
                      text=f"q = {q:.1f} kN/m²",
                      showarrow=False,
                      font=dict(size=11, color="#ff6b35", weight="bold"))
    
    # Layout
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-B*1.6, B*1.6], scaleanchor="y", scaleratio=1
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-D-T-0.7, 0.9]
        ),
        height=450
    )
    
    return fig


def lag_utnyttelse_gauge(utnyttelse: float) -> go.Figure:
    """Lager gauge for utnyttelsesgrad"""
    if utnyttelse <= 0.7:
        bar_color = "#2e7d32"
    elif utnyttelse <= 0.9:
        bar_color = "#f57c00"
    else:
        bar_color = "#c62828"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=utnyttelse * 100,
        number={'suffix': '%', 'font': {'size': 48, 'color': bar_color}},
        gauge={
            'axis': {'range': [0, 150], 'tickwidth': 2, 'tickcolor': "#ccc"},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e0e0e0",
            'steps': [
                {'range': [0, 70], 'color': 'rgba(46, 125, 50, 0.1)'},
                {'range': [70, 90], 'color': 'rgba(245, 124, 0, 0.1)'},
                {'range': [90, 100], 'color': 'rgba(198, 40, 40, 0.1)'},
                {'range': [100, 150], 'color': 'rgba(198, 40, 40, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#1a1a1a", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#333"},
        height=280,
        margin=dict(l=30, r=30, t=40, b=10)
    )
    
    return fig
