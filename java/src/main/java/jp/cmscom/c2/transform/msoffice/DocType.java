package jp.cmscom.c2.transform.msoffice;

import java.io.IOException;
import java.io.InputStream;
import java.util.Optional;

import org.apache.poi.openxml4j.exceptions.OpenXML4JException;
import org.apache.poi.openxml4j.opc.OPCPackage;
import org.apache.poi.poifs.filesystem.FileMagic;
import org.apache.poi.poifs.filesystem.POIFSFileSystem;
import org.apache.xmlbeans.XmlException;

public enum DocType {

	OLE2(FileMagic.OLE2) {
		@Override
		public DocExtracter getExtracter(InputStream is) throws IOException, OpenXML4JException, XmlException {
			POIFSFileSystem fs = new POIFSFileSystem(is);
			return new MSDocExtracter(fs);
		}
	},

	OOXML(FileMagic.OOXML) {
		@Override
		public DocExtracter getExtracter(InputStream is) throws IOException, OpenXML4JException, XmlException {
			OPCPackage pkg = OPCPackage.open(is);
			return new MSDocExtracter(pkg);
		}
	},

	RTF(FileMagic.RTF) {
		@Override
		public DocExtracter getExtracter(InputStream is) throws IOException, OpenXML4JException, XmlException {
			return new RTFExtracter(is);
		}
	};

	abstract DocExtracter getExtracter(InputStream is) throws IOException, OpenXML4JException, XmlException;

	private final FileMagic fileType;

	DocType(FileMagic fileType) {
		this.fileType = fileType;
	}

	public FileMagic getFileType() {
		return this.fileType;
	}

	public static Optional<DocType> valueOf(FileMagic fileType) {
		for (DocType docType : DocType.values()) {
			if (docType.getFileType().equals(fileType)) {
				return Optional.ofNullable(docType);
			}
		}
		return Optional.empty();
	}
}