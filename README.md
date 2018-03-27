# msdoc2txt

## build environment

* Apache Maven 3.3.9
* Java 1.8.0

## how to build

run mvn command to build.

```bash
$ mvn package
$ ls -l target/msdoc2txt-1.0-SNAPSHOT*
-rw-r--r--  1 user group 10386782 Mar 27 17:05 target/msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar
-rw-r--r--  1 user group     5800 Mar 27 17:05 target/msdoc2txt-1.0-SNAPSHOT.jar
```

*msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar* is single executable jar including apache poi libraries.

## how to run

The *msdoc2txt.jar* receives doc/docx file as standard input, like this.

```bash
$ java -jar target/msdoc2txt-1.0-SNAPSHOT-jar-with-dependencies.jar < samples/welcome-to-word.docx
...
Quick access to commands
At the top of your document, the Quick Access Toolbar puts the commands you use frequently just one click away.
...
```
