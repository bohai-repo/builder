package com.jd.genie.data.jdbc.dialect.h2;



import com.jd.genie.data.jdbc.dialect.DialectEnum;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;

import java.util.Properties;

public class H2Dialect implements JdbcDialect {
    @Override
    public DialectEnum dialectName() {
        return DialectEnum.H2;
    }

    @Override
    public String driverName() {
        return "org.h2.Driver";
    }

    @Override
    public Properties defaultProperties() {
        Properties properties = new Properties();
        properties.setProperty("remarks", "true");
        properties.setProperty("useInformationSchema", "true");
        return properties;
    }
}
