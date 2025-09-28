package com.jd.genie.data.jdbc.dialect;

public interface JdbcDialectFactory {

    boolean acceptsURL(String url);

    JdbcDialect create();
}
