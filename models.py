"""
Datamodeller for bæreevneberegning
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class JordParameter:
    """Jordparametre for geoteknisk beregning"""
    analysetype: str  # 'effektiv' eller 'udrenert'
    friksjonsvinkel: float  # phi' [°]
    udrenert_skjaerstyrke: float  # su [kN/m²]
    romvekt_eff: float  # gamma' [kN/m³]
    attraksjon: float  # a [kN/m²]
    materialfaktor: float  # gamma_M


@dataclass
class FundamentGeometri:
    """Fundamentets geometriske egenskaper"""
    bredde: float  # B [m]
    lengde: Optional[float]  # L [m], None = stripefundament
    tykkelse: float  # T [m]
    romvekt: float  # gamma_c [kN/m³]
    vegg_bredde: float  # bs [m]
    soyle_lengde: float  # Ls [m] (for rektangulære)


@dataclass 
class Belastning:
    """Belastning på fundamentet"""
    vertikal: float  # V [kN eller kN/m]
    horisontal_B: float  # H_B [kN eller kN/m]
    horisontal_L: float  # H_L [kN] (kun rektangulære)
    moment_B: float  # M_B [kNm eller kNm/m]
    moment_L: float  # M_L [kNm] (kun rektangulære)
    centeravvik_B: float  # e_B [m]
    centeravvik_L: float  # e_L [m]


@dataclass
class TerrengForhold:
    """Terrengforhold rundt fundamentet"""
    fundamentdybde: float  # D [m]
    romvekt_over: float  # gamma_jord [kN/m³]
    overflatelast: float  # q_0 [kN/m²]
    skraaningshelning: float  # beta_s [°]
    terrenghelning: float  # beta_t [°]
    Ka: float  # aktiv jordtrykkskoeffisient
    Kp: float  # passiv jordtrykkskoeffisient


@dataclass
class Resultat:
    """Beregningsresultater"""
    grunntrykk: float  # q [kN/m²]
    baereevne: float  # s [kN/m²]
    utnyttelsesgrad: float  # q/s
    margin: float  # s/q
    Nq: Optional[float]
    Ny: Optional[float]
    Nc: Optional[float]
    eff_bredde: float  # Bo [m]
    eff_lengde: Optional[float]  # Lo [m]
    eksentrisitet_B: float  # eB [m]
    eksentrisitet_L: Optional[float]  # eL [m]
    ruhet: float  # r
    reduksjonsfaktor: float  # f_beta
    V_total: float  # Total vertikallast inkl. egenvekt
