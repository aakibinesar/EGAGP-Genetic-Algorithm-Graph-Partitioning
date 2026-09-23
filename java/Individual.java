import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.Random;

public class Individual {

    private int[] genes;
    private double[] usedCapacities;       // used amount of each machine
    private double fitness;
    private double graphCutCost;
    private int validity;
    private boolean fitnessCalculated;

    private int bestGeneIndex;

    public static final int VALID = 1;
    public static final int INVALID = 0;
    public static final int DONTKNOW = -1;

    private static int [] taboo = new int[FitnessCalc.numberOfVertex];
    private static int tabooCount = 100;
    private static boolean tabooSet = false;

    public Individual() {
        genes = new int[FitnessCalc.numberOfVertex];
        usedCapacities = new double[FitnessCalc.numberOfMachines];

        validity = INVALID;
        fitnessCalculated = false;

        bestGeneIndex = -1;
    }

    public Individual(Individual you) {

        genes = new int[FitnessCalc.numberOfVertex];
        for (int i = 0; i < genes.length; i++) {
            genes[i] = you.getGene(i);
        }
        double[] youUsedCapacities = you.getUsedCapacities();

        usedCapacities = new double[FitnessCalc.numberOfMachines];
        for (int i = 0; i < FitnessCalc.numberOfMachines; i++) {
            usedCapacities[i] = youUsedCapacities[i];
        }
        this.fitness = you.getFitness();
        this.graphCutCost = you.getGraphCutCost();

        this.validity = you.isValid();
        fitnessCalculated = you.getFitnessCalculated();

        bestGeneIndex = you.getBestGeneIndex();
    }

    public int isValid() {

        if (validity != DONTKNOW) return validity;

        double[] M = FitnessCalc.M;

        for (int i = 0; i < FitnessCalc.numberOfMachines; i++) {
            if (usedCapacities[i] > M[i]) {
                validity = INVALID;
                return validity;
            }
        }
        validity = VALID;
        return validity;
    }

    public void generateValidIndividual() {

        double[] free = new double[FitnessCalc.numberOfMachines];
        int[] machine = new int[FitnessCalc.numberOfMachines];

        for (int i = 0; i < free.length; i++) {
            free[i] = FitnessCalc.M[i];
            machine[i] = i;
        }
        int value, temp, gene;
        Random random = new Random();
        for (int i = 0; i < size(); i++) {
            for (int j = 0; j < FitnessCalc.numberOfMachines; j++) {

                value = random.nextInt(FitnessCalc.numberOfMachines - j);
                gene = machine[value];
                if (free[gene] >= FitnessCalc.W[i]) {
                    genes[i] = gene;
                    free[gene] -= FitnessCalc.W[i];
                    usedCapacities[gene] += FitnessCalc.W[i];
                    break;
                }
                temp = machine[FitnessCalc.numberOfMachines - j - 1];
                machine[FitnessCalc.numberOfMachines - j - 1] = machine[value];
                machine[value] = temp;
            }
        }
        this.validity = VALID;
    }

    public void onePointCrossover(Individual indiv1, Individual indiv2) {
        Random random = new Random();
        int index = random.nextInt(indiv1.size());
        int bgene1 = indiv1.getBestGeneIndex(), bgene2 = indiv2.getBestGeneIndex();
        int i;

        for(int j=0; j<FitnessCalc.numberOfMachines; j++) usedCapacities[j] = 0;

        for (i = 0; i < index; i++) {
            if(i==bgene2){
                genes[i] =  indiv2.getGene(bgene2);
                usedCapacities[genes[i]] += FitnessCalc.W[i];
                continue;
            }
            int gene = indiv1.getGene(i);
            genes[i] = gene;
            usedCapacities[gene] += FitnessCalc.W[i];
        }
        for (; i < indiv1.size(); i++) {
            if(i==bgene1){
                genes[i] =  indiv1.getGene(bgene1);
                usedCapacities[genes[i]] += FitnessCalc.W[i];
                continue;
            }
            int gene = indiv2.getGene(i);
            genes[i] = gene;
            usedCapacities[gene] += FitnessCalc.W[i];
        }

        validity = DONTKNOW;
    }

    public int getGene(int index) {
        return genes[index];
    }

