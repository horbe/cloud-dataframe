"""
Utilities for interacting with the Pure Relation REPL.
"""
import os
import csv
import tempfile
import sys
import subprocess
import time
import json
import re
import threading
import queue

repl_process = None
repl_output_queue = queue.Queue()
repl_ready = threading.Event()

def start_repl():
    """Start the REPL and keep it running."""
    global repl_process

    if repl_process is not None:
        print("REPL is already running.")
        return

    repl_dir = "/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-config/legend-engine-repl/legend-engine-repl-relational"

    os.chdir(repl_dir)

    cmd = "java -classpath /Users/ahauser/Documents/work/legend/legend-engine/legend-engine-config/legend-engine-repl/legend-engine-repl-relational/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-config/legend-engine-repl/legend-engine-repl-client/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-compiled-core/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-standard/legend-engine-pure-runtime-java-extension-compiled-functions-standard/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-standard/legend-engine-pure-runtime-java-extension-shared-functions-standard/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-dsl-diagram-java/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-diagram-pure/5.36.1/legend-pure-m2-dsl-diagram-pure-5.36.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-dsl-graph-java/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-dsl-tds-java/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-unclassified/legend-engine-pure-runtime-java-extension-compiled-functions-unclassified/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-unclassified/legend-engine-pure-functions-unclassified-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-unclassified/legend-engine-pure-runtime-java-extension-shared-functions-unclassified/target/classes:/Users/ahauser/.m2/repository/org/bouncycastle/bcprov-jdk15on/1.67/bcprov-jdk15on-1.67.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-json/legend-engine-pure-runtime-java-extension-compiled-functions-json/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-json/legend-engine-pure-functions-json-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-json/legend-engine-pure-runtime-java-extension-shared-functions-conversion/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-relation/legend-engine-pure-runtime-java-extension-compiled-functions-relation/target/classes:/Users/ahauser/.m2/repository/io/deephaven/deephaven-csv/0.12.0/deephaven-csv-0.12.0.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-dsl-path-java/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-compiled-dsl-tds/5.36.1/legend-pure-runtime-java-extension-compiled-dsl-tds-5.36.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-json/legend-engine-pure-runtime-java-extension-shared-functions-json/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-relation/legend-engine-pure-runtime-java-extension-shared-functions-relation/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-compiled-dsl-diagram/5.36.1/legend-pure-runtime-java-extension-compiled-dsl-diagram-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-engine-compiled/5.36.1/legend-pure-runtime-java-engine-compiled-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-engine-shared/5.36.1/legend-pure-runtime-java-engine-shared-5.36.1.jar:/Users/ahauser/.m2/repository/io/github/classgraph/classgraph/4.8.25/classgraph-4.8.25.jar:/Users/ahauser/.m2/repository/io/opentracing/opentracing-noop/0.32.0/opentracing-noop-0.32.0.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-java/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-core-extension/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-executionPlan-generation/legend-engine-executionPlan-generation/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-java/legend-engine-xt-javaPlatformBinding-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-java/legend-engine-xt-javaGeneration-featureBased-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-generation/legend-engine-language-pure-dsl-generation-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-java/legend-engine-xt-javaGeneration-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-java/legend-engine-xt-javaGeneration-conventions-essential-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-java/legend-engine-xt-javaGeneration-conventions-standard-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-java/legend-engine-xt-javaPlatformBinding-PCT/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-shared/legend-engine-shared-extensions/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-shared/legend-engine-shared-structures/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-identity/legend-engine-xt-identity-kerberos/target/classes:/Users/ahauser/.m2/repository/com/fasterxml/jackson/core/jackson-databind/2.10.5.1/jackson-databind-2.10.5.1.jar:/Users/ahauser/.m2/repository/org/apache/commons/commons-lang3/3.7/commons-lang3-3.7.jar:/Users/ahauser/.m2/repository/commons-io/commons-io/2.7/commons-io-2.7.jar:/Users/ahauser/.m2/repository/org/jline/jline-terminal-jansi/3.26.3/jline-terminal-jansi-3.26.3.jar:/Users/ahauser/.m2/repository/org/fusesource/jansi/jansi/2.4.1/jansi-2.4.1.jar:/Users/ahauser/.m2/repository/org/jline/jline-terminal/3.26.3/jline-terminal-3.26.3.jar:/Users/ahauser/.m2/repository/org/jline/jline-native/3.26.3/jline-native-3.26.3.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m3-core/5.36.1/legend-pure-m3-core-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m4/5.36.1/legend-pure-m4-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m3-bootstrap-generator/5.36.1/legend-pure-m3-bootstrap-generator-5.36.1.jar:/Users/ahauser/.m2/repository/org/antlr/antlr4-runtime/4.8-1/antlr4-runtime-4.8-1.jar:/Users/ahauser/.m2/repository/com/googlecode/json-simple/json-simple/1.1.1/json-simple-1.1.1.jar:/Users/ahauser/.m2/repository/commons-codec/commons-codec/1.15/commons-codec-1.15.jar:/Users/ahauser/.m2/repository/io/prometheus/simpleclient/0.8.1/simpleclient-0.8.1.jar:/Users/ahauser/.m2/repository/com/fasterxml/jackson/core/jackson-annotations/2.10.5/jackson-annotations-2.10.5.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-language-pure/legend-engine-language-pure-grammar/target/classes:/Users/ahauser/.m2/repository/org/slf4j/slf4j-api/1.7.25/slf4j-api-1.7.25.jar:/Users/ahauser/.m2/repository/com/fasterxml/jackson/core/jackson-core/2.10.5/jackson-core-2.10.5.jar:/Users/ahauser/.m2/repository/org/apache/commons/commons-text/1.10.0/commons-text-1.10.0.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-language-pure/legend-engine-protocol-pure/target/classes:/Users/ahauser/.m2/repository/org/mongodb/bson/3.12.8/bson-3.12.8.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-language-pure/legend-engine-language-pure-compiler/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-mapping-grammar/5.36.1/legend-pure-m2-dsl-mapping-grammar-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-path-grammar/5.36.1/legend-pure-m2-dsl-path-grammar-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-graph-grammar/5.36.1/legend-pure-m2-dsl-graph-grammar-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-store-grammar/5.36.1/legend-pure-m2-dsl-store-grammar-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-mapping-pure/5.36.1/legend-pure-m2-dsl-mapping-pure-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-path-pure/5.36.1/legend-pure-m2-dsl-path-pure-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-graph-pure/5.36.1/legend-pure-m2-dsl-graph-pure-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-compiled-dsl-path/5.36.1/legend-pure-runtime-java-extension-compiled-dsl-path-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-compiled-dsl-graph/5.36.1/legend-pure-runtime-java-extension-compiled-dsl-graph-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-compiled-dsl-mapping/5.36.1/legend-pure-runtime-java-extension-compiled-dsl-mapping-5.36.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-dsl-mapping-java/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-dsl-store-java/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-precisePrimitives-pure/target/classes:/Users/ahauser/.m2/repository/io/opentracing/opentracing-api/0.32.0/opentracing-api-0.32.0.jar:/Users/ahauser/.m2/repository/io/opentracing/opentracing-util/0.32.0/opentracing-util-0.32.0.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-executionPlan-execution/legend-engine-executionPlan-execution/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-identity/legend-engine-xt-identity-pac4j/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/shared/legend-shared-pac4j-kerberos/0.25.7/legend-shared-pac4j-kerberos-0.25.7.jar:/Users/ahauser/.m2/repository/org/pac4j/pac4j-kerberos/3.8.3/pac4j-kerberos-3.8.3.jar:/Users/ahauser/.m2/repository/javax/servlet/javax.servlet-api/3.1.0/javax.servlet-api-3.1.0.jar:/Users/ahauser/.m2/repository/org/finos/legend/shared/legend-shared-pac4j/0.25.7/legend-shared-pac4j-0.25.7.jar:/Users/ahauser/.m2/repository/org/pac4j/dropwizard-pac4j/3.0.0/dropwizard-pac4j-3.0.0.jar:/Users/ahauser/.m2/repository/org/pac4j/pac4j-config/3.0.0/pac4j-config-3.0.0.jar:/Users/ahauser/.m2/repository/org/pac4j/jersey225-pac4j/3.0.0/jersey225-pac4j-3.0.0.jar:/Users/ahauser/.m2/repository/org/pac4j/jax-rs/core/3.0.0/core-3.0.0.jar:/Users/ahauser/.m2/repository/javax/inject/javax.inject/1/javax.inject-1.jar:/Users/ahauser/.m2/repository/org/pac4j/j2e-pac4j/4.0.0/j2e-pac4j-4.0.0.jar:/Users/ahauser/.m2/repository/org/commonjava/mimeparse/mimeparse/0.1.3.3/mimeparse-0.1.3.3.jar:/Users/ahauser/.m2/repository/com/fasterxml/jackson/dataformat/jackson-dataformat-yaml/2.10.5/jackson-dataformat-yaml-2.10.5.jar:/Users/ahauser/.m2/repository/org/yaml/snakeyaml/1.33/snakeyaml-1.33.jar:/Users/ahauser/.m2/repository/org/mongodb/mongo-java-driver/3.12.8/mongo-java-driver-3.12.8.jar:/Users/ahauser/.m2/repository/com/hazelcast/hazelcast/5.3.1/hazelcast-5.3.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-shared/legend-engine-shared-javaCompiler/target/classes:/Users/ahauser/.m2/repository/org/codehaus/janino/janino/3.1.0/janino-3.1.0.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-executionPlan-execution/legend-engine-executionPlan-dependencies/target/classes:/Users/ahauser/.m2/repository/com/fasterxml/jackson/dataformat/jackson-dataformat-xml/2.10.5/jackson-dataformat-xml-2.10.5.jar:/Users/ahauser/.m2/repository/com/fasterxml/jackson/module/jackson-module-jaxb-annotations/2.10.5/jackson-module-jaxb-annotations-2.10.5.jar:/Users/ahauser/.m2/repository/jakarta/xml/bind/jakarta.xml.bind-api/2.3.2/jakarta.xml.bind-api-2.3.2.jar:/Users/ahauser/.m2/repository/jakarta/activation/jakarta.activation-api/1.2.1/jakarta.activation-api-1.2.1.jar:/Users/ahauser/.m2/repository/org/codehaus/woodstox/stax2-api/4.2.1/stax2-api-4.2.1.jar:/Users/ahauser/.m2/repository/com/fasterxml/woodstox/woodstox-core/6.2.1/woodstox-core-6.2.1.jar:/Users/ahauser/.m2/repository/org/openjdk/jol/jol-core/0.9/jol-core-0.9.jar:/Users/ahauser/.m2/repository/commons-lang/commons-lang/2.6/commons-lang-2.6.jar:/Users/ahauser/.m2/repository/org/freemarker/freemarker/2.3.30/freemarker-2.3.30.jar:/Users/ahauser/.m2/repository/io/opentracing/contrib/opentracing-concurrent/0.3.0/opentracing-concurrent-0.3.0.jar:/Users/ahauser/.m2/repository/org/apache/commons/commons-csv/1.5/commons-csv-1.5.jar:/Users/ahauser/.m2/repository/com/google/guava/guava/30.0-jre/guava-30.0-jre.jar:/Users/ahauser/.m2/repository/com/google/guava/failureaccess/1.0.1/failureaccess-1.0.1.jar:/Users/ahauser/.m2/repository/com/google/guava/listenablefuture/9999.0-empty-to-avoid-conflict-with-guava/listenablefuture-9999.0-empty-to-avoid-conflict-with-guava.jar:/Users/ahauser/.m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar:/Users/ahauser/.m2/repository/org/checkerframework/checker-qual/3.5.0/checker-qual-3.5.0.jar:/Users/ahauser/.m2/repository/com/google/errorprone/error_prone_annotations/2.3.4/error_prone_annotations-2.3.4.jar:/Users/ahauser/.m2/repository/com/google/j2objc/j2objc-annotations/1.3/j2objc-annotations-1.3.jar:/Users/ahauser/.m2/repository/org/codehaus/janino/commons-compiler/3.1.0/commons-compiler-3.1.0.jar:/Users/ahauser/.m2/repository/org/pac4j/pac4j-core/3.7.0/pac4j-core-3.7.0.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-store-pure/5.36.1/legend-pure-m2-dsl-store-pure-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-store-relational-pure/5.36.1/legend-pure-m2-store-relational-pure-5.36.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-execution/legend-engine-xt-relationalStore-executionPlan-connection/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-identity/legend-engine-xt-identity-middletier/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-identity/legend-engine-xt-identity-plainTextUserPassword/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-identity/legend-engine-xt-identity-apiToken/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-identity/legend-engine-xt-identity-oauth/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-shared/legend-engine-shared-vault/legend-engine-shared-vault-core/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-execution/legend-engine-xt-relationalStore-executionPlan-connection-authentication/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-executionPlan-execution/legend-engine-executionPlan-execution-authorizer/target/classes:/Users/ahauser/.m2/repository/org/slf4j/jcl-over-slf4j/1.7.25/jcl-over-slf4j-1.7.25.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-execution/legend-engine-xt-relationalStore-h2-1.4.200-execution/target/classes:/Users/ahauser/.m2/repository/com/zaxxer/HikariCP/4.0.3/HikariCP-4.0.3.jar:/Users/ahauser/.m2/repository/io/dropwizard/metrics/metrics-core/4.1.16/metrics-core-4.1.16.jar:/Users/ahauser/.m2/repository/com/h2database/h2/2.1.214/h2-2.1.214.jar:/Users/ahauser/.m2/repository/com/databricks/databricks-jdbc/2.6.27/databricks-jdbc-2.6.27.jar:/Users/ahauser/.m2/repository/com/microsoft/sqlserver/mssql-jdbc/6.2.1.jre7/mssql-jdbc-6.2.1.jre7.jar:/Users/ahauser/.m2/repository/org/postgresql/postgresql/9.4.1208.jre7/postgresql-9.4.1208.jre7.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-generation/legend-engine-xt-relationalStore-protocol/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-execution/legend-engine-xt-relationalStore-executionPlan/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-authentication/legend-engine-xt-authentication-implementation-core/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-authentication/legend-engine-xt-authentication-protocol/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-identity/legend-engine-xt-identity-privateKey/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-testable/legend-engine-test-framework/target/classes:/Users/ahauser/.m2/repository/org/apache/poi/poi-ooxml/4.1.1/poi-ooxml-4.1.1.jar:/Users/ahauser/.m2/repository/org/apache/poi/poi/4.1.1/poi-4.1.1.jar:/Users/ahauser/.m2/repository/org/apache/commons/commons-collections4/4.4/commons-collections4-4.4.jar:/Users/ahauser/.m2/repository/org/apache/commons/commons-math3/3.6.1/commons-math3-3.6.1.jar:/Users/ahauser/.m2/repository/org/apache/poi/poi-ooxml-schemas/4.1.1/poi-ooxml-schemas-4.1.1.jar:/Users/ahauser/.m2/repository/org/apache/xmlbeans/xmlbeans/3.1.0/xmlbeans-3.1.0.jar:/Users/ahauser/.m2/repository/org/apache/commons/commons-compress/1.21/commons-compress-1.21.jar:/Users/ahauser/.m2/repository/com/github/virtuald/curvesapi/1.06/curvesapi-1.06.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-generation/legend-engine-xt-relationalStore-grammar/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-store-relational-grammar/5.36.1/legend-pure-m2-store-relational-grammar-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-compiled-store-relational/5.36.1/legend-pure-runtime-java-extension-compiled-store-relational-5.36.1.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-shared-store-relational/5.36.1/legend-pure-runtime-java-extension-shared-store-relational-5.36.1.jar:/Users/ahauser/.m2/repository/org/apache/tomcat/tomcat-dbcp/10.0.4/tomcat-dbcp-10.0.4.jar:/Users/ahauser/.m2/repository/org/apache/tomcat/tomcat-juli/10.0.4/tomcat-juli-10.0.4.jar:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-runtime-java-extension-compiled-dsl-store/5.36.1/legend-pure-runtime-java-extension-compiled-dsl-store-5.36.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-platform-modular-generation/legend-engine-pure-platform-store-relational-java/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-generation/legend-engine-xt-relationalStore-pure/legend-engine-xt-relationalStore-core-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-service/legend-engine-language-pure-dsl-service-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-data-space/legend-engine-xt-data-space-pure-metamodel/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-diagram/legend-engine-xt-diagram-pure-metamodel/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-json/legend-engine-xt-json-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-testable/legend-engine-test-fct/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-external-format/legend-engine-external-format-language/legend-engine-external-format-compiler/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-external-format/legend-engine-external-format-language/legend-engine-external-format-core/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-duckdb/legend-engine-xt-relationalStore-duckdb-PCT/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-duckdb/legend-engine-xt-relationalStore-duckdb-protocol/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-standard/legend-engine-pure-functions-standard-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-relation/legend-engine-pure-functions-relation-pure/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-tds-grammar/5.36.1/legend-pure-m2-dsl-tds-grammar-5.36.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-PCT/legend-engine-pure-functions-relationalStore-PCT-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-PCT/legend-engine-pure-runtime-java-extension-compiled-functions-relationalStore-PCT/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-legendCompiler/legend-engine-pure-runtime-java-extension-compiled-functions-legendCompiler/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-legendCompiler/legend-engine-pure-functions-legendCompiler-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-pure/legend-engine-pure-code-functions-legendCompiler/legend-engine-pure-runtime-java-extension-shared-functions-legendCompiler/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-PCT/legend-engine-pure-runtime-java-extension-shared-functions-relationalStore-PCT/target/classes:/Users/ahauser/.m2/repository/org/finos/legend/pure/legend-pure-m2-dsl-tds-pure/5.36.1/legend-pure-m2-dsl-tds-pure-5.36.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-h2/legend-engine-xt-relationalStore-h2-PCT/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-postgres/legend-engine-xt-relationalStore-postgres-PCT/target/classes:/Users/ahauser/.m2/repository/org/testcontainers/testcontainers/1.18.3/testcontainers-1.18.3.jar:/Users/ahauser/.m2/repository/org/rnorth/duct-tape/duct-tape/1.0.8/duct-tape-1.0.8.jar:/Users/ahauser/.m2/repository/org/jetbrains/annotations/17.0.0/annotations-17.0.0.jar:/Users/ahauser/.m2/repository/com/github/docker-java/docker-java-api/3.3.0/docker-java-api-3.3.0.jar:/Users/ahauser/.m2/repository/com/github/docker-java/docker-java-transport-zerodep/3.3.0/docker-java-transport-zerodep-3.3.0.jar:/Users/ahauser/.m2/repository/com/github/docker-java/docker-java-transport/3.3.0/docker-java-transport-3.3.0.jar:/Users/ahauser/.m2/repository/net/java/dev/jna/jna/5.12.1/jna-5.12.1.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-postgres/legend-engine-xt-relationalStore-postgres-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-postgres/legend-engine-xt-relationalStore-postgres-execution/target/classes:/Users/ahauser/.m2/repository/org/testcontainers/postgresql/1.18.3/postgresql-1.18.3.jar:/Users/ahauser/.m2/repository/org/testcontainers/jdbc/1.18.3/jdbc-1.18.3.jar:/Users/ahauser/.m2/repository/org/testcontainers/database-commons/1.18.3/database-commons-1.18.3.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-snowflake/legend-engine-xt-relationalStore-snowflake-PCT/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-shared/legend-engine-shared-vault/legend-engine-shared-vault-aws/target/classes:/Users/ahauser/.m2/repository/software/amazon/awssdk/auth/2.17.129/auth-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/http-client-spi/2.17.129/http-client-spi-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/eventstream/eventstream/1.0.1/eventstream-1.0.1.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/secretsmanager/2.17.129/secretsmanager-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/aws-json-protocol/2.17.129/aws-json-protocol-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/protocol-core/2.17.129/protocol-core-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/aws-core/2.17.129/aws-core-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/metrics-spi/2.17.129/metrics-spi-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/apache-client/2.17.129/apache-client-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/regions/2.17.129/regions-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/annotations/2.17.129/annotations-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/utils/2.17.129/utils-2.17.129.jar:/Users/ahauser/.m2/repository/org/reactivestreams/reactive-streams/1.0.3/reactive-streams-1.0.3.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/sdk-core/2.17.129/sdk-core-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/profiles/2.17.129/profiles-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/json-utils/2.17.129/json-utils-2.17.129.jar:/Users/ahauser/.m2/repository/software/amazon/awssdk/third-party-jackson-core/2.17.129/third-party-jackson-core-2.17.129.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-snowflake/legend-engine-xt-relationalStore-snowflake-protocol/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-snowflake/legend-engine-xt-relationalStore-snowflake-grammar/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-snowflake/legend-engine-xt-relationalStore-snowflake-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-snowflake/legend-engine-xt-relationalStore-snowflake-execution/target/classes:/Users/ahauser/.m2/repository/net/snowflake/snowflake-jdbc/3.13.5/snowflake-jdbc-3.13.5.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-duckdb/legend-engine-xt-relationalStore-duckdb-execution/target/classes:/Users/ahauser/.m2/repository/org/duckdb/duckdb_jdbc/1.0.0/duckdb_jdbc-1.0.0.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-duckdb/legend-engine-xt-relationalStore-duckdb-grammar/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-xts-relationalStore/legend-engine-xt-relationalStore-dbExtension/legend-engine-xt-relationalStore-duckdb/legend-engine-xt-relationalStore-duckdb-pure/target/classes:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-shared/legend-engine-shared-core/target/classes:/Users/ahauser/.m2/repository/javax/ws/rs/javax.ws.rs-api/2.0.1/javax.ws.rs-api-2.0.1.jar:/Users/ahauser/.m2/repository/io/zipkin/reporter2/zipkin-reporter/2.15.0/zipkin-reporter-2.15.0.jar:/Users/ahauser/.m2/repository/io/zipkin/zipkin2/zipkin/2.21.1/zipkin-2.21.1.jar:/Users/ahauser/.m2/repository/org/apache/httpcomponents/httpclient/4.5.13/httpclient-4.5.13.jar:/Users/ahauser/.m2/repository/org/apache/httpcomponents/httpcore/4.4.13/httpcore-4.4.13.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-identity/legend-engine-identity-core/target/classes:/Users/ahauser/.m2/repository/org/eclipse/collections/eclipse-collections/10.2.0/eclipse-collections-10.2.0.jar:/Users/ahauser/.m2/repository/org/eclipse/collections/eclipse-collections-api/10.2.0/eclipse-collections-api-10.2.0.jar:/Users/ahauser/.m2/repository/org/jline/jline/3.26.3/jline-3.26.3.jar:/Users/ahauser/Documents/work/legend/legend-engine/legend-engine-core/legend-engine-core-base/legend-engine-core-language-pure/legend-engine-protocol/target/classes org.finos.legend.engine.repl.relational.client.RClient"
    print(f"Starting REPL with command: {cmd}")

    repl_process = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def read_output():
        while repl_process.poll() is None:
            line = repl_process.stdout.readline()
            if line:
                repl_output_queue.put(line)
                print(f"REPL output: {line.strip()}")
                if "REPL ready" in line or "Press 'Enter'" in line or "legend" in line.lower():
                    repl_ready.set()

    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()

    print("Waiting for REPL to be ready...")
    wait_start = time.time()
    max_wait = 30  # seconds

    if not repl_ready.wait(timeout=max_wait):
        print("WARNING: REPL startup may not be complete yet. Sending test command...")
        try:
            repl_process.stdin.write("\n")
            repl_process.stdin.flush()
            time.sleep(5)
            if not repl_ready.is_set():
                print("WARNING: REPL still not ready after additional wait time.")
            else:
                print("REPL is now ready to accept commands.")
        except Exception as e:
            print(f"Error checking REPL readiness: {e}")
    else:
        print("REPL is ready to accept commands.")

    try:
        print("Sending test command to verify REPL is responsive...")
        repl_process.stdin.write("help\n")
        repl_process.stdin.flush()

        verification_timeout = time.time() + 10
        while time.time() < verification_timeout:
            try:
                output = repl_output_queue.get(timeout=0.5)
                if output and ("Available commands" in output or "help" in output):
                    print("REPL verified as responsive!")
                    break
            except queue.Empty:
                continue

        time.sleep(2)
    except Exception as e:
        print(f"Error sending verification command: {e}")

    return repl_process


