package edu.duke.ece568.amazon;

import static edu.duke.ece568.amazon.interactions.sendMesgTo;
import static edu.duke.ece568.amazon.interactions.recvMesgFrom;

import edu.duke.ece568.amazon.protos.AmazonUps.*;
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
    private List<AInitWarehouse> warehouses;
    Socket toups;
    Socket toWorld;

    //construct function
    public backfuncs() throws IOException{
        AInitWarehouse.Builder newWH = AInitWarehouse.newBuilder().setId(1).setX(5).setY(5);
        warehouses.add(newWH.build());

    }

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
        Thread upsthread = new Thread(() -> {
            while(!Thread.currentThread().isInterrupted()) {
                if(toups!=null){
                    handle_ups();
                }
            }
        });
    }
}
