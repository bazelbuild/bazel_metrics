#!/bin/bash

if [[ $# -ne 2 ]] ; then
  echo 'usage: raw_to_csv.sh year month'
  exit 1
fi
year=$1
month=$(printf %02d $2)

RAW=downloads/raw/$year/${year}${month}.txt
if [[ ! -f "$RAW" ]] ; then
  echo Could not find input "$RAW".
  exit 1
fi

CATEGORIZED=downloads/categorized/${year}${month}.csv

python src/categorize_raw.py "$RAW"  >"$CATEGORIZED"

# TODO: Delta the categorized data per day, then reduce to the CSV buckets
# by stripping the raw file name.

exit 0