def send_to_repl(command, timeout=10):
    """Send a command to the running REPL process."""
    global repl_process, repl_ready

    if repl_process is None or repl_process.poll() is not None:
        print("Starting REPL...")
        start_repl()

    if not repl_ready.is_set():
        print("Waiting for REPL to be ready before sending command...")
        if not repl_ready.wait(timeout=30):
            print("WARNING: REPL may not be fully ready, but attempting to send command anyway.")

    print(f"Sending to REPL: {command}")

    try:
        try:
            while True:
                repl_output_queue.get_nowait()
        except queue.Empty:
            pass

        repl_process.stdin.write(command + "\n")
        repl_process.stdin.flush()

        print("Waiting for REPL response...")
        wait_start = time.time()
        max_wait = 20  # Increased timeout for complex queries

        time.sleep(1)

        output = []
        consecutive_empty_count = 0
        max_consecutive_empty = 3  # Wait for this many consecutive empty reads before concluding

        if command.startswith("#>"):
            max_wait = 60  # Much longer timeout for Pure expressions with debug output
            max_consecutive_empty = 8  # More patience for Pure expressions with verbose output

        while time.time() - wait_start < max_wait:
            try:
                line = repl_output_queue.get(timeout=0.5)
                output.append(line)
                print(f"Received: {line.strip()}")
                wait_start = time.time()  # Reset wait timer when we get output
                consecutive_empty_count = 0  # Reset empty counter
            except queue.Empty:
                consecutive_empty_count += 1
                if output and consecutive_empty_count >= max_consecutive_empty:
                    print(f"No more output after {consecutive_empty_count} consecutive empty reads")
                    break
                continue

        result = "".join(output)
        if not result:
            print("No output received from REPL within timeout period.")
            return "Command sent to REPL (no output within timeout period)"

        print(f"Total output length: {len(result)} characters, {len(output)} lines")
        return result

    except Exception as e:
        print(f"Error sending command to REPL: {e}")
        return f"Error: {str(e)}"


def load_csv_to_repl(csv_path, connection_name, table_name):
    """
    Load a CSV file into the REPL.

    Args:
        csv_path: Path to the CSV file
        connection_name: Name of the connection to use
        table_name: Name of the table to create

    Returns:
        dict: The parsed JSON response from the REPL
    """
    load_cmd = f"load {csv_path} {connection_name} {table_name}"
    return send_to_repl(load_cmd)


def execute_pure_query(pure_query):
    """
    Execute a Pure Relation query in the REPL.

    Args:
        pure_query: The Pure Relation query to execute

    Returns:
        dict: The parsed JSON response from the REPL
    """
    return send_to_repl(pure_query)


def is_repl_running():
    """
    Check if the Pure Relation REPL is running.

    Returns:
        bool: True if the REPL is running, False otherwise
    """
    if repl_process is None:
        start_repl()

    return repl_process != None
