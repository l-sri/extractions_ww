#!/bin/bash

# Create resource directory and copy resource files from GCS.

sudo mkdir -p /mnt/resources/
sudo chmod 777 /mnt/resources/
mkdir -p /mnt/resources/woolworths
rm -rf /mnt/resources/woolworths/extracted_txt_teamcare_format
mkdir -p /mnt/resources/woolworths/extracted_txt_teamcare_format
rm -rf /mnt/resources/woolworths/extracted_txt
mkdir -p /mnt/resources/woolworths/extracted_txt
rm -rf /mnt/resources/woolworths/raw_data
mkdir -p /mnt/resources/woolworths/raw_data
rm -rf /mnt/resources/woolworths/raw_pdfs
mkdir -p /mnt/resources/woolworths/raw_pdfs
mkdir -p /mnt/resources/woolworths/test_uploads
gsutil -m cp -r "gs://woolworths_argo/extracted_txt_teamcare_format/*" /mnt/resources/woolworths/extracted_txt_teamcare_format/
gsutil -m cp -r "gs://woolworths_argo/extracted_txt/*" /mnt/resources/woolworths/extracted_txt/ 
gsutil -m cp -r "gs://woolworths_argo/raw_data/*" /mnt/resources/woolworths/raw_data/
gsutil -m cp -r "gs://woolworths_argo/raw_pdfs/*" /mnt/resources/woolworths/raw_pdfs/