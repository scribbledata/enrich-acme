#!/bin/bash

echo "###############################"
echo "Installing Acme Datasets"
echo "###############################"

if [ -z "$ENRICH_ROOT" ];
then
   echo "This script needs enrich environment setup"
   exit
fi

DATA_ROOT="$ENRICH_DATA/acme/Marketing"
SHARED="$DATA_ROOT/shared/acme"
SALES_TEST_SHARED="$ENRICH_TEST/CarSales/shared/acme"
MODEL_TEST_SHARED="$ENRICH_TEST/CarModel/shared/acme"

# Download the dataset
mkdir -p $SHARED
mkdir -p $SALES_TEST_SHARED
mkdir -p $MODEL_TEST_SHARED
URL="https://raw.githubusercontent.com/irJERAD/Intro-to-Data-Science-in-Python/master/MyNotebooks/cars.csv"
wget -q $URL -O $SHARED/usedcars.csv
wget -q $URL -O $MODEL_TEST_SHARED/usedcars.csv
wget -q $URL -O $SALES_TEST_SHARED/usedcars.csv

URL="https://communities.sas.com/kntur85557/attachments/kntur85557/programming/113336/1/Car%20sales.csv"
wget -q $URL -O $SHARED/carsales.csv
wget -q $URL -O $SALES_TEST_SHARED/carsales.csv

echo -e "\nDownloaded usedcars and car sales dataset into "
echo "   (1) $SHARED"
echo "   (2) $SALES_TEST_SHARED"
echo "   (3) $MODEL_TEST_SHARED"


