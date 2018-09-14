#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>

#include "jojo.h"

jo_t TAG_SOCKET;

void p_tcp_socket_listen() {
  // [:service <string> :backlog <int>] -> [<socket>]

  struct addrinfo hints, *servinfo, *p;
  int yes = 1;

  struct dp a = ds_pop();
  int backlog = a.d;

  struct dp b = ds_pop();
  struct gp* bp = b.d;
  char* service = bp->p;

  memset(&hints, 0, sizeof hints);
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;
  hints.ai_flags = AI_PASSIVE;

  int rv = getaddrinfo(0, service, &hints, &servinfo);
  if (rv != 0) {
    report("- p_tcp_socket_listen fail to getaddrinfo\n");
    report("  service : %s\n", service);
    report("getaddrinfo: %s\n", gai_strerror(rv));
    p_debug();
    return;
  }

  int sockfd;
  for(p = servinfo; p != 0; p = p->ai_next) {
    sockfd = socket(p->ai_family,
                    p->ai_socktype,
                    p->ai_protocol);
    if (sockfd == -1) { continue; }
    // ><><>< why setsockopt ?
    if (setsockopt(sockfd,
                   SOL_SOCKET,
                   SO_REUSEADDR, &yes, sizeof(int)) == -1) {
      report("- p_tcp_socket_listen fail to listen\n");
      report("  service : %s\n", service);
      perror("  setsockopt error : ");
      p_debug();
    }
    if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
      close(sockfd);
      continue;
    }
    break;
  }
  freeaddrinfo(servinfo);

  if (p == 0)  {
    report("- p_tcp_socket_listen fail to bind\n");
    report("  service : %s\n", service);
    p_debug();
  }

  if (listen(sockfd, backlog) == -1) {
    report("- p_tcp_socket_listen fail to listen\n");
    report("  service : %s\n", service);
    perror("  listen error : ");
    p_debug();
  }

  ds_push(TAG_SOCKET, sockfd);
}

// get sockaddr, ipv4 or ipv6:
void *get_in_addr(struct sockaddr *sa) {
  if (sa->sa_family == AF_INET) {
    return &(((struct sockaddr_in*)sa)->sin_addr);
  }
  return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

void p_socket_accept() {
  // [:sockfd <socket>] ->
  // [:newfd <socket> :connector-address <string>]

  struct dp a = ds_pop();
  int sockfd = a.d;

  struct sockaddr_storage their_addr; // connector's address information
  socklen_t sin_size;
  char str[INET6_ADDRSTRLEN];

  sin_size = sizeof their_addr;
  int newfd = accept(sockfd, (struct sockaddr *)&their_addr, &sin_size);
  if (newfd == -1) {
    report("- p_socket_accept fail\n");
    perror("  accept error : ");
    return;
  }

  inet_ntop(their_addr.ss_family,
            get_in_addr((struct sockaddr *)&their_addr),
            str,
            sizeof(str));

  ds_push(TAG_SOCKET, newfd);
  ds_push(TAG_STRING, new_string_gp(str));
}

void p_tcp_socket_connect() {
  // [:host <string> :service <string>] -> [<socket>]

  struct dp a = ds_pop();
  struct gp* ap = a.d;
  char* service = ap->p;

  struct dp b = ds_pop();
  struct gp* bp = b.d;
  char* host = bp->p;

  struct addrinfo hints, *servinfo, *p;

  memset(&hints, 0, sizeof hints);
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;

  int rv = getaddrinfo(host, service, &hints, &servinfo);
  if (rv != 0) {
    report("- p_tcp_socket_connect fail to getaddrinfo\n");
    report("  host : %s\n", host);
    report("  service : %s\n", service);
    report("  getaddrinfo error : %s\n", gai_strerror(rv));
    p_debug();
    return;
  }

  int sockfd;
  for(p = servinfo; p != 0; p = p->ai_next) {
    sockfd = socket(p->ai_family,
                    p->ai_socktype,
                    p->ai_protocol);
    if (sockfd == -1) { continue; }
    if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
      close(sockfd);
      continue;
    }
    break;
  }
  freeaddrinfo(servinfo);

  if (p == 0)  {
    report("- p_tcp_socket_connect fail to connect\n");
    report("  host : %s\n", host);
    report("  service : %s\n", service);
    p_debug();
  }

  ds_push(TAG_SOCKET, sockfd);
}

void p_socket_send() {
  // [<socket> <string>] -> []

  struct dp a = ds_pop();
  struct gp* ap = a.d;
  char* str = ap->p;

  struct dp b = ds_pop();
  int sockfd = b.d;

  if (send(sockfd, str, strlen(str), 0) == -1) {
    report("- p_socket_send fail\n");
    perror("  send error : ");
  }
}

void p_socket_recv() {
  // [<socket>] -> [<string>]
  struct dp a = ds_pop();
  int sockfd = a.d;

  char* buf[1024];

  ssize_t real_bytes = recv(sockfd, buf, 1024-1, 0);
  if (real_bytes == -1) {
    report("- p_socket_recv fail\n");
    perror("  recv error : ");
  }

  ds_push(TAG_STRING, new_string_gp(strdup(buf)));
}
