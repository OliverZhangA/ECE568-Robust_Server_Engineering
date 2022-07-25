#include "operations.hpp"
//#include <pthread.h>
using namespace std;

// vector<string> split_str(string & str) {
//   vector<string> str_vec;
//   int end;
//   while ((end=str.find("\n\n")) != string::npos) {
//     str_vec.push_back(str.substr(0, end + 1);
//     str = str.substr(end + 1);
//   }
//   return str_vec;
// }
int initserver(const char * port) {
    int status;
    int socket_fd;
    struct addrinfo host_info;
    struct addrinfo *host_info_list;
    const char *hostname = NULL;
    //const char *port = "2618";
    
    memset(&host_info, 0, sizeof(host_info));

    host_info.ai_family = AF_UNSPEC;
    host_info.ai_socktype = SOCK_STREAM;
    host_info.ai_flags = AI_PASSIVE;
    //problem is here port i
    status = getaddrinfo(hostname, port, &host_info, &host_info_list);
    if (status != 0) {
        cerr << "Error: cannot get address info for host" << endl;
        cerr << "  (" << hostname << "," << port << ")" << endl;
        exit(EXIT_FAILURE);
    }

    if (strcmp(port, "") == 0) {
        ((struct sockaddr_in *)(host_info_list->ai_addr))->sin_port = 0;
    }
    //create a socket
    socket_fd = socket(host_info_list->ai_family, 
		     host_info_list->ai_socktype, 
		     host_info_list->ai_protocol);
    if (socket_fd == -1) {
        cerr << "Error: cannot create socket" << endl;
        cerr << "  (" << hostname << "," << port << ")" << endl;
        exit(EXIT_FAILURE);
    }
    //bind the socket
    int yes = 1;
    status = setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));
    status = bind(socket_fd, host_info_list->ai_addr, host_info_list->ai_addrlen);
    if (status == -1) {
        cerr << "Error: cannot bind socket" << endl;
        cerr << "  (" << hostname << "," << port << ")" << endl;
        exit(EXIT_FAILURE);
    }
    status = listen(socket_fd, 100);
    if (status == -1) {
        cerr << "Error: cannot listen on socket" << endl; 
        cerr << "  (" << hostname << "," << port << ")" << endl;
        exit(EXIT_FAILURE);
    }
    freeaddrinfo(host_info_list);
    //can not close the socket here, will use later
    return socket_fd;
}
int main(int argc, char* argv[]) {
    //initialize the tables
    connection* C = create_table();
    C->disconnect();
    delete C;
    const char* port_num = "12345";
    //generate ringmaster
    int server_fd = initserver(port_num);
    //let each of the players to connect
    
    struct sockaddr_storage socket_addr;
    socklen_t socket_addr_len = sizeof(socket_addr);
    int client_fd;
    while(1) {
        client_fd = accept(server_fd, (struct sockaddr *)&socket_addr, &socket_addr_len);
        cout<<"client_fd is "<<client_fd<<endl;
        if (client_fd == -1) {
            cerr << "Error: cannot accept connection on socket" << endl;
            continue;
            //exit(EXIT_FAILURE);
        }
        thread newthread(handle_request, client_fd);

        /*
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(0, &cpuset);
        pthread_setaffinity_np(newthread.native_handle(), sizeof(cpu_set_t), &cpuset);
        */

        newthread.detach();
    }
    
    // send(player_connection_fd, total_num, sizeof(num_players), 0);
    // send(player_connection_fd, rank, sizeof(i), 0);

        //???no need to keep track of ports because we can always get it from socket_storage
    // char buffer[65535];
    // while(1) {
    //     memset(buffer, 0, sizeof(buffer));
    //     recv(client_fd, buffer, sizeof(buffer), 0);
    //     string received_data = string(buffer);
    //     //cout<<received_data<<endl;
    //     string resp = xml_handler(received_data, C);
    //     send(client_fd, resp.c_str(), resp.size(), 0);
    // }
    // recv(client_fd, buffer, sizeof(buffer), 0);
    // string received_data = string(buffer);
    // cout<<received_data<<endl;
    // string resp = xml_handler(received_data, C);
    // send(client_fd, resp.c_str(), resp.size(), 0);
    //freeaddrinfo();
    close(server_fd);
    return EXIT_SUCCESS;
}