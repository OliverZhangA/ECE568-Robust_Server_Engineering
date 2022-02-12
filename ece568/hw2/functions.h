#include <cstdlib>
#include <iostream>
#include <cstring>
#include <unistd.h>

void request_handler(int socket_fd);
vector<char> receive_data(int socket_fd);