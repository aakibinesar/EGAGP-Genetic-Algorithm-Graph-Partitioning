import java.io.BufferedReader;
import java.io.FileReader;
 
public class FitnessCalc {
    public static double[][] C;       // Component communication cost
    public static double[] W;         // Weight of component
    public static double[][] B;       // Machine communication cost
    public static double[] M;         // Machine capacity

    public static int numberOfMachines, numberOfVertex;

    public static void extractData(String path) {
        try {
            BufferedReader br = new BufferedReader(new FileReader(path));
            String line;
            int n, m;
            int x, y;
            String[] array;

            //1st Graph
            n = Integer.parseInt(br.readLine());
            m = Integer.parseInt(br.readLine());
            numberOfVertex = n;
            C = new double[n][n];
            W = new double[n];
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    C[i][j] = 0;
                }
            }
            for (int i = 0; i < m; i++) {
                line = br.readLine();
                array = line.split(" ");
                x = Integer.parseInt(array[0]);
                y = Integer.parseInt(array[1]);
                C[x][y] = Double.parseDouble(array[2]);
                C[y][x] = Double.parseDouble(array[2]);
            }
            line = br.readLine();
            array = line.split(" ");
            for (int i = 0; i < array.length; i++) {
                W[i] = Double.parseDouble(array[i]);
            }

            n = Integer.parseInt(br.readLine());
            m = Integer.parseInt(br.readLine());
            numberOfMachines = n;
            B = new double[n][n];
            M = new double[n];
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    B[i][j] = 1000000.0;
                }
            }
            for (int i = 0; i < m; i++) {
                line = br.readLine();
                array = line.split(" ");
                x = Integer.parseInt(array[0]);
                y = Integer.parseInt(array[1]);
                B[x][y] = Double.parseDouble(array[2]);
                B[y][x] = Double.parseDouble(array[2]);
            }
            line = br.readLine();
            array = line.split(" ");
            for (int i = 0; i < array.length; i++) {
                M[i] = Double.parseDouble(array[i]);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}