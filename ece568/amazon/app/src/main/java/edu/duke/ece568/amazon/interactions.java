package edu.duke.ece568.amazon;

import com.google.protobuf.CodedInputStream;
import com.google.protobuf.CodedOutputStream;
import com.google.protobuf.GeneratedMessageV3;

import java.io.*;

public class interactions {
    public static <T extends GeneratedMessageV3> boolean sendMesgTo(T message, OutputStream out) throws IOException{
        byte[] data = message.toByteArray();
        CodedOutputStream outstream = CodedOutputStream.newInstance(out);
        outstream.writeUInt32NoTag(data.length);
        message.writeTo(outstream);
        // NOTE!!! always flush the result to stream
        outstream.flush();
        return true;
    }

    public static <T extends GeneratedMessageV3.Builder<?>> boolean recvMesgFrom(T message, InputStream in) throws IOException{
        CodedInputStream instream = CodedInputStream.newInstance(in);
        int msg_length = instream.readRawVarint32();
        int original_lim = instream.pushLimit(msg_length);
        message.mergeFrom(instream);
        instream.popLimit(original_lim);
        return true;
    }
}
