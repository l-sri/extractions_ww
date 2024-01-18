#!/bin/bash

# Upload resource files to GCS.
gsutil -m cp -r /mnt/resources/woolworths/extracted_infographics_txt/* "gs://woolworths_argo/extracted_infographics_txt/"
gsutil -m cp -r /mnt/resources/woolworths/extracted_txt/* "gs://woolworths_argo/extracted_txt/"
gsutil -m cp -r /mnt/resources/woolworths/extracted_txt_teamcare_format/* "gs://woolworths_argo/extracted_txt_teamcare_format/"
gsutil -m cp -r /mnt/resources/woolworths/toc_json/* "gs://woolworths_argo/toc_json/"
#gsutil -m cp -r /mnt/resources/woolworths/raw_infographics/* "gs://woolworths_argo/raw_infographics/"