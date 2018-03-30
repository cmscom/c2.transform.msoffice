package jp.cmscom.c2.transform.msoffice;

import java.io.IOException;
import java.io.InputStream;
import java.util.logging.Logger;

import com.rtfparserkit.converter.text.StringTextConverter;
import com.rtfparserkit.parser.RtfStreamSource;

public class RTFExtracter implements DocExtracter {

	protected static Logger logger;

	protected static void setLogger(Logger l) {
		logger = l;
	}

	private String contents;

	@Override
	public String getContents() {
		return this.contents;
	}

	public RTFExtracter(InputStream is) throws IOException {
		StringTextConverter converter = new StringTextConverter();
		converter.convert(new RtfStreamSource(is));
		this.contents = converter.getText();
	}
}