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
TEST_SHARED="$ENRICH_TEST/shared/acme"

# Download the dataset 
mkdir -p $SHARED
mkdir -p $TEST_SHARED
URL="https://raw.githubusercontent.com/irJERAD/Intro-to-Data-Science-in-Python/master/MyNotebooks/cars.csv"
wget -q $URL -O $SHARED/usedcars.csv
wget -q $URL -O $TEST_SHARED/usedcars.csv

URL="https://communities.sas.com/kntur85557/attachments/kntur85557/programming/113336/1/Car%20sales.csv"
wget -q $URL -O $SHARED/carsales.csv
wget -q $URL -O $TEST_SHARED/carsales.csv

echo -e "\nDownloaded usedcars and car sales dataset into "
echo "   (1) $SHARED"
echo "   (2) $TEST_SHARED" 


