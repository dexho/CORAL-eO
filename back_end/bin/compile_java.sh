#!/bin/bash

PROJECT_ROOT="$(grep -o '"project_root": "[^"]*' ../modules/var/config.json | grep -o '[^"]*$')"

CLASSPATH="${PROJECT_ROOT}/java/classes:${PROJECT_ROOT}/java/GenericsUtil/lib/src:${PROJECT_ROOT}/java/jars/lib/jars/jackson/jackson-core-2.5.4.jar:${PROJECT_ROOT}/java/jars/lib/jars/jackson/jackson-annotations-2.5.4.jar:${PROJECT_ROOT}/java/jars/lib/jars/jackson/jackson-databind-2.5.4.jar:${PROJECT_ROOT}/java/jars/lib/jars/jackson/jackson-jaxrs-base-2.5.4.jar:${PROJECT_ROOT}/java/jars/lib/jars/jackson/jackson-jaxrs-json-provider-2.5.4.jar:${PROJECT_ROOT}/java/jars/lib/jars/jackson/jackson-module-jaxb-annotations-2.5.4.jar:${PROJECT_ROOT}/java/jars/lib/jars/opencsv/opencsv-3.9.jar:${PROJECT_ROOT}/java/jars/lib/jars/annotation/javax.annotation-api-1.3.2.jar:${PROJECT_ROOT}/java/jars/lib/jars/strbio/strbio-1.3.jar:${PROJECT_ROOT}/java/jars/lib/jars/apache_commons/commons-lang3-3.5.jar"
export CLASSPATH

javac "$PROJECT_ROOT"/java/classes/gov/lbl/enigma/app/*.java
