package edu.duke.ece568.amazon;

import edu.duke.ece568.amazon.protos.AmazonUps.Warehouse;
import edu.duke.ece568.amazon.protos.WorldAmazon.APack;

public class Package {
    // public static String PACKING = "packing";
    // public static String PACKED = "packed";
    // public static String LOADING = "loading";
    // public static String LOADED = "loaded";
    // public static String DELIVERING = "delivering";
    // public static String DELIVERED = "delivered";

    private long package_id;
    private int truck_id;
    private int warehouse_id;
    private String status;
    private String username;
    private APack amazon_pack;
    //destination
    private Warehouse target_warehouse;

    public Package(){
        truck_id = -1;
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

    //setter
    public void setTruckid(int id){
        truck_id = id;
    }

    public void setStatus(String newstatus){
        status = newstatus;
    }
}
