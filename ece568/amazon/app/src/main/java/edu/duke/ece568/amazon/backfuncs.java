package edu.duke.ece568.amazon;

import static edu.duke.ece568.amazon.interactions.sendMesgTo;
import static edu.duke.ece568.amazon.interactions.recvMesgFrom;
import edu.duke.ece568.amazon.dbProcess.*;

import com.google.common.collect.ImmutableMultiset;
 
import java.util.List;

import edu.duke.ece568.amazon.protos.AmazonUps.*;
import edu.duke.ece568.amazon.protos.AmazonUps.Error;
import edu.duke.ece568.amazon.protos.WorldAmazon.*;
import oracle.net.aso.b;
import oracle.security.o3logon.a;

import java.io.IOException;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.SQLException;
import java.util.*;
import java.util.concurrent.*;
import java.util.HashSet;

import java.io.BufferedReader;
import java.io.PrintWriter;
import java.io.InputStreamReader;

//for test
import java.lang.Math;

public class backfuncs {
    /*
    ups group 1:
    */
    private static final String WORLD_HOST = "vcm-25610.vm.duke.edu";
    //private static final String WORLD_HOST = "vcm-24561.vm.duke.edu";
    private static final String UPS_HOST = "vcm-26136.vm.duke.edu";
    private static final int WORLD_PORT = 23456;
    private static final int UPS_PORT = 6066;
    private static final int FRONT_PORT = 7777;

    /*
    ups group 2:
    */
    // private static final String WORLD_HOST = "vcm-26608.vm.duke.edu";
    // private static final String UPS_HOST = "vcm-26608.vm.duke.edu";
    // private static final int WORLD_PORT = 23456;
    // private static final int UPS_PORT = 33333;
    // private static final int FRONT_PORT = 7777;

    private static final int MAXTIME = 20000;

    //private List<AInitWarehouse> warehouses = new ArrayList<>();
    private Map<Integer, AInitWarehouse> warehouses;
    Socket toups;
    Socket toWorld;
    //a data structure to store the identifiers in the response to figure out what rqst a msg is in response to
    //处理drop ack的情况，收到处理过的response不是什么都不做，而是要回复ack
    private HashSet<Long> seqnumFromworld_list;
    
    private final Map<Long, Package> package_list;
    private long seqnum;
    // a data sturcture to record the time each command is sent
    private final Map<Long, Timer> rqst_list;

    //for test response ack to world
    private Random random = new Random(); 

