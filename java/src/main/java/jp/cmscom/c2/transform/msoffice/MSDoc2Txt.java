package jp.cmscom.c2.transform.msoffice;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.PushbackInputStream;
import java.util.Arrays;
import java.util.Date;
import java.util.Optional;
import java.util.logging.ConsoleHandler;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import java.util.stream.Collectors;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.poi.openxml4j.exceptions.OpenXML4JException;
import org.apache.poi.poifs.filesystem.FileMagic;
import org.apache.xmlbeans.XmlException;

public class MSDoc2Txt {

	private static Logger logger = Logger.getLogger(MSDoc2Txt.class.getName());

	private static void prn(String s) {
		if (s != null && !s.trim().isEmpty()) {
			System.out.println(s);
		}
	}

	private static CommandLine parseArgument(String[] args) throws ParseException {
		CommandLineParser parser = new DefaultParser();
		Options options = new Options();
		options.addOption("h", "help", false, "print this message");
		options.addOption("v", "verbose", false, "verbose mode for debugging");
		options.addOption(
				Option.builder("f").longOpt("file").hasArg().desc("set path to file to retreive contents").build());

		CommandLine cmd = parser.parse(options, args);
		if (cmd.hasOption("help")) {
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("msdoc2txt", options);
		}

		return cmd;
	}

	private static void configureLogger() {
		logger.setLevel(Level.OFF);
		logger.setUseParentHandlers(false);
		Handler handler = new ConsoleHandler();
		handler.setFormatter(new SimpleFormatter() {
			private static final String format = "%1$tF %1$tT [%2$s] %3$s %n";

			@Override
			public synchronized String format(LogRecord lr) {
				Date date = new Date(lr.getMillis());
				return String.format(format, date, lr.getLevel().getLocalizedName(), lr.getMessage());
			}
		});
		logger.addHandler(handler);

		// TODO: logger configuration
		MSDocExtracter.setLogger(logger);
		RTFExtracter.setLogger(logger);
	}

	public static void main(String[] args)
			throws FileNotFoundException, IOException, XmlException, ParseException, OpenXML4JException {
		configureLogger();

		CommandLine cmd = parseArgument(args);
		if (cmd.hasOption("help")) {
			return;
		}

		if (cmd.hasOption("verbose")) {
			logger.setLevel(Level.INFO);
		}
		logger.info("start msdoc2txt for debugging");

		InputStream is = System.in;
		if (cmd.hasOption("file")) {
			String path = cmd.getOptionValue("file");
			logger.info("path to file: " + path);
			is = new FileInputStream(path);
		}

		try (InputStream pis = FileMagic.prepareToCheckMagic(new PushbackInputStream(is, 8))) {
			FileMagic fileType = FileMagic.valueOf(pis);
			Optional<DocType> opt = DocType.valueOf(fileType);
			if (opt.isPresent()) {
				DocType docType = opt.get();
				logger.info("file type: " + fileType.toString());

				DocExtracter extracter = docType.getExtracter(pis);
				prn(extracter.getProperties());
				prn(extracter.getHeader());
				prn(extracter.getFooter());
				prn(extracter.getNotes());
				prn(extracter.getContents());
			} else {
				logger.info("file type: " + fileType.toString());
				String types = Arrays.asList(DocType.values()).stream().map(i -> i.toString())
						.collect(Collectors.joining(", "));
				String msg = fileType.toString() + " is not supported, msdoc2txt supports " + types + " format";
				throw new IllegalArgumentException(msg);
			}
		}

		logger.info("end msdoc2txt for debugging");
	}
}