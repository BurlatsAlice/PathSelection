package monitoring;

import org.apache.commons.cli.*;

import java.io.FileWriter;
import java.io.IOException;

public class Main {
    public static void main(String[] args) {
        Option routesFileOpt = Option.builder().longOpt("routes").argName("ROUTES_FILE").required().hasArg()
                .desc("routes file").build();

        Option writeStatsOutOpt = Option.builder().longOpt("write-stats").argName("STATS_FILE").hasArg()
                .desc("file to write statistics").build();

        Option printStatsOutOpt = Option.builder().longOpt("print-stats").hasArg()
                .desc("print the statistics").build();

        Option solOutOpt = Option.builder().longOpt("print-solution").hasArg(false)
                .desc("print solution").build();

        Option solFileOpt = Option.builder().longOpt("write-solution").hasArg()
                .desc("file to write the solution").build();

        Option seedOpt = Option.builder().longOpt("seed").argName("SEED").hasArg().desc("random seed").build();

        Options options = new Options();
        options.addOption(routesFileOpt);
        options.addOption(writeStatsOutOpt);
        options.addOption(printStatsOutOpt);
        options.addOption(solOutOpt);
        options.addOption(solFileOpt);
        options.addOption(seedOpt);

        CommandLineParser parser = new DefaultParser();
        CommandLine cmd = null;
        try {
            cmd = parser.parse(options, args);
        } catch (ParseException exp) {
            System.err.println(exp.getMessage());
            new HelpFormatter().printHelp("solve path selection problem", options);
            System.exit(1);
        }

        String routeFilename = cmd.getOptionValue("routes");
        String statsFilename = cmd.getOptionValue("write-stats");
        String solutionFilename = cmd.getOptionValue("write-solution");
        int seed = 1358476;
        if (cmd.hasOption("seed"))
            seed = Integer.parseInt(cmd.getOptionValue("seed"));

        // Initialize the problem
        PathSelection problem = new PathSelection(routeFilename, seed);

        // Solve the problem
        long startTime = System.currentTimeMillis();
        problem.solve();
        long endTime = System.currentTimeMillis();
        double solvingTime = (endTime - startTime) / 1000.0;
        int nbrUncovered = problem.verifyCover();
        int nbrUndistinguishable = problem.verifyOneId();

        // Output the statisitcs
        String output = "";
        output += routeFilename + ";greedy" + ";" + problem.getMeasurementPaths().size() + ";" + seed
                + ";" + nbrUncovered + ";" + nbrUndistinguishable + ";" + solvingTime;
        output += ";" + problem.nbrCover +
                ";" + problem.nbrOneId +
                ";" + problem.nbrReduction;
        output += "\n";
        if (cmd.hasOption("print-stats"))
            System.out.println(output);
        if (cmd.hasOption("write-stats")) {
            try {
                FileWriter writer = new FileWriter(statsFilename, true);
                writer.write(output);
                writer.close();
            }
            catch (IOException error) {
                System.out.println("Stat file not found");
            }
        }

        // Print the solution
        if (cmd.hasOption("print-solution")) {
            System.out.println(solvingTime);
            System.out.print(problem.solutionString());
        }

        // Write the solution in the given file
        if (cmd.hasOption("write-solution")) {
            try {
                FileWriter solutionOutput = new FileWriter(solutionFilename);
                String solution = problem.solutionString();
                solutionOutput.write(solution);
                solutionOutput.close();
            } catch (IOException e) {
                System.out.println(e);
            }
        }

    }
}
