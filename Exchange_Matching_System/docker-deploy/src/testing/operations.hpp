//headers for dp operations
#include <iostream>
#include <pqxx/pqxx>
#include <string>
#include <vector>
#include <sstream>
#include <ctime>
using namespace std;
using namespace pqxx;
//header for Xml operations
#include "tinyxml2.h"
using namespace tinyxml2;
//headers for serv
#include <vector>
#include <utility>
#include <algorithm>
#include <arpa/inet.h>
#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <thread>
//Xml functions
string xml_handler(string xmltext, connection * C);

//mutex for multi-threading
#include <mutex>
extern mutex account_mtx;
extern mutex sym_mtx;
extern mutex trans_mtx;
extern mutex order_mtx;

//db operations below
connection* create_table();
connection* connect_database();
void handle_request(int client_fd);
void create_account(XMLElement* cur, connection * C, string & resp);
void create_symbol(XMLElement* root, connection * C, string & resp);
void create_symbol(string symname, string account_id, int amount, connection *C, work & W);
void transactions_handler(XMLElement* root, connection* C, string &resp);
void create_order(XMLElement* cur, connection * C, string & resp, string account_id);
void create_query(XMLElement* cur, connection * C, string & resp, string account_id);
void create_cancel(XMLElement* cur, connection * C, string & resp, string account_id);
void buy_match(XMLElement* cur, connection * C, string & resp, string account_id, work & W);
void sell_match(XMLElement* cur, connection * C, string & resp, string account_id, work & W);
string trim_num(float f);
string get_time();
string trim_xml_num(string & str);