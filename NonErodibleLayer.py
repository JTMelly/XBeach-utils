# creates a non-erodible layer covering the entire model domain
# needs a bed.dep file as input
# to use, activate in the model's params.txt file

# %%
from pathlib import Path

# %%
drctry = '/path_to_model_directory/'

# %%
folder = Path(drctry)
input_file = folder / 'bed.dep'
output_file = folder / 'NonErodibleLayer.dep'

if not input_file.exists():
  raise FileNotFoundError(f'File not found: {input_file}')

with input_file.open() as in_file, output_file.open('w') as out_file:
  out_file.writelines(' '.join('0.0' for _ in line.split()) + '\n' for line in in_file)

print(f'{output_file} saved.')