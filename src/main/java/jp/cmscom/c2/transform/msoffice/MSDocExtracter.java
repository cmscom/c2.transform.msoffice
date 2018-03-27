package jp.cmscom.c2.transform.msoffice;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.logging.Logger;
import java.util.stream.Collectors;

import org.apache.poi.POIDocument;
import org.apache.poi.POIOLE2TextExtractor;
import org.apache.poi.POITextExtractor;
import org.apache.poi.POIXMLDocument;
import org.apache.poi.POIXMLProperties;
import org.apache.poi.POIXMLProperties.CoreProperties;
import org.apache.poi.extractor.ExtractorFactory;
import org.apache.poi.hdgf.HDGFDiagram;
import org.apache.poi.hdgf.extractor.VisioTextExtractor;
import org.apache.poi.hpsf.SummaryInformation;
import org.apache.poi.hslf.extractor.PowerPointExtractor;
import org.apache.poi.hssf.extractor.ExcelExtractor;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.hwpf.HWPFDocument;
import org.apache.poi.hwpf.extractor.WordExtractor;
import org.apache.poi.openxml4j.exceptions.OpenXML4JException;
import org.apache.poi.openxml4j.opc.OPCPackage;
import org.apache.poi.openxml4j.opc.PackagePart;
import org.apache.poi.openxml4j.opc.PackageRelationshipCollection;
import org.apache.poi.poifs.filesystem.DirectoryNode;
import org.apache.poi.poifs.filesystem.Entry;
import org.apache.poi.poifs.filesystem.POIFSFileSystem;
import org.apache.poi.xslf.extractor.XSLFPowerPointExtractor;
import org.apache.poi.xslf.usermodel.XSLFRelation;
import org.apache.poi.xslf.usermodel.XSLFSlideShow;
import org.apache.poi.xssf.usermodel.XSSFRelation;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFRelation;
import org.apache.xmlbeans.XmlException;

public class MSDocExtracter implements DocExtracter {
	public static final String CORE_DOCUMENT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument";

	protected static Logger logger;

	protected static void setLogger(Logger l) {
		logger = l;
	}

	private Map<DocPart, List<Optional<String>>> document;

	@Override
	public String getProperties() {
		logger.info("=== properties ===");
		return this.join(document.get(DocPart.Properties));
	}

	@Override
	public String getNotes() {
		logger.info("=== notes ===");
		return this.join(document.get(DocPart.Notes));
	}

	@Override
	public String getHeader() {
		logger.info("=== header ===");
		return this.join(document.get(DocPart.Header));
	}

	@Override
	public String getFooter() {
		logger.info("=== footer ===");
		return this.join(document.get(DocPart.Footer));
	}

	@Override
	public String getContents() {
		logger.info("=== contents ===");
		return this.join(document.get(DocPart.Contents));
	}

	public MSDocExtracter() {
		this.document = new HashMap<DocPart, List<Optional<String>>>();
		for (DocPart part : DocPart.values()) {
			this.document.put(part, new ArrayList<Optional<String>>());
		}
	}

	public MSDocExtracter(POIFSFileSystem fs) throws IOException, OpenXML4JException, XmlException {
		this();
		this.extractMetadata(fs);
		POIOLE2TextExtractor oleTextExtractor = ExtractorFactory.createExtractor(fs);
		this.extractContents(oleTextExtractor);
	}

