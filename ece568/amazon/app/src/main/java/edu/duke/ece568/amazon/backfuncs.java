package edu.duke.ece568.amazon;

import static edu.duke.ece568.amazon.interactions.sendMesgTo;
import static edu.duke.ece568.amazon.interactions.recvMesgFrom;

import edu.duke.ece568.amazon.protos.AmazonUps.*;
import edu.duke.ece568.amazon.protos.AmazonUps.Error;
import edu.duke.ece568.amazon.protos.WorldAmazon.*;

import java.io.*;
import java.net.Socket;
import java.util.*;
import java.util.concurrent.*;

public class backfuncs {
    private static final String WORLD_HOST = "vcm-24561.vm.duke.edu";
    private static final String UPS_HOST = "vcm-24561.vm.duke.edu";
    private static final int WORLD_PORT = 12345;
    private static final int UPS_PORT = 54321;

    private static final int MAXTIME = 1000;

    private List<AInitWarehouse> warehouses;
    Socket toups;
    Socket toWorld;
    private final Map<Long, Package> package_list;
    private long seqnum;
    private final ThreadPoolExecutor threadPool;
    private final Map<Long, Timer> rqst_list;

    //construct function
    public backfuncs() throws IOException{
        AInitWarehouse.Builder newWH = AInitWarehouse.newBuilder().setId(1).setX(5).setY(5);
        warehouses.add(newWH.build());

    }

    //DEALING WITH UPS responses!!


    //amazon connect to ups
    public void connect_ups() throws IOException{
        System.out.println("connecting to ups server");
        toups = new Socket(UPS_HOST, UPS_PORT);
        while(true){
            if(toups != null){
                U2AConnect.Builder connect = U2AConnect.newBuilder();
                recvMesgFrom(connect, toups.getInputStream());
                if(connect.hasWorldid()){
                    //connect to world
                    //if connect successfully
                    if(connect_world(connect.getWorldid())){
                        System.out.println("connected to world yeah");
                        A2UConnected.Builder connected = A2UConnected.newBuilder();
                        sendMesgTo(connected.setSeqnum(connect.getSeqnum()).build(), toups.getOutputStream());
                        break;
                    }
                }
            }
        }
    }

    //amazon connect to world
    public boolean connect_world(long id) throws IOException{
        System.out.println("connecting to World simulator");
        toWorld = new Socket(WORLD_HOST, WORLD_PORT);
        AConnect.Builder connect = AConnect.newBuilder();
        connect.setWorldid(id).setIsAmazon(true).addAllInitwh(warehouses);
        sendMesgTo(connect.build(), toWorld.getOutputStream());
        AConnected.Builder connected = AConnected.newBuilder();
        recvMesgFrom(connected, toWorld.getInputStream());
        return connected.getResult().equals("connected!");
    }

