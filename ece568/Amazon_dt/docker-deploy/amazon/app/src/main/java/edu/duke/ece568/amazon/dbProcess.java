package edu.duke.ece568.amazon;

import edu.duke.ece568.amazon.protos.WorldAmazon.*;
//import edu.duke.ece568.amazon.protos.AmazonUps.*;
//import JDBC
import java.sql.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;
import oracle.ucp.util.Pair;


public class dbProcess {
    private static final String URL = "jdbc:postgresql://db:5432/postgres";
    private static final String USERNAME = "postgres";
    private static final String PASSWD = "postgres";

    public dbProcess(){}

    /*============ Query functions for backend to access DB ==============
    */
    //access the warehouse table to get the warehouse to initialize AInitWarehouse
    public Map<Integer, AInitWarehouse> initAmazonWarehouse() throws ClassNotFoundException, SQLException{
        Map<Integer, AInitWarehouse> warehouses_list = new ConcurrentHashMap<>();
        
        //loading the driver
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);

        Statement W = db.createStatement();
        String sql_line = "SELECT * FROM shopping_warehouse;";
        ResultSet R = W.executeQuery(sql_line);

        while(R.next()){
            int warehouse_id = R.getInt("id");
            int x = R.getInt("pos_x");
            int y = R.getInt("pos_y");
            AInitWarehouse.Builder ainitwarehouse = AInitWarehouse.newBuilder();
            ainitwarehouse.setId(warehouse_id);
            ainitwarehouse.setX(x).setY(y);
            warehouses_list.put(warehouse_id, ainitwarehouse.build());
        }

