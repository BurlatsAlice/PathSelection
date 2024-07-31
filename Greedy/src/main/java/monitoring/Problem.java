package monitoring;

import org.apache.commons.collections4.CollectionUtils;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static monitoring.Utils.hashPair;

public abstract class Problem {

    protected int n; //number of nodes;
    protected int seed;
    protected ArrayList<Route> routes; //routes availables for the network
    final protected HashSet<Integer> measurementPaths; // indexes of the chosen measurement paths
    protected LinkedList<HashSet<Integer>> flowers;
    protected HashSet<Integer> leafNodes;
    protected LinkedList<HashSet<Integer>> biconnectedComponents;
    protected HashSet<Integer> removedRoutes;


    /**
     * Initialize the problem
     * @param routeFilename: path to the routes definition
     */
    public Problem(String routeFilename, int seed) {
        this.routes = new ArrayList<>();
        parseInstance(routeFilename);
        measurementPaths = new HashSet<>();
        removedRoutes = new HashSet<>();
        this.seed = seed;
    }

    /**
     * Parse routes and number of nodes from the given instance file.
     * @param filename: the path to the file where routes are stored.
     */
    public void parseInstance(String filename) {
        int n = -1;
        try {
            BufferedReader reader = new BufferedReader(new FileReader(filename));

            Pattern findInt = Pattern.compile("\\d+");
            Matcher mInt;

            this.n = Integer.parseInt(reader.readLine().split(" ")[0]);

            String currentLine = reader.readLine();
            int startingNode;
            int endingNode;
            BitSet newRoute;
            while (currentLine != null) {
                mInt = findInt.matcher(currentLine);
                mInt.find();
                startingNode = Integer.parseInt(mInt.group());
                mInt.find();
                endingNode = Integer.parseInt(mInt.group());
                newRoute = new BitSet(this.n);
                int node;
                while (mInt.find()) {
                    node = Integer.parseInt(mInt.group());
                    newRoute.set(node);
                }
                this.routes.add(new Route(this.routes.size(), startingNode, endingNode));
                this.routes.get(this.routes.size() - 1).setNodes(newRoute);
                currentLine = reader.readLine();
            }
        } catch (IOException e) {
            System.out.println(e);
        }
    }

    /**
     * Solve the problem
     */
    public void solve() {
    }

    /**
     * Verify that the solution makes the network entirely covered
     * necessitates to run solve() before
     * @return the number of uncovered nodes
     */
    public int verifyCover() {
        BitSet coveredNodes = new BitSet(this.n);
        for (Integer i : this.measurementPaths) {
            coveredNodes.or(this.routes.get(i).getNodes());
        }
        return this.n - coveredNodes.cardinality();
    }

    /**
     * Verify that the solution makes the network entirely 1-identifiable
     * necessitates to run solve() before
     * @return the number of undistinguishable pair of nodes
     */
    public int verifyOneId() {
        BitSet totalPairs = new BitSet(n*(n-1)/2);
        for (int i = 1; i < n; i++)
            for (int j = 0; j < i; j++)
                totalPairs.set(hashPair(j, i, n));

        BitSet discrimPairs = new BitSet(n*(n-1)/2);
        for (Integer i: this.measurementPaths)
            discrimPairs.or(this.routes.get(i).getDiscrimSet(n));
        return totalPairs.cardinality() - discrimPairs.cardinality();
    }

    /**
     * @return a string containing a description of the measurement paths
     */
    public String solutionString() {
        StringBuilder solution = new StringBuilder();
        solution.append(n).append("\n");
        for (Integer a : measurementPaths) {
            solution.append(routes.get(a).src).append(" ").append(routes.get(a).dest)
                    .append(" | ");
            for (int i = 0; i < n; i++)
                if (routes.get(a).getNodes().get(i))
                    solution.append(i).append(" ");
            solution.append("\n");
        }
        return solution.toString();
    }

    /**
     * @return an array list containing the chosen measurement path
     */
    public ArrayList<Route> getMeasurementPaths() {
        ArrayList<Route> measurementPathsDescription = new ArrayList<>();
        for (Integer path_index : measurementPaths) {
            measurementPathsDescription.add(routes.get(path_index));
        }
        return measurementPathsDescription;
    }
}
