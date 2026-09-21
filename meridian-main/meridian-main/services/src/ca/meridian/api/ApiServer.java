package ca.meridian.api;

import ca.meridian.db.Db;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

/**
 * Meridian service layer.
 *
 * Started as a Spring application in 2014 and reduced to the JDK HTTP
 * server in 2017 when the container host was retired. The package
 * layout still reflects the Spring structure.
 *
 * A. Okonkwo 2014-09, M. Brandt 2017-02
 */
public final class ApiServer {

    public static final String VERSION = "4.2.1";

    private final HttpServer server;

    public ApiServer(int port, String dbPath) throws IOException {
        Db db = new Db(dbPath);
        this.server = HttpServer.create(new InetSocketAddress(port), 0);
        server.createContext("/api/stations", new StationHandler(db));
        server.createContext("/api/forecast", new ForecastHandler(db));
        server.createContext("/api/series", new SeriesHandler(db));
        server.createContext("/api/health", ex -> {
            byte[] b = ("{\"status\":\"ok\",\"version\":\"" + VERSION + "\"}")
                    .getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().add("Content-Type", "application/json");
            ex.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
            ex.sendResponseHeaders(200, b.length);
            try (OutputStream os = ex.getResponseBody()) {
                os.write(b);
            }
        });
        server.setExecutor(Executors.newFixedThreadPool(8));
    }

    public void start() {
        server.start();
    }

    public void stop() {
        server.stop(0);
    }

    static void sendError(HttpExchange ex, int code, String message) throws IOException {
        String safe = message == null ? "" : message.replace("\"", "'");
        byte[] b = ("{\"error\":\"" + safe + "\"}").getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().add("Content-Type", "application/json");
        ex.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        ex.sendResponseHeaders(code, b.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(b);
        }
    }

    public static void main(String[] args) throws Exception {
        int port = Integer.parseInt(System.getProperty("meridian.port", "8081"));
        String db = System.getProperty("meridian.db", "data/meridian.db");
        ApiServer s = new ApiServer(port, db);
        s.start();
        System.out.println("Meridian API " + VERSION + " listening on " + port
                + " against " + db);
    }
}
