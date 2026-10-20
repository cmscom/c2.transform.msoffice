package jp.cmscom.c2.transform.msoffice;

public interface DocExtracter {
	default public String getProperties() {
		return "";
	}

	default public String getNotes() {
		return "";
	}

	default public String getHeader() {
		return "";
	}

	default public String getFooter() {
		return "";
	}

	default public String getContents() {
		return "";
	}
}