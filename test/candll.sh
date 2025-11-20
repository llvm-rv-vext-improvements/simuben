#!/bin/sh

set -e

cd "$(dirname "$0")" || exit
cd ..

rm -rf /tmp/candll.c
rm -rf /tmp/sum.ll
rm -rf /tmp/simuben.yml

echo "#include <klib.h>                                 " >> /tmp/candll.c
echo "                                                  " >> /tmp/candll.c
echo "extern int sum(int a, int b);                     " >> /tmp/candll.c
echo "                                                  " >> /tmp/candll.c
echo "int main() {                                      " >> /tmp/candll.c
echo "    printf(\"Goodbye, XiangShan %d\", sum(1, 2)); " >> /tmp/candll.c
echo "    return 0;                                     " >> /tmp/candll.c
echo "}                                                 " >> /tmp/candll.c

echo "define dso_local i32 @sum(i32 noundef %a, i32 noundef %b) {   " >> /tmp/sum.ll
echo "entry:                                                        " >> /tmp/sum.ll
echo "  %a.addr = alloca i32, align 4                               " >> /tmp/sum.ll
echo "  %b.addr = alloca i32, align 4                               " >> /tmp/sum.ll
echo "  store i32 %a, ptr %a.addr, align 4                          " >> /tmp/sum.ll
echo "  store i32 %b, ptr %b.addr, align 4                          " >> /tmp/sum.ll
echo "  %0 = load i32, ptr %a.addr, align 4                         " >> /tmp/sum.ll
echo "  %1 = load i32, ptr %b.addr, align 4                         " >> /tmp/sum.ll
echo "  %add = add nsw i32 %0, %1                                   " >> /tmp/sum.ll
echo "  ret i32 %add                                                " >> /tmp/sum.ll
echo "}                                                             " >> /tmp/sum.ll

echo "nexus_am:                                 " >> /tmp/simuben.yml
echo "  path: $HOME/nexus-am                    " >> /tmp/simuben.yml
echo "  toolchain_path: $(llvm-config --prefix) " >> /tmp/simuben.yml

./simuben/main.py --sources /tmp/candll.c /tmp/sum.ll --config /tmp/simuben.yml
