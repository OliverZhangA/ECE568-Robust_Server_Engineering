#include "operations.hpp"
mutex account_mtx;
mutex sym_mtx;
mutex trans_mtx;
mutex order_mtx;

string trim_num(float f) {
    std::string str = std::to_string(f);
    str.erase (str.find_last_not_of('0') + 1, std::string::npos);
    if(str.find('.')==str.size()-1){
        str.erase(str.end() - 1);
    }
    return str;
}
string get_time() {
    return to_string(time(NULL));
}

string trim_xml_num(string & str) {
    size_t xml_begin = str.find('<');
    return str.substr(xml_begin, string::npos);
}

void transactions_handler(XMLElement* root, connection* C, string &resp) {
    string account_id = root->Attribute("id");
    work W0(*C);
    stringstream sql;
    sql << "SELECT COUNT(*) FROM \"ACCOUNT\" WHERE \"ACCOUNT_ID\" = "<<W0.quote(account_id)<<";";
    result R(W0.exec(sql.str()));
    W0.commit();
    if(R[0][0].as<int>() == 0) {
        resp += "<error id=\"" + account_id + "\">ACCONT_NOT_EXIST</error>\n";
        return;
    }

    XMLElement* cur = root->FirstChildElement();
    while(cur) {
        if(strcmp(cur->Name(), "order") == 0) {
            //parameters and return value???
            sym_mtx.lock();
            trans_mtx.lock();
            order_mtx.lock();
            create_order(cur, C, resp, account_id);
            // string symname = cur->Attribute("sym");
            // work W(*C);
            // stringstream sql0;
            // sql0 << "SELECT COUNT(*) FROM \"ACCOUNT\" WHERE \"ACCOUNT_ID\" = "<<W.quote(account_id)<<";";
            // result R(W.exec(sql0.str()));
            // W.commit();
            //if the account exits
            // if(R[0][0].as<int>() == 1) {
            //     create_order(cur, C, resp, account_id);
            // } else {
            //     // Respond error (account does not exist)
            //     resp += "<error sym=\"" + symname + "\" id=\"" + string(cur->Attribute("id")) + "\">ACCOUNT_NOT_EXISTS</error>";
            // }
            order_mtx.unlock();
            trans_mtx.unlock();
            sym_mtx.unlock();
        } else if(strcmp(cur->Name(), "query") == 0) {
            //cout<<"cancelling order!"<<endl;
            create_query(cur, C, resp, account_id);
        } else if(strcmp(cur->Name(), "cancel") == 0) {
            //sym_mtx.lock();
            trans_mtx.lock();
            order_mtx.lock();
            //account_mtx.lock();
            create_cancel(cur, C, resp, account_id);
            //sym_mtx.lock();
            order_mtx.unlock();
            trans_mtx.unlock();
            //account_mtx.lock();
        } else {
            cerr<<"wrong format"<<endl;
        }
        cur = cur->NextSiblingElement();
    }
}
string xml_handler(string xmltext, connection* C){
    string resp("<results>\n");
    XMLDocument doc;
    // doc.LoadXml("<book xmlns:bk='urn:samples'>" +
    //             "<bk:ISBN>1-861001-57-5</bk:ISBN>" +
    //             "<title>Pride And Prejudice</title>" +
    //             "</book>");
    doc.Parse(xmltext.c_str());
    XMLElement* elmtRoot = doc.RootElement();
    //initalize a response variable x
    while(elmtRoot) {
        if(strcmp(elmtRoot->Name(), "create") == 0) {
            //cout<<"this xml is create"<<endl;
            XMLElement* cur = elmtRoot->FirstChildElement();
            while(cur) {
                if(strcmp(cur->Name(), "account") == 0) {
                    //parameters and return value???
                    create_account(cur, C, resp);
                } else if(strcmp(cur->Name(), "symbol") == 0) {
                    create_symbol(cur, C, resp);
                } else {
                    cerr<<"wrong format"<<endl;
                }
                cur = cur->NextSiblingElement();
            }
        } else if(strcmp(elmtRoot->Name(), "transactions") == 0) {
            transactions_handler(elmtRoot, C, resp);
        } else {
            //report error
            resp += "<error>Not a valid operation</error>\n";
        }
        elmtRoot = elmtRoot->NextSiblingElement();
    }
    resp += "</results>\n";
    return resp;
}

void handle_request(int client_fd) {
    connection* C = connect_database();
    char buffer[65535];
    cout<<"going to handle request"<<endl;
    while(1){
        memset(buffer, 0, sizeof(buffer));
        int recsize = recv(client_fd, buffer, sizeof(buffer), 0);
        if(recsize == 0) {
            break;
        }
        //cout<<"recsize is "<<recsize<<endl;
        string received_data = string(buffer);
        //cout<<received_data<<endl;
        string resp = xml_handler(trim_xml_num(received_data), C);
        //cout<<"resp is"<<resp<<endl;
        int sendflag = send(client_fd, resp.c_str(), resp.size(), 0);
        //cout<<"sendflag is "<<sendflag<<endl;
    }
    C->disconnect();
    delete C;
    close(client_fd);
}