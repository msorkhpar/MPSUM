#!/usr/bin/bash

mkdir -p ESBM-eval
WORKING_DIR="$(pwd)/ESBM-eval"
ESBM_VERSION="v1.0"
ESBM_NAME="ESBM_benchmark"
ESBM_EVAL_JAR_NAME="esummeval_v1.0.jar"
to_float() {
  echo "$1" | bc -l
}

execute_and_move_the_result() {
  rm -rf MPSUM_output
  python3 core/lda_test_and_output.py
  rm -rf $WORKING_DIR/result
  mv MPSUM_output $WORKING_DIR/result
}

if [ ! -d "$WORKING_DIR/$ESBM_NAME" ]; then
  echo "Downloading ESBM benchmark dataset"
  curl https://codeload.github.com/nju-websoft/ESBM/tar.gz/master |
    tar -xz -C $WORKING_DIR --strip=2 ESBM-master/$ESBM_VERSION/$ESBM_NAME
fi

if [ ! -f "$WORKING_DIR/$ESBM_EVAL_JAR_NAME" ]; then
  echo "Downloading ESBM $ESBM_EVAL_JAR_NAME file..."
  curl --request GET -sL \
    --url "https://raw.githubusercontent.com/nju-websoft/ESBM/master/v1.0/Evaluator/$ESBM_EVAL_JAR_NAME" \
    --output "$WORKING_DIR/$ESBM_EVAL_JAR_NAME"
fi


echo "dbpedia_5, dbpedia_10, lmdb_5, lmdb_10" >F_measure.csv
echo "dbpedia_5, dbpedia_10, lmdb_5, lmdb_10" >MAP.csv
for ((i = 1; i <= 1; i++));
do
  echo "Generating result of the current project [Round $i]"
  execute_and_move_the_result
  result=$(java -jar $WORKING_DIR/$ESBM_EVAL_JAR_NAME $WORKING_DIR/$ESBM_NAME $WORKING_DIR/result |
    grep -Eo '\((dbpedia|lmdb)@\w+):\s+F-measure=([0-9.]+), MAP=([0-9.]+)' |
    sed -E 's/\((dbpedia|lmdb)@(\w+)\):\s+F-measure=([0-9.]+), MAP=([0-9.]+)/\1@\2,\3,\4/')

  while IFS=',' read -r key f_measure MAP; do
    echo "$key, $f_measure, $MAP"
    if [[ $key == "dbpedia@top5" ]]; then
      f_measure_dbpedia_5=$(to_float "$f_measure")
      map_dbpedia_5=$(to_float "$MAP")
    elif [[ $key == "dbpedia@top10" ]]; then
      f_measure_dbpedia_10=$(to_float "$f_measure")
      map_dbpedia_10=$(to_float "$MAP")
    elif [[ $key == "lmdb@top5" ]]; then
      f_measure_lmdb_5=$(to_float "$f_measure")
      map_lmdb_5=$(to_float "$MAP")
    elif [[ $key == "lmdb@top10" ]]; then
      f_measure_lmdb_10=$(to_float "$f_measure")
      map_lmdb_10=$(to_float "$MAP")
    fi
  done <<<"$result"
  echo "$f_measure_dbpedia_5, $f_measure_dbpedia_10, $f_measure_lmdb_5, $f_measure_lmdb_10" >>F_measure.csv
  echo "$map_dbpedia_5, $map_dbpedia_10, $map_lmdb_5, $map_lmdb_10" >>MAP.csv

done