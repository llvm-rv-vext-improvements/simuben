#!/usr/bin/env bash

set -e

cd "$(dirname "$0")" || exit
cd ..

cat > /tmp/goodbye.c <<TEST
#include <klib.h>

int main()
{
    printf("Goodbye, XiangShan");
    return 0;
}
TEST

cat > /tmp/simuben.yml <<TEST
nexus_am:
  path: $HOME/nexus-am
  toolchain_path: $(llvm-config --prefix)
TEST

./simuben/main.py --sources /tmp/goodbye.c --config /tmp/simuben.yml
