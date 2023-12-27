#!/bin/bash

# Upload resource files to GCS.
gsutil -m cp -r /mnt/resources/woolworths/extracted_text/* "gs://woolworths_argo/extracted_text/"
gsutil -m cp -r /mnt/resources/woolworths/extracted_text_teamcare_format/* "gs://woolworths_argo/extracted_text_teamcare_format/"
gsutil -m cp -r /mnt/resources/woolworths/toc_json/* "gs://woolworths_argo/toc_json/"