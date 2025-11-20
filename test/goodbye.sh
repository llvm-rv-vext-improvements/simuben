#!/bin/sh

set -e

cd "$(dirname "$0")" || exit
cd ..

rm -rf /tmp/goodbye.c
rm -rf /tmp/simuben.yml

echo "#include <klib.h>                         " >> /tmp/goodbye.c
echo "                                          " >> /tmp/goodbye.c
echo "int main()                                " >> /tmp/goodbye.c
echo "{                                         " >> /tmp/goodbye.c
echo "    printf(\"Goodbye, XiangShan\");       " >> /tmp/goodbye.c
echo "    return 0;                             " >> /tmp/goodbye.c
echo "}                                         " >> /tmp/goodbye.c

echo "nexus_am:                                 " >> /tmp/simuben.yml
echo "  path: $HOME/nexus-am                    " >> /tmp/simuben.yml
echo "  toolchain_path: $(llvm-config --prefix) " >> /tmp/simuben.yml

./simuben/main.py --sources /tmp/goodbye.c --config /tmp/simuben.yml
