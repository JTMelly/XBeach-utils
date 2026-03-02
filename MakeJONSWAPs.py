# make multiple JONSWAP files from arrays of boundary conditions
# assumes a jonswapTemplate.txt file exists with placeholdrs "wvheight", "wvperiod", and "wvdirection"

# %%
from pathlib import Path

# %%
drctry = '/path_to_model_directory/'
template = 'jonswapTemplate.txt'

# %%
waveheights = ["2.5", "3.0", "3.5", "4.0"]
waveperiods = ["9.0", "10.0", "11.0", "12.0"]
wavedirections = ["200.0", "205.0", "210.0", "215.0"]

# %%
with open(f'{drctry}{template}', 'r') as text:
    text_contents = text.read()
    print(text_contents)

# %%
for i in waveheights:
    for j in waveperiods:
        for k in wavedirections:
            with open(f'{drctry}{template}', 'r') as text:
                text_contents = text.read()
            text_contents = text_contents.replace('wvheight', i)
            text_contents = text_contents.replace('wvperiod', j)
            text_contents = text_contents.replace('wvdirection', k)
            with open(f'{drctry}jonswap_Hs{i}_Tp{j}_Dir{k}.txt', 'w') as newfile:
                newfile.write(text_contents)

# %%
for JSfile in Path(drctry).iterdir():
    if 'jonswap_Hs' not in JSfile.name:
        continue
    print(JSfile)
