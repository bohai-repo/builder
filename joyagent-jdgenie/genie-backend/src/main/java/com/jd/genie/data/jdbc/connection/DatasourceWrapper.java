package com.jd.genie.data.jdbc.connection;

import com.jd.genie.data.jdbc.catalog.JdbcCatalog;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;
import lombok.Data;

import javax.sql.DataSource;

@Data
public class DatasourceWrapper {

    private DataSource dataSource;

    private JdbcDialect jdbcDialect;

    private JdbcCatalog catalog;

    private Long freshTime;
}
