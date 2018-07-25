import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

public class GA {

    static long time;
    static void setTime(){
        time = System.currentTimeMillis();
    }
    static void printTime(String no){
        long cTime = System.currentTimeMillis();
        System.out.println(no + ": " + ((cTime - time)/1000) + "s");
        time = cTime;
    }

    public static void main(String[] args) {
        setTime();
        Individual AT_BEST = null;
        double t_avg = 0, avg=0, minimum, t_min = 0;

        int iterations=20;

        for (int index = 0; index < 10; index++){
            String fileName = "G200_"+index+".txt";
            System.out.println(fileName);
            System.out.print("Iterations: ");
            avg = 0;
            minimum = 9999999999999.999;
            for (int r = 0; r < iterations; r++) {
                System.out.print(r + " ");

                FitnessCalc.extractData("C:\\GAThesis\\Data\\DataSet\\" + fileName);

                Population myPop = new Population(20, true);

                int generationCount = 0;
                double bestFitness, graphCutCost;
                double prevBest, currentBest = -1;
                do {

                    generationCount++;
                    int count = 0;
                    for (int i = 0; i < myPop.size(); i++) {
                        if (myPop.getIndividual(i).isValid() == Individual.VALID) {
                            count++;
                        }
                    }

                    if (generationCount % 50 == 0) {
                        myPop = Algorithm.removeTwins(myPop);
                    }
                    bestFitness = myPop.getFittest().getFitness();

                    myPop = Algorithm.evolvePopulation(myPop);

                    if (generationCount % 100 == 0) {
                        if (currentBest == -1.0) {
                            currentBest = bestFitness;
                        } else {
                            prevBest = currentBest;
                            currentBest = bestFitness;
                            if (currentBest == prevBest) {
                                myPop = Algorithm.randomRestart(myPop);
                            }
                        }
                    }
                }
                while (generationCount < 3000 && bestFitness > 0.0);

                double mnCost = myPop.getFittest().getGraphCutCost();
                if(mnCost<minimum){
                    minimum = mnCost;
                }
                avg += mnCost;
            }
            System.out.println();
            System.out.println("Avg Graph Cut Cost: " + avg/iterations);
            System.out.println("Min Graph Cut Cost: " + minimum);
            System.out.println();
            t_avg+=(avg/iterations);
            t_min+=minimum;
        }
        System.out.println("Summation of Avg Graph Cut Cost: " + t_avg);
        System.out.println("Summation of Min Graph Cut Cost: " + t_min);
        printTime("Time");
    }
}