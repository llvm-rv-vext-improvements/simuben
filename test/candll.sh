#!/usr/bin/env bash

set -e

cd "$(dirname "$0")" || exit
cd ..

cat > /tmp/candll.c <<TEST
#include <klib.h>

extern int sum(int a, int b);

int main() {
    printf("Goodbye, XiangShan %d", sum(1, 2));
    return 0;
}
TEST

cat > /tmp/sum.ll <<TEST
define dso_local i32 @sum(i32 noundef %a, i32 noundef %b) {
entry:
  %a.addr = alloca i32, align 4
  %b.addr = alloca i32, align 4
  store i32 %a, ptr %a.addr, align 4
  store i32 %b, ptr %b.addr, align 4
  %0 = load i32, ptr %a.addr, align 4
  %1 = load i32, ptr %b.addr, align 4
  %add = add nsw i32 %0, %1
  ret i32 %add
}
TEST

cat > /tmp/simuben.yml <<TEST
nexus_am:
  path: $HOME/nexus-am
  toolchain_path: $(llvm-config --prefix)
TEST

./simuben/main.py --sources /tmp/candll.c /tmp/sum.ll --config /tmp/simuben.yml
