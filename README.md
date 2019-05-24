# Human-Machine Text Extraction for Biocollections
This repository provides access to the scripts utilized during the research titled "Quality-aware Human-Machine Text Extraction for Biocollections using Ensembles of OCRs".

The automated steps of the text extraction process are the following (in order)
1. Lines' Extraction<br/>
1.1. Resize the images that are bigger than 10MB (Google Cloud limitations). Manually use script [resizeDir_mt.py](src/resizeDir_mt.py).<br/>
1.2. Line segmentation from the Google Cloud Vision API. Script [get_lines_google.py](src/get_lines_google.py). This process also extracts the text from the lines.<br/>
1.3. Binarization of the lines with OCRopus. Script [binarizeDir_mt.py](src/binarizeDir_mt.py).<br/>
1.4. Extraction of the lines' text using OCRopus. Script [recognizeDir_mt.py](src/recognizeDir_mt.py).<br/>
1.5. Extraction of the lines' text using Tesseract. Script [tessDir_mt.py](src/tessDir_mt.py).<br/>

2. Ensemble of OCRs<br/>
2.1. Accept line through majority voting. Script [getLinesAccepted.py](src/getLinesAccepted.py).<br/>
2.2. Separate the lines with match for the 3 OCR engines. Script [getLinesAccepted_Match3.py](src/getLinesAccepted_Match3.py).<br/>
2.3. N-grams construction. Script [get_n_grams.py](src/get_n_grams.py).<br/>
2.4. Computation of the per-character descriptive statistics. Script [get_stats_from_probs.py](src/get_stats_from_probs.py).<br/>
2.5. Augment the probabilities of the characters in the lines using the n-grams and descriptive statistics. Script [augment_prob_ngrams.py](src/augment_prob_ngrams.py).<br/>
2.6. Accept the lines with all their characters with probability 1.0. Script [accept_from_ngrams.py](src/accept_from_ngrams.py)<br/>

3. Compose the Full Transcription Text of the Images.<br/>
3.1. Construction of the full text transcriptions from the lines. Script [build_labels.py](src/build_labels.py).<br/>
3.2. Computation of the Damerau-Levenshtein similarity to the ground truth data. Script [fulltext_similarity_DL_dir.py](src/fulltext_similarity_DL_dir.py).<br/>
<br/>
<br/>
For a more detailed description of the text extraction process, review the following Jupyter Notebooks:<br/>
1. Lines' Extraction: [L_aocr_entomology.ipynb](notebooks/L_aocr_entomology.ipynb).<br/>
2. Ensemble of OCRs: [E_aocr_entomology.ipynb](notebooks/E_aocr_entomology.ipynb).<br/>
<br/><br/><br/>

Copyright 2019 Advanced Computing and Information Systems (ACIS) Lab - UF (https://www.acis.ufl.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.