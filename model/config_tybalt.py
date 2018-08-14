#!/usr/bin/env python
# configurations of Tybalt data, produced by VAE on cancer gene expression.

dset = 'tybalt'
data_type = 'other'
dims = [100]

# MySQL table schema
schema_meta = '''
i, name, platform, age_at_diagnosis, race, stage, vital_status,
disease, organ, gender, analysis_center, year_of_diagnosis,
ovarian_cancer_subtype'''

schema_header = 'i, gene'
