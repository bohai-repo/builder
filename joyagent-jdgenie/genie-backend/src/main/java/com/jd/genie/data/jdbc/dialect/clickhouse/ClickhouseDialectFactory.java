package com.jd.genie.data.jdbc.dialect.clickhouse;


import com.google.auto.service.AutoService;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;
import com.jd.genie.data.jdbc.dialect.JdbcDialectFactory;

@AutoService(JdbcDialectFactory.class)
public class ClickhouseDialectFactory implements JdbcDialectFactory {
    @Override
    public boolean acceptsURL(String url) {
        return url.startsWith("jdbc:ch:") || url.startsWith("jdbc:clickhouse:");
    }

    @Override
    public JdbcDialect create() {
        return new ClickhouseDialect();
    }
}