    public void setGene(int index, int value) {

        int prevValue = genes[index];
        if (value == prevValue) {
            return;
        }
        genes[index] = value;
        validity = DONTKNOW;

        double[] W = FitnessCalc.W;
        double[] M = FitnessCalc.M;

        if (!fitnessCalculated) {
            usedCapacities[prevValue] -= W[index];
            usedCapacities[value] += W[index];
            getFitness();
        } else {
            if (usedCapacities[prevValue] > M[prevValue] && usedCapacities[prevValue] - W[index] <= M[prevValue])
                fitness -= 1000000.0;

            if (usedCapacities[value] <= M[value] && usedCapacities[value] + W[index] > M[value])
                fitness += 1000000.0;

            usedCapacities[prevValue] -= W[index];
            usedCapacities[value] += W[index];

            double[][] C = FitnessCalc.C;
            double[][] B = FitnessCalc.B;

            double fitnessPlus = 0, fitnessMinus = 0;

            for (int i = 0; i < FitnessCalc.numberOfVertex; i++) {
                if (genes[i] != value) {
                    fitnessPlus += C[i][index] * B[genes[i]][value];
                }
                if (genes[i] != prevValue) {
                    fitnessMinus += C[i][index] * B[genes[i]][prevValue];
                }
            }

            fitness += fitnessPlus;
            fitness -= fitnessMinus;

            graphCutCost += fitnessPlus;
            graphCutCost -= fitnessMinus;

//            double ffitness = FitnessCalc.getFitness(this);
//            double graphCC = FitnessCalc.getGraphCutCost(this);
//
//            if (Math.abs(ffitness - fitness) > 0.5 || Math.abs(graphCC - graphCutCost) > 0.5) {
//
//
//                BigDecimal bd1 = new BigDecimal(ffitness);
//                BigDecimal bd2 = new BigDecimal(fitness);
//                BigDecimal bd3 = new BigDecimal(graphCC);
//                BigDecimal bd4 = new BigDecimal(graphCutCost);
//
//                System.out.println("---------------");
//                System.out.println("---------------");
//                System.out.println("---------------");
//                System.out.println("---------------");
//
//                System.out.println("ffitness: " + bd1);
//                System.out.println("fitness : " + bd2);
//                System.out.println("graphCC: " + bd3);
//                System.out.println("graphcc: " + bd4);
//
//                System.out.println("---------------");
//                System.out.println("---------------");
//                System.out.println("---------------");
//                System.out.println("---------------");
//
//                System.out.println();
//            }
        }
        validity = DONTKNOW;
    }

    public int size() {
        return genes.length;
    }

    public double getFitness() {

        if (!fitnessCalculated) {
            fitness = 0;
            for (int i = 0; i < FitnessCalc.numberOfMachines; i++) {
                if (usedCapacities[i] > FitnessCalc.M[i]) {
                    fitness += 1000000.0;
                }
            }
            double[][] C = FitnessCalc.C;
            double[][] B = FitnessCalc.B;
            graphCutCost = 0;
            for (int i = 0; i < FitnessCalc.numberOfVertex; i++) {
                for (int j = i + 1; j < FitnessCalc.numberOfVertex; j++) {
                    if (genes[i] != genes[j]) {
                        double d = (C[i][j] * B[genes[i]][genes[j]]);
                        fitness += d;
                        graphCutCost += d;

                    }
                }
            }
            fitnessCalculated = true;
        }
        return fitness;
    }

    public double getGraphCutCost() {
        if (!fitnessCalculated) {
            getFitness();
        }
        return graphCutCost;
    }

    public boolean getFitnessCalculated() {
        return fitnessCalculated;
    }


    @Override
    public String toString() {
        StringBuffer strBuff = new StringBuffer();
        for (int i = 0; i < size(); i++) {
            strBuff.append("(Vertex " + i + " ==> Machine " + getGene(i) + ")\n");
        }
        return strBuff.toString();
    }

    public double[] getUsedCapacities() {
        return usedCapacities;
    }

    public static int getTabooOfIndex(int index){
        if(tabooSet) return taboo[index];
        else {
            setTaboo();
            tabooSet = true;
            return 0;
        }
    }

    public static void setTabooOfIndex(int index) {
        if (tabooSet) {
            taboo[index] = tabooCount;
        } else {
            setTaboo();
            tabooSet = true;
            taboo[index] = tabooCount;
        }
        tabooCount++;
    }


    private static void setTaboo(){
        for(int i=0; i<FitnessCalc.numberOfMachines; i++) taboo[i] = 0;
    }

    public static int getTabooCount() {
        return tabooCount;
    }

    public int getBestGeneIndex() {
        return bestGeneIndex;
    }

    public void setBestGeneIndex(int bestGene) {
        this.bestGeneIndex = bestGene;
    }
}