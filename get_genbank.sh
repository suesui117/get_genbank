#!/usr/bin/env bash


if [ ! -d "$(echo ~)/edirect" ]; then
    sh -c "$(curl -fsSL ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"
fi


echo Please enter a GRCh37 preferred transcript without version number: e.g. NM_020742:

read input

varname=$(echo "$input" | sed -E -e 's/\.[0-9]+.*|\..*|.[0-9]+\://g')

if ! [[  $varname = NM_[0-9]* ||  $varname = NR_[0-9]*  ]]; then
  echo "Wrong accession format"
  exit
fi

echo $varname

mkdir -p auto_genbank
mkdir -p completed

gene=$(esearch -db nuccore -query "$varname" | elink -target gene | efetch -format name|sed -n -e 's/^1.* //p')
echo $gene

esearch -db gene -query "$gene"'[gene] AND human[orgn]' |  efetch -format docsum |  xtract -pattern DocumentSummary -block LocationHistType -if AnnotationRelease -equals 105 -tab "\n" -element ChrAccVer,ChrStart,ChrStop | grep NC_0000 | awk -F '\t' '{{OFS = "\t"} if ($2 < $3) {print $1, $2+1, $3+1} else {print $1, $2+1, $3+1}}' | xargs -n 3 sh -c 'efetch -db nucleotide -id "$0" -seq_start "$1" -seq_stop "$2" -format gbwithparts' > auto_genbank/"$gene"_"$varname"_.gbk

python3 parse_preferred_transcript.py
