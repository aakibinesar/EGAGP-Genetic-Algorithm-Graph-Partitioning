public class Population {
    Individual[] individuals;

    public Population(int populationSize, boolean initialise) {
        individuals = new Individual[populationSize];
        if (initialise) {
            for (int i = 0; i < size(); i++) {
                Individual newIndividual = new Individual();
                newIndividual.generateValidIndividual();
                saveIndividual(i, newIndividual);
            }
        }
    }

    public Individual getIndividual(int index) {
        return individuals[index];
    }

    public Individual getFittest() {
        Individual fittest = null;
        for (int i = 0; i < size(); i++) {
            if (getIndividual(i).isValid() == Individual.VALID) {
                fittest = getIndividual(i);
                break;
            }
        }

        if (fittest != null) {
            for (int i = 0; i < size(); i++) {
                if (getIndividual(i).isValid() == Individual.VALID) {
                    if (fittest.getFitness() > getIndividual(i).getFitness()) {
                        fittest = getIndividual(i);
                    }
                }
            }
            return fittest;
        } else
            return null;
    }

    public int size() {
        return individuals.length;
    }

    public void saveIndividual(int index, Individual indiv) {
        individuals[index] = indiv;
    }
}