#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Runs preprocessing and scansion on a text.

Usage:
  run_clients.sh -r <run_id> [-p <path_to_poem_file>]

Options:
  -r   Run ID (required). Creates ../texts/run_<run_id>
  -p   Optional path to a poem text file. If omitted, uses the POEM heredoc.
USAGE
}

run_id=""
poem_path=""

while getopts ":r:p:h" opt; do
  case "$opt" in
    r) run_id="$OPTARG" ;;
    p) poem_path="$OPTARG" ;;
    h) usage; exit 0 ;;
    :) echo "Error: -$OPTARG requires an argument." >&2; exit 2 ;;
    \?) echo "Error: Unknown option -$OPTARG" >&2; exit 2 ;;
  esac
done

if [[ -z "${run_id}" ]]; then
  echo "Error: -r <run_id> is required." >&2
  usage
  exit 2
fi

# Paths
run_dir="../texts/run_${run_id}"
out_txt="${run_dir}/example_001.txt"

mkdir -p "${run_dir}"

# Write poem content
if [[ -n "${poem_path}" ]]; then
  if [[ ! -r "${poem_path}" ]]; then
    echo "Error: Cannot read file: ${poem_path}" >&2
    exit 2
  fi
  cp -f "${poem_path}" "${out_txt}"
else
  cat > "${out_txt}" <<'POEM'
Os que decís, qu' a muller
non ten a cabeza feita
pra soster unha coroa
e que non sirve pra reina.
É qu' esquencedes cicais
que tod' a hestoria está chea
de nomes qu' o brilo teñen
de luminosas estrelas.
Semíramis i-Artemisa:
duas Aspasias y-a nena
File, filla d' Antipatro,
con quen iste s' aconsella;
Livia que domin' á Augusto
y-o mundo co-él goberna:
Agripina qu' ô seu fillo
de Roma o imperio lle dera:
a ilustrada Amalasunta
qu' entende todal-as lengoas:
a gran reina anque croel
Sabela d' Ingalaterra:
a Catelina de Médeces
y-a Católeca Sabela,
POEM
fi

# Preprocess

echo "= Starts preprocessing for run ID: ${run_id}"

python run_prepro.py "${out_txt}" \
  --preprocess --normalize --stress_possessives \
  --disambiguate_stress --destress \
  --run_id "${run_id}" --run_comment "run example text"

# Scansion

echo "= Starts scansion"
python run_scan_eval.py \
  "../texts/run_${run_id}/out_${run_id}/example_001_pp_out_norm_spa_${run_id}.txt" dummy "${run_id}" \
  --skip_eval --out_dir "../texts/run_${run_id}/out_${run_id}"

echo "Processing complete. Scansion output in ${run_dir}/out_${run_id}/scansion_output_${run_id}.tsv"
