#include <vector>
#include <utility>
#include <algorithm>
#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <fstream>
using namespace std;
string readin_file(string filename){
  ifstream infile(filename);
  string oneline;
  string ret;
  if(infile.is_open()){
    while (getline(infile, oneline))
    {
      ret += oneline + "\n";
    }
  } else {
    cerr<<"can not open and read the file!"<<endl;
    exit(EXIT_FAILURE);
  }
  infile.close();
  return ret;
}

vector<string> split_str(string & str) {
  vector<string> str_vec;
  size_t start = -2;
  size_t end = str.find("\n\n");
  while (end != string::npos) {
    str_vec.push_back(str.substr(start + 2, end - (start + 2)));
    start = end;
    end = str.find("\n\n", start + 2);
  }
  str_vec.push_back(str.substr(start + 2, string::npos));
  return str_vec;
}

int initclient(const char* hostname, const char* port) {
    int status;
    int socket_fd;
    struct addrinfo host_info;
    struct addrinfo *host_info_list;
    //const char *hostname = mastername;
    //const char *port = "2618";
    
    memset(&host_info, 0, sizeof(host_info));

    host_info.ai_family = AF_UNSPEC;
    host_info.ai_socktype = SOCK_STREAM;
    //host_info.ai_flags = AI_PASSIVE;

    status = getaddrinfo(hostname, port, &host_info, &host_info_list);
    if (status != 0) {
        cerr << "Error: cannot get address info for host" << endl;
        cerr << "  (" << hostname << "," << port << ")" << endl;
        exit(EXIT_FAILURE);
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
    //int yes = 1;
    // status = setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));
    // status = bind(socket_fd, host_info_list->ai_addr, host_info_list->ai_addrlen);
    // if (status == -1) {
    //     cerr << "Error: cannot bind socket" << endl;
    //     cerr << "  (" << hostname << "," << port << ")" << endl;
    //     exit(EXIT_FAILURE);
    // }
    // status = listen(socket_fd, 100);
    // if (status == -1) {
    //     cerr << "Error: cannot listen on socket" << endl; 
    //     cerr << "  (" << hostname << "," << port << ")" << endl;
    //     exit(EXIT_FAILURE);
    // }

    //connect
    status = connect(socket_fd, host_info_list->ai_addr, host_info_list->ai_addrlen);
    if (status == -1) {
        cerr << "Error: cannot connect to socket" << endl;
        cerr << "  (" << hostname << "," << port << ")" << endl;
        return -1;
    }
    freeaddrinfo(host_info_list);
    //can not close the socket here, will use later
    return socket_fd;
}
// int fetch_portnum(int socket_num) {
//     struct sockaddr_in sock;
//     socklen_t length = sizeof(sock);
//     int status;
//     status = getsockname(socket_num, (struct sockaddr*)&sock, &length);
//     if(status == -1) {
//         cerr << "not able to get socketname and the port num"<<endl;
//         exit(EXIT_FAILURE);
//     }
//     return ntohs(sock.sin_port);
// }
int main(int argc, char* argv[]) {
    if(argc != 4) {
      cout<<"usage: filename, query_id, account_id"<<endl;
      return EXIT_FAILURE;
    }
    const char* master_name = "vcm-24561.vm.duke.edu";
    const char* port_num = "12345";
    int status;
    //connect the player to the ringmaster
    int player_socknum = initclient(master_name, port_num);
    
    //send and receive and store information accordingly before the start of the game
    //send port num of this client, how to get it?
    //cout<<"selfsockfd is"<<self_sockfd<<endl;
    //int player_portnum = fetch_portnum(self_sockfd);
    string buff = readin_file(string(argv[1]));
    vector<string> buff_vec = split_str(buff);
    /*
    cout << buff_vec.size() << endl;
    cout << endl;
    cout << endl;
    for (size_t i = 0; i < buff_vec.size(); ++i) {
      cout << buff_vec[i] << endl;
      cout << endl;
      cout << endl;
    }
    */
    // "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
    // "<create><account id=\"123456\" balance=\"1000\"/>" \
    // "<symbol sym=\"SPY\">" \
    // "<account id=\"123456\">100000</account>" \
    // "</symbol>" \
    // "</create>";
    //char send_data[] = buff.c_str();
    //cout<<"num of requests is "<<buff_vec.size()<<endl;
    time_t start = time(NULL);
    for (size_t i = 0; i < buff_vec.size(); ++i) {
      //cout<<"client sending xml data: "<<endl<<buff<<endl;
      send(player_socknum, buff_vec[i].c_str(), buff_vec[i].length() + 1, 0);
      char buffer[65535];
      memset(buffer, 0, sizeof(buffer));
      recv(player_socknum, buffer, sizeof(buffer), 0);
      //cout<<"*************************"<<endl;
      //cout<<"response received:\n"<<string(buffer);
      //cout<<"*************************"<<endl<<endl;
    }

    for (size_t i = 0; i < 1000; ++i) {
      string req("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
      req += "<transactions id=\"" + string(argv[3]) + "\">";
      req += "<query id=\"" + string(argv[2]) + "\"/>";
      req += "</transactions>";
      send(player_socknum, req.c_str(), req.length() + 1, 0);
      char buffer[65535];
      memset(buffer, 0, sizeof(buffer));
      recv(player_socknum, buffer, sizeof(buffer), 0);
      //cout<<"*************************"<<endl;
      //cout<<"response received:\n"<<string(buffer);
      //cout<<"*************************"<<endl<<endl;
    }

    time_t end = time(NULL);
    cout << "Total time used: " << end - start << "s" << endl;
    cout << "Start time: " << start << endl;
    cout << "End time: " << end << endl;
    /*
    cout<<"client sending xml data: "<<endl<<buff<<endl;
    send(player_socknum, buff.c_str(), buff.size(), 0);
    char buffer[65535];
    recv(player_socknum, buffer, sizeof(buffer), 0);
    cout<<"response received:"<<string(buffer)<<endl;
    */
    close(player_socknum);
    cout<<"before return"<<endl;
    return EXIT_SUCCESS;
}