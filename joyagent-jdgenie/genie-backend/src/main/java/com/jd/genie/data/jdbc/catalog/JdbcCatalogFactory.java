package com.jd.genie.data.jdbc.catalog;


import com.jd.genie.data.jdbc.dialect.DialectEnum;

public interface JdbcCatalogFactory {

    DialectEnum jdbcDialect();

    /**
     * Creates a {@link JdbcCatalog} using the options.
     */
    JdbcCatalog createCatalog();
}
