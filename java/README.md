# msdoc2txt

## Build environment

* Apache Maven 3.3.9
* Java 1.8.0

## How to build

Download external jar files which are not put in maven repository. These downloaded jar files are cached, so run it once except remove the *extjar* directory.

```bash
$ mvn initialize
$ tree extjar/
extjar/
└── com
    └── rtfparserkit
        └── rtfparserkit
            └── 1.10.0
                └── rtfparserkit-1.10.0.jar

4 directories, 1 file
```

Run to create jar files including all dependencies. Downloaded jar files would be copied to local maven repository.

```bash
$ mvn package
$ ls ~/.m2/repository/com/rtfparserkit/rtfparserkit/1.10.0/rtfparserkit-1.10.0.jar
path/to/.m2/repository/com/rtfparserkit/rtfparserkit/1.10.0/rtfparserkit-1.10.0.jar
```

```bash
$ ls -l target/msdoc2txt-1.0-SNAPSHOT*
-rw-r--r--  1 user group 10386782 Mar 27 17:05 target/msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar
-rw-r--r--  1 user group     5800 Mar 27 17:05 target/msdoc2txt-1.0-SNAPSHOT.jar
```

The *msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar* is single executable jar including Apache POI and other external libraries.

## How to run

The *msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar* receives doc/docx file as standard input, like this.

```bash
$ java -jar target/msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar < samples/welcome-to-word.docx
...
Quick access to commands
At the top of your document, the Quick Access Toolbar puts the commands you use frequently just one click away.
...
```

For debugging, use command line options.

```bash
$ java -jar target/msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar --help
usage: msdoc2txt
 -f,--file <arg>   set path to file to retreive contents
 -h,--help         print this message
 -v,--verbose      verbose mode for debugging
```

For example, *--verbose* option outputs INFO logging.

```bash
$ java -jar target/msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar --verbose --file samples/welcome-to-word.docx
2018-03-30 01:37:33 [INFO] start msdoc2txt for debugging
2018-03-30 01:37:33 [INFO] path to file: samples/welcome-to-word.docx
2018-03-30 01:37:33 [INFO] file type: OOXML
2018-03-30 01:37:33 [INFO] document type: XWPFDocument
2018-03-30 01:37:34 [INFO] extracter is Others
...
```

## Confirm revision information

The built jar has git revision as SCM-Revision in *META-INF/MANIFEST.MF*.

```bash
$ cd target
$ jar xvf msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar
$ cat META-INF/MANIFEST.MF
Manifest-Version: 1.0
SCM-Revision: 3cf671e
Built-By: user
Created-By: Apache Maven 3.3.9
Build-Jdk: 1.8.0_111
Main-Class: jp.cmscom.c2.transform.msoffice.MSDoc2Txt
```
