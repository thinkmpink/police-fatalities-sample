#!/bin/bash
parallel -j16 --pipe --block 10M grep -of victim_names/4-7_2015_names.tsv < lynx_docs/4-7_2015_lxdocs.tsv > name_hits/4-7_2015_lxhits.tsv