    //construct function
    public backfuncs() throws IOException, ClassNotFoundException, SQLException{
        // AInitWarehouse.Builder newWH = AInitWarehouse.newBuilder().setId(1).setX(5).setY(5);
        // warehouses.add(newWH.build());
        dbProcess database = new dbProcess();
        warehouses = database.initAmazonWarehouse();
        //print our result of warehouses initialization
        for (Map.Entry<Integer, AInitWarehouse> entry : warehouses.entrySet()){
            System.out.println("Wh_Id = " + entry.getKey() +
                             ", Value = " + entry.getValue());
        }
        seqnumFromworld_list = new HashSet<Long>();
        package_list = new ConcurrentHashMap<>();
        seqnum = 0;
        rqst_list = new ConcurrentHashMap<>();
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
                    long world_id = connect.getWorldid();
                    System.out.println("worldid is: " + world_id);
                    A2UConnected.Builder connected = A2UConnected.newBuilder();
                    if(connect_world(world_id)){
                        System.out.println("connected to world yeah");
                        connected.setWorldid(world_id).setResult("connected!");
                        sendMesgTo(connected.build(), toups.getOutputStream());
                        break;
                    }
                    else{
                        String result_msg = String.format("error: Amazon fail to connect the World %d", world_id);
                        connected.setResult(result_msg);
                    }
                }
            }
        }
    }

    //amazon connect to world
    public boolean connect_world(long id) throws IOException{
        System.out.println("connecting to World simulator");
        toWorld = new Socket(WORLD_HOST, WORLD_PORT);
        System.out.println("world socket");

        AConnect.Builder connect = AConnect.newBuilder();
        //connect.setWorldid(id).setIsAmazon(true).addAllInitwh(warehouses);
        connect.setWorldid(id).setIsAmazon(true);
        for(Map.Entry<Integer, AInitWarehouse> entry : warehouses.entrySet()){
            connect.addInitwh(entry.getValue());
        }
        sendMesgTo(connect.build(), toWorld.getOutputStream());

        AConnected.Builder connected = AConnected.newBuilder();
        recvMesgFrom(connected, toWorld.getInputStream());
        System.out.println("result from world is:" + connected.getResult());
        return connected.getResult().equals("connected!");
    }

    //thread for comm with ups
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
                    } catch (ClassNotFoundException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    } catch (SQLException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                });
                upsthread.start();
            }
        }
    }

    //thread for comm with the world
    public void init_worldthread() throws IOException{
        while(!Thread.currentThread().isInterrupted()) {
            if(toWorld!=null){
                AResponses.Builder aresponses = AResponses.newBuilder();
                recvMesgFrom(aresponses, toWorld.getInputStream());
                Thread worldthread = new Thread(() -> {
                    try {
                        handle_world(aresponses);
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    } catch (ClassNotFoundException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    } catch (SQLException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                });
                worldthread.start();
            }
        }
    }

    //handle request from Ups that "truck arrived"
    void truckArrived(U2ATruckArrived upstruckarrived) throws IOException, ClassNotFoundException, SQLException{
        //to be modified: update the truck arrived protocol to have package_id!!
        System.out.println("handling truck arrived:");
        System.out.println(upstruckarrived.toString());
        for(long package_id : upstruckarrived.getShipidList()){
            System.out.println("truck for package " + package_id+" arrived");
            if(package_list.containsKey(package_id)){
                Package pkg = package_list.get(package_id);
                pkg.setTruckid(upstruckarrived.getTruckid());
                System.out.println("UPS truck "+ upstruckarrived.getTruckid() +" arrived");
                //check if amazon packed or not
                if(pkg.getPackageStatus().equals("packed")){
                    //start loading
                    worldPutOnTruck(pkg);
                    //加给ups的loading信息
                    
                }
            }
            else {
                //can not find the package according to id
                System.out.println("package does not exists!");
            }
        }
    }

    //handle request from Ups that "package delivering"
    void packageDelivering(U2ADelivering.Builder upsPkgDelivering) throws IOException, ClassNotFoundException, SQLException {
        for(long id : upsPkgDelivering.getShipidList()){
            if(package_list.containsKey(id)){
                package_list.get(id).setStatus("delivering");
            } else {
                //can not find the package according to id
                System.out.println("package update to delivering does not exists!");
            }
        }
    }

    //handle request from Ups that "package delivering"
    void packageDelivered(U2ADelivered.Builder upsPkgDelivered) throws IOException, ClassNotFoundException, SQLException {
        //到底是单独还是重复
        for(long id : upsPkgDelivered.getShipidList()){
            if(package_list.containsKey(id)){
                package_list.get(id).setStatus("delivered");
                package_list.remove(id);
            } else {
                //can not find the package according to id
                System.out.println("package update to delivering does not exists!");
            }
        }
        // long package_id = upsPkgDelivered.getShipid();
    }

    //query status from UPS, 好像不需要主动调用
    void queryShiptoUps(long package_id) throws IOException{
        A2UQueryShip.Builder a2uqueryship = A2UQueryShip.newBuilder();
        long seq = getSeqNum();
        a2uqueryship.setSeqnum(seq);
        a2uqueryship.setShipid(package_id);
        AmazonCommands.Builder amazoncommands = AmazonCommands.newBuilder();
        amazoncommands.addQuery(a2uqueryship);
        sendMesgTo(amazoncommands.build(), toups.getOutputStream());
    }

    //hanlde U2AShipStatus
    void packageSetstatus_fromUps(U2AShipStatus.Builder upsPkgstatus) throws IOException, ClassNotFoundException, SQLException { 
        long id = upsPkgstatus.getShipid();
        String status = upsPkgstatus.getStatus();
        if(package_list.containsKey(id)){
            package_list.get(id).setStatus(status);
        } else {
            //can not find the package according to id
            System.out.println("package query status from UPS does not exists!");
        }
        // long package_id = upsPkgDelivered.getShipid();
    }

    //change address in our database if we receive U2AChangeAddress from UPS
    public void changeAddrinDB(U2AChangeAddress.Builder changeaddr) throws ClassNotFoundException, SQLException{
        long id = changeaddr.getShipid();
        int x = changeaddr.getX();
        int y = changeaddr.getY();
        if(package_list.containsKey(id)){
            package_list.get(id).setAddress(x, y);;
        } else {
            //can not find the package according to id
            System.out.println("package changing address from UPS does not exists!");
        }
    }


    //handle communication with Ups
    public void handle_ups(UPSCommands.Builder recvUps) throws IOException, ClassNotFoundException, SQLException{
        // UPSCommands.Builder recvUps = UPSCommands.newBuilder();
        // recvMesgFrom(recvUps, toups.getInputStream());
        //ackToUps(recvUps);
        for(U2ATruckArrived x : recvUps.getArrivedList()){
            System.out.println("entering truck arrived");
            truckArrived(x);
        }
        for(U2ADelivering x : recvUps.getDeliveringList()){
            packageDelivering(x.toBuilder());
        }
        for(U2ADelivered x : recvUps.getDeliveredList()){
            packageDelivered(x.toBuilder());
        }
        for(U2AShipStatus x : recvUps.getStatusList()){
            //response to query status, update the status of the package
            packageSetstatus_fromUps(x.toBuilder());
        }
        for(U2AChangeAddress x : recvUps.getAddressList()){
            //change the address, 如果我们前端需要显示地址就需要做操作
            //change address in our database
            changeAddrinDB(x.toBuilder());
        }
        for(edu.duke.ece568.amazon.protos.AmazonUps.Error x : recvUps.getErrorList()){
            if(x.getInfo() != null){
                System.err.println(x.getInfo());
            }
        }
        if(recvUps.hasFinish()){
            System.out.println("UPS close the connection, finish!");
        }
    }

    //send acks back to Ups, no need to send ack to ups, TCP connection
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
        // for(U2AChangeAddress x : recvUps.getAddressList()){
        //     recvUps.addAcks(x.getSeqnum());
        // }
        for(Error x : recvUps.getErrorList()){
            recvUps.addAcks(x.getSeqnum());
        }
        System.out.println("sending acks back to Ups");
        sendMesgTo(recvUps.build(), toups.getOutputStream());
    }


    //DEALING WITH WORLD responses!!
    //to do:start handle_world
    public void handle_world(AResponses.Builder recvWorld) throws IOException, ClassNotFoundException, SQLException{
        // UPSCommands.Builder recvUps = UPSCommands.newBuilder();
        // recvMesgFrom(recvUps, toups.getInputStream());

        int r = random.nextInt(3);
        if(r!=2){
            ackToWorld(recvWorld);
        } else {
            System.out.println("<<<<<<<<<<<<<<<<<< drop ack to world >>>>>>>>>>>>>>>>");
        }
        for(APurchaseMore x : recvWorld.getArrivedList()){
            //handle purchased item from world to warehouse
            System.out.println("=============receive world arrived msg===========");
            long seq_fromworld = x.getSeqnum();
            //check this sequence number is in the list or not
            if(seqnumFromworld_list.contains(seq_fromworld)){
                System.out.println("=============arrived msg: already handled===========");
                continue;
            }
            else{
                System.out.println("=============arrived msg: not handle, now handling===========");
                worldPurchased(x);
                seqnumFromworld_list.add(seq_fromworld);
            }
        }
        for(APacked x : recvWorld.getReadyList()){
            //handle the packed package: packed->load
            long seq_fromworld = x.getSeqnum();
            //check this sequence number is in the list or not
            if(seqnumFromworld_list.contains(seq_fromworld)){
                continue;
            }
            else{
                worldPacked(x);
                seqnumFromworld_list.add(seq_fromworld);
            }
            
            //worldPacked(x);
        }
        for(ALoaded x : recvWorld.getLoadedList()){
            //handle loaded truck from world to amazon: loaded->delivering
            long seq_fromworld = x.getSeqnum();
            //check this sequence number is in the list or not
            if(seqnumFromworld_list.contains(seq_fromworld)){
                continue;
            }
            else{
                worldLoaded(x);
                seqnumFromworld_list.add(seq_fromworld);
            }
            //worldLoaded(x);
        }
        for(AErr x : recvWorld.getErrorList()){
            //print the error message
            long seq_fromworld = x.getSeqnum();
            //check this sequence number is in the list or not
            if(seqnumFromworld_list.contains(seq_fromworld)){
                continue;
            }
            else{
                System.err.println("error msg from world:" + x.getErr());
                seqnumFromworld_list.add(seq_fromworld);
            }
            //System.err.println("error msg from world:" + x.getErr());
        }
        for(APackage x : recvWorld.getPackagestatusList()){
            //get the status of package from world, change the status in Package
            long seq_fromworld = x.getSeqnum();
            //check this sequence number is in the list or not
            if(seqnumFromworld_list.contains(seq_fromworld)){
                continue;
            }
            else{
                package_list.get(x.getPackageid()).setStatus(x.getStatus());
                seqnumFromworld_list.add(seq_fromworld);
            }
            //package_list.get(x.getPackageid()).setStatus(x.getStatus());
        }
        //handle acks mechanism, for re-send
        for(long x : recvWorld.getAcksList()){
            if(rqst_list.containsKey(x)){
                rqst_list.get(x).cancel();
                rqst_list.remove(x);
            }
        }
        //handle disconnect
        if(recvWorld.hasFinished()){
            //connection disconnected, need to close the connection
            System.out.println("disconnect to world");
            //查一下这个逻辑，不知道是不是我们这边close
            toWorld.close();
        }
    }

    void ackToWorld(AResponses.Builder recvWorld) throws IOException{
        List<Long> seqnum_list = new ArrayList<>();
        for(APurchaseMore x : recvWorld.getArrivedList()){
            seqnum_list.add(x.getSeqnum());
        }
        for(APacked x : recvWorld.getReadyList()){
            seqnum_list.add(x.getSeqnum());
        }
        for(ALoaded x : recvWorld.getLoadedList()){
            seqnum_list.add(x.getSeqnum());
        }
        for(AErr x : recvWorld.getErrorList()){
            seqnum_list.add(x.getSeqnum());
        }
        for(APackage x : recvWorld.getPackagestatusList()){
            seqnum_list.add(x.getSeqnum());
        }
        System.out.println("sending acks back to world");
        ACommands.Builder acommands = ACommands.newBuilder();
        if(seqnum_list.size() > 0){
            for(long x : seqnum_list){
                acommands.addAcks(x);
            }
            synchronized(toWorld.getOutputStream()){
                sendMesgTo(acommands.build(), toWorld.getOutputStream());
            }
        }
        //sendMesgTo(recvWorld.build(), toWorld.getOutputStream());
    }

    /*=======the world purchase products for warehouse====== */
    void worldPurchased(APurchaseMore x) throws IOException, ClassNotFoundException, SQLException{
        //需要synchronized吗？？？？？
        //find the package
        for(Package pkg : package_list.values()){
            System.out.println("=================world purchased processing for each package======");
            if(pkg.getWarehouseid() != x.getWhnum()){
                System.out.println("=================world purchased processing: warehouse not match======");
                continue;
            }
            //judge if the products are correct or not
            //compare the size
            List<AProduct> a = pkg.getAmazonPack().getThingsList();
            List<AProduct> b = x.getThingsList();
            if(!checkProductList(a, b)){
                continue;
            }

            //sorting
            // List<AProduct> a = pkg.getAmazonPack().getThingsList();
            // List<AProduct> b = x.getThingsList();
            // Collections.sort(a, new Comparator<AProduct>() {

            //     public int compare(AProduct o1, AProduct o2) {
            //         // compare two instance of `Score` and return `int` as result.
            //         if(Long.compare(x, y)) {
            //             return 1;
            //         } else {
            //             return -1;
            //         }
            //     }
            // });
            // Collections.sort(b, new Comparator<AProduct>() {

            //     public int compare(AProduct o1, AProduct o2) {
            //         // compare two instance of `Score` and return `int` as result.
            //         if(o1.getId()>o2.getId()) {
            //             return 1;
            //         } else {
            //             return -1;
            //         }
            //     }
            // });
            
            // if(!a.equals(b)){
            //     // System.out.println("first compare result is" + Arrays.equals(pkg.getAmazonPack().getThingsList().toArray(), x.getThingsList().toArray()));
            //     // System.out.println("second compare result is" + (Arrays.toString(pkg.getAmazonPack().getThingsList().toArray())).equals(Arrays.toString(x.getThingsList().toArray())));
            //     System.out.println("==================================================================");
            //     System.out.println(Arrays.toString(a.toArray()));
            //     System.out.println("---------------------------------------------------------------");
            //     System.out.println(Arrays.toString(b.toArray()));
            //     System.out.println("=================world purchased processing: products not match======");
            //     continue;
            // }
            // if(!pkg.getAmazonPack().getThingsList().equals(x.getThingsList())){
            //     System.out.println("==================================================================");
            //     System.out.println(Arrays.toString(pkg.getAmazonPack().getThingsList().toArray()));
            //     System.out.println("---------------------------------------------------------------");
            //     System.out.println(Arrays.toString(pkg.getAmazonPack().getThingsList().toArray()));
            //     System.out.println("=================world purchased processing: products not match======");
            //     continue;
            // }
            System.out.println("world purchased this item");
            //request trucks from UPS
            System.out.println("&&&&&&&&&&requesting a truck");
            rqstTrucks(pkg);
            //request pack from world
            rqstTopack(pkg);
            break;
        }
    }

    //check if two products list are equal
    // public static boolean isEqualIgnoringOrder(List<Integer> x, List<Integer> y) {
    //     if (x == null) {
    //         return y == null;
    //     }
 
    //     if (x.size() != y.size()) {
    //         return true;
    //     }
 
    //     return ImmutableMultiset.copyOf(x).equals(ImmutableMultiset.copyOf(y));
    // }

    public static boolean checkProductList(List<AProduct> a, List<AProduct> b){
        if(a.size() != b.size()){
            return false;
        }
        return ImmutableMultiset.copyOf(a).equals(ImmutableMultiset.copyOf(b));
    }

    //send request to UPS to send us trucks
    void rqstTrucks(Package pkg) throws IOException, ClassNotFoundException, SQLException{
        long package_id = pkg.getPackageId();
        if(package_list.containsKey(package_id)){
            System.out.println("asking trucks");
            // Package new_pkg = package_list.get(package_id);
            //没有用thread处理？？？
            //get the sequence number
            long seq = getSeqNum();
            //create the A2UAskTruck rqst
            
            A2UAskTruck.Builder asktruck = A2UAskTruck.newBuilder();
            asktruck.setSeqnum(seq);
            asktruck.setWarehouse(AInintToWarehouse(warehouses.get(pkg.getWarehouseid())));
            //类型转换: Apack to Packageinfo
            //还没有对user name赋值????
            //destination
            int x = pkg.getDest().getX();
            int y = pkg.getDest().getY();
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
    //keep track of the incrementing of seqnum coming from our side
    synchronized long getSeqNum() {
        long cur = seqnum;
        seqnum++;
        return cur;
    }

    //send request to pack the package
    void rqstTopack(Package pkg) throws IOException, ClassNotFoundException, SQLException{
        long package_id = pkg.getPackageId();
        if(package_list.containsKey(package_id)){
            pkg.setStatus("packing");
            //没有写线程池取处理
            //threadPool.execute(() -> {
            //construct the Acommand
            ACommands.Builder acommand = ACommands.newBuilder();
            long seq = getSeqNum();
            APack apack = package_list.get(package_id).getAmazonPack();
            acommand.addTopack(apack.toBuilder().setSeqnum(seq));

            //send request Acommand to world 
            sendACommand(acommand.build(), seq);
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
    PackageInfo.Builder APackToPackageinfo(Package p, int x, int y) throws ClassNotFoundException, SQLException{
        PackageInfo.Builder packageinfo = PackageInfo.newBuilder();
        packageinfo.setShipid(p.getPackageId());
        packageinfo.setX(x);
        packageinfo.setY(y);
        //add product infomation
        long package_id = p.getPackageId();
        for(AProduct pdt : p.getAmazonPack().getThingsList()){
            Product.Builder product = Product.newBuilder();
            long product_id = pdt.getId();
            dbProcess db = new dbProcess();
            String name = db.getProduct_name(package_id, product_id);
            product.setName(name);
            product.setCount(pdt.getCount());
            product.setDescription(pdt.getDescription());
            packageinfo.addProduct(product);
        }

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

    //send Acommand to world, hanlde re-send logic
    void sendACommand(ACommands accomands, long seq){
        //set the simspeed for debugging
        //accomands.getSimspeed();
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
        rqst_list.put(seq, timer);
    }


    /*===========the world pack package for Amazon================*/
    void worldPacked(APacked x) throws ClassNotFoundException, SQLException, IOException{
        System.out.println("----------enter worldpacked-----------");
        long package_id = x.getShipid();
        if(package_list.containsKey(package_id)){
            Package pkg = package_list.get(package_id);
            pkg.setStatus("packed");
            //tell ups we have already packed
            A2UPacked.Builder a2upacked = A2UPacked.newBuilder();
            long seq = getSeqNum();
            a2upacked.setSeqnum(seq);
            a2upacked.setShipid(package_id);
            AmazonCommands.Builder amazoncommand = AmazonCommands.newBuilder();
            amazoncommand.addPacked(a2upacked);
            sendMesgTo(amazoncommand.build(), toups.getOutputStream());

            //if the truck is arrived, we can load the packages
            System.out.println("---------------------getting truck id:"+pkg.getTruckid());
            if(pkg.getTruckid() != -1 ){
                System.out.println("----------start loading-----------");
                //start load the package
                worldPutOnTruck(pkg);
            }
        }
        else{
            //can not find the package according to id
            System.out.println("package for asking packing does not exists!");
        }
    }

    //tell world to load for us
    void worldPutOnTruck(Package pkg) throws ClassNotFoundException, SQLException, IOException{
        long package_id = pkg.getPackageId();
        if(package_list.containsKey(package_id)){
            pkg.setStatus("loading");
            //没有用线程池处理
            long seq = getSeqNum();
            //tell world to load our packages
            APutOnTruck.Builder aputontruck = APutOnTruck.newBuilder();
            aputontruck.setWhnum(pkg.getWarehouseid());
            aputontruck.setTruckid(pkg.getTruckid());
            aputontruck.setShipid(package_id);
            aputontruck.setSeqnum(seq);
            ACommands.Builder acommand = ACommands.newBuilder();
            acommand.addLoad(aputontruck);
            //send Acommand to the world
            sendACommand(acommand.build(), seq);

            //tell ups we start loading
            long seqnum_forloading = getSeqNum(); 
            A2ULoading.Builder a2uloading = A2ULoading.newBuilder();
            a2uloading.setSeqnum(seqnum_forloading);
            a2uloading.setWarehouse(AInintToWarehouse(warehouses.get(pkg.getWarehouseid())));
            a2uloading.setTruckid(pkg.getTruckid());
            a2uloading.addShipid(package_id);
            AmazonCommands.Builder amazoncommands = AmazonCommands.newBuilder();
            amazoncommands.addLoading(a2uloading);
            //send A2ULoading to ups
            sendMesgTo(amazoncommands.build(), toups.getOutputStream());
        }
        else{
            //can not find the package according to id
            System.out.println("package for asking loading does not exists!");
        }
    }

    //loaded->delivering
    void worldLoaded(ALoaded x) throws IOException, ClassNotFoundException, SQLException{
        long package_id = x.getShipid();
        if(package_list.containsKey(package_id)){
            Package pkg = package_list.get(package_id);
            pkg.setStatus("loaded");
            //tell ups we loaded, send A2ULoaded and start deliver
            A2ULoaded.Builder loaded = A2ULoaded.newBuilder();
            long seq = getSeqNum();
            loaded.setSeqnum(seq);
            loaded.setWarehouse(AInintToWarehouse(warehouses.get(pkg.getWarehouseid())));
            loaded.setTruckid(pkg.getTruckid());
            loaded.addShipid(package_id);
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

    //for query from world, AQuery
    public void queryToworld(long package_id){
        long seq = getSeqNum();
        AQuery.Builder query = AQuery.newBuilder();
        query.setSeqnum(seq);
        query.setPackageid(package_id);
        ACommands.Builder accomands = ACommands.newBuilder();
        sendACommand(accomands.build(), seq);
    }

    //for disconnect from world
    public void disconnectFromworld(){
        ACommands.Builder acommand = ACommands.newBuilder();
        acommand.setDisconnect(true);
        sendACommand(acommand.build(), 0);
    }

    /*=========== interact with front-end ==============*/
    //thread for comm with front-end
    public void init_frontEndthread() throws IOException, ClassNotFoundException{
        while(!Thread.currentThread().isInterrupted()) {
            ServerSocket frontend_socket_for_listen = new ServerSocket(FRONT_PORT);
            //frontend_socket_for_listen.setSoTimeout(20000);
            System.out.println("start listening the connection request from front-end");
            while(!Thread.currentThread().isInterrupted()) {
                Socket frontend_socket_for_connect = frontend_socket_for_listen.accept();
                if(frontend_socket_for_connect != null){
                    //handle the requests from front-end 没写完
                    handle_frontend(frontend_socket_for_connect);
                }
            }
        }
    }

    //handle requests from front-end
    void handle_frontend(Socket frontend_socket) throws IOException, ClassNotFoundException{
        InputStreamReader input_reader = new InputStreamReader(frontend_socket.getInputStream());
        BufferedReader reader = new BufferedReader(input_reader);
        PrintWriter writer = new PrintWriter(frontend_socket.getOutputStream());
        String front_rqst = reader.readLine();
        System.out.println("the received front-end request is: " + front_rqst);
        //parse the package id
        long package_id = Long.parseLong(front_rqst);
        writer.write(String.format("received the package id: %d", package_id));
        writer.flush();

        frontend_socket.close();
        //handle the buy request, request the world to buy something for specific warehouse 没写完 
        try {
            worldBuy(package_id);
        } catch (SQLException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

    //world buy for warehouse，构造Apurchasemore
    void worldBuy(long id) throws SQLException, ClassNotFoundException{
        //没有用线程池处理 没写完
        dbProcess DB = new dbProcess();
        APurchaseMore.Builder apurchasemore = APurchaseMore.newBuilder();

        long seq_number = getSeqNum();
        apurchasemore.setSeqnum(seq_number);
        try {
            DB.construcBuyrqst(id, apurchasemore);
        } catch (ClassNotFoundException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        // long seq_number = getSeqNum();
        // apurchasemore.setSeqnum(seq_number);

        ACommands.Builder acommands = ACommands.newBuilder();
        acommands.addBuy(apurchasemore);
        //send the ACommand to world
        //用来测试小函数的时候把它注释掉了
        sendACommand(acommands.build(), seq_number);

        //update some info of the package
        APack.Builder apack = APack.newBuilder();
        int whnum = apurchasemore.getWhnum();
        apack.setWhnum(whnum);
        apack.addAllThings(apurchasemore.getThingsList());
        apack.setShipid(id);
        apack.setSeqnum(-1);

        //initialize the package list, since when backend receives the front-end's buy rqst
        //we rqst to world to buy for us, meanwhile we create a package
        Package pkg = new Package(whnum, id, apack.build());
        
        package_list.put(id, pkg);

    }
    


    /*=========== start all threads ===========*/
    void startAllthreads() throws IOException, ClassNotFoundException{
        Thread upsthread = new Thread(() -> {
            
            try {
                init_upsthread();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        });
        upsthread.start();
        Thread worldthread = new Thread(() -> {
            try {
                init_worldthread();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        });
        worldthread.start();
        // Thread worldthread = new Thread(() -> {
        //start the thread for comm with ups
        //init_upsthread();

        //start a thread for comm with world
        //init_worldthread();
        init_frontEndthread();
    }


    /*========== main function ==========*/
    public static void main(String[] args) throws IOException, ClassNotFoundException, SQLException{
        //=================== test the func to cheack product list ======================
        // AProduct.Builder pdt1 = AProduct.newBuilder();
        // pdt1.setCount(2222);
        // pdt1.setDescription("fuck!");
        // pdt1.setId(2);
        // AProduct.Builder pdt2 = AProduct.newBuilder();
        // pdt2.setCount(35635);
        // pdt2.setDescription("fuck!fuck!");
        // pdt2.setId(3);
        // List<AProduct> a = new ArrayList<AProduct>();
        // List<AProduct> b = new ArrayList<AProduct>();
        // a.add(pdt1.build());
        // a.add(pdt2.build());
        // b.add(pdt2.build());
        // b.add(pdt2.build());
        // System.out.println(checkProductList(a, b));

        //checkProductList(List<AProduct> a, List<AProduct> b)
        backfuncs backend = new backfuncs();
        //connect with ups
        backend.connect_ups();
        //run all threads
        backend.startAllthreads();
        //backend.init_frontEndthread();


    }
}

