#include <mutex>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <unordered_map>
#include <iostream>
#include <netdb.h>
#include <cstring>
#include <string>
#include <vector>
#include <sys/select.h>
#include <unistd.h>
#include <time.h>
#include <fstream>
#include <list>
#include <utility>
//就是干！！ bro
//就是干！！我干自己
//final clean up all includes
using namespace std;

//Todo: headers parse can be here

class Http_Request{
    vector<char> buffer;
    string startline;
    string headers;
    string body;
    //need to get from startline 
    string method;
    string uri;
    string http_version;
    //need to get from headers
    unordered_map<string, std::string> header;
    //need to get from uri
    string ip;
    string port;
    string hostname;
    //Todo: initialize the buffer member 5min
    Http_Request(vector<char> req_buffer){
        buffer = req_buffer;
        parse_buffer();
    }
    void parse_buffer() {
        //logic to give startline, headers, body
        string temp_buffer = buffer.data();
        //get startline
        size_t cur_pos;
        if(temp_buffer.find("\r\n") != string::npos){
            cur_pos = temp_buffer.find("\r\n");
            startline = temp_buffer.substr(0,pos_startline);
        }else{
            return;//no start line
        }
        //get headers
        size_t headers_end = temp_buffer.find("\r\n\r\n")
        headers = temp_buffer.substr(cur_pos + 2, headers_end + 2);
        cur_pos = headers_end + 4;
        // while(temp_buffer.find(temp_buffer.begin() + cur_pos + 2, temp_buffer.end(), "\r\n") != string::npos) {
        //     size_t pos = temp_buffer.find(temp_buffer.begin() + cur_pos + 2, temp_buffer.end(), "\r\n";
        //     if(temp_buffer.substr(cur_pos + 2, pos) == "") {
        //         break;
        //     }
        //     cur_pos = cur_pos + 2;
        // }
        //get body
        body = temp_buffer.substr(cur_pos);
        //make call of subparse functions
        parse_startline();
        //parse_headers();
        //parse_body();
        parse_uri();
    }
    void parse_startline() {
        size_t cur_pos;
        cur_pos = startline.find(" ");
        //if not find the method, report 400 error
        method = startline.substr(0, cur_pos);
        cur_pos = cur_pos + 1;
        uri = startline.sub(cur_pos, startline.find(startline.begin() + cur_pos, startline.end(), " "));
        cur_pos = startline.find(startline.begin() + cur_pos, startline.end(), " ") + 1;
        http_version = startline.sub(cur_pos, startline.find("\r\n"));
        parse_uri();
    }
    // void parse_headers() {
    //     string temp_headers = headers;
    //     string
    //     while(temp_header.size() != 0) {
    //         //get
    //     }
    // }

    void parse_uri(){
        string temp_uri = uri;
        size_t pos1 = temp_uri.find("//");
        if(pos1 == string::npos){
            pos1 = 0;
        }else{
            pos1 += 2;
        }
        size_t pos2 = temp_uri.find(":",pos1);
        size_t pos3 = temp_uri.find("/",pos1);
        if(pos3 == string::npos){
            if(pos2 != string::npos){//no '/' have ':'
                hostname = temp_uri.substr(pos1,pos2);
                port = temp_uri.substr(pos2+1);
            }else{//no '/' no ':'
                hostname = temp_uri.substr(pos1);
                if(method == "CONNECT"){
                    port = "443";
                }else{
                    port = "80";
                }
            }
        }else{
            if(pos2 != string::npos){//have '/' and ':'
                hostname = temp_uri.substr(pos1,pos2);
                port = temp_uri.substr(pos2+1,pos3);
            }else{//have '/', no ':'
                hostname = temp_uri.substr(pos1,pos3);
                if(method == "CONNECT"){
                    port = "443";
                }else{
                    port = "80";
                }
            }
        }


    }
    //Todo: implement Toget, Topost, Toconnect
    /*
        1.Toget: response = get response; see what code we get;
        2.Topost: 
        3.Toconnect:
    */
    vector<char> Toget(int client_fd){
        Http_Response response;
        response = get_response();

    }
    Http_Response get_response() {
        int status;
        int server_fd;
        struct addrinfo host_info;
        struct addrinfo *host_info_list;
        const char *hostname = hostname.c_str();
        const char *port     = port.c_str();
    

        memset(&host_info, 0, sizeof(host_info));
        host_info.ai_family   = AF_UNSPEC;
        host_info.ai_socktype = SOCK_STREAM;

        status = getaddrinfo(hostname, port, &host_info, &host_info_list);
        if (status != 0) {
            cerr << "Error: cannot get address info for host" << endl;
            cerr << "  (" << hostname << "," << port << ")" << endl;
            return -1;
        } //if

        server_fd = socket(host_info_list->ai_family, 
                    host_info_list->ai_socktype, 
                    host_info_list->ai_protocol);
        if (server_fd == -1) {
            cerr << "Error: cannot create socket" << endl;
            cerr << "  (" << hostname << "," << port << ")" << endl;
            return -1;
        } //if
        
        cout << "Connecting to " << hostname << " on port " << port << "..." << endl;
        
        status = connect(server_fd, host_info_list->ai_addr, host_info_list->ai_addrlen);
        if (status == -1) {
            cerr << "Error: cannot connect to socket" << endl;
            cerr << "  (" << hostname << "," << port << ")" << endl;
            return -1;
        } //if

        send(server_fd, buffer.data(), sizeof(buffer), 0);
        vector<char> received_from_serve = receive_data(server_fd);
        freeaddrinfo(host_info_list);
        close(server_fd);
        return Http_Response(received_from_serve);
    }
    
};
class Http_Response{
    vector<char> buffer;
    string startline;
    string headers;
    string body;
    //need to get from startline 
    string http_version;
    string status_code;
    string reason;
    //need to get from headers
    unordered_map<string, std::string> header;
    //Todo: initialize the buffer member
    //Todo: parse_buffer(give value to startline, headers and bdy)and(parse(startline), 
    //parse(headers), parse(body))
};