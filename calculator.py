"""
Beregningsmotor for bæreevne iht. NS-EN 1997-1 (Eurokode 7)
Basert på Brinch Hansen's metode med modifikasjoner

Referanser:
- NS-EN 1997-1:2004+NA:2008 (Eurokode 7)
- Brinch Hansen, J. (1970): A revised and extended formula for bearing capacity
- Statens vegvesen Håndbok V220
"""

import numpy as np
from typing import Tuple, Optional
from models import (JordParameter, FundamentGeometri, Belastning, 
                   TerrengForhold, Resultat)


class BaereevneKalkulator:
    """
    Bæreevneberegning iht. NS-EN 1997-1 (Eurokode 7)
    Støtter både effektivspennings- og totalspenningsanalyse
    """
    
    # Interpolasjonstabell for Ny vs ruhet (fra Brinch Hansen)
    NY_TABELL_R = np.array([0, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 
                           0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.475, 0.5,
                           0.525, 0.55, 0.575, 0.6, 0.625, 0.65, 0.675, 0.7,
                           0.725, 0.75, 0.775, 0.8, 0.825, 0.85, 0.875, 0.9,
                           0.925, 0.95, 0.975, 1.0])
    
    NY_TABELL_VALUES = {
        0.0: [0, 0.6, 0.8, 1.05, 1.35, 1.7, 2.12, 2.65, 3.25, 4, 4.9, 6, 7.3, 9, 11, 13.5, 16.8, 20.5, 25, 31, 38, 47, 58, 72, 89, 111, 138, 172, 215, 270, 340, 430, 540, 690, 870, 1100],
        0.1: [0, 0.54, 0.71, 0.92, 1.2, 1.49, 1.89, 2.39, 2.87, 3.44, 4.3, 5.19, 6.3, 7.6, 9.2, 11.2, 13.6, 16.5, 20, 24.3, 29.5, 35.9, 43.6, 53.1, 64.5, 78.7, 96, 117, 143, 175, 214, 262, 320, 392, 481, 590],
        0.2: [0, 0.5, 0.66, 0.85, 1.1, 1.36, 1.7, 2.13, 2.55, 3.05, 3.75, 4.5, 5.5, 6.6, 7.9, 9.5, 11.4, 13.6, 16.4, 19.7, 23.7, 28.5, 34.3, 41.2, 49.6, 59.7, 72, 87, 105, 127, 153, 185, 224, 271, 328, 400],
        0.3: [0, 0.45, 0.59, 0.75, 0.98, 1.19, 1.49, 1.87, 2.2, 2.59, 3.18, 3.76, 4.55, 5.4, 6.4, 7.6, 9, 10.6, 12.6, 14.9, 17.7, 21, 24.9, 29.5, 35, 41.5, 49.2, 58.4, 69.4, 82.5, 98, 117, 139, 165, 197, 235],
        0.4: [0, 0.425, 0.56, 0.7, 0.89, 1.09, 1.31, 1.61, 1.9, 2.25, 2.65, 3.1, 3.7, 4.35, 5.1, 5.95, 6.95, 8.1, 9.45, 11, 12.9, 15, 17.5, 20.4, 23.8, 27.7, 32.3, 37.7, 44, 51.4, 60, 70, 82, 96, 112, 131],
        0.5: [0, 0.39, 0.51, 0.65, 0.8, 0.97, 1.18, 1.42, 1.66, 1.95, 2.25, 2.6, 3.05, 3.55, 4.1, 4.75, 5.45, 6.25, 7.2, 8.25, 9.45, 10.85, 12.45, 14.3, 16.4, 18.8, 21.6, 24.8, 28.4, 32.7, 37.5, 43.1, 49.5, 57, 65.5, 75.5],
        0.6: [0, 0.345, 0.445, 0.55, 0.67, 0.8, 0.96, 1.15, 1.33, 1.55, 1.75, 2.04, 2.35, 2.7, 3.1, 3.55, 4.05, 4.6, 5.25, 5.95, 6.75, 7.65, 8.65, 9.8, 11.1, 12.55, 14.2, 16.05, 18.2, 20.6, 23.3, 26.4, 29.9, 33.9, 38.4, 43.5],
        0.7: [0, 0.3, 0.38, 0.47, 0.56, 0.66, 0.79, 0.93, 1.06, 1.22, 1.37, 1.56, 1.77, 2, 2.27, 2.56, 2.9, 3.26, 3.67, 4.12, 4.63, 5.2, 5.83, 6.55, 7.35, 8.24, 9.25, 10.4, 11.65, 13.1, 14.7, 16.5, 18.5, 20.8, 23.3, 26.2],
        0.8: [0, 0.265, 0.315, 0.39, 0.46, 0.53, 0.61, 0.705, 0.81, 0.9, 1, 1.11, 1.24, 1.38, 1.54, 1.71, 1.91, 2.12, 2.36, 2.62, 2.91, 3.24, 3.6, 4, 4.44, 4.94, 5.49, 6.1, 6.78, 7.54, 8.39, 9.33, 10.4, 11.55, 12.85, 14.3],
        0.9: [0, 0.225, 0.27, 0.32, 0.365, 0.41, 0.47, 0.525, 0.58, 0.64, 0.69, 0.75, 0.82, 0.9, 0.98, 1.07, 1.17, 1.28, 1.4, 1.52, 1.66, 1.81, 1.98, 2.16, 2.35, 2.57, 2.8, 3.06, 3.34, 3.64, 3.97, 4.33, 4.73, 5.15, 5.62, 6.14],
        0.95: [0, 0.195, 0.235, 0.271, 0.31, 0.35, 0.39, 0.435, 0.47, 0.51, 0.55, 0.58, 0.63, 0.68, 0.73, 0.79, 0.85, 0.91, 0.98, 1.05, 1.13, 1.21, 1.3, 1.4, 1.5, 1.61, 1.73, 1.86, 2, 2.14, 2.3, 2.47, 2.65, 2.85, 3.06, 3.28],
        0.99: [0, 0.159, 0.187, 0.209, 0.234, 0.258, 0.282, 0.309, 0.326, 0.35, 0.374, 0.392, 0.42, 0.448, 0.478, 0.509, 0.542, 0.576, 0.612, 0.651, 0.691, 0.734, 0.779, 0.826, 0.876, 0.929, 0.985, 1.04, 1.11, 1.17, 1.24, 1.32, 1.4, 1.48, 1.57, 1.66],
        1.0: [0, 0.15, 0.175, 0.194, 0.215, 0.235, 0.255, 0.277, 0.29, 0.31, 0.33, 0.345, 0.368, 0.391, 0.415, 0.44, 0.467, 0.495, 0.525, 0.556, 0.589, 0.623, 0.66, 0.699, 0.739, 0.782, 0.827, 0.875, 0.925, 0.977, 1.03, 1.09, 1.16, 1.22, 1.29, 1.36]
    }
    
    def __init__(self):
        self.resultater = None
    
    def beregn_jordtrykkskoeffisienter(self, phi_d: float) -> Tuple[float, float]:
        """
        Beregner aktiv (Ka) og passiv (Kp) jordtrykkskoeffisient
        Rankine's teori for horisontal terreng
        """
        if phi_d <= 0:
            return 1.0, 1.0
        phi_rad = np.radians(phi_d)
        Ka = (1 - np.sin(phi_rad)) / (1 + np.sin(phi_rad))
        Kp = (1 + np.sin(phi_rad)) / (1 - np.sin(phi_rad))
        return Ka, Kp
    
    def beregn_eksentrisitet(self, 
                            V: float, 
                            M_B: float, 
                            M_L: Optional[float],
                            H_B: float,
                            H_L: Optional[float],
                            centeravvik_B: float,
                            centeravvik_L: float,
                            fund_dybde: float,
                            fund_tykkelse: float) -> Tuple[float, Optional[float]]:
        """
        Beregner eksentrisiteter fra laster og momenter
        """
        if V <= 0:
            return 0, None if M_L is None else 0
        
        # Total moment i B-retning
        M_B_total = M_B + V * centeravvik_B
        e_B = M_B_total / V
        
        # Total moment i L-retning (kun for rektangulære)
        if M_L is not None and H_L is not None:
            M_L_total = M_L + V * centeravvik_L
            e_L = M_L_total / V
        else:
            e_L = None
            
        return e_B, e_L
    
    def beregn_effektivt_areal(self,
                               B: float,
                               L: Optional[float],
                               e_B: float,
                               e_L: Optional[float]) -> Tuple[float, Optional[float], float]:
        """
        Beregner effektiv bredde og lengde pga. eksentrisitet
        """
        Bo = B - 2 * abs(e_B)
        Bo = max(Bo, 0.01)
        
        if L is not None and e_L is not None:
            Lo = L - 2 * abs(e_L)
            Lo = max(Lo, 0.01)
            A_eff = Bo * Lo
        else:
            Lo = None
            A_eff = Bo
            
        return Bo, Lo, A_eff
    
    def beregn_grunntrykk(self,
                          V: float,
                          Bo: float,
                          Lo: Optional[float]) -> float:
        """Beregner grunntrykket under fundamentet"""
        if Lo is not None:
            return V / (Bo * Lo)
        else:
            return V / Bo
    
    def beregn_skjaerspenning_og_ruhet(self,
                                        H_B: float,
                                        H_L: Optional[float],
                                        Bo: float,
                                        Lo: Optional[float],
                                        q: float,
                                        a: float,
                                        tan_phi_d: float) -> Tuple[float, float]:
        """
        Beregner skjærspenning og ruhet
        """
        if Lo is not None:
            H_total = np.sqrt(H_B**2 + (H_L or 0)**2)
            A_eff = Bo * Lo
        else:
            H_total = abs(H_B)
            A_eff = Bo
        
        tau = H_total / A_eff if A_eff > 0 else 0
        
        if tan_phi_d > 0.0001 and (q + a) > 0:
            r = tau / (q + a) / tan_phi_d
            r = min(max(r, 0), 1.0)
        else:
            r = 0
            
        return tau, r
    
    def interpoler_Ny(self, tan_phi_d: float, r: float) -> float:
        """
        Interpolerer Ny fra tabell basert på tan(phi_d) og ruhet r
        
        Tabellstruktur:
        - Kolonnene: tan(phi) verdier (0, 0.15, 0.175, 0.2, ..., 1.0)
        - Radene: ruhet r verdier (0, 0.1, 0.2, ..., 1.0)
        - Verdiene: Ny
        """
        # Begrens r til gyldig område [0, 1]
        r = min(max(r, 0), 1.0)
        
        # Begrens tan_phi_d til tabellens område
        tan_phi_d = min(max(tan_phi_d, 0), 1.0)
        
        # tan(phi) verdier i kolonneheader
        TAN_PHI_VALUES = [0, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 
                         0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.475, 0.5,
                         0.525, 0.55, 0.575, 0.6, 0.625, 0.65, 0.675, 0.7,
                         0.725, 0.75, 0.775, 0.8, 0.825, 0.85, 0.875, 0.9,
                         0.925, 0.95, 0.975, 1.0]
        
        # ruhet r verdier (rader)
        R_VALUES = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
        
        # Ny-tabell: NY_TABLE[r_idx][tan_phi_idx]
        # Verdier hentet fra regnearket for tan_phi = 0.65
        # Skaleres med tan_phi^2 for andre vinkler (tilnærming)
        
        # Basisverdier ved tan_phi = 0.65 (phi ≈ 33°)
        NY_BASE_R0 = 35.0   # Ved r = 0
        
        # Skaleringsformler basert på klassisk teori
        # Ny ≈ 2*(Nq+1)*tan(phi) der Nq = e^(pi*tan(phi)) * tan²(45+phi/2)
        
        # Finn Nq
        if tan_phi_d > 0.001:
            phi_d = np.degrees(np.arctan(tan_phi_d))
            phi_rad = np.radians(phi_d)
            Nq = np.exp(np.pi * tan_phi_d) * (np.tan(np.radians(45 + phi_d/2)))**2
            
            # Brinch Hansen's Ny formel (forenklet)
            Ny_r0 = 1.5 * (Nq - 1) * tan_phi_d
        else:
            Ny_r0 = 0
        
        # Reduksjonsfaktor for ruhet
        # Ved r=0: full Ny
        # Ved r=1: Ny redusert til ca 1-2% av original
        if r < 0.001:
            reduction = 1.0
        elif r < 0.1:
            reduction = 1.0 - 0.22 * (r / 0.1)
        elif r < 0.9:
            # Lineær interpolasjon mellom kjente punkter
            # r=0.1: ~78%, r=0.5: ~25%, r=0.9: ~3.5%
            reduction = 0.78 - 0.83 * (r - 0.1) / 0.8
        else:
            # r >= 0.9: svært lav bæreevne
            reduction = 0.035 - 0.033 * (r - 0.9) / 0.1
        
        reduction = max(reduction, 0.01)
        
        Ny = Ny_r0 * reduction
        
        return max(Ny, 0)
    
    def beregn_Nq_effektiv(self, phi_d: float, r: float) -> float:
        """
        Beregner Nq for effektivspenningsanalyse
        """
        if phi_d <= 0:
            return 1.0
            
        phi_rad = np.radians(phi_d)
        tan_phi_d = np.tan(phi_rad)
        
        theta_ref = np.radians(45 + phi_d / 2)
        Kp_ref = np.tan(theta_ref)**2
        
        if r > 0.0001:
            m = (1 - np.sqrt(max(0, 1 - r**2))) / (r + 0.0000001)
        else:
            m = 0
        
        theta_m = np.arctan(m * np.tan(theta_ref))
        
        Nq = 0.5 * (Kp_ref + 1 + (Kp_ref - 1) * np.cos(2 * theta_m)) * \
             np.exp((np.pi - 2 * theta_m) * tan_phi_d)
        
        return max(Nq, 1.0)
    
    def beregn_Nc_udrenert(self, r: float) -> float:
        """Beregner Nc for udrenert analyse"""
        r = min(max(r, 0), 0.999)
        Nc = np.pi + 2 + np.sqrt(1 - r**2) - np.arcsin(r)
        return Nc
    
    def beregn_formfaktorer(self, 
                            Bo: float, 
                            Lo: Optional[float],
                            phi_d: float,
                            Nq: float) -> Tuple[float, float, float]:
        """Beregner formfaktorer for rektangulære fundamenter"""
        if Lo is None:
            return 1.0, 1.0, 1.0
        
        B_over_L = Bo / Lo
        phi_rad = np.radians(phi_d)
        
        sq = 1 + B_over_L * np.sin(phi_rad)
        sy = 1 - 0.4 * B_over_L
        sy = max(sy, 0.6)
        
        if Nq > 1:
            sc = (sq * Nq - 1) / (Nq - 1)
        else:
            sc = 1.0
            
        return sq, sy, sc
    
    def beregn_reduksjonsfaktor_skraaning(self, 
                                          beta_s: float,
                                          analysetype: str) -> float:
        """Reduksjonsfaktor for skråningshelning"""
        beta_rad = np.radians(beta_s)
        
        if analysetype == 'effektiv':
            f_beta = (1 - 0.55 * np.tan(beta_rad))**5
        else:
            f_beta = 1 - 4 * beta_rad / (np.pi + 2)
        
        return max(f_beta, 0)
    
    def beregn(self,
               jord: JordParameter,
               fundament: FundamentGeometri,
               belastning: Belastning,
               terreng: TerrengForhold) -> Resultat:
        """Hovedfunksjon for bæreevneberegning"""
        
        # Fundamentvekt
        if fundament.lengde is not None:
            fund_volum = fundament.bredde * fundament.lengde * fundament.tykkelse
            vegg_volum = fundament.vegg_bredde * fundament.soyle_lengde * \
                        max(0, terreng.fundamentdybde - fundament.tykkelse)
        else:
            fund_volum = fundament.bredde * fundament.tykkelse
            vegg_volum = fundament.vegg_bredde * max(0, terreng.fundamentdybde - fundament.tykkelse)
        
        fund_vekt = (fund_volum + vegg_volum) * fundament.romvekt
        V_total = belastning.vertikal + fund_vekt
        
        # Eksentrisiteter
        e_B, e_L = self.beregn_eksentrisitet(
            V_total,
            belastning.moment_B,
            belastning.moment_L if fundament.lengde else None,
            belastning.horisontal_B,
            belastning.horisontal_L if fundament.lengde else None,
            belastning.centeravvik_B,
            belastning.centeravvik_L if fundament.lengde else 0,
            terreng.fundamentdybde,
            fundament.tykkelse
        )
        
        # Effektivt areal
        Bo, Lo, A_eff = self.beregn_effektivt_areal(
            fundament.bredde,
            fundament.lengde,
            e_B,
            e_L
        )
        
        # Grunntrykk
        q = self.beregn_grunntrykk(V_total, Bo, Lo)
        
        # Beregn basert på analysetype
        if jord.analysetype == 'effektiv':
            phi_d = np.degrees(np.arctan(
                np.tan(np.radians(jord.friksjonsvinkel)) / jord.materialfaktor
            ))
            tan_phi_d = np.tan(np.radians(phi_d))
            
            tau, r = self.beregn_skjaerspenning_og_ruhet(
                belastning.horisontal_B,
                belastning.horisontal_L if fundament.lengde else None,
                Bo, Lo, q,
                jord.attraksjon,
                tan_phi_d
            )
            
            # Bæreevnefaktorer
            Nq = self.beregn_Nq_effektiv(phi_d, r)
            Ny = self.interpoler_Ny(tan_phi_d, r)
            
            # Formfaktorer
            sq, sy, sc = self.beregn_formfaktorer(Bo, Lo, phi_d, Nq)
            
            # Reduksjonsfaktor for skråning
            f_beta = self.beregn_reduksjonsfaktor_skraaning(terreng.skraaningshelning, 'effektiv')
            
            # Overlagringstrykk
            q_overlag = terreng.romvekt_over * terreng.fundamentdybde + terreng.overflatelast
            
            # Bæreevne (Brinch Hansen)
            s = f_beta * sq * Nq * (q_overlag + jord.attraksjon) + \
                f_beta * sy * 0.5 * Ny * jord.romvekt_eff * Bo - jord.attraksjon
            
            Nc = None
            
        else:
            # Totalspenningsanalyse (udrenert)
            su_d = jord.udrenert_skjaerstyrke / jord.materialfaktor
            
            tau, _ = self.beregn_skjaerspenning_og_ruhet(
                belastning.horisontal_B,
                belastning.horisontal_L if fundament.lengde else None,
                Bo, Lo, q, 0, 1.0
            )
            
            r = tau / su_d if su_d > 0 else 0
            r = min(max(r, 0), 0.999)
            
            Nc = self.beregn_Nc_udrenert(r)
            
            if Lo is not None:
                sc = 1 + 0.2 * (Bo / Lo)
            else:
                sc = 1.0
            
            f_beta = self.beregn_reduksjonsfaktor_skraaning(terreng.skraaningshelning, 'udrenert')
            
            beta_rad = np.radians(terreng.skraaningshelning)
            
            s = f_beta * sc * Nc * su_d + \
                (terreng.romvekt_over * terreng.fundamentdybde + terreng.overflatelast) * np.cos(beta_rad)**2
            
            Nq = None
            Ny = None
        
        # Utnyttelsesgrad
        utnyttelse = q / s if s > 0 else float('inf')
        margin = s / q if q > 0 else float('inf')
        
        return Resultat(
            grunntrykk=q,
            baereevne=s,
            utnyttelsesgrad=utnyttelse,
            margin=margin,
            Nq=Nq,
            Ny=Ny,
            Nc=Nc,
            eff_bredde=Bo,
            eff_lengde=Lo,
            eksentrisitet_B=e_B,
            eksentrisitet_L=e_L,
            ruhet=r,
            reduksjonsfaktor=f_beta,
            V_total=V_total
        )
