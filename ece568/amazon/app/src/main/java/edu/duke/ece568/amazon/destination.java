package edu.duke.ece568.amazon;


public class destination {
    private int x;
    private int y;

    public destination(){}

    public destination(int x, int y){
        this.x = x;
        this.y = y;
    }

    //getter
    public int getX(){
        return x;
    }
    public int getY(){
        return y;
    }

    //setter
    public void setX(int x){
        this.x = x;
    }

    public void setY(int y){
        this.y = y;
    }



}
