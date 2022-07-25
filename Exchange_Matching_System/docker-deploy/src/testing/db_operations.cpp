#include "operations.hpp"
connection* connect_database() {
  //Allocate & initialize a Postgres connection object
  connection *C;

  try{
    //Establish a connection to the database
    //Parameters: database name, user name, user password
    C = new connection("host=db port=5432 dbname=postgres user=postgres password=postgres");
    if (C->is_open()) {
      cout << "Opened database successfully: " << C->dbname() << endl;
    } else {
      cout << "Can't open database" << endl;
      exit(EXIT_FAILURE);
    }
  } catch (const std::exception &e){
    cerr << e.what() << std::endl;
    exit(EXIT_FAILURE);
  }
  return C;
}
connection* create_table() {

  //Allocate & initialize a Postgres connection object
  connection *C = connect_database();

  // try{
  //   //Establish a connection to the database
  //   //Parameters: database name, user name, user password
  //   C = new connection("dbname=EXCHANGE user=postgres password=passw0rd");
  //   if (C->is_open()) {
  //     cout << "Opened database successfully: " << C->dbname() << endl;
  //   } else {
  //     cout << "Can't open database" << endl;
  //     exit(EXIT_FAILURE);
  //   }
  // } catch (const std::exception &e){
  //   cerr << e.what() << std::endl;
  //   exit(EXIT_FAILURE);
  // }


  //TODO: create PLAYER, TEAM, STATE, and COLOR tables in the ACC_BBALL database
  //      load each table with rows from the provided source txt files
  work W(*C);

  string sql_drop;

  sql_drop = "DROP TABLE IF EXISTS \"SYMBOL\" CASCADE; " \
  "DROP TABLE IF EXISTS \"ORDER\" CASCADE; " \
  "DROP TABLE IF EXISTS \"TRANSACTION\" CASCADE; " \
  "DROP TABLE IF EXISTS \"ACCOUNT\" CASCADE;";

  W.exec(sql_drop);

  string sql_account;
  sql_account = "CREATE TABLE \"ACCOUNT\" (" \
  "\"ACCOUNT_ID\" VARCHAR(20) NOT NULL," \
  "\"BALANCE\" FLOAT NOT NULL," \
  "PRIMARY KEY (\"ACCOUNT_ID\"));";

  W.exec(sql_account);

  string sql_trans;
  sql_trans = "CREATE TABLE \"TRANSACTION\" (" \
  "\"TRANS_ID\" SERIAL PRIMARY KEY," \
  "\"BUY_ID\" VARCHAR(20) NOT NULL," \
  "\"SELL_ID\" VARCHAR(20) NOT NULL," \
  "\"SYM\" VARCHAR(20) NOT NULL,"
  "\"NUM\" FLOAT NOT NULL," \
  "\"PRICE\" FLOAT NOT NULL," \
  "\"BUYORDER_ID\" INT NOT NULL," \
  "\"SELLORDER_ID\" INT NOT NULL," \
  "\"STATUS\" VARCHAR(20) NOT NULL," \
  "\"TRANS_TIME\" INT NOT NULL," \
  "FOREIGN KEY (\"BUY_ID\") REFERENCES \"ACCOUNT\"(\"ACCOUNT_ID\") ON DELETE CASCADE," \
  "FOREIGN KEY (\"SELL_ID\") REFERENCES \"ACCOUNT\"(\"ACCOUNT_ID\") ON DELETE CASCADE);";

  W.exec(sql_trans);

  string sql_order;
  sql_order = "CREATE TABLE \"ORDER\" (" \
  "\"ID\" SERIAL PRIMARY KEY," \
  "\"ACCOUNT_ID\" VARCHAR(20) NOT NULL," \
  // Is symbol a foreign key?
  "\"SYM\" VARCHAR(20) NOT NULL," \
  "\"AMOUNT\" FLOAT NOT NULL," \
  "\"PRICE\" FLOAT NOT NULL," \
  "\"STATUS\" VARCHAR(10) NOT NULL," \
  "FOREIGN KEY (\"ACCOUNT_ID\") REFERENCES \"ACCOUNT\"(\"ACCOUNT_ID\") ON DELETE CASCADE);";
  W.exec(sql_order);

  string sql_symbol;
  // How to know the number of symbols?
  sql_symbol = "CREATE TABLE \"SYMBOL\" (" \
  "\"ACCOUNT_ID\" VARCHAR(20) NOT NULL," \
  "\"SYM\" VARCHAR(20) NOT NULL," \
  "\"SHARE\" FLOAT NOT NULL," \
  /*
  "\"TEAM_ID\" INT NOT NULL," \
  "\"UNIFORM_NUM\" INT NOT NULL," \
  "\"FIRST_NAME\" VARCHAR(30) NOT NULL," \
  "\"LAST_NAME\" VARCHAR(30) NOT NULL," \
  "\"MPG\" INT NOT NULL," \
  "\"PPG\" INT NOT NULL," \
  "\"RPG\" INT NOT NULL," \
  "\"APG\" INT NOT NULL," \
  "\"SPG\" DECIMAL(2,1) NOT NULL," \
  "\"BPG\" DECIMAL(2,1) NOT NULL," \
  */
  "PRIMARY KEY (\"ACCOUNT_ID\", \"SYM\"), " \
  "FOREIGN KEY (\"ACCOUNT_ID\") REFERENCES \"ACCOUNT\"(\"ACCOUNT_ID\") ON DELETE CASCADE);";

  W.exec(sql_symbol);

  W.commit();

  /*
  string colorStr("color.txt");
  vector<string> colorLines = readFile(colorStr.c_str());
  insertColors(C, colorLines);
  string stateStr("state.txt");
  vector<string> stateLines = readFile(stateStr.c_str());
  insertStates(C, stateLines);
  string teamStr("team.txt");
  vector<string> teamLines = readFile(teamStr.c_str());
  insertTeams(C, teamLines);
  string playerStr("player.txt");
  vector<string> playerLines = readFile(playerStr.c_str());
  insertPlayers(C, playerLines);


  exercise(C);
  */


  //Close database connection
  C->disconnect();
  return C;

}
// Check balance cannot be negative
void create_account(XMLElement* cur, connection * C, string & resp) {
  account_mtx.lock();
  work W(*C);
  //count if acount exists, if not, create
  stringstream sql0;
  sql0 << "SELECT COUNT(*) FROM \"ACCOUNT\" WHERE \"ACCOUNT_ID\" = "<<W.quote(cur->Attribute("id"))<<";";
  // nontransaction N(*C);
  result R(W.exec(sql0.str()));
  if (R[0][0].as<int>() != 0) {
    // Respond error                                                                      
    resp += "<error id=\"" + string(cur->Attribute("id")) + "\">ACCOUNT_ALREADY_EXISTS</error>\n";
    account_mtx.unlock();
    return;
  }
  stringstream sql;
  sql <<"INSERT INTO \"ACCOUNT\" VALUES ("<<W.quote(cur->Attribute("id"))<<","<<stof(cur->Attribute("balance"))<<");";
  W.exec(sql.str());
  W.commit();
  account_mtx.unlock();
  resp += "<created id=\"" + string(cur->Attribute("id")) + "\"/>\n";
}
//this is the function for symbol in creation
void create_symbol(XMLElement* root, connection * C, string & resp) {
  string symname = root->Attribute("sym");
  XMLElement* cur = root->FirstChildElement();
  while(cur) {
    //count if acount exists
    //count if symbol exists
    sym_mtx.lock();
    account_mtx.lock();
    work W(*C);
    stringstream sql0;
    sql0 << "SELECT COUNT(*) FROM \"ACCOUNT\" WHERE \"ACCOUNT_ID\" = "<<W.quote(cur->Attribute("id"))<<";";
    result R(W.exec(sql0.str()));
    //if the count exits
    if(R[0][0].as<int>() == 1) {
      //if symbol exists
      stringstream sql1;
      sql1 << "SELECT COUNT(*) FROM \"SYMBOL\" WHERE \"ACCOUNT_ID\" = "<<W.quote(cur->Attribute("id"))
          <<" AND "<<"\"SYM\" = "<<W.quote(symname)<<";";
      //sql2<<"INSERT INTO \"SYMBOL\" VALUES ("<<W.quote(cur->Attribute("id"))<<","<<stoi(cur->Attribute("balance"))<<");";
      result D(W.exec(sql1.str()));
      if (D[0][0].as<int>() == 1) {
        //get the origin share value
        stringstream sql2;
        sql2 << "SELECT \"SHARE\" FROM \"SYMBOL\" WHERE \"ACCOUNT_ID\" = "<<W.quote(cur->Attribute("id"))
          <<" AND "<<"\"SYM\" = "<<W.quote(symname)<<" FOR UPDATE;";
        result H(W.exec(sql2.str()));
        float origin_share = H[0][0].as<float>();
        float add_share = stof(string(cur->GetText()));
        stringstream sql3;
        sql3 <<"UPDATE \"SYMBOL\" SET \"SHARE\"=" << origin_share + add_share << "WHERE \"ACCOUNT_ID\" = "<<W.quote(cur->Attribute("id"))
          <<" AND "<<"\"SYM\" = "<<W.quote(symname)<<";";
        W.exec(sql3.str());
      } else {
        //cout<<"new share is "<<cur->Name()<<endl;
        float share = stof(string(cur->GetText()));
        stringstream sql4;
        sql4 <<"INSERT INTO \"SYMBOL\" VALUES ("<<W.quote(cur->Attribute("id"))<<","<<W.quote(symname)<<","<<share<<");";
        W.exec(sql4.str());
      }
      resp += "<created sym=\"" + symname + "\" id=\"" + string(cur->Attribute("id")) + "\"/>\n";
    } else {
      // Respond error (account does not exist)
      resp += "<error sym=\"" + symname + "\" id=\"" + string(cur->Attribute("id")) + "\">ACCOUNT_NOT_EXISTS</error>\n";
    }
    cur = cur->NextSiblingElement();
    W.commit();
    account_mtx.unlock();
    sym_mtx.unlock();
  }
}
//this is the function for symbol in tra
void create_symbol(string symname, string account_id, float amount, connection * C, work & W) {
  //if symbol exists
  stringstream sql1;
  sql1 << "SELECT COUNT(*) FROM \"SYMBOL\" WHERE \"ACCOUNT_ID\" = "<<W.quote(account_id)
      <<" AND "<<"\"SYM\" = "<<W.quote(symname)<<";";
  //sql2<<"INSERT INTO \"SYMBOL\" VALUES ("<<W.quote(cur->Attribute("id"))<<","<<stoi(cur->Attribute("balance"))<<");";
  result D(W.exec(sql1.str()));
  if (D[0][0].as<int>() == 1) {
    //get the origin share value
    stringstream sql2;
    sql2 << "SELECT \"SHARE\" FROM \"SYMBOL\" WHERE \"ACCOUNT_ID\" = "<<W.quote(account_id)
      <<" AND "<<"\"SYM\" = "<<W.quote(symname)<<" FOR UPDATE;";
    result H(W.exec(sql2.str()));
    float origin_share = H[0][0].as<float>();
    float add_share = amount;
    stringstream sql3;
    sql3 <<"UPDATE \"SYMBOL\" SET \"SHARE\"=" << origin_share + add_share << "WHERE \"ACCOUNT_ID\" = "<<W.quote(account_id)
      <<" AND "<<"\"SYM\" = "<<W.quote(symname)<<";";
    W.exec(sql3.str());
  } else {
    //cout<<"new share is "<<symname<<endl;
    float share = amount;
    stringstream sql4;
    sql4 <<"INSERT INTO \"SYMBOL\" VALUES ("<<W.quote(account_id)<<","<<W.quote(symname)<<","<<share<<");";
    W.exec(sql4.str());
  }
  //resp += "<created sym=\"" + symname + "\" id=\"" + string(cur->Attribute("id")) + "\"/>";
}
void create_order(XMLElement* cur, connection * C, string & resp, string account_id) {
  string sym = cur->Attribute("sym");
  float amount = stof(cur->Attribute("amount"));
  float limit = stof(cur->Attribute("limit"));
  work W(*C);
  if(amount > 0) {
    //to buy
    string sql_balance;
    sql_balance = "SELECT \"BALANCE\" FROM \"ACCOUNT\" WHERE \"ACCOUNT_ID\"=\'" + account_id + "\' FOR UPDATE;";
    result R1(W.exec(sql_balance));
    //W1.commit();
    float cur_balance = R1[0][0].as<float>();
    if (amount * limit <= cur_balance) {
      //work W2(*C);
      string sql_deduct;
      sql_deduct = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=" + to_string(cur_balance - amount * limit) + "WHERE " \
      "\"ACCOUNT_ID\"=\'" + account_id +"\';";
      W.exec(sql_deduct);
      //W2.commit();
    } else {
      // buyer not having enough money, respond error
      resp += "<error sym=\""+sym+"\" amount=\""+trim_num(amount)+"\" limit=\""
            +trim_num(limit)+"\">Buyer not having enough money to post the order!</error>\n";
      W.commit();
      return;
    }
    buy_match(cur, C, resp, account_id, W);
  } else if(amount < 0) {
    //to sell
    amount = -amount;
    string sql_share;
    sql_share = "SELECT \"SHARE\" FROM \"SYMBOL\" WHERE \"ACCOUNT_ID\"=\'" + account_id + "\' AND \"SYM\"=\'" 
    + sym + "\' FOR UPDATE;";
    result R2(W.exec(sql_share));
    //W3.commit();
    if(R2.size()==0) {
      // if seller does not have that kind of symbol, respond error
      resp += "<error sym=\""+sym+"\" amount=\""+trim_num(-amount)+"\" limit=\""
            +trim_num(limit)+"\">Seller not having that symbol to post the order!</error>\n";
      W.commit();
      return;
    }
    float cur_share = R2[0][0].as<float>();
    if (amount <= cur_share) {
      //work W4(*C);
      string sql_deduct;
      sql_deduct = "UPDATE \"SYMBOL\" SET \"SHARE\"=" + to_string(cur_share - amount) + "WHERE " \
      "\"ACCOUNT_ID\"=\'" + account_id + "\' AND \"SYM\"=\'" + sym + "\';";
      W.exec(sql_deduct);
      //W4.commit();
    } else {
      // if seller does not have enough share, respond error
      resp += "<error sym=\""+sym+"\" amount=\""+trim_num(-amount)+"\" limit=\""
            +trim_num(limit)+"\">Seller not having enough share to post the order!</error>\n";
      W.commit();
      return;
    }
    sell_match(cur, C, resp, account_id, W);
  } else {
    //if amount in order is 0, report error
    resp += "<error sym=\""+sym+"\" amount=\""+trim_num(-amount)+"\" limit=\""
            +trim_num(limit)+"\">order amount is 0, this order is invalid!</error>\n";
    W.commit();
    return;
  }
  W.commit();
}
void buy_match(XMLElement* cur, connection * C, string & resp, string account_id, work & W) {
  string sym = cur->Attribute("sym");
  float amount = stof(cur->Attribute("amount"));
  float limit = stof(cur->Attribute("limit"));
  //work W0(*C);
  string add_buy_order;
  add_buy_order = "INSERT INTO \"ORDER\" (\"ACCOUNT_ID\", \"SYM\", \"AMOUNT\", \"PRICE\", \"STATUS\") VALUES (\'" 
  + account_id + "\', \'" + sym + "\', " + to_string(amount) 
  + ", " + to_string(limit) + ", \'BUY\') RETURNING \"ID\";";
  result R0(W.exec(add_buy_order));
  //W0.commit();
  int buy_order_id = R0[0][0].as<int>();
  //add open statement to response
  resp+="<opened sym=\""+sym+"\" amount=\""+trim_num(amount)+"\" limit=\""
        +trim_num(limit)+"\" id=\""+to_string(buy_order_id)+"\"/>\n";
  //
  //work W1(*C);
  string sql_sell;
  sql_sell = "SELECT * FROM \"ORDER\" WHERE \"STATUS\" = \'SELL\' AND \"SYM\"=\'" + sym + "\' AND \"PRICE\"<="
  + to_string(limit) + " ORDER BY \"PRICE\" ASC FOR UPDATE;";
  result R(W.exec(sql_sell));
  // W.commit();
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
    //work W(*C);
    // if (c[4].as<int>() <= limit) {
    if (c[3].as<float>() > amount) {
      // Add a transaction
      // Update seller amount, account
      // Update buyer's share
      // break
      string sql_trans;
      sql_trans = "INSERT INTO \"TRANSACTION\" (\"BUY_ID\", \"SELL_ID\", \"SYM\", \"NUM\", \"PRICE\", \"BUYORDER_ID\", \"SELLORDER_ID\", \"STATUS\", \"TRANS_TIME\") VALUES (\'" 
      + account_id + "\', \'" + c[1].as<string>() + "\', \'" 
      + sym + "\', " + to_string(amount) + ", " + to_string(c[4].as<float>()) + ", " + to_string(buy_order_id) + ", " + to_string(c[0].as<int>()) + ", \'EXECUTED\', " + get_time() + ");";
      W.exec(sql_trans);
      string sql_amount;
      sql_amount = "UPDATE \"ORDER\" SET \"AMOUNT\"=" + to_string(c[3].as<float>() - amount) + " WHERE \"ID\"=" + to_string(c[0].as<int>()) + ";";
      W.exec(sql_amount);
      string sql_balance;
      sql_balance = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(amount*c[4].as<float>())+" WHERE \"ACCOUNT_ID\"=\'"+c[1].as<string>()+"\';";
      W.exec(sql_balance);
      //W.commit();
      create_symbol(sym, account_id, amount, C, W);
      //refund delta
      //work W5(*C);
      string sql_refund;
      sql_refund = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(amount*(limit - c[4].as<float>()))+" WHERE \"ACCOUNT_ID\"=\'"+account_id+"\';";
      W.exec(sql_refund);
      amount = 0;
      //W5.commit();
      break;
    } else if (c[3].as<float>() < amount) {
      // delete seller order, update seller's account
      // add a transaction, and update buyer's amount
      // go on
      string delete_sellorder;
      delete_sellorder = "DELETE FROM \"ORDER\" WHERE \"ID\"="+to_string(c[0].as<int>())+";";
      W.exec(delete_sellorder);

      string sql_seller_balance;
      sql_seller_balance = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(amount*c[4].as<float>())+" WHERE \"ACCOUNT_ID\"=\'"+c[1].as<string>()+"\';";
      W.exec(sql_seller_balance);

      string sql_trans;
      sql_trans = "INSERT INTO \"TRANSACTION\" (\"BUY_ID\", \"SELL_ID\", \"SYM\", \"NUM\", \"PRICE\", \"BUYORDER_ID\", \"SELLORDER_ID\", \"STATUS\", \"TRANS_TIME\") VALUES (\'" 
      + account_id + "\', \'" + c[1].as<string>() + "\', \'" 
      + sym + "\', " + to_string(c[3].as<float>()) + ", " + to_string(c[4].as<float>()) + ", " + to_string(buy_order_id) + ", " + to_string(c[0].as<int>()) + ", \'EXECUTED\', " + get_time() + ");";
      W.exec(sql_trans);
      //W.commit();

      create_symbol(sym, account_id, c[3].as<float>(), C, W);
      amount-=c[3].as<float>();
      //refund delta
      //work W6(*C);
      string sql_refund;
      sql_refund = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(c[3].as<float>()*(limit - c[4].as<float>()))+" WHERE \"ACCOUNT_ID\"=\'"+account_id+"\';";
      W.exec(sql_refund);
      //W6.commit();
    } else {
      // delete seller order, update seller's account
      // add a transaction, update buyer's amount
      string delete_sellorder;
      delete_sellorder = "DELETE FROM \"ORDER\" WHERE \"ID\"="+to_string(c[0].as<int>())+";";
      W.exec(delete_sellorder);

      string sql_seller_balance;
      sql_seller_balance = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(amount*c[4].as<float>())+" WHERE \"ACCOUNT_ID\"=\'"+c[1].as<string>()+"\';";
      W.exec(sql_seller_balance);

      string sql_trans;
      sql_trans = "INSERT INTO \"TRANSACTION\" (\"BUY_ID\", \"SELL_ID\", \"SYM\", \"NUM\", \"PRICE\", \"BUYORDER_ID\", \"SELLORDER_ID\", \"STATUS\", \"TRANS_TIME\") VALUES (\'" + account_id + "\', \'" + c[1].as<string>() + "\', \'" 
      + sym + "\', " + to_string(c[3].as<float>()) + ", " + to_string(c[4].as<float>()) + ", " + to_string(buy_order_id) + ", " + to_string(c[0].as<int>()) + ", \'EXECUTED\', " + get_time() + ");";
      W.exec(sql_trans);
      // W.commit();

      create_symbol(sym, account_id, c[3].as<float>(), C, W);
      amount-=c[3].as<float>();
      //refund delta
      //work W7(*C);
      string sql_refund;
      sql_refund = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(c[3].as<float>()*(limit - c[4].as<float>()))+" WHERE \"ACCOUNT_ID\"=\'"+account_id+"\';";
      W.exec(sql_refund);

      //W7.commit();
      break;
    }
  }
  //work W2(*C);
  if(amount != 0) {
    //insert the buyer order
    string update_buyer_order;
    update_buyer_order = "UPDATE \"ORDER\" SET \"AMOUNT\"=" + to_string(amount) + " WHERE \"ID\"=" + to_string(buy_order_id) + ";";
    W.exec(update_buyer_order);
  } else {
    string delete_buyer_order;
    delete_buyer_order = "DELETE FROM \"ORDER\" WHERE \"ID\"=" + to_string(buy_order_id) + ";";
    W.exec(delete_buyer_order);
  }
  //W2.commit();
}
void sell_match(XMLElement* cur, connection * C, string & resp, string account_id, work & W) {
  string sym = cur->Attribute("sym");
  float amount = -stof(cur->Attribute("amount"));
  float limit = stof(cur->Attribute("limit"));
  //work W0(*C);
  string add_sell_order;
  add_sell_order = "INSERT INTO \"ORDER\" (\"ACCOUNT_ID\", \"SYM\", \"AMOUNT\", \"PRICE\", \"STATUS\") VALUES (\'" 
  + account_id + "\', \'" + sym + "\', " + to_string(amount) 
  + ", " + to_string(limit) + ", \'SELL\') RETURNING \"ID\";";
  result R0(W.exec(add_sell_order));
  //W0.commit();
  int sell_order_id = R0[0][0].as<int>();
  //add open statement to response
  resp+="<opened sym=\""+sym+"\" amount=\""+trim_num(-amount)+"\" limit=\""
        +trim_num(limit)+"\" id=\""+to_string(sell_order_id)+"\"/>\n";
  //
  //work W1(*C);
  string sql_buy;
  sql_buy = "SELECT * FROM \"ORDER\" WHERE \"STATUS\" = \'BUY\' AND \"SYM\"=\'" + sym + "\' AND \"PRICE\">="
  + to_string(limit) + " ORDER BY \"PRICE\" DESC FOR UPDATE;";
  result R(W.exec(sql_buy));
  //W1.commit();
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
    //work W(*C);
    // if (c[4].as<int>() <= limit) {
    if (c[3].as<float>() > amount) {
      // Add a transaction
      // Update seller amount, account
      // Update buyer's share
      // break
      string sql_trans;
      sql_trans = "INSERT INTO \"TRANSACTION\" (\"BUY_ID\", \"SELL_ID\", \"SYM\", \"NUM\", \"PRICE\", \"BUYORDER_ID\", \"SELLORDER_ID\", \"STATUS\", \"TRANS_TIME\") VALUES (\'" + c[1].as<string>() + "\', \'" + account_id + "\', \'" 
      + sym + "\', " + to_string(amount) + ", " + to_string(c[4].as<float>()) + ", " + to_string(c[0].as<int>()) + ", " + to_string(sell_order_id) + ", \'EXECUTED\', " + get_time() + ");";
      W.exec(sql_trans);
      string sql_amount;
      sql_amount = "UPDATE \"ORDER\" SET \"AMOUNT\"=\"AMOUNT\"-" + to_string(amount) + " WHERE \"ID\"=" + to_string(c[0].as<int>()) + ";";
      W.exec(sql_amount);
      string sql_balance;
      sql_balance = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(amount*c[4].as<float>())+" WHERE \"ACCOUNT_ID\"=\'"+account_id+"\';";
      W.exec(sql_balance);
      //W.commit();
      create_symbol(sym, c[1].as<string>(), amount, C, W);
      amount = 0;
      break;
    } else if (c[3].as<float>() < amount) {
      // delete seller order, update seller's account
      // add a transaction, and update buyer's amount
      // go on
      string delete_buyorder;
      delete_buyorder = "DELETE FROM \"ORDER\" WHERE \"ID\"="+to_string(c[0].as<int>())+";";
      W.exec(delete_buyorder);

      string sql_seller_balance;
      sql_seller_balance = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(c[3].as<float>()*c[4].as<float>())+" WHERE \"ACCOUNT_ID\"=\'"+account_id+"\';";
      W.exec(sql_seller_balance);

      string sql_trans;
      sql_trans = "INSERT INTO \"TRANSACTION\" (\"BUY_ID\", \"SELL_ID\", \"SYM\", \"NUM\", \"PRICE\", \"BUYORDER_ID\", \"SELLORDER_ID\", \"STATUS\", \"TRANS_TIME\") VALUES (\'" 
      + c[1].as<string>() + "\', \'" + account_id + "\', \'" 
      + sym + "\', " + to_string(c[3].as<float>()) + ", " + to_string(c[4].as<float>()) + ", " + to_string(c[0].as<int>()) + ", " + to_string(sell_order_id) + ", \'EXECUTED\', " + get_time() + ");";
      W.exec(sql_trans);
      //W.commit();
      create_symbol(sym, c[1].as<string>(), c[3].as<float>(), C, W);
      amount-=c[3].as<float>();
    } else {
      // delete seller order, update seller's account
      // add a transaction, update buyer's amount
      string delete_buyorder;
      delete_buyorder = "DELETE FROM \"ORDER\" WHERE \"ID\"="+to_string(c[0].as<int>())+";";
      W.exec(delete_buyorder);

      string sql_seller_balance;
      sql_seller_balance = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+"+to_string(c[3].as<float>()*c[4].as<float>())+" WHERE \"ACCOUNT_ID\"=\'"+account_id+"\';";
      W.exec(sql_seller_balance);

      string sql_trans;
      sql_trans = "INSERT INTO \"TRANSACTION\" (\"BUY_ID\", \"SELL_ID\", \"SYM\", \"NUM\", \"PRICE\", \"BUYORDER_ID\", \"SELLORDER_ID\", \"STATUS\", \"TRANS_TIME\") VALUES (\'" 
      + c[1].as<string>() + "\', \'" + account_id + "\', \'" 
      + sym + "\', " + to_string(c[3].as<float>()) + ", " + to_string(c[4].as<float>()) + ", " + to_string(c[0].as<int>()) + ", " + to_string(sell_order_id) + ", \'EXECUTED\', " + get_time() + ");";
      W.exec(sql_trans);
      //W.commit();
      create_symbol(sym, c[1].as<string>(), c[3].as<float>(), C, W);
      amount-=c[3].as<float>();
      // W.commit();
      break;
    }
  }
  //work W2(*C);
  if(amount != 0) {
    //insert the buyer order
    string update_seller_order;
    update_seller_order = "UPDATE \"ORDER\" SET \"AMOUNT\"=" + to_string(amount) + " WHERE \"ID\"=" + to_string(sell_order_id) + ";";
    W.exec(update_seller_order);
  } else {
    string delete_seller_order;
    delete_seller_order = "DELETE FROM \"ORDER\" WHERE \"ID\"=" + to_string(sell_order_id) + ";";
    W.exec(delete_seller_order);
  }
  //W2.commit();
}
void create_query(XMLElement* cur, connection * C, string & resp, string account_id) {
  int trans_id = stoi(cur->Attribute("id"));
  string check_open;
  //find open order
  check_open = "SELECT COUNT(*) FROM \"ORDER\" WHERE \"ID\"=" + to_string(trans_id) + ";";
  work W0(*C);
  result R0(W0.exec(check_open));

  //find executed and cancel by order
  string check_trans = "SELECT COUNT(*) FROM \"TRANSACTION\" WHERE \"BUYORDER_ID\"=" + to_string(trans_id) 
  + " OR \"SELLORDER_ID\"=" + to_string(trans_id) + ";";
  result R2(W0.exec(check_trans));
  if (R0[0][0].as<int>() == 0 && R2[0][0].as<int>() == 0) {
    // report error
    resp+="<error trans_id=\""+to_string(trans_id)+"\">Transaction not exists, can not be queried!</error>\n";
    return;
  }
  resp+="<status id=\""+to_string(trans_id)+"\">\n";
  if (R0[0][0].as<int>() > 0) {
    string open_shares;
    open_shares = "SELECT \"AMOUNT\" FROM \"ORDER\" WHERE \"ID\"=" + to_string(trans_id) + " FOR UPDATE;";
    result R1(W0.exec(open_shares));
    float share_amount = R1[0][0].as<float>();
    resp += "<open shares=\"" + trim_num(share_amount) + "\"/>\n";
  }
  
  // if (R0[0][0].as<int>() == 0 && R2[0][0].as<int>() == 0) {
  //   // report error
  //   resp+="<error trans_id=\""+to_string(trans_id)+"\">Transaction not exists, can not be queried!</error>\n";
  // } else 
  if(R2[0][0].as<int>() > 0){
    //find cancel
    //?????????how to extract timestamp from result object????????????
    string find_cancel = "SELECT \"NUM\", \"TRANS_TIME\" FROM \"TRANSACTION\" WHERE (\"BUYORDER_ID\"=" + to_string(trans_id) 
                        + " OR \"SELLORDER_ID\"=" + to_string(trans_id) + ") AND " + "\"STATUS\"=\'CANCELED\'"+" FOR UPDATE;";
    result R3(W0.exec(find_cancel));
    for(result::const_iterator it = R3.begin(); it != R3.end(); ++it) {
      resp += "<canceled shares=\"" + trim_num(it[0].as<float>()) + "\" time=\"" + to_string(it[1].as<int>()) + "\"/>\n";
    }
    //find execute
    string find_execute = "SELECT \"NUM\", \"PRICE\", \"TRANS_TIME\" FROM \"TRANSACTION\" WHERE (\"BUYORDER_ID\"=" + to_string(trans_id) 
                        + " OR \"SELLORDER_ID\"=" + to_string(trans_id) + ") AND " + "\"STATUS\"=\'EXECUTED\'"+" FOR UPDATE;";
    result R4(W0.exec(find_execute));
    for(result::const_iterator it = R4.begin(); it != R4.end(); ++it) {
      resp += "<executed shares=\"" + trim_num(it[0].as<float>()) + "\" price=\""+ trim_num(it[1].as<float>()) +"\" time=\"" + to_string(it[2].as<int>()) + "\"/>\n";
    }
  }
  W0.commit();
  resp += "</status>\n";
}
void create_cancel(XMLElement* cur, connection * C, string & resp, string account_id) {
  //get (tansaction)order_id
  //find open order in order table
  //delete order and add the cancellation to transaction table
  int order_id = stoi(cur->Attribute("id"));
  //cout<<"cancelling order with number "<<order_id<<endl;
  string count_target_order;
  count_target_order = "SELECT COUNT(*) FROM \"ORDER\" WHERE \"ID\"=" + to_string(order_id) + ";";
  work W(*C);
  result R0(W.exec(count_target_order));
  if(R0[0][0].as<int>() != 0) {
    //retrieve the order info
    string get_order;
    get_order = "SELECT * FROM \"ORDER\" WHERE \"ID\"="+ to_string(order_id) + " FOR UPDATE;";
    result R1(W.exec(get_order));
    //refund to whatever buyer or seller
    if(R1[0][5].as<string>() == "BUY") {
      //refund money to buyer
      string refund_money;
      refund_money = "UPDATE \"ACCOUNT\" SET \"BALANCE\"=\"BALANCE\"+" + to_string(R1[0][3].as<float>() * R1[0][4].as<float>())
                    + "WHERE \"ACCOUNT_ID\"=" + W.quote(R1[0][1].as<string>()) + ";";
      W.exec(refund_money);
    } else {
      //refund share to seller
      string refund_share;
      refund_share = "UPDATE \"SYMBOL\" SET \"SHARE\"=\"SHARE\"+" + to_string(R1[0][3].as<float>()) 
                    + "WHERE \"ACCOUNT_ID\"=" + W.quote(R1[0][1].as<string>()) + " AND \"SYM\"="+W.quote(R1[0][2].as<string>()) + ";";
      W.exec(refund_share);
    }
    //delete the order
    string del_order;
    del_order = "DELETE FROM \"ORDER\" WHERE \"ID\"=" + to_string(order_id) + ";";
    //add cancellation to transaction
    string add_cancellation;
    add_cancellation = "INSERT INTO \"TRANSACTION\" (\"BUY_ID\", \"SELL_ID\", \"SYM\", \"NUM\", \"PRICE\", \"BUYORDER_ID\", \"SELLORDER_ID\", \"STATUS\", \"TRANS_TIME\") VALUES(\'" + R1[0][1].as<string>() + "\', \'" + R1[0][1].as<string>() + "\', " 
                        + W.quote(R1[0][2].as<string>()) +", "
                        +to_string(R1[0][3].as<float>())+ ", " + to_string(R1[0][4].as<float>()) + ", "+ to_string(R1[0][0].as<int>()) + ", " 
                        + to_string(R1[0][0].as<int>()) + ", \'CANCELED\', " + get_time() + ") RETURNING \"TRANS_TIME\";";
    W.exec(del_order);
    result R2(W.exec(add_cancellation));
    //W.commit();
    //string cancel_time = R2[0][0].as<string>;
    resp += "<canceled id=\"" + to_string(order_id) + "\">\n";
    resp += "<canceled shares=\"" + trim_num(R1[0][3].as<float>()) + "\" time=\"" + to_string(R2[0][0].as<int>()) +"\"/>\n";
    //executed shares
    //work W0(*C);
    string find_execute = "SELECT \"NUM\", \"PRICE\", \"TRANS_TIME\" FROM \"TRANSACTION\" WHERE (\"BUYORDER_ID\"=" + to_string(order_id) 
                        + " OR \"SELLORDER_ID\"=" + to_string(order_id) + ") AND " + "\"STATUS\"=\'EXECUTED\'"+" FOR UPDATE;";
    result R4(W.exec(find_execute));
    for(result::const_iterator it = R4.begin(); it != R4.end(); ++it) {
      resp += "<executed shares=\"" + trim_num(it[0].as<float>()) + "\" price=\""+ trim_num(it[1].as<float>()) +"\" time=\"" + to_string(it[2].as<int>()) + "\"/>\n";
    }
    //
    resp += "</canceled>\n";
  } else {
    resp+="<error trans_id=\""+to_string(order_id)+"\">Transaction does not exist, it can not be canceled!</error>\n";
    //cout<<"***************"<<endl<<"cannot cancel none open order!!!"<<"***************"<<endl;
    //cancelling a none open order!!
  }
  W.commit();
}