    public void init_upsthread() throws IOException{
        while(!Thread.currentThread().isInterrupted()) {
            if(toups!=null){
                UPSCommands.Builder recvUps = UPSCommands.newBuilder();
                recvMesgFrom(recvUps, toups.getInputStream());
                Thread upsthread = new Thread(() -> {
                    try {
                        handle_ups(recvUps);
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                });
            }
        }
    }
    //handle request from Ups that "truck arrived"
    void truckArrived(U2ATruckArrived.Builder upstruckarrived) throws IOException{
        //to be modified: update the truck arrived protocol to have package_id!!
        // for(long package_id : upstruckarrived.getPackageIdlist()){
        //     if()
        // }
        long package_id = upstruckarrived.getPackageId();
        if(package_list.containsKey(package_id)){
            Package pkg = package_list.get(package_id);
            System.out.println("UPS truck arrived");
            pkg.setTruckid(upstruckarrived.getTruckid());
            //check if amazon packed or not
            if(pkg.getPackageStatus().equals("packed")){
                //start loading
            }
        } else {
            //can not find the package according to id
            System.out.println("package does not exists!");
        }
    }

    //handle request from Ups that "package delivering"
    void packageDelivering(U2ADelivering.Builder upsPkgDelivering) throws IOException {
        for(PackageInfo p : upsPkgDelivering.getPackageList()) {
            long package_id = p.getShipid();
            if(package_list.containsKey(package_id)){
                package_list.get(package_id).setStatus("delivering");
            } else {
                //can not find the package according to id
                System.out.println("package update to delivering does not exists!");
            }
        }
    }

    //handle request from Ups that "package delivering"
    void packageDelivered(U2ADelivered.Builder upsPkgDelivered) throws IOException {
        long package_id = upsPkgDelivered.getShipid();
        if(package_list.containsKey(package_id)){
            package_list.get(package_id).setStatus("delivered");
            package_list.remove(package_id);
        } else {
            //can not find the package according to id
            System.out.println("package update to delivering does not exists!");
        }
    }

    //handle communication with Ups
    public void handle_ups(UPSCommands.Builder recvUps) throws IOException{
        // UPSCommands.Builder recvUps = UPSCommands.newBuilder();
        // recvMesgFrom(recvUps, toups.getInputStream());
        ackToUps(recvUps);
        for(U2ATruckArrived x : recvUps.getArrivedList()){
            truckArrived(x.toBuilder());
        }
        for(U2ADelivering x : recvUps.getDeliveringList()){
            packageDelivering(x.toBuilder());
        }
        for(U2ADelivered x : recvUps.getDeliveredList()){
            packageDelivered(x.toBuilder());
        }
        // for(U2AShipStatus x : recvUps.getStatusList()){
        //     //response to query status
        // }
    }

    //send acks back to Ups
    void ackToUps(UPSCommands.Builder recvUps) throws IOException{
        for(U2ATruckArrived x : recvUps.getArrivedList()){
            recvUps.addAcks(x.getSeqnum());
        }
        for(U2ADelivering x : recvUps.getDeliveringList()){
            recvUps.addAcks(x.getSeqnum());
        }
        for(U2ADelivered x : recvUps.getDeliveredList()){
            recvUps.addAcks(x.getSeqnum());
        }
        for(U2AShipStatus x : recvUps.getStatusList()){
            recvUps.addAcks(x.getSeqnum());
        }
        for(Error x : recvUps.getErrorList()){
            recvUps.addAcks(x.getSeqnum());
        }
        System.out.println("sending acks back to Ups");
        sendMesgTo(recvUps.build(), toups.getOutputStream());
    }


    //DEALING WITH WORLD responses!!
    //to do:start handle_world
    public void handle_world(AResponses.Builder recvWorld) throws IOException{
        // UPSCommands.Builder recvUps = UPSCommands.newBuilder();
        // recvMesgFrom(recvUps, toups.getInputStream());
        ackToWorld(recvWorld);
        for(APurchaseMore x : recvWorld.getArrivedList()){
            //handle purchased item from world to warehouse
            worldPurchased(x);
        }
        for(APacked x : recvWorld.getReadyList()){
            //handle the packed package: packed->load
            worldPacked(x);
        }
        for(ALoaded x : recvWorld.getLoadedList()){
            //handle loaded truck from world to amazon: loaded->delivering
            worldLoaded(x);
        }
        for(AErr x : recvWorld.getErrorList()){
            //print the error message
            System.err.println("error msg:" + x.getErr());
        }
        for(APackage x : recvWorld.getPackagestatusList()){
            //get the status of package from world, change the status in Package
            package_list.get(x.getPackageid()).setStatus(x.getStatus());
        }
        //handle acks mechanism, for re-send
        for(long x : recvWorld.getAcksList()){
            if(rqst_list.containsKey(x)){
                
            }
        }
    }

    void ackToWorld(AResponses.Builder recvWorld) throws IOException{

        for(APurchaseMore x : recvWorld.getArrivedList()){
            recvWorld.addAcks(x.getSeqnum());
        }
        for(APacked x : recvWorld.getReadyList()){
            recvWorld.addAcks(x.getSeqnum());
        }
        for(ALoaded x : recvWorld.getLoadedList()){
            recvWorld.addAcks(x.getSeqnum());
        }
        for(AErr x : recvWorld.getErrorList()){
            recvWorld.addAcks(x.getSeqnum());
        }
        for(APackage x : recvWorld.getPackagestatusList()){
            recvWorld.addAcks(x.getSeqnum());
        }
        System.out.println("sending acks back to world");
        sendMesgTo(recvWorld.build(), toWorld.getOutputStream());
    }

    /*=======the world purchase products for warehouse====== */
    void worldPurchased(APurchaseMore x) throws IOException{
        //需要synchronized吗？？？？？
        //find the package
        for(Package pkg : package_list.values()){
            if(pkg.getWarehouseid() != x.getWhnum()){
                continue;
            }
            if(!pkg.getAmazonPack().getThingsList().equals(x.getThingsList())){
                continue;
            }
            System.out.println("world purchased this item");
            //request trucks from UPS
            rqstTrucks(pkg);
            //request pack from world
            rqstTopack(pkg);
            break;
        }
    }

    //send request to UPS to send us trucks
    void rqstTrucks(Package pkg) throws IOException{
        long package_id = pkg.getPackageId();
        if(package_list.containsKey(package_id)){
            System.out.println("asking trucks");
            // Package new_pkg = package_list.get(package_id);
            //没有用thread处理？？？
            //get the sequence number
            long seqnum = getSeqNum();
            //create the A2UAskTruck rqst
            A2UAskTruck.Builder asktruck = A2UAskTruck.newBuilder();
            asktruck.setSeqnum(seqnum);
            asktruck.setWarehouse(AInintToWarehouse(warehouses.get(pkg.getWarehouseid() - 1)));
            //类型转换: Apack to Packageinfo
            //还没有对user name赋值????
            int x = warehouses.get(pkg.getWarehouseid() - 1).getX();
            int y = warehouses.get(pkg.getWarehouseid() - 1).getY();
            asktruck.addPackage(APackToPackageinfo(pkg, x, y));

            //send A2UAskTruck rqst to ups
            AmazonCommands.Builder amazoncommand = AmazonCommands.newBuilder();
            amazoncommand.addGetTruck(asktruck);

            //send to UPS 不知道需不需要多个socket去处理，需要处理ack吗？？？？目前没有处理
            sendMesgTo(amazoncommand.build(), toups.getOutputStream());
            //sendAmazonCommands(amazoncommand.build());
        }else{
            //can not find the package according to id
            System.out.println("package for asking trucks does not exists!");
        }
    }

    //set the sequence number to each rqst
    synchronized long getSeqNum() {
        long cur = seqnum;
        seqnum++;
        return cur;
    }

    //send request to pack the package
    void rqstTopack(Package pkg) throws IOException{
        long package_id = pkg.getPackageId();
        if(package_list.containsKey(package_id)){
            pkg.setStatus("packing");
            //没有写线程池取处理
            //threadPool.execute(() -> {
            //construct the Acommand
            ACommands.Builder acommand = ACommands.newBuilder();
            long seqnum = getSeqNum();
            APack apack = package_list.get(package_id).getAmazonPack();
            acommand.addTopack(apack.toBuilder().setSeqnum(seqnum));

            //send request Acommand to world 
            sendACommand(acommand.build(), seqnum);
            //});
        }
        else{
            //can not find the package according to id
            System.out.println("package for asking topack does not exists!");
        }
    }


    //+++++++++++++for type convert or assign some object+++++++++++++//
    //类型转换: Anitwarehouse to Warehouse
    Warehouse.Builder AInintToWarehouse(AInitWarehouse ainitwarehouse){
        Warehouse.Builder warehouse = Warehouse.newBuilder();
        warehouse.setWarehouseid(ainitwarehouse.getId());
        warehouse.setX(ainitwarehouse.getX());
        warehouse.setY(ainitwarehouse.getY());
        return warehouse;
    }

    //assign PackageInfo: Apack to Packageinfo
    PackageInfo.Builder APackToPackageinfo(Package p, int x, int y){
        PackageInfo.Builder packageinfo = PackageInfo.newBuilder();
        packageinfo.setShipid(p.getPackageId());
        packageinfo.setX(x);
        packageinfo.setY(y);
        if(p.getAcccount() != null){
            packageinfo.setUserName(p.getAcccount());
        }
        return packageinfo;
    }


    //send AmazonCommands to UPS
    // void sendAmazonCommands(AmazonCommands amazoncommands) throws IOException{
    //     //create a new socket to send AmazonCommands to ups
    //     //Socket toups_amazoncommds = new Socket(UPS_HOST, UPS_PORT);
    //     sendMesgTo(amazoncommands, toups.getOutputStream());
    //     //
    // }

    //send Acommand to world
    void sendACommand(ACommands accomands, long seqnum){
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                //为什么需要单独定义toWorld.getOutputStream()为out
                try {
                    synchronized (toWorld.getOutputStream()){
                        try {
                            sendMesgTo(accomands, toWorld.getOutputStream());
                        } catch (IOException e) {
                            // TODO Auto-generated catch block
                            e.printStackTrace();
                        }
                    }
                } catch (IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
        }, 0, MAXTIME);
        //update the reqeust hash map
        rqst_list.put(seqnum, timer);
    }


