#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <vector>
#include <arpa/inet.h>
#include <cstdlib>
#include "functions.h"
void request_handler(int socket_fd) {
    //receive之后要获得requesttime
    /*
    std::time_t seconds = std::time(nullptr);
    std::string request_time = std::string(std::asctime(std::gmtime(&seconds)));
    request_time = request_time.substr(0, request_time.find("\n"));*/
    string received = receive_data(socket_fd);
    http_request();
}
//different
bool Is_Last_Chunk(vector<char> buffer) {
    buffer.push_back('\0');
    string temp = buffer;
    size_t end_pos = temp.find("0\r\n\r\n");
    if(end_pos == string::npos) {
        return false;
    } else {
        return true;
    }
}

vector<char> deal_chunck_transmission(int socket_fd,vector<char> buffer ){
    vector<char> res;
    vector<char> temp(4096);
    res = buffer;
    while(!Is_Last_Chunk(res)) {
        int temp_size = recv(socket_fd, temp.data(), 4096, 0);
        if(temp_size < 0) {
            cerr<<"error when receiving data segment"<<endl;
            exit(EXIT_FAILURE);
        } else if(temp_size == 0) {
            res.push_back('\0');
            continue;
        }
        for(int i = 0; i < temp_size; i++) {
            res.push_back(temp[i]);
        }
        fill(temp.begin(),temp.end(), 0);
    }
    //bool is_last_chunk =  Is_Last_Chunk(buffer);
    buffer.push_back('\0');
    for(int i = 0; buffer[i] != '\0'; i++) {
        res.push_back(buffer[i]);
        res.push_back('\0');
        return res;
    }
    return buffer;
}

vector<char> receive_data(int socket_fd) {
    vector<char> buffer;
    vector<char> temp(4096, 0);
    while(true) {
        //int temp_size = recv(socket_fd, &temp.data()[0], 4096, 0);
        int temp_size = recv(socket_fd, temp.data(), 4096, 0);
        if(temp_size < 0) {
            cerr<<"error when receiving this data segment"<<endl;
            close(socket_fd);
            exit(EXIT_FAILURE);
        }
        buffer = temp;
        for(int i = 0; i < temp.size(); i++) {
            temp[i] = 0;
        }
        //for empty request
        if(temp_size == 0) {
            buffer.push_back('\0');
        }
        if(temp_size < temp.size()) {
            //check if the end of chunk transmission
            vector<char> buffer_copy = buffer;
            buffer_copy.push_back('\0');
            string request_lines = buffer_copy;
            //check chunk,0 is not chunk, 1 is chunk
            int flag = 0;
            size_t start = request_lines.find("Transfer-Encoding");
            if(start != string::npos){
                if(request_line.find("chunked",start) != string::npos){
                    flag = 1;
                }
            }
            if(flag == 1){
                //needs to do something further for chunk transmission
                return deal_chunck_transmission(socket_fd, buffer);
            }else{
                //finish receive, responding.
                buffer.push_back('\0');
                //to do: write response class
                return buffer;
            }
            
        }
    }
}