	private void extractMetadata(POIFSFileSystem fs) throws IOException {
		POIDocument doc = this.getDocument(fs);
		if (doc == null) {
			return;
		}

		SummaryInformation summary = doc.getSummaryInformation();
		if (summary == null) {
			return;
		}

		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getAuthor()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getApplicationName()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getComments()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getLastAuthor()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getRevNumber()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getSubject()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getTemplate()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(summary.getTitle()));
	}

	public POIDocument getDocument(POIFSFileSystem fs) throws IOException {
		DirectoryNode dir = fs.getRoot();
		for (Iterator<?> entries = dir.getEntries(); entries.hasNext();) {
			Entry entry = (Entry) entries.next();
			String entryName = entry.getName();
			logger.info("entry name: " + entryName);

			if (entryName.equals("Workbook")) {
				logger.info("document type: HSSFWorkbook");
				return new HSSFWorkbook(dir, fs, true);
			}
			if (entryName.equals("WordDocument")) {
				logger.info("document type: HWPFDocument");
				return new HWPFDocument(fs);
			}
			if (entryName.equals("PowerPoint Document")) {
				try (PowerPointExtractor pptExtractor = new PowerPointExtractor(fs)) {
					POIDocument doc = pptExtractor.getDocument();
					logger.info("document type: PowerPointExtractor");
					return doc;
				}
			}
			if (entryName.equals("VisioDocument")) {
				logger.info("document type: VisioDocument");
				return new HDGFDiagram(fs);
			}
		}

		logger.info("document type: HSSFWorkbook");
		return new HSSFWorkbook(dir, fs, true);
	}

	public MSDocExtracter(OPCPackage pkg) throws IOException, OpenXML4JException, XmlException {
		this();
		this.extractMetadata(pkg);
		POITextExtractor oleTextExtractor = ExtractorFactory.createExtractor(pkg);
		this.extractContents(oleTextExtractor);
	}

	private void extractMetadata(OPCPackage pkg) throws IOException, OpenXML4JException, XmlException {
		POIXMLDocument doc = this.getDocument(pkg);
		if (doc == null) {
			return;
		}

		POIXMLProperties prop = doc.getProperties();
		CoreProperties cp = prop.getCoreProperties();
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getCategory()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getDescription()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getSubject()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getTitle()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getContentStatus()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getContentType()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getRevision()));
		this.document.get(DocPart.Properties).add(Optional.ofNullable(cp.getCreator()));
	}

	public POIXMLDocument getDocument(OPCPackage pkg) throws IOException, OpenXML4JException, XmlException {
		PackageRelationshipCollection core = pkg.getRelationshipsByType(CORE_DOCUMENT_REL);
		PackagePart corePart = pkg.getPart(core.getRelationship(0));

		if (corePart.getContentType().equals(XSSFRelation.WORKBOOK.getContentType())
				|| corePart.getContentType().equals(XSSFRelation.MACRO_TEMPLATE_WORKBOOK.getContentType())
				|| corePart.getContentType().equals(XSSFRelation.MACRO_ADDIN_WORKBOOK.getContentType())
				|| corePart.getContentType().equals(XSSFRelation.TEMPLATE_WORKBOOK.getContentType())
				|| corePart.getContentType().equals(XSSFRelation.MACROS_WORKBOOK.getContentType())) {
			logger.info("document type: XSSFWorkbook");
			return new XSSFWorkbook(pkg);
		}

		if (corePart.getContentType().equals(XWPFRelation.DOCUMENT.getContentType())
				|| corePart.getContentType().equals(XWPFRelation.TEMPLATE.getContentType())
				|| corePart.getContentType().equals(XWPFRelation.MACRO_DOCUMENT.getContentType())
				|| corePart.getContentType().equals(XWPFRelation.MACRO_TEMPLATE_DOCUMENT.getContentType())) {
			logger.info("document type: XWPFDocument");
			return new XWPFDocument(pkg);
		}

		if (corePart.getContentType().equals(XSLFRelation.MAIN.getContentType())) {
			logger.info("document type: XSLFSlideShow");
			return new XSLFSlideShow(pkg);
		}

		return null;
	}

	private void extractContents(POITextExtractor textExtractor) {
		// If the embedded object was an Excel spreadsheet.
		if (textExtractor instanceof ExcelExtractor) {
			logger.info("extracter is ExcelExtractor");
			ExcelExtractor excelExtractor = (ExcelExtractor) textExtractor;
			this.document.get(DocPart.Contents).add(Optional.ofNullable(excelExtractor.getText()));
		}
		// A Word Document
		else if (textExtractor instanceof WordExtractor) {
			logger.info("extracter is WordExtractor");
			WordExtractor wordExtractor = (WordExtractor) textExtractor;
			String[] paragraphText = wordExtractor.getParagraphText();
			for (String paragraph : paragraphText) {
				this.document.get(DocPart.Contents).add(Optional.ofNullable(paragraph));
			}
			this.document.get(DocPart.Footer).add(Optional.ofNullable(wordExtractor.getFooterText()));
			this.document.get(DocPart.Header).add(Optional.ofNullable(wordExtractor.getHeaderText()));
		}
		// PowerPoint Presentation.
		else if (textExtractor instanceof PowerPointExtractor) {
			logger.info("extracter is PowerPointExtractor");
			PowerPointExtractor powerPointExtractor = (PowerPointExtractor) textExtractor;
			this.document.get(DocPart.Contents).add(Optional.ofNullable(powerPointExtractor.getText()));
			this.document.get(DocPart.Notes).add(Optional.ofNullable(powerPointExtractor.getNotes()));
		}
		// XSLFPowerPoint Presentation.
		else if (textExtractor instanceof XSLFPowerPointExtractor) {
			logger.info("extracter is XSLFPowerPointExtractor");
			XSLFPowerPointExtractor powerPointExtractor = (XSLFPowerPointExtractor) textExtractor;
			this.document.get(DocPart.Contents).add(Optional.ofNullable(powerPointExtractor.getText()));
			this.document.get(DocPart.Notes).add(Optional.ofNullable(powerPointExtractor.getText(false, true)));
		}
		// Visio Drawing
		else if (textExtractor instanceof VisioTextExtractor) {
			logger.info("extracter is VisioTextExtractor");
			VisioTextExtractor visioTextExtractor = (VisioTextExtractor) textExtractor;
			this.document.get(DocPart.Contents).add(Optional.ofNullable(visioTextExtractor.getText()));
		}
		// Others
		else {
			logger.info("extracter is Others");
			this.document.get(DocPart.Contents).add(Optional.ofNullable(textExtractor.getText()));
		}
	}

	private String join(List<Optional<String>> data) {
		return data.stream().filter(o -> o.isPresent()).map(o -> o.get())
				.collect(Collectors.joining(System.lineSeparator()));
	}
}