
cat > /tmp/simuben.yml <<TEST
nexus_am:
  path: $HOME/nexus-am
  toolchain_path: $(llvm-config --prefix)
verilator:
  path: $HOME/emu
nemu:
  path: $HOME/NEMU/build/riscv64-nemu-interpreter
TEST
