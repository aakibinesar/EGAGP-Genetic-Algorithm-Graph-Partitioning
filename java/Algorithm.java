import java.util.ArrayList;
import java.util.Random;

public class Algorithm {

    private static int greedyMutationValues = FitnessCalc.numberOfMachines;
    private static final int tournamentSize = 5;
    private static final int tabooLimit = 25;
    private static final boolean elitism = true;
    private static final boolean tabooFlag = false;

    public static Population evolvePopulation(Population pop) {
        Population newPopulation = new Population(pop.size(), false);
        if (elitism) {
            newPopulation.saveIndividual(0, pop.getFittest());
        }
        int elitismOffset;
        if (elitism) {
            elitismOffset = 1;
        } else {
            elitismOffset = 0;
        }
        for (int i = elitismOffset; i < pop.size(); i++) {
            int j = 0;
            while (j < FitnessCalc.numberOfVertex) {
                Individual indiv1 = tournamentSelection(pop);
                Individual indiv2 = tournamentSelection(pop);
                Individual newIndiv = onePointCrossover(indiv1, indiv2);
                if (newIndiv.isValid() == Individual.VALID) {
                    newPopulation.saveIndividual(i, newIndiv);
                    break;
                }
                j++;
            }
            if (j == FitnessCalc.numberOfVertex) {
                newPopulation.saveIndividual(i, pop.getIndividual(i));
            }
        }
        for (int i = elitismOffset; i < newPopulation.size(); i++) {
            greedymutate(newPopulation.getIndividual(i));
        }
        return newPopulation;
    }

    public static Population randomRestart(Population pop) {
        Population newPopulation = new Population(pop.size(), false);
        if (elitism) {
            newPopulation.saveIndividual(0, pop.getFittest());
        }
        int elitismOffset;
        if (elitism) {
            elitismOffset = 1;
        } else {
            elitismOffset = 0;
        }
        int i;
        for (i = elitismOffset; i < (pop.size() / 5); i++) {
            Individual indiv1 = tournamentSelection(pop);
            newPopulation.saveIndividual(i, indiv1);
        }
        for (; i < newPopulation.size(); i++) {
            Individual indiv = new Individual();
            indiv.generateValidIndividual();
            newPopulation.saveIndividual(i, indiv);
        }
        return newPopulation;
    }

    private static Individual onePointCrossover(Individual indiv1, Individual indiv2) {
        Individual newIndiv = new Individual();
        newIndiv.onePointCrossover(indiv1, indiv2);
        return newIndiv;
    }

    private static void greedymutate(Individual indiv) {
        Individual temp = new Individual(indiv);

        Random random = new Random();
        int minIndex;
        int gene_index;
        int min_gene_value = -1;
        int k = 0;
        int tabooCount = Individual.getTabooCount();
        while (k < FitnessCalc.numberOfVertex) {

            gene_index = random.nextInt(FitnessCalc.numberOfVertex);
            if(tabooCount - Individual.getTabooOfIndex(gene_index) < tabooLimit && tabooFlag){
                k++;
                continue;
            }

            greedyMutationValues = FitnessCalc.numberOfMachines;

            ArrayList<Integer> values = new ArrayList<Integer>();
            for (int i = 0; i < greedyMutationValues; i++) {
                values.add(random.nextInt(FitnessCalc.numberOfMachines));
            }
            int i = 0;
            double minFitness = 99999999999999.0, fitness;
            minIndex = -1;
            while (i < greedyMutationValues) {
                indiv.setGene(gene_index, values.get(i));
                if (indiv.isValid() == Individual.VALID) {
                    fitness = indiv.getFitness();
                    if(fitness < minFitness){
                        minIndex = i;
                        min_gene_value = values.get(i);
                    }
                }
                i++;
            }
            if (minIndex != -1) {
                indiv.setGene(gene_index, min_gene_value);
                indiv.setBestGeneIndex(gene_index);
                Individual.setTabooOfIndex(gene_index);
                break;
            } else {
                indiv.setGene(gene_index, temp.getGene(gene_index));
            }
            k++;
        }
    }

    private static Individual tournamentSelection(Population pop) {
        Population tournament = new Population(tournamentSize, false);
        for (int i = 0; i < tournamentSize; i++) {
            int randomId = (int) (Math.random() * pop.size());
            tournament.saveIndividual(i, pop.getIndividual(randomId));
        }
        Individual fittest = tournament.getFittest();
        return fittest;
    }

    public static Population removeTwins(Population myPop) {
        int count = 0;
        for (int i = 0; i < myPop.size(); i++) {
            for (int j = i + 1; j < myPop.size(); j++) {
                if (isTwins(myPop.getIndividual(i), myPop.getIndividual(j))) {
                    Individual indiv = new Individual();
                    indiv.generateValidIndividual();
                    myPop.saveIndividual(j, indiv);
                    count++;
                }
            }
        }
//        System.out.println("Twins found: " + count);
        return myPop;
    }

    private static boolean isTwins(Individual ind1, Individual ind2) {
        int hammingDistance = 0;
        for (int i = 0; i < ind1.size(); i++) {
            if (ind1.getGene(i) != ind2.getGene(i))
                hammingDistance++;
        }
        if ((hammingDistance * 100 / (double) ind1.size()) <= 2.50)
            return true;
        else
            return false;
    }
}