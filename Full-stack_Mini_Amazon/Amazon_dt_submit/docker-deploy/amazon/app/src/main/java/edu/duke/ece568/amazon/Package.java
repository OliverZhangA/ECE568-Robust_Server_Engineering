package edu.duke.ece568.amazon;

import java.sql.SQLException;

import edu.duke.ece568.amazon.protos.AmazonUps.Warehouse;
import edu.duke.ece568.amazon.protos.WorldAmazon.APack;
//import oracle.ucp.util.Pair;
import java.util.*;

public class Package {
    private long package_id;
    private int truck_id;
    private int warehouse_id;
    private String status;
    // UPS username to associate UPS and Amazon
    private String username;
    private APack amazon_pack;
    
    //destination
    private destination dest;

    //======= constructor =========
    public Package(){
        truck_id = -1;
    }
    //for initialize package
    public Package(int wh_id, long id, APack pack) throws ClassNotFoundException, SQLException{
        warehouse_id = wh_id;
        package_id = id;
        amazon_pack = pack;
        truck_id = -1;
        //initialize the destination
        dbProcess db = new dbProcess();
        //username = db.InitAmazonAccount(package_id);
        username = db.InitUPSAccount(package_id);
        dest = db.setDest(package_id);
    }

    //getter
    public long getPackageId(){
        return package_id;
    }

    public String getPackageStatus(){
        return status;
    }

    public String getAcccount(){
        return username;
    }

    public int getWarehouseid(){
        return warehouse_id;
    }

    public APack getAmazonPack(){
        return amazon_pack;
    }

    public int getTruckid(){
        return truck_id;
    }

    public destination getDest(){
        return dest;
    }

    //setter
    public void setTruckid(int id){
        truck_id = id;
    }

    public void setAddress(int x, int y) throws ClassNotFoundException, SQLException{
        dest.setX(x);
        dest.setY(y);
        //change addr in our database
        dbProcess db = new dbProcess();
        db.updateAddr(package_id, x, y);
    }

    public void setStatus(String newstatus) throws ClassNotFoundException, SQLException{
        status = newstatus;
        //change the status in database
        dbProcess db = new dbProcess();
        db.setStatusforDB(package_id, status);
    }
}
