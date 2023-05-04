import pandas as pd

EXCEL_PATH = './assets/data/dropship.xlsx'
OUTPUT_PATH = './assets/data/dropship_updated.xlsx'

data = pd.read_excel(EXCEL_PATH, dtype={'NDC': str})
df = pd.DataFrame(data, columns=['NDC', 'Item', 'Drop Ship'])

unique_drugs = {
    'NDC': [],
    'Item': [],
    'Drop Ship': []
}

for ndc, item, dropship in zip(df['NDC'], df['Item'], df['Drop Ship']):
    if ndc not in unique_drugs['NDC']:
        unique_drugs['NDC'].append(ndc)
        unique_drugs['Item'].append(item)
        unique_drugs['Drop Ship'].append(dropship)

output_df = pd.DataFrame(unique_drugs)
writer = pd.ExcelWriter(OUTPUT_PATH, engine='xlsxwriter')
output_df.to_excel(
    writer, sheet_name='Drugs', startrow=0, startcol=0, index=False
)
writer.save()
