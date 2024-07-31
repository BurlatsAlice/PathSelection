package monitoring;

import java.util.*;

import static monitoring.Utils.hashPair;

public class PathSelection extends Problem{
    protected int nbrReduction; //number of paths discards during optimisation of Solution
    protected int nbrCover; //number of added paths during the cover loop
    protected int nbrOneId; //number of paths after the 1id loop

    public PathSelection(String routeFilename, int seed) {
        super(routeFilename, seed);
    }

    @Override
    public void solve() {
        BitSet undistiguishablePairs = new BitSet(n*(n-1)/2);
        BitSet uncoveredNodes = new BitSet(n);
        for (int i = 0; i < n; i++) {
            uncoveredNodes.set(i);
            for (int j = i+1; j < n; j++) {
                undistiguishablePairs.set(hashPair(j, i, n));
            }
        }


        for (Integer path_index : this.measurementPaths)
            undistiguishablePairs.andNot(routes.get(path_index).getDiscrimSet(n));

        int bestDistinguishability = -1;
        int bestRoute = -1;
        int counter = 0;
        BitSet distinguishabilitySet;
        LinkedList<Integer> candidates = new LinkedList<>();
        Random random = new Random(this.seed);
        while (!undistiguishablePairs.isEmpty()) {
            for (int i = 0; i < this.routes.size(); i++) {
                if (!measurementPaths.contains(i) && !removedRoutes.contains(i)) {
                    distinguishabilitySet = (BitSet) this.routes.get(i).getDiscrimSet(n).clone();
                    distinguishabilitySet.and(undistiguishablePairs);
                    if (distinguishabilitySet.cardinality() > bestDistinguishability) {
                        // bestRoute = i;
                        bestDistinguishability = distinguishabilitySet.cardinality();
                        candidates.clear();
                        candidates.add(i);
                    } else if (distinguishabilitySet.cardinality() == bestDistinguishability)
                        candidates.add(i);
                }
            }
            bestRoute = candidates.get(random.nextInt(candidates.size()));
            distinguishabilitySet = (BitSet) this.routes.get(bestRoute).getDiscrimSet(n).clone();
            distinguishabilitySet.and(undistiguishablePairs);



            uncoveredNodes.andNot(this.routes.get(bestRoute).getNodes());
            undistiguishablePairs.andNot(this.routes.get(bestRoute).getDiscrimSet(n));
            measurementPaths.add(bestRoute);
            bestDistinguishability = -1;
            candidates.clear();
            counter++;
        }

        // If a single node is uncovered, we add a random route in its symptom
        for (int i = 0; i < this.n; i++)
            if (uncoveredNodes.get(i)) {
                for (int j = 0; j < this.routes.size(); j++)
                    if (!removedRoutes.contains(j) && this.routes.get(j).getNodes().get(i)) {
                        measurementPaths.add(j);
                        break;
                    }
            }


        this.nbrOneId = counter;
    }
}
