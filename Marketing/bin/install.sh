#!/bin/bash 

echo "Installing Acme Datasets" 

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
wget $URL -O $SHARED/usedcars.csv
wget $URL -O $TEST_SHARED/usedcars.csv

echo "Downloaded usedcars dataset into "
echo "   (1) $SHARED"
echo "   (2) $TEST_SHARED" 


