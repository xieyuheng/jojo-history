#include <stdio.h>

#include "../../../core/0.0.1/libjojo.h"

void p_welcome() {
  printf("  welcome to jojo ^-^/\n");
}

void expose() {
  define_prim("welcome", p_welcome);
}
