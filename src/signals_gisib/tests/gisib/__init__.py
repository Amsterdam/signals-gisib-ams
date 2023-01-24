import os

from vcr import VCR

gisib_api_vcr = VCR(
    cassette_library_dir=os.path.join(os.path.dirname(__file__), 'cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml'),
    match_on=['uri', 'method'],
)