    /*===========the world pack package for Amazon================*/
    void worldPacked(APacked x){
        long package_id = x.getShipid();
        if(package_list.containsKey(package_id)){
            Package pkg = package_list.get(package_id);
            pkg.setStatus("packed");
            //if the truck is arrived, we can load the packages
            if(pkg.getTruckid() != -1 ){
                //start load the package
                worldPutOnTruck(pkg);
            }
        }
        else{
            //can not find the package according to id
            System.out.println("package for asking packing does not exists!");
        }
    }

    void worldPutOnTruck(Package pkg){
        long package_id = pkg.getPackageId();
        if(package_list.containsKey(package_id)){
            pkg.setStatus("loading");
            //没有用线程池处理
            long seqnum = getSeqNum();
            APutOnTruck.Builder aputontruck = APutOnTruck.newBuilder();
            aputontruck.setWhnum(pkg.getWarehouseid());
            aputontruck.setTruckid(pkg.getTruckid());
            aputontruck.setShipid(package_id);
            aputontruck.setSeqnum(seqnum);

            ACommands.Builder acommand = ACommands.newBuilder();
            acommand.addLoad(aputontruck);

            //send Acommand to the world
            sendACommand(acommand.build(), seqnum);
        }
        else{
            //can not find the package according to id
            System.out.println("package for asking loading does not exists!");
        }
    }

    //loaded->delivering
    void worldLoaded(ALoaded x) throws IOException{
        long package_id = x.getShipid();
        if(package_list.containsKey(package_id)){
            Package pkg = package_list.get(package_id);
            pkg.setStatus("loaded");
            //tell ups we loaded, send A2ULoaded and start deliver
            A2ULoaded.Builder loaded = A2ULoaded.newBuilder();
            long seqnum = getSeqNum();
            loaded.setSeqnum(seqnum);
            loaded.setWarehouse(AInintToWarehouse(warehouses.get(pkg.getWarehouseid() - 1)));
            loaded.setTruckid(pkg.getTruckid());
            AmazonCommands.Builder amazoncommand = AmazonCommands.newBuilder();
            amazoncommand.addLoaded(loaded);

            //send AmazonCommands to ups
            sendMesgTo(amazoncommand.build(), toups.getOutputStream());

            //set the status to "delivering"
            pkg.setStatus("delivering");
        }
        else{
            //can not find the package according to id
            System.out.println("package for loaded does not exists!");
        }
    }

}