        //close sql and driver
        W.close();
        db.close();
        return warehouses_list;
    }

    //access the packageinfo table to construct the APurchaseMore
    //pass the address of the APurchaseMore.Builder and construct it in this func
    public void construcBuyrqst(long package_id, APurchaseMore.Builder apurchasemore) throws ClassNotFoundException, SQLException{
        int whnum = getwhnum(package_id);
        apurchasemore.setWhnum(whnum);
        
        //loading the driver
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);

        Statement W = db.createStatement();
        String sql_line = "SELECT shopping_commodity.id, shopping_commodity.commodity_desc, shopping_order.commodity_amt FROM shopping_commodity, shopping_order WHERE shopping_order.commodity_id = shopping_commodity.id AND shopping_order.package_info_id = " + package_id + ";";
        ResultSet R = W.executeQuery(sql_line);

        while (R.next()){
            int product_id = R.getInt("id");
            String description = R.getString("commodity_desc");
            int count = R.getInt("commodity_amt");
            AProduct.Builder aproduct = AProduct.newBuilder();
            aproduct.setId(product_id).setDescription(description).setCount(count);
            apurchasemore.addThings(aproduct);
        }
        
        //close sql and driver
        W.close();
        db.close();
    }

    //abstract the product name from database to initialize the package info
    public String getProduct_name(long package_id, long product_id) throws SQLException, ClassNotFoundException{
        String product_name = "";
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);

        Statement W = db.createStatement();
        //String sql_line = String.format("SELECT shopping_commodity.commodity_name FROM %s, %s WHERE shopping_order.commodity_id = shopping_commodity.id AND shopping_order.package_info_id = %d AND shopping_commodity.id = %d;", PRODUCT, ORDER, package_id, product_id);
        String sql_line = "SELECT shopping_commodity.commodity_name FROM shopping_commodity, shopping_order WHERE shopping_order.commodity_id = shopping_commodity.id AND shopping_order.package_info_id = " + package_id + "AND shopping_commodity.id = " + package_id + ";";
        ResultSet R = W.executeQuery(sql_line);

        if(R.next()){
            String name = R.getString("commodity_name");
            product_name = name;   
        }
        W.close();
        db.close();
        return product_name;
    }

    //helper function for setting the whnum for APurchaseMore
    public int getwhnum(long package_id) throws ClassNotFoundException, SQLException{
        //set default is -1
        int whnum = -1;
        //loading the driver
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);

        Statement W = db.createStatement();
        String sql_line = "SELECT shopping_package_info.from_wh_id FROM shopping_package_info WHERE id = " + package_id +";";
        ResultSet R = W.executeQuery(sql_line);
        
        //set the whnum
        if (R.next()){
            whnum  = R.getInt("from_wh_id");
        }

        //close sql and driver
        W.close();
        db.close();
        return whnum;
    }

    //update the status in our database
    public void setStatusforDB(long package_id, String status) throws ClassNotFoundException, SQLException{
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);

        Statement W = db.createStatement();
        System.out.println("updating the status of package <" + package_id + "> to" + status);
        //String sql_line = String.format("UPDATE %s SET status = '%s' WHERE id = %d;", PACKAGE, status, package_id);
        String sql_line = "UPDATE shopping_package_info SET status = " + "\'"+ status + "\'" + "WHERE id = " + package_id + ";";
        W.executeUpdate(sql_line);
        db.commit();
        //close sql and driver
        W.close();
        db.close();
        
    }

    //access the package_info table to set the destination according to the package id
    public destination setDest(long package_id) throws ClassNotFoundException, SQLException{
        destination dest = new destination();
        
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);
        Statement W = db.createStatement();
        //String sql_line = String.format("SELECT dest_x, dest_y FROM %s WHERE id = %d;", PACKAGE, package_id);
        String sql_line = "SELECT dest_x, dest_y FROM shopping_package_info WHERE id = " + package_id + ";";
        ResultSet R = W.executeQuery(sql_line);

        if (R.next()){
            dest.setX(R.getInt("dest_x"));
            dest.setY(R.getInt("dest_y"));
        }
        W.close();
        db.close();
        return dest;
    }

    //access the package_info to set the username
    // public String InitAmazonAccount(long package_id) throws ClassNotFoundException, SQLException{
    //     String username = "";
    //     Class.forName("org.postgresql.Driver");
    //     Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
    //     db.setAutoCommit(false);
    //     Statement W = db.createStatement();
    //     //String sql_line = String.format("SELECT shopping_package_info.owner_username FROM %s WHERE id = %d;", PACKAGE, package_id);
    //     String sql_line = String.format("SELECT auth_user.username FROM auth_user, %s WHERE shopping_package_info.id = %d AND auth_user.id = shopping_package_info.owner_id;", PACKAGE, package_id);
    //     ResultSet R = W.executeQuery(sql_line);

    //     if (R.next()){
    //         // username = R.getString("shopping_package_info.owner_username");
    //         username = R.getString("username");
    //     }
    //     W.close();
    //     db.close();
    //     return username;

    // }
    public String InitUPSAccount(long package_id) throws ClassNotFoundException, SQLException{
        String username = "";
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);
        Statement W = db.createStatement();
        //String sql_line = String.format("SELECT shopping_package_info.owner_username FROM %s WHERE id = %d;", PACKAGE, package_id);
        //String sql_line = String.format("SELECT ups_account FROM %s WHERE shopping_package_info.id = %d;", PACKAGE, package_id);
        String sql_line = "SELECT ups_account FROM shopping_package_info WHERE shopping_package_info.id = " + package_id + ";";
        ResultSet R = W.executeQuery(sql_line);

        if (R.next()){
            // username = R.getString("shopping_package_info.owner_username");
            username = R.getString("ups_account");
        }
        W.close();
        db.close();
        return username;
    }

    //update delivery address
    public void updateAddr(long package_id, int x, int y) throws ClassNotFoundException, SQLException{
        Class.forName("org.postgresql.Driver");
        Connection db = DriverManager.getConnection(URL, USERNAME, PASSWD);
        db.setAutoCommit(false);

        Statement W = db.createStatement();
        System.out.println("updating the delivery address: x is "+ x + ", y is" + y);
        //String sql_line = String.format("UPDATE %s SET dest_x = %d, dest_y = %d WHERE id = %d;", PACKAGE, x, y, package_id);
        String sql_line = "UPDATE shopping_package_info SET dest_x = " + x + ", dest_y = " + y + " WHERE id = " + package_id + ";";
        W.executeUpdate(sql_line);
        db.commit();
        //close sql and driver
        W.close();
        db.close();
    }
    
}
