
cat > /tmp/simuben.yml <<TEST
nexus_am:
  path: $HOME/nexus-am
  toolchain_path: $(llvm-config --prefix)
TEST
