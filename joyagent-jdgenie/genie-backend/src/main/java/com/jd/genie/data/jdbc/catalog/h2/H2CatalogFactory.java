package com.jd.genie.data.jdbc.catalog.h2;

import com.google.auto.service.AutoService;
import com.jd.genie.data.jdbc.catalog.JdbcCatalog;
import com.jd.genie.data.jdbc.catalog.JdbcCatalogFactory;
import com.jd.genie.data.jdbc.dialect.DialectEnum;


@AutoService(JdbcCatalogFactory.class)
public class H2CatalogFactory implements JdbcCatalogFactory {
    @Override
    public DialectEnum jdbcDialect() {
        return DialectEnum.H2;
    }

    @Override
    public JdbcCatalog createCatalog() {
        return new H2SqlCatalog();
    }
}
