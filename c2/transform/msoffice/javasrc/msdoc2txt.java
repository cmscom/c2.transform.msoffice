import java.io.*;
import org.apache.poi.extractor.ExtractorFactory;
import org.apache.poi.POITextExtractor;
import org.apache.xmlbeans.XmlException;
import org.apache.poi.openxml4j.exceptions.OpenXML4JException;
import org.apache.poi.openxml4j.exceptions.InvalidFormatException;

public class msdoc2txt
{
    public static void main ( String[] args )
	throws FileNotFoundException, IOException, InvalidFormatException, OpenXML4JException, XmlException
    {
	POITextExtractor ex = ExtractorFactory.createExtractor(System.in);
	String result = ex.getText();
	System.out.println(result);
    }
}