# calculate breaker depth for various modeled scenarios
# provide (paleo) sea level and spectral wave estimates (from literature/satellite/buoy...)
# based on Lorscheid and Rovere (2019) - https://doi.org/10.1186/s40965-019-0069-8
# ...and Holthuijsen (2007) - https://doi.org/10.1017/CBO9780511618536

# %%
ModernDDCP = 0      # modern sea level
HoloDDCP = 7.5      # Holocene relative sea level
PleistDDCP = 16.0   # Pleistocene relative sea level

H0 = 4.160          # wave height
T = 7.576           # wave period
C0 = 11.824         # wave celerity
s = 0.155           # beach slope

# %%
L0 = C0 * T
hb = (((3.86*(s**2))-(1.98*s)+0.88)*(H0/L0)**0.84)*L0
Modern_hb = ModernDDCP - hb
Holo_hb = HoloDDCP - hb
Pleist_hb = PleistDDCP - hb

# %%
print(f'Modern downdrift control point elevation: {round(ModernDDCP, ndigits=1)} m')
print(f'Holo downdrift control point elevation: {round(HoloDDCP, ndigits=1)} m')
print(f'Pleist downdrift control point elevation: {round(PleistDDCP, ndigits=1)} m', end='\n\n')

print(f'Modern wave breaker depth: {round(Modern_hb, ndigits=1)} m')
print(f'Holo wave breaker depth (elev): {round(Holo_hb, ndigits=1)} m')
print(f'Pleist wave breaker depth (elev): {round(Pleist_hb, ndigits=1)} m')